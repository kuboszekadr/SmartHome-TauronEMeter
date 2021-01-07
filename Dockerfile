FROM python:alpine3.7

COPY . /SmartHome-TauronEMeter
WORKDIR /SmartHome-TauronEMeter

RUN pip install -r requirements.txt