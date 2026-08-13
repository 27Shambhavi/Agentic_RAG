from pathlib import Path

from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def validate_image(
    image_path: str
) -> bool:

    path = Path(image_path)

    if not path.exists():
        return False

    return (
        path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    )


def get_image_info(
    image_path: str
) -> dict:

    image = Image.open(
        image_path
    )

    return {
        "width": image.width,
        "height": image.height,
        "format": image.format,
    }