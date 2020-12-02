from puller.kafkapuller import KafkaPuller
from config_consumer.config import Config
import requests


class ConsumerManager:
    def __init__(self):
        self._args = None
        self._kafka_puller = None
        self._config = None

    def __call__(self, args):
        self._args = args
        self._config = Config()
        result, error_message = self._config.set_configs(self._args.config_file)
        if result is False:
            yield self._config.ERROR_TO_EXIT, error_message
        # TODO: if user API is not available
        try:
            self._kafka_puller = KafkaPuller(self._config.KAFKA_BROKER, self._config.KAFKA_GROUP_NAME,
                                             self._args.client_id, self._args.session_timeout,
                                             True, self._config.ORG_NAME,
                                             self._config)
            for i in self._kafka_puller.listener(self._config.KAFKA_TOPIC, "0.1"):
                yield i
        except requests.exceptions.ConnectionError as e:
            yield False
