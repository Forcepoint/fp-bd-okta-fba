#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from flask import jsonify


class UserAPI:
    def __init__(self, config, logger):
        self._user = None
        self._logger = logger
        self._config = config

    def set_user(self, user):
        self._user = user

    def get_user(self, user_id=None):
        error_code, error_message, users = self._user.get_user(user_id)
        if error_code != 0:
            return jsonify({"error": error_message}), 400
        else:
            return jsonify(users), 200

    def find_user_by_name(self, first_name, last_name):
        if first_name is None:
            return jsonify({"error": "Missing the first_name parameter"}), 400
        if last_name is None:
            return jsonify({"error": "Missing the last_name parameter"}), 400
        error_code, error_message, users = self._user.find_user_by_name(first_name, last_name)
        if error_code != 0:
            return jsonify({"error": error_message}), 400
        else:
            return jsonify(users), 200

