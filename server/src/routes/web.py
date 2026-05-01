from flask import Blueprint, send_from_directory

from src.config import CLIENT_DIST_DIRECTORY

web = Blueprint("web", __name__)


@web.route("/", methods=["GET"])
def index_handler():
    return send_from_directory(str(CLIENT_DIST_DIRECTORY), "index.html")
