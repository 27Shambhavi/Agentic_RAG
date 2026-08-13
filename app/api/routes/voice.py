from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from app.tools.voice_tool import (
    transcribe_audio
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


# =========================================================
# ALLOWED AUDIO
# =========================================================

ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".mpeg",
    ".mp4",
    ".m4a",
    ".webm",
    ".ogg",
}


# =========================================================
# TRANSCRIBE
# =========================================================

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # VALIDATE FILENAME
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Audio filename is missing.",
        )


    # -----------------------------------------------------
    # VALIDATE EXTENSION
    # -----------------------------------------------------

    extension = (
        "." +
        file.filename.rsplit(
            ".",
            1
        )[-1].lower()
    )


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                "Supported: WAV, MP3, MPEG, "
                "MP4, M4A, WEBM, OGG."
            ),
        )


    try:

        # -------------------------------------------------
        # READ AUDIO
        # -------------------------------------------------

        audio_bytes = await file.read()


        if not audio_bytes:

            raise HTTPException(
                status_code=400,
                detail="Audio file is empty.",
            )


        # -------------------------------------------------
        # MISTRAL VOXTRAL
        # -------------------------------------------------

        result = transcribe_audio(
            audio_bytes=audio_bytes,
            filename=file.filename,
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {
            "status": "success",

            "filename": file.filename,

            "text": result.get(
                "text",
                ""
            ),

            "language": result.get(
                "language"
            ),

            "model": result.get(
                "model",
                "voxtral-mini-latest"
            ),
        }


    except HTTPException:
        raise


    except Exception as error:

        print(
            "\nVOICE TRANSCRIPTION ERROR:"
        )

        print(
            repr(error)
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        )