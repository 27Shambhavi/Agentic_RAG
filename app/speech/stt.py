from pathlib import Path

from faster_whisper import WhisperModel


# =========================================================
# MODEL
# =========================================================

MODEL_SIZE = "base"

whisper_model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8",
)


# =========================================================
# SPEECH TO TEXT
# =========================================================

def transcribe_audio(
    audio_path: str
) -> str:

    path = Path(audio_path)

    if not path.exists():

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    segments, info = whisper_model.transcribe(
        str(path),
        beam_size=5,
        vad_filter=True,
    )

    text_parts = []

    for segment in segments:

        text = segment.text.strip()

        if text:

            text_parts.append(text)

    return " ".join(
        text_parts
    ).strip()