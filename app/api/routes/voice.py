from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import FileResponse

from pydantic import BaseModel, Field

from app.speech.stt import transcribe_audio
from app.speech.tts import text_to_speech


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


# =========================================================
# TTS REQUEST
# =========================================================

class SpeakRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
    )


# =========================================================
# VOICE → TEXT
# =========================================================

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
):

    print(
        "\n=============================================="
    )

    print(
        "       FASTAPI VOICE TRANSCRIPTION"
    )

    print(
        "=============================================="
    )

    print(
        "Filename:",
        file.filename,
    )

    print(
        "Content type:",
        file.content_type,
    )

    # =====================================================
    # READ
    # =====================================================

    try:

        audio_bytes = await file.read()

    except Exception as error:

        print(
            "READ ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not read audio: {error}"
            ),
        )

    print(
        "Received bytes:",
        len(audio_bytes),
    )

    # =====================================================
    # EMPTY
    # =====================================================

    if not audio_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded audio is empty.",
        )

    # =====================================================
    # EXTENSION
    # =====================================================

    original_name = (
        file.filename
        or "voice_recording.wav"
    )

    extension = (
        Path(
            original_name
        ).suffix.lower()
    )

    allowed = {
        ".wav",
        ".mp3",
        ".mpeg",
        ".mp4",
        ".m4a",
        ".webm",
        ".ogg",
    }

    if extension not in allowed:

        extension = ".wav"

    temporary_path = None

    try:

        # =================================================
        # TEMP AUDIO
        # =================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:

            temporary_file.write(
                audio_bytes
            )

            temporary_file.flush()

            temporary_path = (
                temporary_file.name
            )

        print(
            "Temporary file:",
            temporary_path,
        )

        print(
            "Temporary size:",
            os.path.getsize(
                temporary_path
            ),
        )

        # =================================================
        # WHISPER
        # =================================================

        print(
            "\n[VOICE] Running Faster-Whisper..."
        )

        transcript = transcribe_audio(
            temporary_path
        )

        transcript = (
            transcript or ""
        ).strip()

        print(
            "[VOICE] Transcript:",
            transcript,
        )

        # =================================================
        # EMPTY TRANSCRIPT
        # =================================================

        if not transcript:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Audio was received, but "
                    "no understandable speech was detected."
                ),
            )

        # =================================================
        # SUCCESS
        # =================================================

        print(
            "\n[VOICE] STT SUCCESS"
        )

        print(
            "==============================================\n"
        )

        return {

            "status": "success",

            "filename": original_name,

            "text": transcript,

            "transcript": transcript,

            "language": None,

            "model": "faster-whisper-base",
        }

    except HTTPException:

        raise

    except Exception as error:

        print(
            "\n========== WHISPER ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "===================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Speech-to-text failed: {error}"
            ),
        )

    finally:

        if temporary_path:

            try:

                if os.path.exists(
                    temporary_path
                ):

                    os.remove(
                        temporary_path
                    )

            except Exception as error:

                print(
                    "Cleanup error:",
                    repr(error),
                )


# =========================================================
# TEXT → SPEECH
# =========================================================

@router.post("/speak")
async def speak_text(
    request: SpeakRequest,
):

    text = (
        request.text or ""
    ).strip()

    if not text:

        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    print(
        "\n=============================================="
    )

    print(
        "             TEXT TO SPEECH"
    )

    print(
        "=============================================="
    )

    print(
        "Characters:",
        len(text),
    )

    try:

        output_path = text_to_speech(
            text
        )

        if not output_path:

            raise RuntimeError(
                "TTS returned no output path."
            )

        output_path = str(
            output_path
        )

        if not os.path.exists(
            output_path
        ):

            raise RuntimeError(
                "TTS output file does not exist."
            )

        size = os.path.getsize(
            output_path
        )

        print(
            "Audio:",
            output_path,
        )

        print(
            "Size:",
            size,
            "bytes",
        )

        if size == 0:

            raise RuntimeError(
                "TTS generated an empty audio file."
            )

        print(
            "[TTS] SUCCESS"
        )

        print(
            "==============================================\n"
        )

        return FileResponse(

            path=output_path,

            media_type="audio/wav",

            filename="assistant_response.wav",
        )

    except Exception as error:

        print(
            "\n========== TTS ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Text-to-speech failed: {error}"
            ),
        )