import requests
import datetime

from enum import Enum, auto
from collections import namedtuple
from typing import List

class EMeterType(Enum):
    OZE = 'oze'
    CONSUM = 'consum'

TauronResponse = namedtuple('TauronResponse', ['date', 'type', 'response'])

class TauronEMeter:
    """
    API allowing user to download smart meter data.
    """

    LOGIN_PAGE_URL = 'https://logowanie.tauron-dystrybucja.pl/login'
    URL = 'https://elicznik.tauron-dystrybucja.pl'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password
        self._session = None
        self._raw_responses: List[TauronResponse] = []

    @property
    def data(self):
        results = []
        for record in self._raw_responses:
            date = record.date.strftime('%Y%m%d')

            data = record.response.get('data')
            values = data.get('values')
            lbls = data.get('labels')

            ts = []
            for x in lbls:
                hour = datetime.time(hour=x-1).strftime('%H0000')
                lbl = f"{date} {hour}"
                ts.append(lbl)
            
            type_ = [record.type for _ in range(len(lbls))]
            records = zip(ts, type_, values)
            records = map(lambda x: {'timestamp': x[0], 'type': x[1], 'value': x[2]}, records)
            records = list(records)
            results += records

        return results

    # def parse(self, value: str) -> json:
    #     """
    #     Gets OZE or chart data from tauron response

    #     @param value: data to be extracted from Tauron chart data
    #     @returns: json data slice
    #     """
    #     if self._raw_response == '':
    #         return ValueError("Tauron data empty")

    #     if value in self._data:
    #         return self._data[value]

    #     results = list(self._raw_response['dane'][value].values())
    #     results = json.loads(json.dumps(results))

    #     return results


    def login(self) -> None:
        """
        Loggin into the Tauron eMeter service and opens new session allowing download of meter data
        """
        payload = {
            'username': self._username,
            'password': self._password,
            'service': TauronEMeter.URL
        }

        self._session = requests.Session()
        self._session.get(TauronEMeter.LOGIN_PAGE_URL)
        r = self._session.post(
            TauronEMeter.LOGIN_PAGE_URL,
            data=payload
            )


    def download(self, date: datetime, type_: EMeterType):
        """
        Downloads meter data at given date

        @param meter_id (int): tauron smart meter number
        @param date (date_time): data date
        """
        
        date_str = date.strftime('%d.%m.%Y')
        payload = {
            "from": date_str,
            "to": date_str,
            "type": type_.value,
            "profile": "full time"
        }

        r = self._session.post(
            TauronEMeter.URL + '/energia/api',
            data=payload,
            headers=TauronEMeter.HEADERS
        )

        response = TauronResponse(date, type_.value, r.json())
        self._raw_responses.append(response)


