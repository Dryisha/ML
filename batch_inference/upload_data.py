from datetime import datetime
from pathlib import Path

from minio import Minio


PROCEED_DATA_FOLDER = Path("proceed_data")
current_date = datetime.now().strftime("%Y-%m-%d")


client = Minio("localhost:9003", access_key="miniouser", secret_key="miniouser", secure=False)
content = client.get_object("data", f"{current_date}.csv")
with open(PROCEED_DATA_FOLDER / f"{current_date}.csv", "wb") as fio:
    fio.write(content.data)
