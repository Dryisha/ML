from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonVirtualenvOperator
from airflow.utils.dates import days_ago

minio = Variable.get("minio")
cardio_bucket = Variable.get("cardio_bucket")
train_bucket = Variable.get("train_bucket")
pkl_bucket = Variable.get("pkl_bucket")
metrics_bucket = Variable.get("metrics_bucket")

def upload_data_to_minio(input_dir, minio, cardio_bucket):
    import os
    from minio import Minio

    file_path = os.path.join(f"{input_dir}", "cardio_data.csv")
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as fl:
        client = Minio(
            minio,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser"
        )
        content = client.put_object(
            bucket_name=cardio_bucket, 
            object_name="cardio_data.csv",
            data=fl,
            length=file_size,  
            content_type="application/csv",
        )

def download_cardio_data(input_dir, minio, train_bucket):
    from minio import Minio
    import os

    file_name = "cardio_train.csv"

    client = Minio(
        minio, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=train_bucket, 
        object_name=file_name
    )

    file_path = os.path.join(f"{input_dir}", "cardio_train.csv")
    with open(file_path, "wb") as fio:
        fio.write(content.data)

def data_train(input_dir):
    import os
    import pickle
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer

    COLUMNS = ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active", "cardio"]
    NUMERIC = ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"]
    TARGET = "cardio"

    FILEPATH = os.path.join(f"{input_dir}", "cardio_train.csv")
    df = pd.read_csv(FILEPATH, sep=';')
    df = df.loc[:, COLUMNS]
    y = df[TARGET]

    train_X, test_X, train_y, test_y = train_test_split(
                df.drop(columns=[TARGET]), y, test_size=0.2, random_state=42,
            shuffle=True, stratify=y
    )

    transforms = ColumnTransformer(
        [
            ("normalizer", Pipeline(
                [
                    ("impute", SimpleImputer(strategy="mean")),
                    ("norm", StandardScaler())
                ]
            ), NUMERIC)
        ]
    )

    pipeline = Pipeline([
        ("transforms", transforms),
        ("model", RandomForestClassifier(n_estimators=50, n_jobs=-1))
    ])

    pipeline.fit(train_X, train_y)
    pred = pipeline.predict(test_X)
    f1 = f1_score(test_y, pred)
    
    pkl_file_path = os.path.join(f"{input_dir}", "model.pkl")
    with open(pkl_file_path, "wb") as pkl:
        pickle.dump(pipeline, pkl)

    roc_auc_path = os.path.join(f"{input_dir}", "f1.txt")
    with open(roc_auc_path, "w") as f1_score:
        f1_score.write(str(f1))

def pkl_to_minio(input_dir, minio, pkl_bucket):
    import os
    from minio import Minio

    pkl_file_path = os.path.join(f"{input_dir}", "model.pkl")
    pkl_file_size = os.path.getsize(pkl_file_path)

    with open(pkl_file_path, "rb") as pkl:
        client = Minio(
            minio,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=pkl_bucket,
            object_name="model.pkl",
            data=pkl,
            length=pkl_file_size,
        )

def metrics_to_minio(input_dir, minio, metrics_bucket):
    import os
    from minio import Minio

    metrics_file_path = os.path.join(f"{input_dir}", "f1.txt")
    metrics_file_size = os.path.getsize(metrics_file_path)

    with open(metrics_file_path, "rb") as metrics:
        client = Minio(
            minio,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=metrics_bucket,
            object_name="f1.txt",
            data=metrics,
            length=metrics_file_size,
        )

default_args = {
    "owner": "Cheboksarov",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "upload_and_download_from_S3_and_train", 
    default_args=default_args, 
    schedule_interval=None, 
    start_date=days_ago(1)
):
    upload_to_minio = PythonVirtualenvOperator(
        task_id="upload_data_to_minio",
        python_callable=upload_data_to_minio,
        op_args=["{{ds}}", minio, cardio_bucket],
        requirements=["minio"]
    )
    download_from_minio = PythonVirtualenvOperator(
        task_id="data_from_minio", 
        python_callable=download_cardio_data,
        op_args=["{{ds}}", minio, train_bucket],
        requirements=["minio"]
    )
    
    model_train = PythonVirtualenvOperator(
        task_id="train",
        python_callable=data_train,
        op_args=["{{ds}}"],
        requirements=["pandas", "scikit-learn"]
    )

    upload_pkl = PythonVirtualenvOperator(
        task_id="upload_pkl", 
        python_callable=pkl_to_minio,
        op_args=["{{ds}}", minio, pkl_bucket],
        requirements=["minio"]
    )

    upload_metrics = PythonVirtualenvOperator(
        task_id="upload_metrics", 
        python_callable=metrics_to_minio,
        op_args=["{{ds}}", minio, metrics_bucket],
        requirements=["minio"]
    )
    upload_to_minio >> download_from_minio >> model_train >> upload_pkl >> upload_metrics