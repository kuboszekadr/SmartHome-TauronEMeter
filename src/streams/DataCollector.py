from datetime import datetime as dt
from dataclasses import dataclass

import requests


@dataclass
class DataCollector:
    device_name: str
    url: str
    port: int

    @property
    def endpoint(self) -> str:
        result = f"http://{self.url}:{self.port}/api/data_collector"
        return result

    def stream(self, data):
        station_data_items = data['stationDataItems']
        readings = [0]*len(station_data_items)

        if len(readings) == 0:
            return

        for idx, station_data_item in enumerate(station_data_items):
            value = station_data_item['generationPower']
            value = 0.0 if value is None else value

            timestamp = station_data_item['dateTime']
            timestamp = dt.fromtimestamp(timestamp)

            reading = {
                'measure_name': "power",
                'value': value,
                'timestamp': timestamp.strftime('%Y%m%d %H%M%S')
            }
            readings[idx] = reading

        payload = {
            'device_name': self.device_name,
            'readings': readings
        }
        headers = {
            'User-Agent': 'Tauron-EMeter'
        }

        r = requests.post(
            url=self.endpoint,
            headers=headers,
            json=payload,
            timeout=(60, 60)
        )
        assert r.status_code == 200, f'Expected 200, {r.status_code} received.'
