from cunsumer.consumer_confluent_kafka import KafkaConsumer


ERROR_CODE_ZERO = 0


class ConsumerHandler:
    def __init__(self, bootstrap_servers, group_id, client_id, timeout, auto_commit, config):
        self._consumer = KafkaConsumer(bootstrap_servers, group_id, client_id, timeout, auto_commit, config)

    def message_listener(self, topic, timeout):
        """
        listen to new messages and yield them
        :return: error_code, error_message, message_json
        """
        """
        demo_message = [
                        {'user_id': 'Lazy Man', 'timestamp': '2019-10-06T22:59:59.989Z', 'risk_level': 3}
                        ]

        for message in demo_message:
            yield ERROR_CODE_ZERO, "", message
        """

        while True:
            for error_code, error_message, message in self._consumer.subscribe(topic, timeout):
                yield error_code, error_message, message
                if error_code == 1:
                    break


