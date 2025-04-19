from typing import OrderedDict

from bomverifier.api import ApiClient
from bomverifier.exceptions import MissingDataException
from bomverifier.base import BaseProvider


class Promelec(BaseProvider):
    params = {'stock': 1, 'tm': 15, 'cur': 'usd', 'id': '65,1794'}
    url = 'https://efind.ru/ajax/efapi/search'

    def __init__(self, api_client: ApiClient, item: OrderedDict, qt:int, search_type='pn', **kwargs) -> None:
        self.qt = qt
        self.item = item
        self.search_type = search_type
        self.api_client = api_client

    @property
    def required_keys(self):
        return ['promelec_sku', 'promelec_mpn', 'promelec_stock','promelec_price', 'promelec_consistent', 'promelec_enough']

    def validate(self):
        self.search_by = self._get_search_by(self.search_type)

    def update_with_data(self):

        self.params.update({'search': self.search_by})
        data = self.api_client.send_request(self.url, self.params)

        data = data['data']
        if data:
            row = data[0]['rows'][0]

            sku = row.get('sku')
            part = row.get('part')
            stock = row.get('stock')
            if row.get('price'):
                price = self._get_price(row['price'])
            else:
                price = None
            consistent = bool((self.item.get('promelec') == sku) and (self.item.get('pn') == part))
            enough = bool(self.qt <= int(stock))

            data = [sku, part, stock, price, consistent, enough]
            self._update(data)
        else:
            self.fill_with_empty_values()

    def _get_price(self, prices):
        for price in prices:
            if price [0] >= self.qt:
                return float(price[1])

    def _get_search_by(self, search_type):
        search_by = None
        if search_type == 'pn':
            search_by = self.item.get('pn')

        if search_by:
            return search_by.strip()
        raise MissingDataException
