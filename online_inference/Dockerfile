FROM python:3.11

WORKDIR /online_inference

RUN mkdir -p /online_inference/data
RUN mkdir -p /online_inference/src

RUN pip3 install --upgrade pip setuptools wheel

COPY data/transfusion.csv data/transfusion.csv 
COPY src/data_model.py src/data_model.py
COPY src/constants.py src/constants.py
COPY src/model.py src/model.py
COPY model_training.py model_training.py 
COPY app.py app.py
COPY requirements-dev.txt requirements-dev.txt
COPY requirements.txt requirements.txt
COPY model.pkl model.pkl

RUN pip3 install -r requirements-dev.txt

EXPOSE 8090/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]