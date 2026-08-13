import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# CONFIG
# =========================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MODEL_NAME = "voxtral-mini-latest"


# =========================================================
# VALIDATE API KEY
# =========================================================

if not MISTRAL_API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY not found in .env"
    )


# =========================================================
# MISTRAL CLIENT
# =========================================================

client = Mistral(
    api_key=MISTRAL_API_KEY
)


# =========================================================
# TRANSCRIBE AUDIO
# =========================================================

def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.wav",
) -> dict:

    if not audio_bytes:
        raise ValueError(
            "Audio data is empty."
        )

    # -----------------------------------------------------
    # CREATE TEMP AUDIO FILE
    # -----------------------------------------------------

    suffix = Path(filename).suffix.lower()

    if not suffix:
        suffix = ".wav"

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(
                audio_bytes
            )

            temp_file.flush()

            temp_path = temp_file.name


        # -------------------------------------------------
        # OPEN AUDIO AS BINARY FILE
        # -------------------------------------------------

        with open(
            temp_path,
            "rb"
        ) as audio_file:

            response = (
                client
                .audio
                .transcriptions
                .complete(
                    model=MODEL_NAME,

                    file={
                        "content": audio_file,
                        "file_name": filename,
                    },

                    diarize=False,
                )
            )


        # -------------------------------------------------
        # EXTRACT RESPONSE
        # -------------------------------------------------

        text = getattr(
            response,
            "text",
            ""
        )

        language = getattr(
            response,
            "language",
            None
        )

        model = getattr(
            response,
            "model",
            MODEL_NAME
        )


        return {
            "text": text or "",
            "language": language,
            "model": model,
        }


    except Exception as error:

        raise RuntimeError(
            f"Mistral transcription failed: {error}"
        ) from error


    finally:

        # -------------------------------------------------
        # DELETE TEMP FILE
        # -------------------------------------------------

        if temp_path:

            try:

                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )

            except Exception:
                pass