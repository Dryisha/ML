import time
import uuid
import random
from os import environ
from kafka import KafkaProducer
from src.data_model import BloodDonationRow
from src.constants import FIRST_KAFKA_TOPIC
from dotenv import load_dotenv

load_dotenv()

SERVER = environ.get("KAFKA_SERVER")

producer = KafkaProducer(bootstrap_servers=SERVER)

while True:
    proba_recency_months=random.randint(0, 74)
    proba_frequency_times=random.randint(1, 50)
    proba_monetary_cc_blood=random.randint(250, 8000)
    proba_time_months=random.randint(2, 98)
    pred_row = BloodDonationRow(recency_months=proba_recency_months,
                             frequency_times=proba_frequency_times,
                             monetary_cc_blood=proba_monetary_cc_blood,
                             time_months=proba_time_months)
    
    producer.send(topic=FIRST_KAFKA_TOPIC, key=str(uuid.uuid4()).encode("utf8"), value=pred_row.json().encode("utf8"))
    time.sleep(5)
