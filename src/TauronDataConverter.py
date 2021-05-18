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
        Returns Tauron data converted to SmartHome api format
        """
        return self._converted_data

    def convert(self) -> None:
        """
        Converts tauron meter data into SmartHome API friendly format.
        """
        results = []
        raw_data = zip(self._production_raw.data, self._consumption_raw.data)

        # loop through hours
        for data in raw_data:
            production_data = data[0]
            consumption_data = data[1]

            # it is indifferent which variable we will use...
            date = production_data['Date']
            hour = int(production_data['Hour'])

            # construct hour data
            r = {}
            r['sensor_id'] = self._production_raw.sensor_id
            r['readings'] = [
                {'measure_id': self._production_raw.measure_id,
                    'value': production_data['EC']},
                {'measure_id': self._consumption_raw.measure_id,
                    'value': consumption_data['EC']}
            ]
            r['timestamp'] = '{} {:02d}0000'.format(date, hour)

            results.append(r)  # add to the final result set

        results = {'device_id': self._device_id, 'data': results}
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
