import json

from copy import deepcopy
from datetime import datetime
from collections import namedtuple

EnergyData = namedtuple("EnergyData", "data sensor_id measure_id")


class TauronDataConverter():
    """
    Class providing easy conversion between Tauron data format and SmartHome app
    """

    def __init__(self, device_id: int, consumption: namedtuple, production: namedtuple):
        self._consumption_raw = deepcopy(consumption)
        self._consumption = None

        self._production_raw = deepcopy(production)
        self._production = None

        self._device_id = device_id
        self._converted_data = ""

    @property
    def converted_data(self) -> str:
        """
        Returns taruon data converted to SmartHome api format
        """
        return self._converted_data

    def convert(self) -> None:
        """
        Converts tauron meter data into SmartHome API friendly format:
        {"device_id": 1, "data": {"s":1,"r":["m":1:,"v":22.22],"t":20200513 063312}}
        where:
            s - sensor_id (int),
            r - reading (dict):
                m - measure_id (int),
                v - value (float),
            t - timestamp

        @param device_id: device_id in smart home app
        @param sensor_id: sensor_id in smart home app
        @param measures_id: measures_id in smart home app

        """
        results = []
        for raw_data in [self._production_raw, self._consumption_raw]:
            for hour in raw_data.data:
                datetime = "{} {:02d}0000".format(
                    hour["Date"], int(hour["Hour"]))
                value = hour['EC']

                r = {}
                r["s"] = raw_data.sensor_id
                r["r"] = {"m": raw_data.measure_id, "v": value}
                r["t"] = datetime

                results.append(r)

        results = {"device_id": self._device_id, "data": results}
        self._converted_data = json.dumps(results)

    def to_flat_file(self, file_name: str, **kwargs) -> bool:
        """
        Saves SmartHome api converted data into file

        @param file_name: target file where data should be saved
        @param **kwargs: paramethers to be send to file writer

        @returns: True if saved successfully
        """
        if len(self.converted_data) == 0:
            raise ValueError
        
        try:
            with open(file_name, **kwargs) as f:
                f.writelines(self.converted_data)
        except FileNotFoundError:
            raise FileNotFoundError("Can not open " + file_name)
        return True
