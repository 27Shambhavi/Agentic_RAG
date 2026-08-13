from app.api.routes.chat import (
    router as chat_router
)

from app.api.routes.documents import (
    router as document_router
)

from app.api.routes.voice import (
    router as voice_router
)

from app.api.routes.multimodal import (
    router as multimodal_router
)

from app.api.routes.health import (
    router as health_router
)


__all__ = [
    "chat_router",
    "document_router",
    "voice_router",
    "multimodal_router",
    "health_router",
]