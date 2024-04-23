import aiogram.utils.markdown as fmt
from utils.bonds.bond import Bond
from tinkoff.invest.schemas import RiskLevel


class CardBond:

    def __init__(self, bond: Bond):
        self.price = bond.last_price
        self.aci_value = bond.aci_value
        self.name = bond.name
        self.ticker = bond.ticker
        self.url = f'https://www.tinkoff.ru/invest/bonds/{bond.ticker}'
        self.val = bond.val
        self.profit = bond.profit
        self.annual_yield = bond.annual_yield
        self.risk_level = bond.risk_level
        self.maturity_date = bond.maturity_date
        self.nominal = bond.nominal
        self.oferta = bond.oferta

    def get_text(self) -> fmt.text:
        if self.oferta:
            date_ = fmt.text(f'Дата оферты: {self.oferta.date()}')
        else:
            date_ = fmt.text(f'Дата погашения: {self.maturity_date.date()}')
        return fmt.text(
            fmt.hlink(self.name, self.url),
            fmt.text(fmt.text('Рейтинг:'), fmt.text('\U00002B50'*self.get_risk(), sep=' ')),
            fmt.text(''),
            fmt.text(f'Номинал: {self.nominal:.2f}'),
            fmt.text(f'Цена: {self.price:.2f}'),
            fmt.text(f'НКД: {self.aci_value:.2f}'),
            date_,
            fmt.text(''),
            fmt.text(f'Доход: {self.val:.2f}'),
            fmt.text(f'Доходность: {self.profit*100:.1f}%'),
            fmt.text(f'Доходность годовых: {self.annual_yield*100:.1f}%'),
            sep='\n'
        )

    def get_risk(self):
        levels = [RiskLevel.RISK_LEVEL_HIGH, RiskLevel.RISK_LEVEL_MODERATE, RiskLevel.RISK_LEVEL_LOW]
        return levels.index(self.risk_level) + 1
