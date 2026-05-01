from typing import Any

from flask import Response, jsonify, make_response


def send_response(
    status_code: int, status: str, message: str, data: dict[str, Any] | None = None
) -> Response:
    response_body: dict[str, Any] = {"status": status, "message": message}

    if data is not None:
        response_body["data"] = data

    return make_response(jsonify(response_body), status_code)
