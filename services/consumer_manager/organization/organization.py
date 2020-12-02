#
# Author:  Dlo Bagari
# created Date: 12-10-2019


class Organization:
    def __init__(self, name, user_utils):
        self._name = name
        self._user_utils = user_utils
        self._users_name = set()

    def add_user(self, user_name):
        self._users_name.add(user_name)

    def is_user_exists(self, user_name):
        return user_name in self._users_name

    def has_user(self, user_id):
        status_code, user = self._user_utils.find_user_by_name(user_id[0], user_id[1])
        if status_code != 200 or len(user) == 0:
            return False, ""
        user = user[0]
        if user['profile']['firstName'] == user_id[0] and user['profile']['lastName'] == user_id[1]:
            return True, user["id"]
        return False, ""


