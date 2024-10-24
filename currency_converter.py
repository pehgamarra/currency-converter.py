import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Callable
import threading
import time

class InvalidCurrencyError(Exception):
    pass

class InvalidAmountError(Exception):
    pass

# Abstract base class for exchange rate providers
class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        pass

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def update_rates(self, interval: int):
        pass

    @abstractmethod
    def start_auto_update(self, interval: int):
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass

# Concrete implementation of online rate provider
class OnlineRateProvider(ExchangeRateProvider):
    def __init__(self, supported_currencies: List[str]):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.supported_currencies = supported_currencies
        self.observers: List[Callable] = []
        self.rates = self.fetch_rates()

    def fetch_rates(self) -> Dict[str, float]:
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            data = response.json()
            rates = {currency: data['rates'][currency] for currency in self.supported_currencies}
            self.notify_observers()
            return rates
        except requests.RequestException as e:
            print(f"Error fetching exchange rates: {e}")
            return {}

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency not in self.rates or to_currency not in self.rates:
            raise InvalidCurrencyError(f"Invalid currency: {from_currency} or {to_currency}")
        
        usd_to_from = self.rates[from_currency]
        usd_to_to = self.rates[to_currency]
        
        return usd_to_to / usd_to_from

    def add_observer(self, observer: Callable):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer()

    def update_rates(self, interval: int = 3600):
        while True:
            time.sleep(interval)
            self.rates = self.fetch_rates()

    def start_auto_update(self, interval: int = 3600):
        thread = threading.Thread(target=self.update_rates, args=(interval,))
        thread.daemon = True
        thread.start()

    def get_provider_name(self) -> str:
        return "Online Provider"

# Singleton decorator
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class ExchangeRateManager:
    def __init__(self):
        self.provider = None

    def set_provider(self, provider: ExchangeRateProvider):
        self.provider = provider

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        if not self.provider:
            raise ValueError("No exchange rate provider set")
        try:
            return self.provider.get_rate(from_currency, to_currency)
        except ValueError:
            raise InvalidCurrencyError(f"Invalid currency: {from_currency} or {to_currency}")

    # OCP:
    def get_provider_name(self) -> str:
        if not self.provider:
            raise ValueError("No exchange rate provider set")
        return self.provider.get_provider_name()

class CurrencyConverter:
    def __init__(self, exchange_rate_manager: ExchangeRateManager):
        self.exchange_rate_manager = exchange_rate_manager

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero")
        rate = self.exchange_rate_manager.get_rate(from_currency, to_currency)
        return amount * rate

    # OCP
    def get_provider_name(self) -> str:
        return self.exchange_rate_manager.get_provider_name()

# Factory for creating providers
class ExchangeRateProviderFactory:
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> ExchangeRateProvider:
        if provider_type == "online":
            return OnlineRateProvider(kwargs.get('supported_currencies', []))
        elif provider_type == "fixed":
            return FixedRateProvider(kwargs.get('fixed_rates', {}))
        raise ValueError(f"Unknown provider type: {provider_type}")

if __name__ == "__main__":
    supported_currencies = ["USD", "BRL", "EUR", "GBP", "CNY"]
    provider = ExchangeRateProviderFactory.create_provider("online", supported_currencies=supported_currencies)
    manager = ExchangeRateManager()
    manager.set_provider(provider)
    converter = CurrencyConverter(manager)
