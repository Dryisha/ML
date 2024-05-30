from os import environ
import json
import uuid
from kafka import KafkaConsumer, KafkaProducer
from src.model import PredictionModel
from src.constants import MODEL_NAME, CONSUMER_GROUP_ID, CONSUMER_AUTORESET, CONSUMER_TIMEOUT, FIRST_KAFKA_TOPIC, SECOND_KAFKA_TOPIC
from dotenv import load_dotenv
from src.data_model import BloodDonationRow

load_dotenv()

SERVER = environ.get("KAFKA_SERVER")
BATCH = 5

prediction_model = PredictionModel(MODEL_NAME)

producer = KafkaProducer(
    bootstrap_servers=SERVER,
    key_serializer=lambda x: str(x).encode("utf8"),
    value_serializer=lambda x: json.dumps(x).encode("utf8")
)

consumer = KafkaConsumer(
    FIRST_KAFKA_TOPIC,
    bootstrap_servers=SERVER, 
    group_id=CONSUMER_GROUP_ID,
    auto_offset_reset=CONSUMER_AUTORESET,
    consumer_timeout_ms=CONSUMER_TIMEOUT,
    value_deserializer=lambda x: BloodDonationRow.parse_raw(x.decode('utf8')),
    enable_auto_commit=True,
    auto_commit_interval_ms=5000
)

while True:
    batch = []
    for _ in range(BATCH):
        try:
            message = consumer.next_v2()
            value = message.value
            batch.append(value)
            print("Received value:", value)
        except StopIteration:
            break
    if len(batch) != 0:
        data_row = [i for i in batch]
        print("Data row:", data_row)
        pred = prediction_model.predict(data_row)
        print("Prediction:", pred)
        for i, data_json in enumerate(batch):
            some_results = {
                "result": pred[i],
                **data_json.dict(),
            }
            producer.send(topic=SECOND_KAFKA_TOPIC, key=str(uuid.uuid4()), value=some_results)
        consumer.commit()
