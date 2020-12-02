#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import requests


class UserUtils:
    def __init__(self, config):
        self._config = config
        self._user_api_url = self._config.USER_API_URL
        self._request_header = {"Accept": "application/json", "Content-Type": "application/json"}

    def find_user_by_name(self, first_name, last_name):
        """
        send request to User API in order to get a user object.
        :param first_name:
        :param last_name:
        :return: status_code, user_app
        """
        try:
            params = {"first_name": first_name, "last_name": last_name}
            url = self._user_api_url + "/filter"
            response = requests.get(url, headers=self._request_header, params=params)
            return response.status_code, response.json()
        except KeyboardInterrupt:
            print()
            exit(0)

    def get_user_by_id(self, user_id):
        url = self._user_api_url + "/" + user_id
        response = requests.request("GET", url)
        return response.status_code, response.json()

    def user_entity_handler(self, user):
        """
        Communicate with User API in order to ensure if entities are created for a user
        :param user: the user object
        :return:
        """
        user_id = user['id']
        user_email = user['profile']['email']
        first_name = user['profile']['firstName']
        last_name = user['profile']['lastName']
        login_name = user['profile']['login']
        params = {"first_name": first_name, "last_name": last_name,
                  "email":  user_email, "login": login_name, "user_id": user_id}
        url = self._user_api_url + "/entity"
        response = requests.request("GET", url, headers=self._request_header, params=params)
        return response.status_code, response.json()
