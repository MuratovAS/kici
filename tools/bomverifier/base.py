from collections import OrderedDict

from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Базовый класс провайдера данных"""

    @property
    @abstractmethod
    def required_keys(self):
        """Ключи для обновления данных"""
        pass

    @abstractmethod
    def validate(self):
        """Валидация входных данных"""
        pass

    @abstractmethod
    def update_with_data(self):
        """Поулчение данных от провайдера"""
        pass

    def _update(self, data):
        """Обновление строки новыми данными"""
        item = OrderedDict(zip(self.required_keys, data))
        self.item.update(item)

    def fill_with_empty_values(self):
        """Заполнение стоки пустыми значениями"""
        data = ['' for _ in range(len(self.required_keys))]
        self._update(data)


