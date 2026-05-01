import pickle
from pathlib import Path

import torch

from src.config import (
    CLIP_DOWNLOAD_DIRECTORY,
    CLIP_MODEL_NAME,
    MODEL_ENCODER_ANSWER_PATH,
    MODEL_ENCODER_ANSWER_TYPE_PATH,
    MODEL_PATH,
)
from src.models import LinearNet


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(
            f"Required VQnA artifact is missing: {path}. "
            "Run the Docker startup artifact downloader or provide the artifact files "
            "under the VQnA artifact directory."
        )


def load_model_and_encoders() -> tuple:
    require_file(MODEL_PATH)
    model = LinearNet(
        num_classes=5410,
        device=torch.device("cpu"),
        model=CLIP_MODEL_NAME,
        clip_download_directory=str(CLIP_DOWNLOAD_DIRECTORY),
    ).to(torch.device("cpu"))
    model.load_model(MODEL_PATH)

    require_file(MODEL_ENCODER_ANSWER_PATH)
    with open(MODEL_ENCODER_ANSWER_PATH, "rb") as f:
        model_encoder_answer = pickle.load(f)

    require_file(MODEL_ENCODER_ANSWER_TYPE_PATH)
    with open(MODEL_ENCODER_ANSWER_TYPE_PATH, "rb") as f:
        model_encoder_answer_type = pickle.load(f)

    return model, model_encoder_answer, model_encoder_answer_type
