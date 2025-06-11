import logging

from datetime import datetime as dt, timedelta
from sys import stdout

from src.Config import app_config

today = dt.today()

logging.basicConfig(
    format="'%(asctime)s | %(name)s | %(message)s'",
    datefmt="%Y-%m-%d %H:%M:%S%z",
    filename=f'{app_config.logs_folder}/{today.strftime(app_config.date_format)}.log',
    level=logging.DEBUG
)
logging.getLogger().addHandler(logging.StreamHandler(stdout))