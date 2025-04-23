from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer


def user_from_dict(user, ctx):
    """
   Десериализация объекта пользователя из dict.
   """
    return user


if __name__ == "__main__":
    schema_registry_url = "http://51.250.37.0:8081"
    topic = "data_topic"

    consumer_conf = {
        "bootstrap.servers": "rc1d-9a231tu2d3r1fgdv.mdb.yandexcloud.net:9091,rc1d-b2oto009a86oslfg.mdb.yandexcloud.net:9091,rc1d-pbv9db5m2h8uf9gq.mdb.yandexcloud.net:9091",
        "group.id": "group",
        "auto.offset.reset": "earliest",
        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "yandex_ca.crt",
        "sasl.mechanism": "SCRAM-SHA-512",
        "sasl.username": "***",
        "sasl.password": "***"
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
    latest = schema_registry_client.get_latest_version(topic + "-value")
    json_schema_str = latest.schema.schema_str
    json_deserializer = JSONDeserializer(json_schema_str, from_dict=user_from_dict)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Error: {msg.error()}")
                break

            context = SerializationContext(msg.topic(), MessageField.VALUE)
            user = json_deserializer(msg.value(), context)
            print(f"Message on {msg.topic()}:\n{user}")
            break
    except KeyboardInterrupt as err:
        print(f"Consumer error: {err}")
    finally:
        consumer.close()
        print("Closing consumer")
