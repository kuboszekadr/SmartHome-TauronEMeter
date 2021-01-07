from collections import namedtuple
from src.TauronEMeter import TauronEMeter
from src import TauronDataConverter
from time import sleep

import argparse
import configparser
import datetime
import json
import os


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

    for val in ['chart', 'OZE']:
        result = TauronDataConverter.EnergyData(
            data=emeter.parse('chart'),
            sensor_id=sensor_id,
            measure_id=energy_consumption_measure_id
        )
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
        device_id=5,
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


def load_argparser():
    parser = argparse.ArgumentParser(
        description='Downloads EMeter data from Tauron')

    parser.add_argument('-date_start',
                        action='store',
                        type=lambda x: datetime.datetime.strptime(
                            x, '%Y-%m-%d'),
                        dest='date_start',
                        help='Start date of extraction (optional)- default yesterday')

    parser.add_argument('-periods',
                        action='store',
                        type=int,
                        dest='periods',
                        default=1,
                        help='End date of extraction (optional)')


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

# get date range to be processed
date_range = get_date_range(date_start, periods)

# read config file
config = configparser.ConfigParser()
config.read('config.ini')

username = config['TAURON']['username']
password = config['TAURON']['password']
meter_id = config['TAURON']['meter_id']

device_id = config['API']['device_id']
sensor_id = config['API']['sensor_id']

energy_consumption_measure_id = config['API']['energy_consumption_measure_id']
energy_production_measure_id = config['API']['energy_production_measure_id']

# create new TauronEMeter class instance
emeter = TauronEMeter(username, password)
emeter.login()  # login to the page

# loop through requested data range
for date in date_range:
    print(date.strftime("%Y_%m_%d"))
    ts = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")

    raw_data = extract_data(date)

    print("Transforming data...")
    transform_data(raw_data[0], raw_data[1])

    # load_data()
    print("Done")
    sleep(10)
