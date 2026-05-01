import urllib.request
import uuid

from flask import Blueprint, request

from src.config import VQNA_IMAGES_DIRECTORY
from src.utils.api import send_response
from src.utils.loaders import load_model_and_encoders
from src.utils.validators import is_valid_image, is_valid_url

predict = Blueprint("predict", __name__)

model, model_encoder_answer, model_encoder_answer_type = load_model_and_encoders()


@predict.route("/", methods=["POST"])
def predict_handler():
    try:
        image_url_user = request.form.get("image_url")
        question_user = request.form.get("question")

        user_image_path = VQNA_IMAGES_DIRECTORY / f"{uuid.uuid4()}.jpg"

        if not question_user:
            return send_response(400, "error", "Question not provided.")

        if (not image_url_user) and "image" not in request.files:
            return send_response(400, "error", "Image not provided.")

        if image_url_user and "image" in request.files:
            return send_response(
                400, "error", "Provide either an image URL or an image file, not both."
            )

        if "image" in request.files:
            image_user = request.files["image"]

            image_user.save(str(user_image_path))

            if not is_valid_image(user_image_path):
                return send_response(400, "error", "Image format not allowed.")

        if image_url_user:
            if not is_valid_url(image_url_user):
                return send_response(400, "error", "Invalid image URL.")

            urllib.request.urlretrieve(image_url_user, str(user_image_path))

        predicted_answer, predicted_answer_type, answerability = model.test_model(
            image_path=str(user_image_path), question=question_user
        )
        answer = model_encoder_answer.inverse_transform(
            predicted_answer.cpu().detach().numpy()
        )
        answer_type = model_encoder_answer_type.inverse_transform(
            predicted_answer_type.cpu().detach().numpy()
        )

        return send_response(
            200,
            "success",
            "Prediction successful.",
            {
                "answer": answer[0][0],
                "answer_type": answer_type[0][0],
                "answerability": answerability.item(),
            },
        )

    except Exception:
        return send_response(500, "error", "An error occurred.")

    finally:
        if user_image_path and user_image_path.exists():
            user_image_path.unlink()
