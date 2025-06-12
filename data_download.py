from datetime import datetime as dt, timedelta
from time import sleep

from src.Checkpoint import Checkpoint
from src.Config import tauron_config, app_config
from src.tauron.TauronEMeter import TauronEMeter, EMeterType
from src.streams.Disk import stream_to_disk
from src.Logging import logging

def download_day_data(emeter: TauronEMeter, date: dt.date) -> None:
    """Download data for a specific date."""
    logging.info(f'Downloading data for {date}')

    oze_data = emeter.download(date=date, type_=EMeterType.OZE)
    consum_data = emeter.download(date=date, type_=EMeterType.CONSUM)

    stream_to_disk(data=oze_data, 
                   root=app_config.raw_data_folder_path, 
                   data_date=date, 
                   type=EMeterType.OZE.value
                   )
    
    stream_to_disk(data=consum_data, 
                   root=app_config.raw_data_folder_path, 
                   data_date=date, 
                   type=EMeterType.CONSUM.value
                   )

checkpoint = Checkpoint(name='data_download')
date_format = app_config.date_format
today = dt.today()

emeter = TauronEMeter(
    username=tauron_config.username, 
    password=tauron_config.password,
    )
emeter.login()  

while checkpoint.last_date < today:

    date = checkpoint.last_date
    logging.info(f'Downloading data for {date}')
    
    try:
        download_day_data(emeter=emeter, date=date)        
    except Exception as e:
        logging.error(f"Unhandled erorr {e}: {repr(e)}")
        raise
    else:
        checkpoint.dump()    

    checkpoint.last_date += timedelta(days=1)
    emeter.clear()
    sleep(10)
