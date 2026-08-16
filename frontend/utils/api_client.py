import requests


# =========================================================
# CONFIGURATION
# =========================================================

DEFAULT_API_URL = "http://127.0.0.1:8000"


CHAT_TIMEOUT = 180
UPLOAD_TIMEOUT = 300
VOICE_TIMEOUT = 180


# =========================================================
# API CLIENT
# =========================================================

class APIClient:

    def __init__(
        self,
        base_url: str = DEFAULT_API_URL,
    ):

        self.base_url = (
            base_url or DEFAULT_API_URL
        ).rstrip("/")


    # =====================================================
    # CHAT
    # =====================================================

    def chat(
        self,
        message: str,
        selected_document: str = "",
        document_context: bool = False,
        web_url: str = "",
        web_context: bool = False,
        ocr_text: str = "",
        history: list[dict] | None = None,
    ) -> dict:

        message = (
            message or ""
        ).strip()

        if not message:

            raise ValueError(
                "Chat message cannot be empty."
            )

        selected_document = (
            selected_document or ""
        ).strip()

        web_url = (
            web_url or ""
        ).strip()

        ocr_text = (
            ocr_text or ""
        ).strip()

        document_context = bool(
            selected_document
        )

        web_context = bool(
            web_url
        )

        payload = {

            "message": message,

            "selected_document": (
                selected_document
            ),

            "document_context": (
                document_context
            ),

            "web_url": web_url,

            "web_context": (
                web_context
            ),

            "ocr_text": ocr_text,

            "history": (
                history or []
            ),
        }

        print(
            "\n========== API CHAT =========="
        )

        print(
            "Message:",
            message,
        )

        print(
            "Document:",
            selected_document or "NONE",
        )

        print(
            "Web URL:",
            web_url or "NONE",
        )

        print(
            "OCR:",
            bool(ocr_text),
        )

        print(
            "History:",
            len(history or []),
        )

        try:

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=CHAT_TIMEOUT,
            )

        except requests.RequestException as error:

            raise RuntimeError(
                f"Could not connect to backend: {error}"
            ) from error

        print(
            "Chat HTTP status:",
            response.status_code,
        )

        if not response.ok:

            raise RuntimeError(
                "Chat API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "Chat API returned an invalid response."
            )

        return data


    # =====================================================
    # UPLOAD DOCUMENT
    # =====================================================

    def upload_document(
        self,
        file,
    ) -> dict:

        if file is None:

            raise ValueError(
                "Document file is required."
            )

        files = {
            "file": (
                getattr(
                    file,
                    "name",
                    "document.pdf",
                ),

                file.getvalue(),

                getattr(
                    file,
                    "type",
                    None,
                )
                or "application/pdf",
            )
        }

        response = requests.post(
            f"{self.base_url}/api/documents/upload",
            files=files,
            timeout=UPLOAD_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "Document upload returned invalid data."
            )

        return data


    # =====================================================
    # GET DOCUMENTS
    # =====================================================

    def get_documents(
        self,
    ) -> list:

        response = requests.get(
            f"{self.base_url}/api/documents/",
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):

            return []

        return data.get(
            "documents",
            [],
        )


    # =====================================================
    # PDF URL
    # =====================================================

    def get_document_url(
        self,
        filename: str,
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
        file,
    ) -> dict:

        if file is None:

            raise ValueError(
                "Image file is required."
            )

        files = {
            "file": (
                getattr(
                    file,
                    "name",
                    "image.jpg",
                ),

                file.getvalue(),

                getattr(
                    file,
                    "type",
                    None,
                )
                or "image/jpeg",
            )
        }

        response = requests.post(
            f"{self.base_url}/api/multimodal/ocr",
            files=files,
            timeout=VOICE_TIMEOUT,
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

        question = (
            question or ""
        ).strip()

        image_text = (
            image_text or ""
        ).strip()

        if not question:

            raise ValueError(
                "Image question cannot be empty."
            )

        response = requests.post(
            f"{self.base_url}/api/multimodal/ask-image",
            json={
                "question": question,

                "image_text": image_text,

                "image_filename": (
                    image_filename or ""
                ),
            },
            timeout=CHAT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()


    # =====================================================
    # VOICE → TEXT
    # =====================================================

    def transcribe_audio(
        self,
        file,
    ) -> dict:
        """
        Send recorded Streamlit audio to FastAPI.

        Streamlit
            ↓
        this method
            ↓
        /api/voice/transcribe
            ↓
        Faster-Whisper
        """

        if file is None:

            raise ValueError(
                "Audio file is required."
            )

        # -------------------------------------------------
        # READ BYTES
        # -------------------------------------------------

        try:

            audio_bytes = file.getvalue()

        except Exception as error:

            raise ValueError(
                f"Could not read recorded audio: {error}"
            ) from error

        if not audio_bytes:

            raise ValueError(
                "Recorded audio is empty."
            )

        # -------------------------------------------------
        # ORIGINAL FILE INFORMATION
        # -------------------------------------------------

        original_name = (
            getattr(
                file,
                "name",
                "",
            )
            or "voice_recording.wav"
        )

        original_type = (
            getattr(
                file,
                "type",
                "",
            )
            or "audio/wav"
        )

        # -------------------------------------------------
        # DETERMINE EXTENSION
        # -------------------------------------------------

        extension = ".wav"

        lower_name = (
            original_name.lower()
        )

        if lower_name.endswith(".webm"):

            extension = ".webm"

        elif lower_name.endswith(".mp3"):

            extension = ".mp3"

        elif lower_name.endswith(".m4a"):

            extension = ".m4a"

        elif lower_name.endswith(".ogg"):

            extension = ".ogg"

        elif lower_name.endswith(".mp4"):

            extension = ".mp4"

        elif lower_name.endswith(".wav"):

            extension = ".wav"

        # -------------------------------------------------
        # SAFE UPLOAD NAME
        # -------------------------------------------------

        upload_name = (
            f"voice_recording{extension}"
        )

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print(
            "\n=============================================="
        )

        print(
            "       FRONTEND → VOICE TRANSCRIPTION"
        )

        print(
            "=============================================="
        )

        print(
            "Original filename:",
            original_name,
        )

        print(
            "Original MIME:",
            original_type,
        )

        print(
            "Audio bytes:",
            len(audio_bytes),
        )

        print(
            "Upload filename:",
            upload_name,
        )

        print(
            "Upload MIME:",
            original_type,
        )

        print(
            "=============================================="
        )

        # -------------------------------------------------
        # MULTIPART UPLOAD
        # -------------------------------------------------

        files = {

            "file": (
                upload_name,

                audio_bytes,

                original_type,
            )
        }

        # -------------------------------------------------
        # SEND TO FASTAPI
        # -------------------------------------------------

        try:

            response = requests.post(
                f"{self.base_url}/api/voice/transcribe",
                files=files,
                timeout=VOICE_TIMEOUT,
            )

        except requests.RequestException as error:

            print(
                "[VOICE] Network error:",
                repr(error),
            )

            raise RuntimeError(
                f"Voice backend is unreachable: {error}"
            ) from error

        # -------------------------------------------------
        # DEBUG RESPONSE
        # -------------------------------------------------

        print(
            "\n========== STT RESPONSE =========="
        )

        print(
            "HTTP status:",
            response.status_code,
        )

        print(
            "Response:",
            response.text,
        )

        print(
            "==================================\n"
        )

        # -------------------------------------------------
        # HTTP ERROR
        # -------------------------------------------------

        if not response.ok:

            raise RuntimeError(
                "Voice transcription failed "
                f"(HTTP {response.status_code}).\n"
                f"{response.text}"
            )

        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "Transcription API returned invalid data."
            )

        return data


    # =====================================================
    # TEXT → SPEECH
    # =====================================================

    def text_to_speech(
        self,
        text: str,
    ) -> bytes:
        """
        Send assistant answer to FastAPI TTS.
        Returns WAV bytes.
        """

        text = (
            text or ""
        ).strip()

        if not text:

            raise ValueError(
                "Text for speech cannot be empty."
            )

        print(
            "\n=============================================="
        )

        print(
            "             FRONTEND → TTS"
        )

        print(
            "=============================================="
        )

        print(
            "Characters:",
            len(text),
        )

        try:

            response = requests.post(
                f"{self.base_url}/api/voice/speak",

                json={
                    "text": text,
                },

                timeout=VOICE_TIMEOUT,
            )

        except requests.RequestException as error:

            raise RuntimeError(
                f"TTS backend is unreachable: {error}"
            ) from error

        print(
            "TTS HTTP status:",
            response.status_code,
        )

        if not response.ok:

            raise RuntimeError(
                "TTS failed "
                f"(HTTP {response.status_code}).\n"
                f"{response.text}"
            )

        audio_bytes = (
            response.content
        )

        if not audio_bytes:

            raise ValueError(
                "TTS returned empty audio."
            )

        print(
            "TTS audio bytes:",
            len(audio_bytes),
        )

        print(
            "==============================================\n"
        )

        return audio_bytes


# =========================================================
# SINGLE CLIENT
# =========================================================

api_client = APIClient()