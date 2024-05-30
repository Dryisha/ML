from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonVirtualenvOperator
from airflow.utils.dates import days_ago

minio = Variable.get("minio")
cardio_bucket = Variable.get("cardio_bucket")
pkl_bucket = Variable.get("pkl_bucket")
prediction_bucket = Variable.get("prediction_bucket")

def data_from_minio(input_dir, minio, cardio_bucket):
    from minio import Minio
    import os

    file_name = "cardio_data.csv"

    client = Minio(
        minio, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=cardio_bucket, 
        object_name=file_name
    )

    file_path = os.path.join(f"{input_dir}", "cardio_data_s3.csv")
    with open(file_path, "wb") as gen_data:
        gen_data.write(content.data)

def artifact_from_s3(input_dir, minio, pkl_bucket):
    from minio import Minio
    import os

    pkl_name = "model.pkl"

    client = Minio(
        minio, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=pkl_bucket, 
        object_name=pkl_name
    )

    pkl_path = os.path.join(f"{input_dir}", "pkl_s3.pkl")
    with open(pkl_path, "wb") as model:
        model.write(content.data)
    
def predict_result(input_dir):
    import os
    import pickle
    import pandas as pd
    from sklearn.pipeline import Pipeline
    from typing import List
    from src.data_model import HealthData

    class Pred_Model:
        
        def __init__(self, path_to_file: str) -> None:
            pickle_path = os.path.join(f"{input_dir}", "pkl_s3.pkl")
            with open(pickle_path, "rb") as f:
                self.model: Pipeline = pickle.load(f)

        def predict(self, data_model: List[HealthData]) -> List:
            data = pd.DataFrame(data_model)
            return self.model.predict(data)

    pickle_path = os.path.join(f"{input_dir}", "pkl_s3.pkl")
    file_path = os.path.join(f"{input_dir}", "cardio_data_s3.csv")

    prediction_model = Pred_Model(pickle_path)
    
    df = pd.read_csv(file_path)
    predictions = prediction_model.predict(df)

    predictions_file_path = os.path.join(f"{input_dir}", "pred.txt")
    with open(predictions_file_path, "w") as pred:
        pred.write(str(predictions))


def upload_predictions_to_minio(input_dir, minio, prediction_bucket):
    import os
    from minio import Minio

    pred_file_path = os.path.join(f"{input_dir}", "pred.txt")
    pred_file_size = os.path.getsize(pred_file_path)

    with open(pred_file_path, "rb") as prdct:
        client = Minio(
            minio,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=prediction_bucket,
            object_name="pred.txt",
            data=prdct,
            length=pred_file_size,
        )


default_args = {
    "owner": "Ksu_Antipova",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "prediction_send_to_minio", 
    default_args=default_args, 
    schedule_interval=None, 
    start_date=days_ago(1)
):
    data_from_s3 = PythonVirtualenvOperator(
        task_id="data_from_s3", 
        python_callable=data_from_minio,
        op_args=["{{ds}}", minio, cardio_bucket],
        requirements=["minio"]
    )

    artifact_from_s3 = PythonVirtualenvOperator(
        task_id="artifact_from_s3", 
        python_callable=artifact_from_s3,
        op_args=["{{ds}}", minio, pkl_bucket],
        requirements=["minio"]
    )
    predict_data = PythonVirtualenvOperator(
        task_id="predict",
        python_callable=predict_result,
        op_args=["{{ds}}"]
    )

    result_to_s3 = PythonVirtualenvOperator(
        task_id="upload_predictions_to_s3", 
        python_callable=upload_predictions_to_minio,
        op_args=["{{ds}}", minio, prediction_bucket],
        requirements=["minio"]
    )

    data_from_s3 >> artifact_from_s3 >> predict_data >> result_to_s3