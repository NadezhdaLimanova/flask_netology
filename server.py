from flask import Flask, jsonify
from flask import request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from models import Advertisement, User,  Session, MODEL, MODEL_TYPE
# from models import Advertisement, User, Token, Session, MODEL, MODEL_TYPE
from schema import CreateUser, CreateAdv, Login
import pydantic
import psycopg2

app = Flask("app")
bcrypt = Bcrypt(app)


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({f"error {error.status_code}": error.description})
    response.status_code = error.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


def validate(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)


def add_item(item: MODEL):
    try:
        request.session.add(item)
        request.session.commit()
    except IntegrityError as err:
        if isinstance(err.orig, psycopg2.errors.UniqueViolation):
            raise HttpError(409, "user already exists")
        else:
            raise err
    return item


def create_item(model: MODEL_TYPE, payload: dict):
    item = model(**payload)
    item = add_item(item)
    return item


# def add_advertisement(adv: Advertisement):
#     try:
#         request.session.add(adv)
#         request.session.commit()
#     except IntegrityError as err:
#         raise HttpError(409, "that advertisement already have been written")
#     return adv


def hash_password(password: str):
    password = password.encode()
    return bcrypt.generate_password_hash(password).decode()


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.check_password_hash(password, hashed_password)


# def check_token(handler):
#     def wrapper(*args, **kwargs):
#         token = request.headers.get("Authorization")
#         if token is None:
#             raise HttpError(401, "token not found")
#         token = request.session.query(Token).filter_by(token=token).first()
#         if token is None:
#             raise HttpError(401, "invalid token")
#         request.token = token
#         return handler(*args, **kwargs)
#
#     return wrapper


class NewUser(MethodView):

    def post(self):
        json_data = validate(CreateUser, request.json)
        json_data["password"] = hash_password(json_data["password"])
        user = create_item(User, **json_data)
        response = jsonify({"id": user.id})
        return response


# class NewLogin(MethodView):
#     def post(self):
#         payload = validate(Login, request.json)
#         user = self.session.query(User).filter_by(name=payload["name"]).first()
#         if user is None:
#             raise HttpError(404, "user not found")
#         if check_password(user.password, payload["password"]):
#             token = create_item(Token, {"user_id": user.id}, self.session)
#             add_item(token, self.session)
#             return jsonify({"token": token.token})
#         raise HttpError(401, "invalid password")

# class NewAdvertisement(MethodView):
#     def get(self):
#         pass
#
#     def post(self):
#         json_data = validate(CreateAdv, request.json)
#         adv = Advertisement(**json_data)
#         add_advertisement(adv)
#         response = jsonify(adv.json)
#         return response
#
#
#     def patch(self):
#         pass
#
#     def delete(self):
#         pass


user_view = NewUser.as_view("user_view")


# adv_view = NewAdvertisement.as_view("adv_view")
# app.add_url_rule("/adv", view_func=adv_view, methods=["POST",],)
app.add_url_rule("/user", view_func=user_view, methods=["POST",],)
# app.add_url_rule("/login", view_func=NewLogin.as_view("login"), methods=["POST",],)
app.run()



# app = Flask("app")
# bcrypt = Bcrypt(app)

# def hash_password(password: str):
#     password = password.encode()
#     return bcrypt.generate_password_hash(password).decode()
#
# def check_password(password: str, hashed_password: str):
#     password = password.encode()
#     hashed_password = hashed_password.encode()
#     return bcrypt.check_password_hash(password, hashed_password)


# def validate(schema_class, json_data):
#     try:
#         return schema_class(**json_data).model_dump(exclude_unset=True)
#     except pydantic.ValidationError as er:
#         error = er.errors()[0]
#         raise HttpError(400, error)


# class HttpError(Exception):
#     def __init__(self, status_code: int, description: str):
#         self.status_code = status_code
#         self.description = description
#
#
# @app.errorhandler(HttpError)
# def error_handler(error: HttpError):
#     response = jsonify({f"error {error.status_code}": error.description})
#     response.status_code = error.status_code
#     return response
#
#
# @app.before_request
# def before_request():
#     session = Session()
#     request.session = session
#
#
# @app.after_request
# def after_request(response):
#     request.session.close()
#     return response
#
#
# def get_adv_by_id(adv_id: int):
#     adv = request.session.get(Advertisement, adv_id)
#     if adv is None:
#         raise HttpError(404, "advertisement not found")
#     return adv
#
# def add_advertisement(adv: Advertisement):
#     try:
#         request.session.add(adv)
#         request.session.commit()
#     except IntegrityError as err:
#         raise HttpError(409, "that advertisement already have been written")
#     return adv


# def add_advertisement(adv: Advertisement):
#     existing_adv = request.session.query(Advertisement).filter_by(
#         author=adv.author,
#         email=adv.email,
#         title=adv.title,
#         description=adv.description
#     ).first()
#     if existing_adv is not None:
#         raise HttpError(409, "that advertisement already have been written")
#     request.session.add(adv)
#     request.session.commit()
#     return adv


# class NewAdvertisement(MethodView):
#     # def get(self, adv_id: int):
#     #     adv = get_adv_by_id(adv_id)
#     #     return jsonify(adv.json)
#
#     def post(self):
#         json_data = request.json
#         # json_data['password'] = hash_password(json_data['password'])
#         adv = Advertisement(**json_data)
#         add_advertisement(adv)
#         response = jsonify(adv.json)
#         return response

    # def patch(self, adv_id: int):
    #     json_data = request.json
    #     adv = get_adv_by_id(adv_id)
    #     for field, value in json_data.items():
    #         setattr(adv, field, value)
    #     add_advertisement(adv)
    #     return jsonify(adv.json)

    # def delete(self, adv_id: int):
    #     adv = get_adv_by_id(adv_id)
    #     request.session.delete(adv)
    #     request.session.commit()
    #     return jsonify({'status': 'success'})

#
# adv_view = NewAdvertisement.as_view("adv_view")
#
# app.add_url_rule("/adv", view_func=adv_view, methods=["POST"])
# app.add_url_rule("/adv/<int:adv_id>", view_func=adv_view, methods=["GET", "PATCH", "DELETE"])
#
#
# app.run()
