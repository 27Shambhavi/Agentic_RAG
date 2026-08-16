import os
import uuid

import pyttsx3


# =========================================================
# TEXT → SPEECH
# =========================================================

def text_to_speech(
    text: str,
    output_dir: str = "data/audio",
) -> str:

    text = (
        text or ""
    ).strip()

    if not text:

        raise ValueError(
            "Text cannot be empty."
        )

    # =====================================================
    # OUTPUT DIRECTORY
    # =====================================================

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    output_path = os.path.abspath(
        os.path.join(
            output_dir,
            f"assistant_{uuid.uuid4().hex}.wav",
        )
    )

    print(
        "[TTS] Generating:",
        output_path,
    )

    # =====================================================
    # ENGINE
    # =====================================================

    engine = pyttsx3.init()

    try:

        # -------------------------------------------------
        # RATE
        # -------------------------------------------------

        engine.setProperty(
            "rate",
            165,
        )

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        engine.setProperty(
            "volume",
            1.0,
        )

        # -------------------------------------------------
        # VOICE
        # -------------------------------------------------

        voices = engine.getProperty(
            "voices"
        )

        if voices:

            # Windows usually has multiple voices.
            # Use the first available one.

            try:

                engine.setProperty(
                    "voice",
                    voices[0].id,
                )

            except Exception:

                pass

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        engine.save_to_file(
            text,
            output_path,
        )

        engine.runAndWait()

    finally:

        try:

            engine.stop()

        except Exception:

            pass

    # =====================================================
    # VALIDATE
    # =====================================================

    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "TTS failed to create audio file."
        )

    file_size = os.path.getsize(
        output_path
    )

    if file_size == 0:

        raise RuntimeError(
            "TTS created an empty audio file."
        )

    print(
        "[TTS] Created:",
        output_path,
    )

    print(
        "[TTS] Size:",
        file_size,
        "bytes",
    )

    return output_path