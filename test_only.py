from confluent_kafka import Producer
import json

if __name__ == "__main__":
    a = {"user_id": "Test SSL", "risk_level": 4, "timestamp": "2019-10-04T11:59:59.999Z"}
    b = json.dumps(a)
    p = Producer({'bootstrap.servers': 'kafka-iamlab.wbsntest.net:9093', 'security.protocol': 'SSL',
                  'ssl.ca.location': '/root/p12/key_store/client-ca.cer',
                  'ssl.certificate.location': '/root/p12/okta/key_store/client.cer',
                  'ssl.key.location': '/root/p12/key_store/client.key', 'ssl.key.password': 'changeme'})
    p.produce('ENTITY_RISK_LEVEL', b)
    p.flush(30)