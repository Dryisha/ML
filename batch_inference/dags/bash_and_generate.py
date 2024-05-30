
from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago

minio = Variable.get("minio")
cardio_bucket = Variable.get("cardio_bucket")

def generate_cardio(input_dir):
    import random
    import pandas as pd
    from src.data_model import HealthData
    from pathlib import Path

    dir_path = Path(input_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    data = []

    for _ in range(1000):
        possible_age = random.randint(17000, 22000) 
        possible_gender = random.randint(1, 2)
        possible_height = random.randint(150, 210)
        possible_weight = random.uniform(60, 120)
        possible_ap_hi = random.randint(100, 230)
        possible_ap_lo = random.randint(50, 110)
        possible_cholesterol = random.choice([1, 2, 3])
        possible_gluc = random.choice([1, 2, 3])
        possible_smoke = random.choice([1, 2])
        possible_alco = random.choice([1, 2])
        possible_active = random.choice([1, 2])
        pred_row = HealthData(age=possible_age, 
                                        gender=possible_gender, 
                                        height=possible_height,
                                        weight=possible_weight,
                                        ap_hi=possible_ap_hi,
                                        ap_lo=possible_ap_lo,
                                        cholesterol=possible_cholesterol,
                                        gluc=possible_gluc,
                                        smoke=possible_smoke,
                                        alco=possible_alco,
                                        active=possible_active)
    data.append(pred_row.dict())

    df = pd.DataFrame(data)
    df.to_csv(dir_path / "cardio_data.csv")

default_args = {
    "owner": "Cheboksarov",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "make_directory_and_cardio_generation",
    default_args=default_args,
    schedule_interval="0 0 * * 5",
    start_date=days_ago(1),
):
    make_dir = BashOperator(
        task_id="make_dir",
        bash_command="mkdir -p ../{{ds}}"
    )

    cardio_data_generation = PythonVirtualenvOperator(
        python_callable=generate_cardio,
        op_args=["{{ds}}"],
        task_id="generate_cardio",
        requirements=["pandas", "pydantic"]
    )

    make_dir >> cardio_data_generation
