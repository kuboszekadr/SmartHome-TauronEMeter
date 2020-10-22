import requests
import datetime
import json


class TauronEMeter:
    """
    API allowing user to download his/her smart meter data.
    """

    LOGIN_PAGE_URL = 'https://logowanie.tauron-dystrybucja.pl/login'
    URL = 'https://elicznik.tauron-dystrybucja.pl'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__session = None
        self.__chart_json = ''

    def login(self) -> None:
        """
        Loggin into the Tauron eMeter service and opens new session allowing download of meter data
        """
        payload = {
            'username': self.__username,
            'password': self.__password,
            'service': TauronEMeter.URL
        }

        self.__session = requests.Session()
        self.__session.get(TauronEMeter.LOGIN_PAGE_URL)
        r = self.__session.post(TauronEMeter.LOGIN_PAGE_URL,
                                data=payload,
                                headers=TauronEMeter.HEADERS)

        # TODO:
        # Check if login succeded

    def get_data(self, meter_id: int, date: datetime) -> json:
        """
        Downloads meter data at given date

        @param meter_id (int): tauron smart meter number
        @param date (date_time): data date
        @return: json 
        """
        
        payload = {
            "dane[chartDay]": date,
            "dane[paramType]": "day",
            "dane[smartNr]": meter_id,
            "dane[checkOZE]": "on"
        }

        r = self.__session.post(
            TauronEMeter.URL + '/index/charts',
            data=payload,
            headers=TauronEMeter.HEADERS)

        return json.loads(r.text)

