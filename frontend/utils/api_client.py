import requests


# =========================================================
# DEFAULT API
# =========================================================

DEFAULT_API_URL = "http://127.0.0.1:8000"


# =========================================================
# API CLIENT
# =========================================================

class APIClient:

    def __init__(
        self,
        base_url: str = DEFAULT_API_URL
    ):

        self.base_url = base_url.rstrip("/")


    # =====================================================
    # CHAT
    # =====================================================

    def chat(
        self,
        message: str,
        selected_document: str = "",
        document_context: bool = False,
    ) -> dict:

        response = requests.post(
            f"{self.base_url}/api/chat",

            json={
                "message": message,

                "selected_document": (
                    selected_document
                ),

                "document_context": (
                    document_context
                ),
            },

            timeout=120,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # UPLOAD DOCUMENT
    # =====================================================

    def upload_document(
        self,
        file
    ) -> dict:

        files = {
            "file": (
                file.name,
                file.getvalue(),
                "application/pdf",
            )
        }

        response = requests.post(
            f"{self.base_url}/api/documents/upload",

            files=files,

            timeout=300,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # GET DOCUMENTS
    # =====================================================

    def get_documents(
        self
    ) -> list:

        response = requests.get(
            f"{self.base_url}/api/documents/",

            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "documents",
            []
        )


    # =====================================================
    # PDF URL
    # =====================================================

    def get_document_url(
        self,
        filename: str
    ) -> str:

        return (
            f"{self.base_url}"
            f"/api/documents/view/"
            f"{filename}"
        )


    # =====================================================
    # OCR IMAGE
    # =====================================================

    def ocr_image(
        self,
        file
    ) -> dict:

        files = {
            "file": (
                file.name,
                file.getvalue(),
                file.type or "image/jpeg",
            )
        }

        response = requests.post(
            f"{self.base_url}/api/multimodal/ocr",

            files=files,

            timeout=180,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # ASK ABOUT IMAGE
    # =====================================================

    def ask_image(
        self,
        question: str,
        image_text: str,
        image_filename: str = "",
    ) -> dict:

        response = requests.post(
            f"{self.base_url}/api/multimodal/ask-image",

            json={
                "question": question,

                "image_text": image_text,

                "image_filename": image_filename,
            },

            timeout=180,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # VOICE — TRANSCRIBE AUDIO
    # =====================================================

    def transcribe_audio(
        self,
        file
    ) -> dict:

        files = {
            "file": (
                file.name,
                file.getvalue(),
                file.type or "audio/wav",
            )
        }

        response = requests.post(
            f"{self.base_url}/api/voice/transcribe",

            files=files,

            timeout=180,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # VOICE — TEXT TO SPEECH
    # =====================================================

    def text_to_speech(
        self,
        text: str
    ):

        response = requests.post(
            f"{self.base_url}/api/voice/speak",

            json={
                "text": text
            },

            timeout=180,
        )

        response.raise_for_status()

        return response.content


# =========================================================
# SINGLE API CLIENT
# =========================================================

api_client = APIClient()