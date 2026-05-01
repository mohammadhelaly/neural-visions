from pathlib import Path
from urllib.parse import urljoin

import requests
from PIL import Image
from werkzeug.datastructures import FileStorage

from src.config import (
    ALLOWED_IMAGE_MIME_TYPES,
    IMAGE_DOWNLOAD_CONNECT_TIMEOUT_SECONDS,
    IMAGE_DOWNLOAD_READ_TIMEOUT_SECONDS,
    MAX_IMAGE_DOWNLOAD_BYTES,
    MAX_IMAGE_PIXELS,
    MAX_IMAGE_REDIRECTS,
    MAX_UPLOADED_IMAGE_BYTES,
)
from src.utils.validators import (
    RequestEntityTooLargeValidationError,
    RequestValidationError,
    validate_image_file,
    validate_public_image_url,
)

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
REQUEST_HEADERS = {"Accept": "image/*", "User-Agent": "neural-visions/1.0"}


def save_uploaded_image(image: FileStorage | None, target_path: Path) -> None:
    if image is None:
        raise RequestValidationError("Image not provided.")

    if not image.filename:
        raise RequestValidationError("Uploaded image file is empty.")

    mimetype = (image.mimetype or "").lower()
    if mimetype and mimetype not in ALLOWED_IMAGE_MIME_TYPES:
        raise RequestValidationError("Uploaded image MIME type is not allowed.")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(target_path))
    validate_image_file(target_path, MAX_UPLOADED_IMAGE_BYTES)


def download_image_from_url(image_url: str | None, target_path: Path) -> None:
    current_url = validate_public_image_url(image_url)
    redirect_count = 0

    try:
        while True:
            with requests.get(
                current_url,
                stream=True,
                timeout=(
                    IMAGE_DOWNLOAD_CONNECT_TIMEOUT_SECONDS,
                    IMAGE_DOWNLOAD_READ_TIMEOUT_SECONDS,
                ),
                allow_redirects=False,
                headers=REQUEST_HEADERS,
            ) as response:
                if 300 <= response.status_code < 400:
                    redirect_count += 1
                    if redirect_count > MAX_IMAGE_REDIRECTS:
                        raise RequestValidationError(
                            "Image URL redirected too many times."
                        )

                    redirect_url = response.headers.get("Location")
                    if not redirect_url:
                        raise RequestValidationError(
                            "Image URL redirect is missing a location."
                        )

                    current_url = validate_public_image_url(
                        urljoin(current_url, redirect_url)
                    )
                    continue

                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "")
                normalized_content_type = content_type.split(";", 1)[0].strip().lower()
                if (
                    normalized_content_type
                    and normalized_content_type not in ALLOWED_IMAGE_MIME_TYPES
                ):
                    raise RequestValidationError(
                        "Image URL did not return a supported image content type."
                    )

                content_length = response.headers.get("Content-Length")
                if content_length:
                    expected_size = int(content_length)
                    if expected_size > MAX_IMAGE_DOWNLOAD_BYTES:
                        raise RequestEntityTooLargeValidationError(
                            "Image URL exceeds the maximum allowed download size."
                        )

                target_path.parent.mkdir(parents=True, exist_ok=True)
                bytes_written = 0

                with target_path.open("wb") as image_file:
                    for chunk in response.iter_content(DOWNLOAD_CHUNK_SIZE):
                        if not chunk:
                            continue

                        bytes_written += len(chunk)
                        if bytes_written > MAX_IMAGE_DOWNLOAD_BYTES:
                            raise RequestEntityTooLargeValidationError(
                                "Image URL exceeds the maximum allowed download size."
                            )

                        image_file.write(chunk)

                validate_image_file(target_path, MAX_IMAGE_DOWNLOAD_BYTES)
                return
    except RequestValidationError:
        raise
    except (OSError, requests.RequestException, ValueError) as exc:
        raise RequestValidationError("Image URL could not be downloaded.") from exc
