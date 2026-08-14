import os
import time

from dotenv import load_dotenv
from google import genai


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# =========================================================
# CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# LLM
# =========================================================

class GeminiLLM:

    def __init__(
        self,
        model: str = "gemini-3.5-flash",
    ):

        self.model = model

        # Fallback models.
        #
        # We don't blindly switch models immediately.
        # First retry the primary model because 503 is often
        # temporary.
        self.fallback_models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
        ]


    # =====================================================
    # GENERATE
    # =====================================================

    def generate(
        self,
        prompt: str,
    ) -> str:

        if not prompt or not prompt.strip():

            raise ValueError(
                "Gemini prompt cannot be empty."
            )

        prompt = prompt.strip()

        last_error = None

        # =================================================
        # PRIMARY MODEL
        # =================================================

        for attempt in range(3):

            try:

                print(
                    f"[LLM] Model: {self.model} "
                    f"| Attempt: {attempt + 1}/3"
                )

                response = (
                    client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if text:

                    return text.strip()

                raise RuntimeError(
                    "Gemini returned no text."
                )

            except Exception as error:

                last_error = error

                error_text = str(
                    error
                ).lower()

                print(
                    "[LLM ERROR]",
                    repr(error),
                )

                # -----------------------------------------
                # Retry temporary server/rate errors
                # -----------------------------------------

                temporary_error = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "429" in error_text
                    or "resource exhausted" in error_text
                    or "timeout" in error_text
                )

                if not temporary_error:

                    break

                if attempt < 2:

                    wait_time = (
                        2 ** attempt
                    )

                    print(
                        f"[LLM] Temporary error. "
                        f"Retrying in {wait_time}s..."
                    )

                    time.sleep(
                        wait_time
                    )


        # =================================================
        # FALLBACK MODELS
        # =================================================

        for fallback_model in self.fallback_models:

            # Don't repeat the primary model.
            if fallback_model == self.model:
                continue

            try:

                print(
                    "[LLM] Trying fallback model:",
                    fallback_model,
                )

                response = (
                    client.models.generate_content(
                        model=fallback_model,
                        contents=prompt,
                    )
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if text:

                    print(
                        "[LLM] Fallback model succeeded:",
                        fallback_model,
                    )

                    return text.strip()

                print(
                    "[LLM] Fallback model returned no text:",
                    fallback_model,
                )

            except Exception as error:

                last_error = error

                print(
                    "[LLM FALLBACK ERROR]",
                    fallback_model,
                    repr(error),
                )

                continue


        # =================================================
        # FINAL ERROR
        # =================================================

        raise RuntimeError(
            "Gemini generation failed after "
            "retries and fallback models."
        ) from last_error


# =========================================================
# SINGLE INSTANCE
# =========================================================

llm = GeminiLLM()