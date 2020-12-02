#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from lib_event.execmd import ExeCmd

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
        print(cmd)
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
              ' -H "Authorization: SSWS {}" "https://{}/api/v1/groups/%s/user_app?limit=200"'.format(self._token,
                                                                                                  self._url, group_id)
        if group_id is not None:
            cmd += "/{}".format(group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def add_user_to_group(self, group_id, user_id):
        """
        add a user to an exist group
        :param group_id: the group id
        :param user_id: the user id
        :return: error_code, error_message, user
        """
        cmd = 'curl -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
              '"Authorization: SSWS %s"  "https://%s/api/v1/groups/%s/users/%s"' % (self._token, self._url,
                                                                                    group_id, user_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

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
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output


if __name__ == "__main__":
    group_class = Groups("00hiXLADgH95LiK4UcKJF562VlbSO5AjXdDx8lz-ig", "livedlo.okta.com")
    print(group_class.create_group("te3st2_1", "wwww"))
    print(group_class.get_group("00g1ku4o8s9vgBAxS357"))

