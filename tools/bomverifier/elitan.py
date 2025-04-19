import re

from typing import OrderedDict

from bomverifier.api import ApiClient
from bomverifier.exceptions import MissingDataException
from bomverifier.base import BaseProvider


class Elitan(BaseProvider):
    params = {'stock': 1, 'tm': 15, 'cur': 'usd', 'id': '172'}
    url = 'https://efind.ru/ajax/efapi/search'

    def __init__(self, api_client: ApiClient, item: OrderedDict, qt: int, search_type='pn', **kwargs) -> None:
        self.qt = qt
        self.item = item
        self.api_client = api_client
        self.search_type = search_type

    @property
    def required_keys(self):
        return ['elitan_sku', 'elitan_mpn', 'elitan_consistent', 'elitan_enough']

    def validate(self):
        self.search_by = self._get_search_by(self.search_type)

    def update_with_data(self):
        self.params.update({'search': self.search_by})
        data = self.api_client.send_request(self.url, self.params)

        data = data['data']
        if data:
            row = data[0]['rows'][0]

            sku = re.findall('item(\d+)?', row['url'])[0]
            part = row.get('part')
            consistent = bool(self.item.get('elitan')== sku and (self.item.get('pn') == part))
            enough =  self._get_enough(row.get('stock'))

            data = [sku, part, consistent, enough]

            self._update(data)
        else:
            self.fill_with_empty_values()

        
    def _get_enough(self, enough):
        if enough == 'да':
            return True
        elif enough == 'нет':
            return False
        return enough

    def _get_search_by(self, search_type):
        search_by = None
        if search_type == 'pn':
            search_by = self.item.get('pn')
        if search_by:
            return search_by.strip()
        raise MissingDataException
       

