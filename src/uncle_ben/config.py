from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    whisper_model: str = Field(default="medium")
    whisper_device: str = Field(default="auto")
    whisper_compute_type: str = Field(default="int8")
    whisper_beam_size: int = Field(default=5)
    whisper_best_of: int = Field(default=5)
    whisper_temperature: float = Field(default=0.0)
    whisper_vad_filter: bool = Field(default=True)
    whisper_condition_on_previous_text: bool = Field(default=True)
    whisper_initial_prompt: str = Field(
        default="Русская речь. Команды ассистента: Эй Бэн, включи диктовку, выключи диктовку."
    )
    language: str = Field(default="ru")
    wake_words: list[str] = Field(default_factory=lambda: ["эй бэн", "эй бен", "hey ben"])
    active_control_seconds: int = Field(default=25)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5:3b-instruct")
    use_diarization: bool = Field(default=False)
    hf_token: str = Field(default="")
    diarization_device: str = Field(default="cpu")
    input_device: str = Field(default="")
    sample_rate: int = Field(default=16000)
    frame_ms: int = Field(default=30)
    vad_aggressiveness: int = Field(default=2)
    min_segment_ms: int = Field(default=600)
    max_segment_ms: int = Field(default=10000)
    silence_padding_ms: int = Field(default=450)
    log_level: str = Field(default="INFO")
    events_log_path: str = Field(default="logs/events.jsonl")
    risky_actions: list[str] = Field(default_factory=lambda: ["move_mouse", "switch_window"])
    confirm_words: list[str] = Field(default_factory=lambda: ["подтверждаю", "да", "выполни"])
    cancel_words: list[str] = Field(default_factory=lambda: ["отмена", "нет", "стоп"])
    confirmation_ttl_seconds: int = Field(default=8)
    dictation_enable_phrases: list[str] = Field(default_factory=lambda: ["включи диктовку", "начни диктовку"])
    dictation_disable_phrases: list[str] = Field(default_factory=lambda: ["выключи диктовку", "останови диктовку", "стоп диктовка"])
    voice_feedback_enabled: bool = Field(default=True)
    voice_feedback_voice: str = Field(default="Milena")
    voice_feedback_rate: int = Field(default=180)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    load_dotenv()
    wake_words_env = os.getenv("WAKE_WORDS", "эй бэн,эй бен,hey ben")
    wake_words = [chunk.strip().lower() for chunk in wake_words_env.split(",") if chunk.strip()]
    risky_actions_env = os.getenv("RISKY_ACTIONS", "move_mouse,switch_window")
    risky_actions = [chunk.strip().lower() for chunk in risky_actions_env.split(",") if chunk.strip()]
    confirm_words_env = os.getenv("CONFIRM_WORDS", "подтверждаю,да,выполни")
    confirm_words = [chunk.strip().lower() for chunk in confirm_words_env.split(",") if chunk.strip()]
    cancel_words_env = os.getenv("CANCEL_WORDS", "отмена,нет,стоп")
    cancel_words = [chunk.strip().lower() for chunk in cancel_words_env.split(",") if chunk.strip()]
    dictation_enable_env = os.getenv("DICTATION_ENABLE_PHRASES", "включи диктовку,начни диктовку")
    dictation_enable_phrases = [chunk.strip().lower() for chunk in dictation_enable_env.split(",") if chunk.strip()]
    dictation_disable_env = os.getenv("DICTATION_DISABLE_PHRASES", "выключи диктовку,останови диктовку,стоп диктовка")
    dictation_disable_phrases = [chunk.strip().lower() for chunk in dictation_disable_env.split(",") if chunk.strip()]
    return AppConfig(
        whisper_model=os.getenv("WHISPER_MODEL", "medium"),
        whisper_device=os.getenv("WHISPER_DEVICE", "auto"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        whisper_beam_size=int(os.getenv("WHISPER_BEAM_SIZE", "5")),
        whisper_best_of=int(os.getenv("WHISPER_BEST_OF", "5")),
        whisper_temperature=float(os.getenv("WHISPER_TEMPERATURE", "0.0")),
        whisper_vad_filter=os.getenv("WHISPER_VAD_FILTER", "true").lower() == "true",
        whisper_condition_on_previous_text=os.getenv("WHISPER_CONDITION_ON_PREVIOUS_TEXT", "true").lower() == "true",
        whisper_initial_prompt=os.getenv(
            "WHISPER_INITIAL_PROMPT",
            "Русская речь. Команды ассистента: Эй Бэн, включи диктовку, выключи диктовку.",
        ),
        language=os.getenv("LANGUAGE", "ru"),
        wake_words=wake_words,
        active_control_seconds=int(os.getenv("ACTIVE_CONTROL_SECONDS", "25")),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct"),
        use_diarization=os.getenv("USE_DIARIZATION", "false").lower() == "true",
        hf_token=os.getenv("HF_TOKEN", ""),
        diarization_device=os.getenv("DIARIZATION_DEVICE", "cpu"),
        input_device=os.getenv("INPUT_DEVICE", ""),
        sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
        frame_ms=int(os.getenv("FRAME_MS", "30")),
        vad_aggressiveness=int(os.getenv("VAD_AGGRESSIVENESS", "2")),
        min_segment_ms=int(os.getenv("MIN_SEGMENT_MS", "600")),
        max_segment_ms=int(os.getenv("MAX_SEGMENT_MS", "10000")),
        silence_padding_ms=int(os.getenv("SILENCE_PADDING_MS", "450")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        events_log_path=os.getenv("EVENTS_LOG_PATH", "logs/events.jsonl"),
        risky_actions=risky_actions,
        confirm_words=confirm_words,
        cancel_words=cancel_words,
        confirmation_ttl_seconds=int(os.getenv("CONFIRMATION_TTL_SECONDS", "8")),
        dictation_enable_phrases=dictation_enable_phrases,
        dictation_disable_phrases=dictation_disable_phrases,
        voice_feedback_enabled=os.getenv("VOICE_FEEDBACK_ENABLED", "true").lower() == "true",
        voice_feedback_voice=os.getenv("VOICE_FEEDBACK_VOICE", "Milena"),
        voice_feedback_rate=int(os.getenv("VOICE_FEEDBACK_RATE", "180")),
    )
