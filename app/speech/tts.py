import os
import uuid

import pyttsx3


# =========================================================
# TEXT TO SPEECH
# =========================================================

def text_to_speech(
    text: str,
    output_dir: str = "data/audio"
) -> str:

    if not text.strip():

        raise ValueError(
            "Text cannot be empty."
        )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        output_dir,
        f"response_{uuid.uuid4().hex}.wav"
    )


    # -----------------------------------------------------
    # ENGINE
    # -----------------------------------------------------

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        165
    )

    engine.setProperty(
        "volume",
        1.0
    )


    # -----------------------------------------------------
    # SAVE AUDIO
    # -----------------------------------------------------

    engine.save_to_file(
        text,
        output_path
    )

    engine.runAndWait()

    engine.stop()


    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "Failed to generate speech."
        )

    return output_path