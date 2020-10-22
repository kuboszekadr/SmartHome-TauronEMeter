from src.TauronEMeter import TauronEMeter

import configparser
import datetime
import json


def parse_tauron_meter_data(data: json) -> dict:
    result = dict()

    for hour in data:
        date_time = "{} {:02d}0000".format(hour['Date'], int(hour['Hour']))
        value = hour['EC']
        result[date_time] = value

    return result


# read config file
config = configparser.ConfigParser()
config.read('config.ini')

username = config['TAURON']['username']
password = config['TAURON']['password']
meter_id = config['TAURON']['meter_id']

# TODO:
# change to argparse to be able to download multiple date at the same time
date = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%d.%m.%Y')

# create new TauronEMeter class instance
emeter = TauronEMeter(username, password)

# TODO:
# check for login status
emeter.login()  # login to the page

meter_data = emeter.get_data(meter_id, date)

# parse energy consumption data
energy_consumption = parse_tauron_meter_data(meter_data['dane']['chart'])

# parse energy generation data
# requires additional steps due to having extra level in json
energy_production_json = list(meter_data['dane']['OZE'].values())
energy_production_json = json.loads(json.dumps(energy_production_json))
energy_production = parse_tauron_meter_data(energy_production_json)

print(energy_consumption)
print(energy_production)

# TODO:
# send to SmartHome API
