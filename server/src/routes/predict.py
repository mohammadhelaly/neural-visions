import uuid

from flask import Blueprint, request

from src.config import VQNA_IMAGES_DIRECTORY
from src.utils.api import send_response
from src.utils.image_ingest import download_image_from_url, save_uploaded_image
from src.utils.loaders import load_model_and_encoders
from src.utils.validators import validate_prediction_sources, validate_question

predict = Blueprint("predict", __name__)

model, model_encoder_answer, model_encoder_answer_type = load_model_and_encoders()


@predict.route("/", methods=["POST"], strict_slashes=False)
def predict_handler():
    user_image_path = VQNA_IMAGES_DIRECTORY / f"{uuid.uuid4().hex}.img"

    try:
        image_url_user = request.form.get("image_url")
        uploaded_image = request.files.get("image")
        question_user = validate_question(request.form.get("question"))
        validate_prediction_sources(image_url_user, uploaded_image)

        if uploaded_image is not None:
            save_uploaded_image(uploaded_image, user_image_path)
        else:
            download_image_from_url(image_url_user, user_image_path)

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

    finally:
        if user_image_path and user_image_path.exists():
            user_image_path.unlink()
