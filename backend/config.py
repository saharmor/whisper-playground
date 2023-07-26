from diart import PipelineConfig

DIARIZATION_PIPELINE_CONFIG = PipelineConfig(
    duration=5,
    step=0.5,
    latency="min",
    tau_active=0.5,
    rho_update=0.1,
    delta_new=0.57
)
SAMPLE_RATE = 16000
NON_SPECIFIC_MODELS = ["large", "large-v1", "large-v2"]

# Language code mapping
LANGUAGE_MAPPING = {
    "english": "en",
    "chinese": "zh",
    "german": "de",
    "spanish": "es",
    "russian": "ru",
    "korean": "ko",
    "french": "fr",
    "japanese": "ja",
    "portuguese": "pt",
    "turkish": "tr",
    "polish": "pl",
    "catalan": "ca",
    "dutch": "nl",
    "arabic": "ar",
    "swedish": "sv",
    "italian": "it",
}
