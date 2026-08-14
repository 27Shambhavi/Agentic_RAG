import os

from dotenv import load_dotenv
from mistralai.client import Mistral


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()


# =========================================================
# CONFIG
# =========================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)


# =========================================================
# VALIDATE KEY
# =========================================================

if not MISTRAL_API_KEY:

    raise ValueError(
        "MISTRAL_API_KEY not found in .env"
    )


# =========================================================
# CLIENT
# =========================================================

client = Mistral(
    api_key=MISTRAL_API_KEY
)


# =========================================================
# LLM WRAPPER
# =========================================================

class MistralLLM:

    def __init__(
        self,
        model: str = MISTRAL_MODEL,
    ):

        self.model = model


    def generate(
        self,
        prompt: str,
    ) -> str:

        if not prompt or not prompt.strip():

            return ""


        response = client.chat.complete(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )


        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


# =========================================================
# SINGLE INSTANCE
# =========================================================

mistral_llm = MistralLLM()