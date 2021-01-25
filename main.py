from collections import namedtuple
from src.TauronEMeter import TauronEMeter
from src import TauronDataConverter
from time import sleep

import argparse
import configparser
import datetime
import json
import os
import requests


def get_date_range(date_start: datetime, periods: int = 1) -> list:
    """
    Generates list of dates for which data should be downloaded. If no parameters passed function returns only date

    @param date_start: beggining date for data download
    @param periods: amount of periods (backwards) to be generated

    @return: list of dates
    """
    date_start = date_start if date_start else datetime.datetime.now() - \
        datetime.timedelta(days=1)

    date_range = [(date_start - datetime.timedelta(days=x))
                  for x in range(periods)]
    return date_range


def extract_data(date: datetime):
    """
    Extracts energy raw data from Tauron web service

    @param date: data date to download
    @returns: tuple for (energy_consumption, energy_production)
    """

    # download daily meter data
    emeter.get_data(meter_id=meter_id, date=date.strftime('%d.%m.%Y'))
    emeter.to_flat_file(
        file_name_pattern.format(
            folder='raw',
            date=date.strftime('%Y_%m_%d'),
            timestamp=ts),
        raw=True,
        mode='w'
    )
    results = []

    for val, measure in [('chart', energy_consumption_measure_id),
                ('OZE', energy_production_measure_id)]:
        result = TauronDataConverter.EnergyData(
            data=emeter.parse(val),
            sensor_id=sensor_id,
            measure_id=measure)
        results.append(result)

    # save raw files
    emeter.to_flat_file(
        file_name_pattern.format(
            folder='interim',
            date=date.strftime('%Y_%m_%d'),
            timestamp=ts),
        mode='w'
    )
    return tuple(results)


def transform_data(
        energy_consumption: TauronDataConverter.EnergyData,
        energy_production:  TauronDataConverter.EnergyData):
    """
    Transforms extracted data into SmartHome Api format

    @returns: TauronDataConveter class object after conversion
    """
    converter = TauronDataConverter.TauronDataConverter(
        device_id=device_id,
        consumption=energy_consumption,
        production=energy_production
    )

    converter.convert()
    converter.to_flat_file(
        file_name=file_name_pattern.format(
            folder='processed',
            date=date.strftime("%Y_%m_%d"),
            timestamp=ts
        ),
        mode='w'
    )

    return converter


def load_data(data: str):
    url = 'http://192.168.0.115:8000/api/data_collector'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'data': data}
    r = requests.post(
        url,
        headers=headers,
        data=payload
    )

    print(r.status_code)


date_start = None
periods = None
timestamp = None
file_name_pattern = os.path.join(
    os.getcwd(),
    'data',
    '{folder}',
    '{folder}_tauron_emeter_{date}_{timestamp}.json'
)

parser = argparse.ArgumentParser(
    description='Downloads EMeter data from Tauron')

parser.add_argument('-date_start',
                    action='store',
                    type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'),
                    dest='date_start',
                    help='Start date of extraction (optional)- default yesterday')

parser.add_argument('-periods',
                    action='store',
                    type=int,
                    dest='periods',
                    default=1,
                    help='End date of extraction (optional)')

args = parser.parse_args()
date_start = args.date_start
periods = args.periods

# read config file
config = configparser.ConfigParser()
config.read('config.ini')

# TODO:
# Change and unify somehow
username = config['TAURON']['username']
password = config['TAURON']['password']
meter_id = config['TAURON']['meter_id']

device_id = config['API']['device_id']
sensor_id = config['API']['sensor_id']

energy_consumption_measure_id = config['API']['energy_consumption_measure_id']
energy_production_measure_id = config['API']['energy_production_measure_id']

# get date range to be processed
date_range = get_date_range(date_start, periods)

ts = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")

# create new TauronEMeter class instance
emeter = TauronEMeter(username, password)
emeter.login()  # login to the page

# loop through requested data range
for date in date_range:
    print(date.strftime("%Y_%m_%d"))

    raw_data = extract_data(date)

    print("Transforming data...")
    c = transform_data(raw_data[0], raw_data[1])

    print("Sending to collector API...")
    load_data(c.converted_data)

    print("Done")
    sleep(10)
