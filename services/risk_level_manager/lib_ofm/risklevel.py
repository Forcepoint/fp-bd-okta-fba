import json
import glob
import requests


class RiskLevel:
    def __init__(self, config, logger):
        self._logger = logger
        self._config = config

    def process_risk_level(self, data):
        """
        change users group according to the user's risk level
        :param data: json file
        :return:error_code, error_message, response_data
        """
        return self._process_job(data)

    def register_with_connector(self):
        data = {"org_name": self._config.ORG_NAME, "endpoint": f"{self._config.SELF_ADDRESS}/submit", "data_format": "json"}
        response = requests.request("POST", "http://{}/{}".format(self._config.CONNECTOR_ADDRESS, "register")
                                    , json=data)
        if response.status_code != 201:
            return False
        return True

    def _process_job(self, job_data):
        """
        change the user's group according to the users risk level
        :param job_data: the job data
        :return: error_code, error_message, response
        """
        try:
            url = "http://{}/user/{}".format(self._config.USER_APP_ADDRESS, job_data["user_id"])
            response = requests.get(url)
            response_json = response.json()
            if response.status_code != 200:
                return self._config.ERROR_CODE_ONE, response_json["error"], {}
            # ensure user name

            return self._risk_level_handler(job_data["user_id"], job_data["group_name"],
                                            int(job_data["risk_level"] - 1))
        except Exception as e:
            return self._config.ERROR_CODE_ONE, "Failed in processing job '{}: {}'".format(job_data, e), {}

    def _risk_level_handler(self, user_id, current_group_name, risk_level):
        group_name = self._config.GROUPS_NAME[risk_level]
        error_code, error_message, response = self._change_users_group(user_id, current_group_name, group_name)
        return error_code, error_message, response

    def _change_users_group(self, user_id, current_group_name, new_group_name):
        url = "{}/groups/change".format(self._config.USER_APP_ADDRESS)
        if not url.startswith("http://") or url.startswith("https://"):
            url = "http://" + url
        param = {"user_id": user_id, "current_group": current_group_name, "new_group": new_group_name}
        response = requests.post(url, json=json.dumps(param))
        if response.status_code != 201:
            return self._config.ERROR_CODE_ONE, response.json()["error"], {}
        return self._config.ERROR_CODE_ZERO, "", response.json()


