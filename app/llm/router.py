from app.llm.gemini import llm as gemini_llm
from app.llm.mistral import mistral_llm


class LLMRouter:

    def generate(self, prompt: str) -> str:

        # -------------------------------------------------
        # TRY GEMINI
        # -------------------------------------------------

        try:

            return gemini_llm.generate(
                prompt
            )

        except Exception as gemini_error:

            error_text = str(
                gemini_error
            ).lower()

            # ---------------------------------------------
            # GEMINI QUOTA / API FAILURE
            # ---------------------------------------------

            if (
                "429" in error_text
                or "resource_exhausted" in error_text
                or "quota" in error_text
            ):

                print(
                    "Gemini quota unavailable. "
                    "Switching to Mistral..."
                )

            else:

                print(
                    "Gemini failed. "
                    "Switching to Mistral..."
                )


        # -------------------------------------------------
        # MISTRAL FALLBACK
        # -------------------------------------------------

        try:

            return mistral_llm.generate(
                prompt
            )

        except Exception as mistral_error:

            raise RuntimeError(
                "Both Gemini and Mistral failed.\n"
                f"Gemini error: {gemini_error}\n"
                f"Mistral error: {mistral_error}"
            )


# =========================================================
# SINGLE INSTANCE
# =========================================================

llm_router = LLMRouter()