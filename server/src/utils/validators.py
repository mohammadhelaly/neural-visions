import ipaddress
import socket
import warnings
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from src.config import (
    ALLOWED_IMAGE_FORMATS,
    MAX_QUESTION_LENGTH,
)


class RequestValidationError(ValueError):
    status_code = 400


class RequestEntityTooLargeValidationError(RequestValidationError):
    status_code = 413


def validate_question(question: str | None) -> str:
    normalized_question = (question or "").strip()

    if not normalized_question:
        raise RequestValidationError("Question not provided.")

    if len(normalized_question) > MAX_QUESTION_LENGTH:
        raise RequestValidationError(
            f"Question exceeds the maximum length of {MAX_QUESTION_LENGTH} characters."
        )

    return normalized_question


def validate_prediction_sources(
    image_url: str | None, image: FileStorage | None
) -> None:
    normalized_image_url = (image_url or "").strip()

    if not normalized_image_url and image is None:
        raise RequestValidationError("Image not provided.")

    if normalized_image_url and image is not None:
        raise RequestValidationError(
            "Provide either an image URL or an image file, not both."
        )


def validate_public_image_url(image_url: str | None) -> str:
    normalized_url = (image_url or "").strip()
    parsed_url = urlparse(normalized_url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise RequestValidationError("Invalid image URL.")

    if parsed_url.username or parsed_url.password:
        raise RequestValidationError("Image URL must not include credentials.")

    hostname = parsed_url.hostname
    if hostname is None or hostname.lower() == "localhost":
        raise RequestValidationError("Image URL must use a public host.")

    try:
        port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    except ValueError as exc:
        raise RequestValidationError("Invalid image URL.") from exc

    validate_public_host(hostname, port)
    return normalized_url


def validate_public_host(hostname: str, port: int) -> None:
    try:
        address_info = socket.getaddrinfo(
            hostname,
            port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise RequestValidationError("Image URL host could not be resolved.") from exc

    for _, _, _, _, sockaddr in address_info:
        ip_address = ipaddress.ip_address(sockaddr[0])
        if (
            ip_address.is_private
            or ip_address.is_loopback
            or ip_address.is_link_local
            or ip_address.is_multicast
            or ip_address.is_reserved
            or ip_address.is_unspecified
        ):
            raise RequestValidationError(
                "Image URL must resolve to a public IP address."
            )


def validate_image_file(image_path: Path, max_bytes: int) -> None:
    if not image_path.is_file():
        raise RequestValidationError("Image file is missing.")

    file_size = image_path.stat().st_size
    if file_size == 0:
        raise RequestValidationError("Image file is empty.")

    if file_size > max_bytes:
        raise RequestEntityTooLargeValidationError(
            "Image file exceeds the maximum allowed size."
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(image_path) as image:
                image.verify()

        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(image_path) as image:
                if (
                    image.format is None
                    or image.format.upper() not in ALLOWED_IMAGE_FORMATS
                ):
                    raise RequestValidationError("Image format not allowed.")

                if image.width <= 0 or image.height <= 0:
                    raise RequestValidationError("Image dimensions are invalid.")
    except RequestValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
        ValueError,
    ) as exc:
        raise RequestValidationError("Uploaded content is not a valid image.") from exc
