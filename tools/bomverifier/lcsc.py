from typing import OrderedDict

from bomverifier.api import ApiClient
from bomverifier.exceptions import MissingDataException, ArgsException
from bomverifier.base import BaseProvider


class LCSC(BaseProvider):
    params = {}
    url = 'https://jlcsearch.tscircuit.com/components/list.json'


    def __init__(self, api_client: ApiClient, item: OrderedDict, qt: int, search_type='pn', **kwargs) -> None:
        self.api_client = api_client
        self.qt = qt
        self.item = item
        self.search_type = search_type

        self.rewrite_column = kwargs.get('rewrite_column')

    @property
    def required_keys(self):
        return ['lcsc_sku', 'lcsc_mpn', 'lcsc_stock', 'lcsc_price', 'lcsc_consistent', 'lcsc_enough']

    def validate(self):
        self.search_by = self._get_search_by(self.search_type)

    def update_with_data(self):
        self.params.update({'search': self.search_by})
        data = self.api_client.send_request(self.url, self.params)
        
        rows = data['components']
        if rows:
            row = rows[0]

            sku = 'C'+ str(row.get('lcsc'))
            mpn = row.get('mfr')
            stock = row.get('stock')
            price = self._get_price(row.get('price'))
            consistent = bool((self.item.get('lcsc')==sku) and (self.item.get('pn') == mpn))
            enough = bool(self.qt <= int(stock))

            data = [sku, mpn, stock, price, consistent, enough]
            self._update(data)

        else:
            self.fill_with_empty_values()

        if self.rewrite_column and rows:
            try:
                self.item[self.rewrite_column]
            except KeyError:
                raise ArgsException('No column to rewrite')
            self.item[self.rewrite_column] = row['mfr']
    
    def _get_price(self, price):
        if price == 'да':
            return True
        elif price == 'нет':
            return False
        return price

    def _get_search_by(self, search_type):
        search_by = None
        if search_type == 'pn':
            search_by = self.item.get('pn').strip()
        elif search_type == 'sku':
            search_by = self.item.get('lcsc').strip()[1:]
        if search_by:
            return search_by
        raise MissingDataException

