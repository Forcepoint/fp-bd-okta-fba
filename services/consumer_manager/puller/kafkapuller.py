#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from cunsumer.consumerhandler import ConsumerHandler
from database.databasehandler import DataBaseHandler
from publisher.publisher import Publisher
from organization.organization import Organization
from database.userutils import UserUtils


class KafkaPuller:
    def __init__(self, bootstrap_servers, group_id, client_id, timeout, auto_commit, org_name, config):
        self._config = config
        self._user_utils = UserUtils(self._config)
        self._org = Organization(org_name, self._user_utils)
        self._consumer = ConsumerHandler(bootstrap_servers, group_id, client_id, timeout, auto_commit, config)
        self._database_handler = DataBaseHandler(self._config.DATABASE_LOCATION, self._org,
                                                 self._user_utils, self._config)
        self._publisher = Publisher(self._config.CONNECTOR_PUBLISH_API_URL)

    def listener(self, topic, timeout):
        """
        Listen to new messages and notify the the DataBaseManager about it.
        :param topic: the topic name
        :param timeout: Maximum time to block waiting for message, event or callback
        :return: error_code, error_message
        """
        for error_code, error_message, message in self._consumer.message_listener(topic, float(timeout)):
            if error_code != 0:
                yield False
            else:
                yield self._database_handler.handle_message(message, self._publisher)
