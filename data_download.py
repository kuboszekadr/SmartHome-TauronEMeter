import logging
import yaml
import os

from datetime import datetime as dt, timedelta
from time import sleep
from sys import stdout
from os import environ

from src.tauron.TauronEMeter import TauronEMeter, EMeterType
from src.streams.Disk import stream_to_disk


checkpoint_file = 'checkpoints/data_download.yaml'
checkpoint = {}
date_format = '%Y-%m-%d'
today = dt.today().date()

def update_checkpoint_file(config: dict) -> None:
    with open(checkpoint_file, 'w', encoding='UTF-8') as f:
        config['last_date'] = date.strftime(date_format)
        yaml.dump(config, f)

if not os.path.exists(checkpoint_file):
    checkpoint['last_date'] = (today - timedelta(days=1)).strftime(date_format)
else:
    with open(checkpoint_file, 'r') as f:
        checkpoint = yaml.load(f, yaml.FullLoader)

date = dt.strptime(checkpoint['last_date'], date_format)

logging.basicConfig(
    format="'%(asctime)s | %(name)s | %(message)s'",
    datefmt="%Y-%m-%d %H:%M:%S%z",
    filename=f'./logs/{today.strftime(date_format)}.log',
    level=logging.DEBUG
)
logging.getLogger().addHandler(logging.StreamHandler(stdout))

emeter = TauronEMeter(
    username=environ['username'], 
    password=environ['password']
    )
emeter.login()  

while date.date() < today:
    logging.info(f'Downloading data for {date.date()}')
    try:
        oze_data = emeter.download(date=date,type_=EMeterType.OZE)
        consum_data = emeter.download(date=date,type_=EMeterType.CONSUM)

        stream_to_disk(oze_data, './data/raw', date, EMeterType.OZE.value)
        stream_to_disk(consum_data, './data/raw', date, EMeterType.CONSUM.value)
    except Exception as e:
        logging.error(f"Unhandled erorr {e}: {repr(e)}")
        raise
    else:
        checkpoint['last_date'] = date.strftime(date_format)
        update_checkpoint_file(checkpoint)    

    date += timedelta(days=1)
    emeter.clear()
    sleep(5)
