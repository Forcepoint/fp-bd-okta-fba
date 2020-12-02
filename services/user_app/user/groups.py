from lib_user.execmd import ExeCmd
from time import sleep
ERROR_CODE_ONE = 1
ERROR_CODE_ZERO = 0


class Groups:
    def __init__(self, token, url):
        self._token = token
        self._url = url
        self._exe_cmd = ExeCmd()

    def create_group(self, group_name, description):
        """
        Create a user group
        :param group_name: the group name
        :param description: the description
        :return: error_code, error_message, group
        """
        cmd = 'curl -v -X POST -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
              '"Authorization: SSWS %s" -d \'{ "profile": { "name": "%s",' \
              ' "description": "%s"}}\' "https://%s/api/v1/groups"' % (self._token, group_name, description, self._url)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "",  output

    def get_group(self, group_id=None):
        """
        find and return the group with ID=group_id, if group_id is None, return all exists groups
        :param group_id:  the group_id
        :return: error_code, error_message, group
        """
        cmd = 'curl -X GET -H "Accept: application/json" -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS {}" "https://{}/api/v1/groups"'.format(self._token, self._url)
        if group_id is not None:
            cmd += "/{}".format(group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def update_group(self, group_id, new_name, new_description):
        """
        update a group by replacing the new profile with the old one
        :param group_id: the group id
        :param new_description: a description
        :param new_name: a new name
        :return: error_code, error_message, group
        """
        cmd = 'curl -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
              '"Authorization: SSWS %s" -d \'{ "profile": { "name": "%s",' \
              ' "description": "%s"}}\' "https://%s/api/v1/groups/%s"' % (self._token, new_name,
                                                                          new_description, self._url, group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def remove_group(self, group_id):
        """
        remove a user group
        :param group_id: The user group
        :return: error_code, error_message, group
        """
        cmd = 'curl -X DELETE -H "Accept: application/json" -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS {}" "https://{}/api/v1/groups/%s"'.format(self._token, self._url, group_id)
        if group_id is not None:
            cmd += "/{}".format(group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def get_group_users(self, group_id):
        """
        get the user_app in a specific group
        :param group_id: the group id
        :return: error_code, error_message, user_app
        """
        cmd = 'curl -X GET -H "Accept: application/json" -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS {}" "https://{}/api/v1/groups/{}/users"'.format(self._token, self._url, group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def add_user_to_group(self, group_id, user_id):
        """
        add a user to an exist group
        :param group_id: the group id
        :param user_id: the user id
        :return: error_code, error_message, user
        """
        # check if user is exists:
        error_code, error_message, users = self.get_group_users(group_id)
        if len(users) != 0:
            for i in users:
                if i["id"] == user_id:
                    self.remove_user_from_group(group_id, user_id)
                    sleep(3)

        cmd = 'curl -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
                '"Authorization: SSWS %s"  "https://%s/api/v1/groups/%s/users/%s"' % (self._token, self._url,
                                                                                        group_id, user_id)
        output, error = self._exe_cmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], ""
        else:
            return ERROR_CODE_ZERO, "", group_id

    def remove_user_from_group(self, group_id, user_id):
        """
        remove a user from a group
        :param group_id: group id
        :param user_id: user id
        :return: error_code, error_message, user
        """
        cmd = 'curl -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
              '"Authorization: SSWS %s"  "https://%s/api/v1/groups/%s/users/%s"' % (self._token, self._url,
                                                                                    group_id, user_id)
        output, error = self._exe_cmd.run(cmd)

        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def filter_groups_by_name(self, group_name):
        """
        Filter groups by name
        :param group_name: the group name
        :return:
        """
        cmd = 'curl -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS {}"' \
              ' "https://{}/api/v1/groups?q={}"'.format(self._token, self._url, group_name)
        output, error = self._exe_cmd.run(cmd)
        if len(output) != 0:
            for group in output:
                if group["profile"]["name"].lower() == group_name.lower():
                    return ERROR_CODE_ZERO, "", group

        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ONE, "the group {} is not found on organization side".format(group_name), output

    def change_group(self, user_id, current_group, new_group, terminate_session):
        """
        removes users from current group and add it to the new group
        :param user_id: the user's id
        :param current_group: the user's current group
        :param new_group: the user's new group
        :param terminate_session: if true, terminate the user's active sessions
        :return: error_code, error_message, response_data
        """
        new_group_name = new_group
        error_code, error_message, new_group = self.filter_groups_by_name(new_group)
        if error_code != 0:
            return error_code, error_message, {}
        if current_group != "":
            error_code, error_message, current_group_object = self.filter_groups_by_name(current_group)
            if error_code != 0:
                return error_code, error_message, {}
            current_group_id = current_group_object["id"]
            error_code, error_message, output = self.remove_user_from_group(current_group_id, user_id)
            if error_code != 0:
                return error_code, error_message, output
            error_code, error_message, group_user = self.get_group_users(current_group_id)
            for u in group_user:
                if u["id"] == user_id:
                    error_code, error_message, output = self.remove_user_from_group(current_group_id, user_id)
                    if error_code != 0:
                        return error_code, error_message, output
            sleep(3)
        new_group_id = new_group["id"]
        error_code, error_message, group_id = self.add_user_to_group(new_group_id, user_id)
        if error_code == 0 and terminate_session is True:
            current_group = current_group[-1] if len(current_group) != 0 else 0
            if int(current_group) < int(new_group_name[-1]):
                error_code_terminate, error_message_terminate, result = self.terminate_session(user_id)
        if error_code != 0:
            return error_code, error_message, group_id
        return 0, "", {"status": "success",
                       "new_group_name": new_group,
                       "new_group_id": group_id}

    def terminate_session(self, user_id):
        """
        Removes all active identity provider sessions. This forces the user to authenticate on the next operation
        :param user_id: user ip
        :return:error_code, error_message, response
        """
        cmd = 'curl -X DELETE -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/sessions"' % (self._token, self._url, user_id)
        output, error = self._exe_cmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

if __name__ == "__main__":
    group_class = Groups("00i3NGyCptMBpO-PbV5v7MHNZ-VeYtjFzXnSRtB9VK", "forcepointbizdev.okta.com")
    #print(group_class.create_group("Risk_level_2", "The Group for risk level 2"))
    print(group_class.filter_groups_by_name("risk_level_4"))

    #print(group_class.add_user_to_group("00g1nizk68ieQ9P8O357", "00u1nj50r1XZD0e1l357"))
    #print(group_class.remove_user_from_group("00g1nizk68ieQ9P8O357", "00u1ok7ywiqPPHowm357"))

    #error, mesg, user = group_class.get_group_users("00g1nizk68ieQ9P8O357")
    #for i in user:
    #   print(i["id"])
