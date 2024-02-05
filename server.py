from flask import Flask


def get_app() -> Flask:
    app = Flask('app')
    return app
