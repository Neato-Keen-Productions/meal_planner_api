from flask import request, Blueprint, g, jsonify
from app.dao.user_dao import get_user_from_username
from app.models.authorization import Authorization
from app.models import db
from app.models.error import Error

auth_blueprint = Blueprint('mod_auth', __name__)


USERNAME_KEY = "username"
PASSWORD_KEY = "password"

@auth_blueprint.route('/login',  methods=['POST'])
def login():
    supplied_username = get_required_key_from_params(USERNAME_KEY, g.request_params)
    supplied_password = get_required_key_from_params(PASSWORD_KEY, g.request_params)

    if supplied_username is not None and supplied_password is not None:
        user = get_user_from_username(supplied_username)

        if user is not None and user.check_hashed_password(supplied_password):
            auth = Authorization(user)
            db.session.add(auth)
            db.session.commit()
            g.response = {"data": {"auth_token": auth.token}}
        else:
            Error.add_to(g.response, Error.auth_invalid())

    return jsonify(**g.response)


def get_required_key_from_params(key, params):
    value = None
    if key in params:
        value = params[key]
    else:
        Error.add_to(g.response, Error.missing_required_param(key))

    return value
