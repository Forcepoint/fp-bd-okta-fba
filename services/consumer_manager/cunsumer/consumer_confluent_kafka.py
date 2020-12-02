
from confluent_kafka import Consumer, KafkaError
from sys import exit
import json

ERROR_CODE_ZERO = 0
ERROR_CODE_ONE = 1
EMPTY_ERROR_MESSAGE = ""


class KafkaConsumer:
    def __init__(self, bootstrap_servers, group_id, client_id, timeout, auto_commit, config):
        self._server = bootstrap_servers
        self._group_id = group_id
        self._timeout = timeout
        self._auto_commit = auto_commit
        self._client_id = client_id
        self._config = config
        self._consumer = self._build_consumer()

    def subscribe(self, topic_name, timeout):
        """
        Subscribe for topic and listen to new messages until the timeout of
         Kafka consumer occurs which will end the session
        :param topic_name: the topic name
        :param timeout: Maximum time to block waiting for message, event or callback
        :return: error_code, error, message
        """
        self._consumer.subscribe([topic_name])
        try:
            while True:
                msg = self._consumer.poll(timeout)
                if msg is None:
                    continue
                elif not msg.error():
                    yield ERROR_CODE_ZERO, EMPTY_ERROR_MESSAGE, json.loads(msg.value())
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    yield ERROR_CODE_ONE, 'End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()), None
                else:
                    yield ERROR_CODE_ONE, 'Error occured: {0}'.format(msg.error().str()), None
        except KeyboardInterrupt:
            exit(0)
        finally:
            self._consumer.close()

    def _build_consumer(self):
        """
        Creates kafka consumer object.
        :return:
        """
        settings = {
            'bootstrap.servers': self._server,
            'group.id': self._group_id,
            'client.id': self._client_id,
            'enable.auto.commit': self._auto_commit,
            'session.timeout.ms': self._timeout,
            'security.protocol': 'SSL',
            'ssl.ca.location': self._config.CLIENT_CA_CER,
            'ssl.certificate.location': self._config.CLIENT_CER,
            'ssl.key.location': self._config.CLIENT_KEY,
            'ssl.key.password': self._config.KEY_STORE_PASS,
            #'auto.offset.reset': 'smallest'
            # 'auto.offset.reset': 'smallest'
        }
        try:
            cons = Consumer(settings)
            return cons
        except Exception as e:
            print("Error in creating the Consumer: ", e)
            #exit(1)


if __name__ == "__main__":
    consumer = KafkaConsumer('10.203.224.205:9094', "okta_test", "client_1",
                             600, True)
    for i, b, c in consumer.subscribe('ENTITY_RISK_LEVEL', 0.1):
        print(i, b, c)


