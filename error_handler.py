from flask import jsonify
from server import get_app

app = get_app()


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({f"error {error.status_code}": error.description})
    response.status_code = error.status_code
    return response
