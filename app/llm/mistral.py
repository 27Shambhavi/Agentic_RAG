from mistralai.client import Mistral

from app.config.settings import settings

from app.llm.base import BaseLLM


# =========================================================
# MISTRAL LLM
# =========================================================

class MistralLLM(BaseLLM):

    def __init__(self):

        if not settings.MISTRAL_API_KEY:

            raise ValueError(
                "MISTRAL_API_KEY not found in .env"
            )

        self.client = Mistral(
            api_key=settings.MISTRAL_API_KEY
        )

        self.model = getattr(
            settings,
            "MISTRAL_MODEL",
            "mistral-small-latest"
        )


    # =====================================================
    # GENERATE
    # =====================================================

    def generate(
        self,
        prompt: str
    ) -> str:

        if not prompt.strip():

            return ""


        response = self.client.chat.complete(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )


        content = (
            response
            .choices[0]
            .message
            .content
        )


        if not content:

            return (
                "I couldn't generate a response."
            )


        return content.strip()


# =========================================================
# SINGLE INSTANCE
# =========================================================

mistral_llm = MistralLLM()