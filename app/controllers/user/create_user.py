from flask import Blueprint, g
from app.constants import USERNAME_KEY, PASSWORD_KEY, MAX_PASSWORD_LENGTH, MAX_USERNAME_LEGNTH, MIN_PASSWORD_LENGTH,MIN_USERNAME_LENGTH, ERRORS_KEY
from app.controllers import get_required_key_from_params
from app.models.error import Error
from app.models.user import User
from app.models import db
from app.dao.user_dao import get_user_from_username

user_blueprint = Blueprint('mod_user', __name__)


@user_blueprint.route('', methods=['POST'])
def create():
    supplied_username = get_required_key_from_params(USERNAME_KEY, g.request_params)
    supplied_password = get_required_key_from_params(PASSWORD_KEY, g.request_params)

    # check username is between min and max length and contains no spaces
    if len(supplied_username) < MIN_USERNAME_LENGTH:
        Error.add_to_response_dict(g.response.response, Error.username_too_short())

    if len(supplied_username) > MAX_USERNAME_LEGNTH:
        Error.add_to_response_dict(g.response.response, Error.username_too_long())

    if " " in supplied_username:
        Error.add_to_response_dict(g.response.response, Error.username_contains_spaces())

    # check password is between min and max length
    if len(supplied_password) < MIN_PASSWORD_LENGTH:
        Error.add_to_response_dict(g.response.response, Error.password_too_short())

    if len(supplied_password) > MAX_PASSWORD_LENGTH:
        Error.add_to_response_dict(g.response.response, Error.password_too_long())

    if ERRORS_KEY in g.response.response:
        g.response.status_code = 422
        return g.response

    # check username is not taken
    if get_user_from_username(supplied_username) is not None:
        Error.add_to_response_dict(g.response.response, Error.username_is_taken())
        g.response.status_code = 409
        return g.response

    # create user in db and save
    user = User(supplied_username, supplied_password)
    db.session.add(user)
    db.session.commit()

    g.response.status_code = 201
    return g.response
