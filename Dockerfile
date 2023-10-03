FROM python:alpine3.10

COPY . /SmartHome-TauronEMeter
WORKDIR /SmartHome-TauronEMeter

RUN pip install -r requirements.txt