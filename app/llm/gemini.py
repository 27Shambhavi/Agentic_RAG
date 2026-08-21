from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY / GOOGLE_API_KEY was not found.\n"
        "Put it in your .env file."
    )


# ============================================================
# CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# CONFIG
# ============================================================

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


# ============================================================
# LLM
# ============================================================

class GeminiLLM:

    def __init__(
        self,
        model: str = PRIMARY_MODEL,
    ):
        self.model = model

        self.fallback_models = [
            model_name
            for model_name in FALLBACK_MODELS
            if model_name != model
        ]

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        prompt: str,
        max_retries: int = 3,
    ) -> str:

        if not isinstance(prompt, str):
            raise TypeError(
                "Gemini prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Gemini prompt cannot be empty."
            )

        errors: list[str] = []

        # ====================================================
        # PRIMARY MODEL
        # ====================================================

        for attempt in range(max_retries):

            try:

                print(
                    f"[LLM] model={self.model} "
                    f"attempt={attempt + 1}/{max_retries}"
                )

                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if text and text.strip():

                    return text.strip()

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                error_text = str(error)

                errors.append(
                    f"{self.model}: {error_text}"
                )

                print(
                    "[LLM ERROR]",
                    repr(error),
                )

                lower = error_text.lower()

                retryable = any(
                    marker in lower
                    for marker in (
                        "429",
                        "503",
                        "504",
                        "unavailable",
                        "resource exhausted",
                        "timeout",
                        "temporarily",
                        "deadline",
                    )
                )

                if (
                    not retryable
                    or attempt == max_retries - 1
                ):
                    break

                wait_time = 2 ** attempt

                print(
                    f"[LLM] retrying in {wait_time}s"
                )

                time.sleep(
                    wait_time
                )

        # ====================================================
        # FALLBACK MODELS
        # ====================================================

        for fallback_model in self.fallback_models:

            try:

                print(
                    "[LLM] fallback model:",
                    fallback_model,
                )

                response = client.models.generate_content(
                    model=fallback_model,
                    contents=prompt,
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if text and text.strip():

                    print(
                        "[LLM] fallback succeeded:",
                        fallback_model,
                    )

                    return text.strip()

                errors.append(
                    f"{fallback_model}: empty response"
                )

            except Exception as error:

                errors.append(
                    f"{fallback_model}: {error}"
                )

                print(
                    "[LLM FALLBACK ERROR]",
                    fallback_model,
                    repr(error),
                )

        # ====================================================
        # FINAL ERROR
        # ====================================================

        raise RuntimeError(
            "Gemini generation failed.\n"
            + "\n".join(errors)
        )


# ============================================================
# SINGLE INSTANCE
# ============================================================

llm = GeminiLLM()