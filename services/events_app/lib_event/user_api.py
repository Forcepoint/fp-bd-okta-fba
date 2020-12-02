#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import requests


class UserApi:
    def __init__(self, config):
        self._config = config

    def acknowledge_user_app(self, url):
        parts = url.split("/")[-1]
        parts = parts.split(":")
        if len(parts) == 1:
            return self._config.SKIP_URL_ACK, ""
        if len(parts) == 3:
            if parts[0] == "unknown":
                return self._config.SKIP_URL_ACK, ""
            user_name = parts[0].split()
            if len(user_name) < 2:
                return self._config.SKIP_URL_ACK, ""
            first_name = user_name[0]
            last_name = user_name[1]
            use_email_address = parts[1]
            if '@' not in use_email_address:
                return self._config.SKIP_URL_ACK, ""
            return self._send_notification(first_name, last_name, use_email_address)

    def _send_notification(self, first_name, last_name, use_email_address):
        url = f"{self._config.USER_APP_API}/entity"
        if not url.startswith("http://") or not url.startswith("https://"):
            url = "http://" + url
        data = {"first_name": first_name,
                "last_name": last_name,
                "email_address": use_email_address
                }
        response = requests.post(url, json=data, )
        response_json = response.json()
        if response.status_code == 201:
            return self._config.ERROR_CODE_ZERO, response_json["entity_id"]
        else:
            return self._config.ERROR_CODE_ONE, response_json["error"]
