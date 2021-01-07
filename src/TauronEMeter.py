import requests
import datetime
import json


class TauronEMeter:
    """
    API allowing user to download smart meter data.
    """

    LOGIN_PAGE_URL = 'https://logowanie.tauron-dystrybucja.pl/login'
    URL = 'https://elicznik.tauron-dystrybucja.pl'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__session = None
        self.__raw_response = ''
        self.__data = {}


    def parse(self, value: str) -> json:
        """
        Gets OZE or chart data from tauron response

        @param value: data to be extracted from Tauron chart data
        @returns: json data slice
        """
        if self.__raw_response == '':
            return ValueError("Tauron data empty")

        if value in self.__data:
            return self.__data[value]

        results = list(self.__raw_response['dane'][value].values())
        results = json.loads(json.dumps(results))

        return results


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


    def get_data(self, meter_id: int, date: datetime):
        """
        Downloads meter data at given date

        @param meter_id (int): tauron smart meter number
        @param date (date_time): data date
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
        self.__raw_response = json.loads(r.text)


    def to_flat_file(self, file_name: str, raw: bool = False, **kwargs):
        """
        Saves raw meter data

        @param file_name: target file where data should be saved
        @param **kwargs: paramethers to be send to file writer
        """       
        try:
            data = self.__raw_response if raw else self.__data
            data = json.dumps(data)

            with open(file_name, **kwargs) as f:
                f.writelines(data)

        except FileNotFoundError:
            raise FileNotFoundError("Can not open " + file_name)
        return True
