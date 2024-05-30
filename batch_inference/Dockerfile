FROM python:3.11 as builder

WORKDIR /batch_inference

RUN mkdir -p /batch_inference/dags
RUN mkdir -p /batch_inference/dags/src

RUN pip3 install --upgrade pip setuptools wheel

COPY download_data.py download_data.py
COPY upload_data.py upload_data.py
COPY requirements.txt requirements.txt
COPY dags/bash_operator.py dags/bash_operator.py
COPY dags/branch_operator.py dags/btanch_operator.py
COPY dags/create_data.py dags/create_data.py
COPY dags/custom_notify.py dags/custom_notify.py
COPY dags/dummy_operator.py dags/dummy_operator.py
COPY dags/python_operator.py dags/python_operator.py
COPY dags/s3_dag.py dags/s3_dag.py
COPY dags/template_dag.py dags/template_dag.py
COPY dags/src/data_model.py dags/src/data_model.py
COPY dags/src/__init__.py dags/src/__init__.py

RUN pip3 install -r requirements.txt

EXPOSE 8090/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]