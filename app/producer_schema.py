from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.json_schema import JSONSerializer


def user_to_dict(user, ctx):
    """
   Сериализация объекта пользователя в dict.
   """
    return user


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered message to topic {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


MESSAGE_SCHEMA_STR = """
{
 "$schema": "http://json-schema.org/message-01/schema#",
 "title": "Message",
 "type": "object",
 "properties": {
    "id": { "type": "integer" },
    "from": { "type": "string" },
    "to": { "type": "string" },
    "msg": { "type": "string" }
 }, 
 "required": ["id", "from", "to","msg"]
}
"""

if __name__ == "__main__":
    bootstrap_servers = "rc1d-9a231tu2d3r1fgdv.mdb.yandexcloud.net:9091,rc1d-b2oto009a86oslfg.mdb.yandexcloud.net:9091,rc1d-pbv9db5m2h8uf9gq.mdb.yandexcloud.net:9091"
    schema_registry_url = "http://51.250.37.0:8081"
    topic = "data_topic"
    subject = topic + "-value"

    producer_conf = {
        "bootstrap.servers": bootstrap_servers,
        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "yandex_ca.crt",
        "sasl.mechanism": "SCRAM-SHA-512",
        "sasl.username": "***",
        "sasl.password": "***",
    }

    producer = Producer(producer_conf)
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

    try:
        latest = schema_registry_client.get_latest_version(subject)
        print(f"Schema is already registered for {subject}:\n{latest.schema.schema_str}")
    except Exception:
        schema_object = Schema(MESSAGE_SCHEMA_STR, "JSON")
        schema_id = schema_registry_client.register_schema(subject, schema_object)
        print(f"Registered schema for {subject} with id: {schema_id}")

    json_serializer = JSONSerializer(MESSAGE_SCHEMA_STR, schema_registry_client, user_to_dict)
    user = {
        "id": 2,
        "from": "demo_user",
        "to": "user_113",
        "msg": "hello1"
    }
    context = SerializationContext(topic, MessageField.VALUE)
    serialized_value = json_serializer(user, context)

    producer.produce(
        topic,
        key="first-user-msg",
        value=serialized_value,
        callback=delivery_report,
    )
    producer.flush()
