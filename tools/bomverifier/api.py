import json
import urllib
import time
from urllib.error import URLError
import requests
from os import getenv
import time;

from bomverifier.exceptions import ApiException

class ApiClient():

    def __init__(self):
        self.headers = {"User-Agent": getenv('USERAGENT',"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0")}
        self.proxy_url = getenv('SOCKS5_URL')
        self.proxy_username = getenv('SOCKS5_USERNAME')
        self.proxy_password = getenv('SOCKS5_PASSWORD')

        # print(f'INFO: {self.headers}')
        if self.proxy_url:
            proxy = f"socks5://{self.proxy_username}:{self.proxy_password}@{self.proxy_url}"
            self.proxies = {'http': proxy, 'https': proxy}
            # print(f'INFO: Using SOCKS5')
        else:
            self.proxies = None

    def send_request(self, url, params):
        for _ in range(3):
            try:
                response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
                response.raise_for_status()
                return json.loads(response.text)
            except requests.RequestException as e:
                print(f'\033[31mERROR\033[0m: API {e}')
                time.sleep(3)
        else:
            raise ApiException