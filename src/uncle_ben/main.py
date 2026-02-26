from __future__ import annotations

import logging
from datetime import datetime

from .audio import AudioCapture, VADSegmenter
from .config import get_config
from .controller import WakeWordController
from .diarization import SpeakerRoleResolver
from .dictation import DictationController
from .intent_router import IntentRouter
from .logging_utils import EventLogger
from .mac_actions import MacActionExecutor
from .models import ActionCommand, TranscriptEvent
from .safety import ConfirmationGuard
from .transcriber import WhisperTranscriber
from .voice_feedback import VoiceFeedback


def run() -> None:
    cfg = get_config()

    logging.basicConfig(
        level=getattr(logging, cfg.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("uncle_ben")

    event_logger = EventLogger(cfg.events_log_path)

    capture = AudioCapture(
        sample_rate=cfg.sample_rate,
        frame_ms=cfg.frame_ms,
        input_device=cfg.input_device,
    )
    segmenter = VADSegmenter(
        source_queue=capture.queue,
        sample_rate=cfg.sample_rate,
        frame_ms=cfg.frame_ms,
        aggressiveness=cfg.vad_aggressiveness,
        min_segment_ms=cfg.min_segment_ms,
        max_segment_ms=cfg.max_segment_ms,
        silence_padding_ms=cfg.silence_padding_ms,
    )
    transcriber = WhisperTranscriber(
        model_name=cfg.whisper_model,
        language=cfg.language,
        device=cfg.whisper_device,
        compute_type=cfg.whisper_compute_type,
        beam_size=cfg.whisper_beam_size,
        best_of=cfg.whisper_best_of,
        temperature=cfg.whisper_temperature,
        vad_filter=cfg.whisper_vad_filter,
        condition_on_previous_text=cfg.whisper_condition_on_previous_text,
        initial_prompt=cfg.whisper_initial_prompt,
    )
    role_resolver = SpeakerRoleResolver(cfg.use_diarization, cfg.hf_token, cfg.diarization_device)
    controller = WakeWordController(cfg.wake_words, cfg.active_control_seconds)
    intent_router = IntentRouter(cfg.ollama_base_url, cfg.ollama_model)
    executor = MacActionExecutor()
    confirmation_guard = ConfirmationGuard(
        risky_actions=cfg.risky_actions,
        confirm_words=cfg.confirm_words,
        cancel_words=cfg.cancel_words,
        ttl_seconds=cfg.confirmation_ttl_seconds,
    )
    dictation_controller = DictationController(
        enable_phrases=cfg.dictation_enable_phrases,
        disable_phrases=cfg.dictation_disable_phrases,
    )
    voice_feedback = VoiceFeedback(
        enabled=cfg.voice_feedback_enabled,
        voice=cfg.voice_feedback_voice,
        rate=cfg.voice_feedback_rate,
    )

    logger.info("Uncle Ben is listening. Say wake word: %s", ", ".join(cfg.wake_words))
    capture.start()

    try:
        while True:
            segment = segmenter.next_segment(timeout=0.5)
            if segment is None:
                continue

            text, language, probability = transcriber.transcribe(segment)
            if not text:
                continue

            speaker = role_resolver.resolve(segment, cfg.sample_rate)
            event = TranscriptEvent(speaker=speaker, text=text, language=language)
            event_logger.emit("transcript", event)
            logger.info("[%s] %s", speaker, text)

            now = datetime.utcnow()
            is_controller, controllable_text = controller.process(
                speaker=speaker,
                text=text,
                now=now,
            )
            if not is_controller:
                continue

            if not controllable_text:
                logger.info("Control granted to %s", speaker)
                voice_feedback.speak("Управление активировано")
                event_logger.emit(
                    "control_granted",
                    {
                        "speaker": speaker,
                        "probability": probability,
                    },
                )
                continue

            if not _is_meaningful_text(controllable_text):
                continue

            if confirmation_guard.pending is not None:
                approved, status = confirmation_guard.handle(
                    speaker=speaker,
                    text=controllable_text,
                    command=ActionCommand(action="none", payload={}, confidence=0.0),
                    now=now,
                )
                event_logger.emit(
                    "confirmation",
                    {
                        "status": status,
                        "speaker": speaker,
                    },
                )

                if approved is None:
                    if status == "confirmation_cancelled":
                        logger.info("Pending action cancelled")
                        voice_feedback.speak("Команда отменена")
                    elif status == "confirmation_timeout":
                        logger.info("Pending action timed out")
                        voice_feedback.speak("Время подтверждения истекло")
                    continue

                logger.info("Confirmation approved")
                voice_feedback.speak("Команда подтверждена")
                result = executor.execute(approved)
                event_logger.emit("action_result", result)
                logger.info("Action: %s -> %s", approved.action, result.message)
                if result.success and approved.action != "none":
                    voice_feedback.speak("Готово")
                elif not result.success:
                    voice_feedback.speak("Не удалось выполнить команду")
                continue

            if dictation_controller.is_active_for(speaker):
                if dictation_controller.should_disable(controllable_text):
                    dictation_controller.deactivate()
                    event_logger.emit("dictation", {"status": "disabled", "speaker": speaker})
                    logger.info("Dictation disabled for %s", speaker)
                    voice_feedback.speak("Диктовка выключена")
                    continue

                dictation_command = ActionCommand(
                    action="dictate_text",
                    payload={"text": controllable_text},
                    confidence=1.0,
                )
                result = executor.execute(dictation_command)
                event_logger.emit("action_result", result)
                logger.info("Dictation text typed: %s", result.message)
                if not result.success:
                    voice_feedback.speak("Не удалось ввести текст")
                continue

            if dictation_controller.should_enable(controllable_text):
                dictation_controller.activate(speaker)
                event_logger.emit("dictation", {"status": "enabled", "speaker": speaker})
                logger.info("Dictation enabled for %s", speaker)
                voice_feedback.speak("Диктовка включена")
                continue

            command = intent_router.route(controllable_text)
            event_logger.emit("intent", command)

            if command.action == "none":
                continue

            approved, status = confirmation_guard.handle(
                speaker=speaker,
                text=controllable_text,
                command=command,
                now=now,
            )
            event_logger.emit(
                "confirmation",
                {
                    "status": status,
                    "speaker": speaker,
                    "action": command.action,
                },
            )
            if approved is None:
                if status == "confirmation_requested":
                    logger.info("Action %s requires confirmation", command.action)
                    voice_feedback.speak("Подтверди выполнение команды")
                continue

            result = executor.execute(approved)
            event_logger.emit("action_result", result)
            logger.info("Action: %s -> %s", approved.action, result.message)
            if result.success and approved.action != "none":
                voice_feedback.speak("Готово")
            elif not result.success:
                voice_feedback.speak("Не удалось выполнить команду")

    except KeyboardInterrupt:
        logger.info("Stopping Uncle Ben...")
    finally:
        capture.stop()


def _is_meaningful_text(text: str) -> bool:
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch.isspace()).strip()
    if len(cleaned) < 3:
        return False
    return any(ch.isalpha() for ch in cleaned)


if __name__ == "__main__":
    run()
