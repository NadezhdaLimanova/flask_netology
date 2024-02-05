from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from models import Advertisement, User, Token, Session, MODEL, MODEL_TYPE
from schema import CreateUser, PatchUser, CreateAdv, PatchAdv, Login
import pydantic
import psycopg2
# from sqlalchemy.orm import Session

app = Flask("app")
bcrypt = Bcrypt(app)


class BaseView(MethodView):
    @property
    def session(self) -> Session:
        return request.session

    @property
    def token(self) -> Token:
        return request.token

    @property
    def user(self) -> User:
        return request.token.user


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({f"error {error.status_code}": error.description})
    response.status_code = error.status_code
    return response


def create_item(model: MODEL_TYPE, payload: dict, session: Session) -> MODEL:
    item = model(**payload)
    item = add_item(item, session)
    return item


def get_item_by_id(model: MODEL_TYPE, item_id: int, session: Session) -> MODEL:
    item = session.get(model, item_id)
    if item is None:
        raise HttpError(404, f"{model.__name__} not found")
    return item


def add_item(item: MODEL, session: Session):
    try:
        session.add(item)
        session.commit()
    except IntegrityError as err:
        if isinstance(err.orig, psycopg2.errors.UniqueViolation):
            raise HttpError(409, f"{item.__class__.__name__} already exists")
        else:
            raise err
    return item


def delete_item(item: MODEL, session: Session) -> MODEL:
    session.delete(item)
    session.commit()


def update_item(item: MODEL, payload: dict, session: Session) -> MODEL:
    for field, value in payload.items():
        setattr(item, field, value)
    add_item(item, session)
    return item


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


class NewLogin(BaseView):
    def post(self):
        payload = validate(Login, request.json)
        user = self.session.query(User).filter_by(name=payload['name']).first()
        if user is None:
            raise HttpError(404, "user not found")
        if check_password(user.password, payload["password"]):
            token = create_item(Token, {"user_id": user.id}, self.session)
            add_item(token, self.session)
            with open('token.txt', 'w') as file:
                file.write(str(token.token))
            return jsonify({"token": token.token})
        raise HttpError(401, "invalid password")


class NewUser(BaseView):
    @check_token
    def get(self):
        return jsonify(self.user.dict)

    def post(self):
        json_data = validate(CreateUser, request.json)
        json_data["password"] = hash_password(json_data["password"])
        user = create_item(User, json_data, self.session)
        response = jsonify({"id": user.id, "name": user.name})
        return response

    @check_token
    def patch(self):
        json_data = validate(PatchUser, request.json)
        user = update_item(self.token.user, json_data, self.session)
        return jsonify({"id": user.id, "name": user.name})

    @check_token
    def delete(self):
        delete_item(self.token.user, self.session)
        return jsonify({"status": "ok"})


class NewAdvertisement(BaseView):
    @check_token
    def get(self, adv_id: int = None):
        if adv_id is None:
            return jsonify([adv.dict for adv in self.user.advertisements])
        adv = get_item_by_id(Advertisement, adv_id, self.session)
        check_user(adv, self.token.user_id)
        return jsonify(adv.json)


    @check_token
    def post(self):
        json_data = validate(CreateAdv, request.json)
        adv = create_item(Advertisement, dict(user_id=self.token.user_id, **json_data), self.session)
        return jsonify(adv.json)


    @check_token
    def patch(self, adv_id: int = None):
        if adv_id is None:
            return "something is wrong"
        json_data = validate(PatchAdv, request.json)
        adv = get_item_by_id(Advertisement, adv_id, self.session)
        check_user(adv, self.token.user_id)
        adv = update_item(adv, json_data, self.session)
        return jsonify({"author": adv.author, "title": adv.title})

    @check_token
    def delete(self, adv_id: int = None):
        adv = get_item_by_id(Advertisement, adv_id, self.session)
        check_user(adv, self.token.user_id)
        delete_item(adv, self.session)
        return jsonify({"status": "ok"})


user_view = NewUser.as_view("user_view")
adv_view = NewAdvertisement.as_view("adv_view")

app.add_url_rule("/user", view_func=user_view, methods=["POST", "GET", "PATCH", 'DELETE'])
app.add_url_rule("/adv", view_func=adv_view, methods=["POST",],)
app.add_url_rule("/adv/<int:adv_id>", view_func=adv_view, methods=["GET", "PATCH", 'DELETE'])
app.add_url_rule("/login", view_func=NewLogin.as_view("login"), methods=["POST"])

app.run()
