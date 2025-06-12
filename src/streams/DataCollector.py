from datetime import datetime as dt
from dataclasses import dataclass

import requests
from itertools import groupby

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
        # data_sorted = sorted(data, key=lambda x: x['type'])
        # data_by_type = groupby(data_sorted, key=lambda x: x['type'])

        # readings = []
        # for _, values in data_by_type:
        #     readings += list(values)

        if len(data) == 0:
            return

        payload = {
            'device_name': self.device_name,
            'readings': data
        }

        headers = {
            'User-Agent': self.device_name
        }

        r = requests.post(
            url=self.endpoint,
            headers=headers,
            json=payload,
            timeout=(60, 60)
        )
        assert r.status_code == 200, f'Expected 200, {r.status_code} received.'
