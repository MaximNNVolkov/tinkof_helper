
Message_default = 'Ошибка, проверьте входное значение'


class NoCoupons(Exception):
    """Купон по бумаге отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NoPrice(Exception):
    """Цена по бумаге отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NoCurrency(Exception):
    """Валюта отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NoBonds(Exception):
    """Облигация отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NoEvent(Exception):
    """События по облигации отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NoBondYields(Exception):
    """События по доходностям облигаций отсутствует в базе"""

    def __init__(self, message: str = Message_default, **kwargs):
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)
