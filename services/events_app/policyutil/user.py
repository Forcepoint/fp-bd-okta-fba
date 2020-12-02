#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from lib_event.execmd import ExeCmd

ERROR_CODE_ONE = 1
ERROR_CODE_ZERO = 0


class User:
    def __init__(self, okta_token, okta_url):
        self._url = okta_url
        self._token = okta_token
        self._execmd = ExeCmd()

    def create_user(self, first_name, last_name, email, mobile,  password,
                    recovery_question, recovery_answer, groups=None):
        """
        Creates a new user with a password and recovery question & answer
        :param first_name: the user's first name
        :param last_name: the user_app last name
        :param email: the user's email address
        :param mobile: the mobile number of the user
        :param password: the user password
        :param recovery_question: the user recovery question
        :param recovery_answer: the user recovery answer
        :param groups: list of groups to add the user_app into these groups
        :return: error_code, error_message, user
        """
        if groups is None:
            groups = ""
        else:
            group_str = ''
            for group in groups:
                group_str += '"{}", '.format(group)
            groups = group_str[:-2]

        cmd = 'curl -X POST -H "Accept: application/json"' \
              ' -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS %s" -d \'{"profile": {"firstName": "%s","lastName": "%s",' \
              ' "email": "%s","login": "%s",' \
              '"mobilePhone": "%s"}, "credentials": { "password" : { "value": "%s" },' \
              ' "recovery_question":{"question": "%s", "answer": "%s"}}%s}\' ' \
              '"https://%s/api/v1/users?activate=false"' % (self._token, first_name,
                                                            last_name, email, email, mobile, password,
                                                            recovery_question, recovery_answer,  self._url, groups)
        output, error = self._execmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorCauses"][0]["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def get_user(self, user_id):
        """
        Fetches a user from your Okta organization
        :param user_id:
        :return:
        """


if __name__ == "__main__":
    user = User("00hiXLADgH95LiK4UcKJF562VlbSO5AjXdDx8lz-ig", "livedlo.okta.com")
