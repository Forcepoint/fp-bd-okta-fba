#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import requests
import json
from time import sleep


class Publisher:
    def __init__(self, publish_url):
        self._publish_url = publish_url

    def send_notification(self, message, org_name, user_org_id, first_name, last_name, group_name):
        data = {"org_name": org_name, "user_id": user_org_id, "first_name": first_name,
                "last_name": last_name, "timestamp": message["timestamp"], "risk_level": message["risk_level"],
                "group_name": group_name}
        response = requests.post(self._publish_url, json=json.dumps(data))
        if response.status_code == 202 and "error" in response.json():
            if response.json()["error"] == 'the group risk_level_3 is not found on organization side':
                return 1, "risk level group does not exists on organization side", {}
        if response.status_code == 202 and "error" not in response.json():
            return 0, "", response.json()
        else:
            for i in range(3):
                print("Failed in published, Retrying  to push the new risk level")
                sleep(10)
                response = requests.post(self._publish_url, json=json.dumps(data))
                if response.status_code == 202:
                    return 0, "", response.json()
            return 1, "Failed in published", response.json()
