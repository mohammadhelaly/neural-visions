import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import kagglehub
from clip.clip import _MODELS

SERVER_DIRECTORY = Path(__file__).resolve().parents[1]
if str(SERVER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SERVER_DIRECTORY))

from src.config import (  # noqa: E402
    CLIP_DOWNLOAD_DIRECTORY,
    CLIP_MODEL_NAME,
    VQNA_ARTIFACT_DIRECTORY,
)

DEFAULT_MODEL_HANDLE = "mohammadhelaly/visualqna/pytorch/default/2"
DEFAULT_CLIP_DOWNLOAD_ATTEMPTS = 3
DEFAULT_CLIP_CONNECTION_ATTEMPTS = 12
CHUNK_SIZE = 1024 * 1024
LOG_INTERVAL_BYTES = 50 * 1024 * 1024
MODEL_FILE = "VisualQnA.pth"
ENCODER_FILES = (
    "model_encoder_answer.pkl",
    "model_encoder_answer_type.pkl",
)
REQUIRED_FILES = (MODEL_FILE, *ENCODER_FILES)
METADATA_FILE = "artifact.json"


def truthy(value: str | None) -> bool:
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


def vqna_artifact_directory() -> Path:
    return VQNA_ARTIFACT_DIRECTORY.resolve()


def model_handle() -> str:
    return os.environ.get("KAGGLE_MODEL_HANDLE", DEFAULT_MODEL_HANDLE).strip()


def metadata_path(target_dir: Path) -> Path:
    return target_dir / METADATA_FILE


def load_metadata(target_dir: Path) -> dict[str, str]:
    path = metadata_path(target_dir)

    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

    return metadata if isinstance(metadata, dict) else {}


def required_files_exist(target_dir: Path) -> bool:
    return all((target_dir / file_name).is_file() for file_name in REQUIRED_FILES)


def has_kaggle_auth() -> bool:
    kaggle_dir = Path.home() / ".kaggle"
    return bool(os.environ.get("KAGGLE_API_TOKEN")) or any(
        (kaggle_dir / file_name).is_file()
        for file_name in ("access_token", "kaggle.json")
    )


def find_file(search_dir: Path, file_name: str) -> Path | None:
    matches = sorted(search_dir.rglob(file_name))
    return matches[0] if matches else None


def downloaded_file_preview(download_dir: Path) -> str:
    available_files = sorted(
        str(path.relative_to(download_dir))
        for path in download_dir.rglob("*")
        if path.is_file()
    )
    return "\n".join(available_files[:25]) or "(no files found)"


def resolve_artifact_files(download_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    model_path = find_file(download_dir, MODEL_FILE)

    if model_path is None:
        raise FileNotFoundError(
            f"Kaggle artifact is missing required model file '{MODEL_FILE}'.\n"
            f"Files found in downloaded artifact:\n{downloaded_file_preview(download_dir)}"
        )

    found[MODEL_FILE] = model_path

    for file_name in ENCODER_FILES:
        downloaded_encoder_path = find_file(download_dir, file_name)

        if downloaded_encoder_path is not None:
            found[file_name] = downloaded_encoder_path
            continue

        raise FileNotFoundError(
            f"Kaggle artifact is missing required encoder '{file_name}'. "
            f"Expected all of: {', '.join(REQUIRED_FILES)}.\n"
            f"Files found in downloaded artifact:\n{downloaded_file_preview(download_dir)}"
        )

    return found


def write_metadata(target_dir: Path, handle: str) -> None:
    metadata = {
        "source": "kaggle",
        "handle": handle,
        "files": list(REQUIRED_FILES),
    }
    temp_path = metadata_path(target_dir).with_suffix(".json.tmp")

    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")

    temp_path.replace(metadata_path(target_dir))


def copy_artifacts(files: dict[str, Path], target_dir: Path, handle: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    for file_name, source_path in files.items():
        target_path = target_dir / file_name
        temp_path = target_dir / f"{file_name}.tmp"
        shutil.copy2(source_path, temp_path)
        temp_path.replace(target_path)

    write_metadata(target_dir, handle)


def download_artifacts(handle: str, target_dir: Path, force_download: bool) -> None:
    if not handle:
        raise RuntimeError("KAGGLE_MODEL_HANDLE is empty.")

    if not has_kaggle_auth():
        raise RuntimeError(
            "Kaggle credentials are required because VQnA artifacts are missing "
            "or need refreshing. Set KAGGLE_API_TOKEN in .env, or provide a "
            "~/.kaggle/access_token or ~/.kaggle/kaggle.json file."
        )

    with tempfile.TemporaryDirectory(prefix="vqna-artifacts-") as temp_dir:
        print(f"Downloading VQnA artifacts from Kaggle handle: {handle}")

        for file_name in REQUIRED_FILES:
            try:
                kagglehub.model_download(
                    handle,
                    path=file_name,
                    output_dir=temp_dir,
                    force_download=force_download,
                )
            except Exception:
                raise RuntimeError(
                    f"Could not download required file '{file_name}' from "
                    f"Kaggle handle '{handle}'."
                ) from None

        files = resolve_artifact_files(Path(temp_dir).resolve())
        copy_artifacts(files, target_dir, handle)


def prepare_vqna_artifacts() -> None:
    target_dir = vqna_artifact_directory()
    handle = model_handle()
    force_download = truthy(os.environ.get("VQNA_FORCE_ARTIFACT_DOWNLOAD"))
    metadata = load_metadata(target_dir)
    current_handle = metadata.get("handle")
    files_exist = required_files_exist(target_dir)

    if files_exist and not force_download and current_handle == handle:
        print(f"VQnA artifacts are ready at {target_dir}.")
        return

    if files_exist and not force_download and not current_handle:
        print(
            "VQnA artifacts exist, but artifact.json is missing. "
            "Writing metadata without downloading."
        )
        write_metadata(target_dir, handle)
        return

    reasons = []
    if not files_exist:
        reasons.append("missing required files")
    if current_handle and current_handle != handle:
        reasons.append(f"configured handle changed from {current_handle} to {handle}")
    if force_download:
        reasons.append("VQNA_FORCE_ARTIFACT_DOWNLOAD is enabled")

    print(f"Preparing VQnA artifacts: {', '.join(reasons) or 'refresh needed'}.")
    download_artifacts(handle, target_dir, force_download)
    print(f"VQnA artifacts are ready at {target_dir}.")


def clip_model_name() -> str:
    return CLIP_MODEL_NAME


def clip_download_directory() -> Path:
    return CLIP_DOWNLOAD_DIRECTORY.resolve()


def clip_model_url(model_name: str) -> str:
    try:
        return _MODELS[model_name]
    except KeyError:
        available_models = ", ".join(sorted(_MODELS))
        raise RuntimeError(
            f"Unknown CLIP model {model_name!r}. Available models: {available_models}"
        ) from None


def expected_clip_sha256(url: str) -> str:
    return url.split("/")[-2]


def clip_target_path(download_root: Path, url: str) -> Path:
    return download_root / Path(url).name


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)

    return digest.hexdigest()


def is_valid_file(path: Path, expected_hash: str) -> bool:
    return path.is_file() and file_sha256(path) == expected_hash


def adopt_valid_temp_file(target: Path, expected_hash: str) -> bool:
    for temp_path in sorted(target.parent.glob(f"{target.name}*.tmp")):
        print(f"Checking existing CLIP temp file {temp_path}.", flush=True)

        if is_valid_file(temp_path, expected_hash):
            temp_path.replace(target)
            print(f"Recovered completed CLIP download at {target}.", flush=True)
            return True

        temp_path.unlink(missing_ok=True)

    return False


def response_total_bytes(response, existing_size: int) -> int:
    content_range = response.headers.get("Content-Range")

    if content_range and "/" in content_range:
        return int(content_range.rsplit("/", 1)[1])

    content_length = int(response.headers.get("Content-Length") or 0)

    if content_length:
        return existing_size + content_length

    return 0


def open_download_response(url: str, existing_size: int):
    headers = {}

    if existing_size:
        headers["Range"] = f"bytes={existing_size}-"

    request = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(request, timeout=300)


def download_clip_file(url: str, target: Path, expected_hash: str) -> None:
    temp_path = target.with_name(f"{target.name}.tmp")
    connection_attempts = DEFAULT_CLIP_CONNECTION_ATTEMPTS
    expected_total = 0
    started_at = time.monotonic()

    print(f"Downloading CLIP model to {target}...", flush=True)

    for connection_attempt in range(1, connection_attempts + 1):
        existing_size = temp_path.stat().st_size if temp_path.exists() else 0

        if expected_total and existing_size >= expected_total:
            break

        next_log_at = ((existing_size // LOG_INTERVAL_BYTES) + 1) * LOG_INTERVAL_BYTES

        try:
            with open_download_response(url, existing_size) as response:
                if existing_size and getattr(response, "status", None) != 206:
                    print(
                        "CLIP server did not honor resume request; restarting download.",
                        flush=True,
                    )
                    temp_path.unlink(missing_ok=True)
                    existing_size = 0
                    next_log_at = LOG_INTERVAL_BYTES

                total = response_total_bytes(response, existing_size)
                if total:
                    expected_total = total

                downloaded = existing_size
                mode = "ab" if existing_size else "wb"

                with temp_path.open(mode) as f:
                    while True:
                        chunk = response.read(CHUNK_SIZE)

                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        if downloaded >= next_log_at:
                            if expected_total:
                                percent = downloaded / expected_total * 100
                                print(
                                    f"Downloaded CLIP: "
                                    f"{downloaded / 1024 / 1024:.0f} MiB "
                                    f"of {expected_total / 1024 / 1024:.0f} MiB "
                                    f"({percent:.0f}%).",
                                    flush=True,
                                )
                            else:
                                print(
                                    f"Downloaded CLIP: "
                                    f"{downloaded / 1024 / 1024:.0f} MiB.",
                                    flush=True,
                                )
                            next_log_at += LOG_INTERVAL_BYTES
        except (TimeoutError, urllib.error.URLError) as exc:
            print(
                f"CLIP download connection interrupted "
                f"({connection_attempt}/{connection_attempts}): {exc}",
                flush=True,
            )
            continue

        current_size = temp_path.stat().st_size if temp_path.exists() else 0

        if expected_total and current_size >= expected_total:
            break

        if not expected_total:
            break

        print(
            f"CLIP download paused at {current_size} of {expected_total} bytes; "
            "resuming.",
            flush=True,
        )
    else:
        current_size = temp_path.stat().st_size if temp_path.exists() else 0
        raise RuntimeError(
            "CLIP download did not complete after "
            f"{connection_attempts} connection attempts "
            f"({current_size} of {expected_total or 'unknown'} bytes)."
        )

    current_size = temp_path.stat().st_size if temp_path.exists() else 0

    if expected_total and current_size != expected_total:
        raise RuntimeError(
            f"CLIP download incomplete: got {current_size} of {expected_total} bytes."
        )

    actual_hash = file_sha256(temp_path)

    if actual_hash != expected_hash:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            "Downloaded CLIP model checksum mismatch. "
            f"Expected {expected_hash}, got {actual_hash}."
        )

    temp_path.replace(target)
    elapsed = time.monotonic() - started_at
    print(f"CLIP model download completed in {elapsed:.1f}s.", flush=True)


def prepare_clip_artifact() -> None:
    model_name = clip_model_name()
    url = clip_model_url(model_name)
    expected_hash = expected_clip_sha256(url)
    download_root = clip_download_directory()
    download_root.mkdir(parents=True, exist_ok=True)
    target = clip_target_path(download_root, url)
    attempts = DEFAULT_CLIP_DOWNLOAD_ATTEMPTS

    if is_valid_file(target, expected_hash):
        print(f"CLIP model is ready at {target}.", flush=True)
        return

    if adopt_valid_temp_file(target, expected_hash):
        return

    if target.exists():
        print(f"Removing invalid CLIP cache file at {target}.", flush=True)
        target.unlink()

    for attempt in range(1, attempts + 1):
        try:
            print(
                f"Preparing CLIP model {model_name}, attempt {attempt}/{attempts}.",
                flush=True,
            )
            download_clip_file(url, target, expected_hash)
            return
        except Exception as exc:
            print(f"Failed to prepare CLIP model: {exc}", file=sys.stderr, flush=True)

            if attempt == attempts:
                raise

            print("Retrying CLIP model download.", flush=True)


def main() -> int:
    prepare_vqna_artifacts()
    prepare_clip_artifact()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Failed to prepare VQnA artifacts: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
