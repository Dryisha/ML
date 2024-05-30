FROM python:3.11 as builder

WORKDIR /near_real_time

RUN mkdir -p /near_real_time/src

RUN pip3 install --upgrade pip setuptools wheel

COPY consumer.py consumer.py
COPY producer.py producer.py
COPY requirements.txt requirements.txt
COPY model.pkl model.pkl
COPY src/data_model.py src/data_model.py
COPY src/constants.py src/constants.py
COPY src/model.py src/model.py
COPY src/__init__.py src/__init__.py
COPY .env .env

RUN pip3 install -r requirements.txt

EXPOSE 8090/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]