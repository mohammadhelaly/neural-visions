from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from src.config import CLIENT_DIST_DIRECTORY, MAX_REQUEST_BODY_BYTES
from src.routes import predict, web
from src.utils.api import send_response
from src.utils.validators import RequestValidationError


def create_app():
    app = Flask(__name__, static_folder=str(CLIENT_DIST_DIRECTORY), static_url_path="/")
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BODY_BYTES

    CORS(app, methods=["GET", "POST", "OPTIONS"])

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(_error):
        return send_response(413, "error", "Request body exceeds the allowed size.")

    @app.errorhandler(RequestValidationError)
    def handle_request_validation_error(error):
        return send_response(error.status_code, "error", str(error))

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error

        app.logger.exception("Unhandled exception while processing request.")
        return send_response(500, "error", "An error occurred.")

    app.register_blueprint(web)
    app.register_blueprint(predict, url_prefix="/predict")

    return app
