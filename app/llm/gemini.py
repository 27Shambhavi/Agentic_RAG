from google import genai

from app.config.settings import settings


# =========================================================
# GEMINI CLIENT
# =========================================================

class GeminiLLM:

    def __init__(self):

        if not settings.GEMINI_API_KEY:

            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL


    # =====================================================
    # GENERATE
    # =====================================================

    def generate(
        self,
        prompt: str
    ) -> str:

        if not prompt.strip():

            return ""


        response = (
            self.client
            .models
            .generate_content(
                model=self.model,
                contents=prompt,
            )
        )


        if not response.text:

            return (
                "I couldn't generate a response."
            )


        return response.text.strip()


# =========================================================
# SINGLE INSTANCE
# =========================================================

llm = GeminiLLM()
