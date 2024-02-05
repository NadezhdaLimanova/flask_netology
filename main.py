from error_handler import get_app, HttpError, error_handler
from flask import Response, request
from models import Session
from view_user_adv import NewUser, NewLogin, NewAdvertisement

app = get_app()


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: Response):
    request.session.close()
    return response


user_view = NewUser.as_view("user_view")
adv_view = NewAdvertisement.as_view("adv_view")

app.add_url_rule("/user", view_func=user_view, methods=["POST", "GET", "PATCH", 'DELETE'],)
app.add_url_rule("/adv", view_func=adv_view, methods=["POST",],)
app.add_url_rule("/adv/<int:adv_id>", view_func=adv_view, methods=["GET", "PATCH", 'DELETE'])
app.add_url_rule("/login", view_func=NewLogin.as_view("login"), methods=["POST"])

app.register_error_handler(HttpError, error_handler)


if __name__ == "__main__":
    app.run()