from urllib.parse import urlparse

from PIL import Image

ALLOWED_IMAGE_FORMATS = frozenset({"JPEG", "PNG", "JPG", "WEBP"})


def is_valid_image(image_path: str, allowed_formats=ALLOWED_IMAGE_FORMATS) -> bool:
    try:
        with Image.open(image_path) as img:
            return img.format.upper() in allowed_formats

    except Exception:
        return False


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
