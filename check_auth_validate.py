from server import get_app
from flask_bcrypt import Bcrypt
from error_handler import HttpError
from flask import request
from models import Token, MODEL
import pydantic

bcrypt = Bcrypt(get_app())


def validate(schema_class, json_data):
    try:
        return schema_class(**json_data).model_dump(exclude_unset=True)
    except pydantic.ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)


def hash_password(password: str):
    password = password.encode()
    return bcrypt.generate_password_hash(password).decode()


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.check_password_hash(password, hashed_password)


def check_token(handler):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            raise HttpError(401, "token not found")
        token = request.session.query(Token).filter_by(token=token).first()
        if token is None:
            raise HttpError(401, "invalid token")
        request.token = token
        return handler(*args, **kwargs)
    return wrapper


def check_user(item: MODEL, user_id: int):
    if item.user_id != user_id:
        raise HttpError(403, "access denied")