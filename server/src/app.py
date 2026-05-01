from flask import Flask
from flask_cors import CORS

from src.config import CLIENT_DIST_DIRECTORY
from src.routes import predict, web


def create_app():
    app = Flask(__name__, static_folder=str(CLIENT_DIST_DIRECTORY), static_url_path="/")

    CORS(app, methods=["GET", "POST", "OPTIONS"])

    app.register_blueprint(web)
    app.register_blueprint(predict, url_prefix="/predict")

    return app
