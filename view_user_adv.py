from flask import jsonify, request
from flask.views import MethodView
from models import Advertisement, User, Token, Session
from schema import CreateUser, PatchUser, CreateAdv, PatchAdv, Login
from error_handler import HttpError
from crud import create_item, add_item, update_item, delete_item, get_item_by_id
from check_auth_validate import hash_password, check_password, check_token, check_user, validate


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
