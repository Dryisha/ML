import os
from datetime import datetime
from minio import Minio

RAW_DATA_FOLDER = "raw_data"
current_date = datetime.now().strftime("%Y-%m-%d")
file_path = f"{RAW_DATA_FOLDER}/{current_date}.csv"

file_size = os.path.getsize(file_path)


client = Minio("localhost:9003", access_key="miniouser", secret_key="miniouser", secure=False)
client.put_object("data", f"{current_date}.csv", data=open(file_path, "rb"), length=file_size)
