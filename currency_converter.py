import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Callable
import threading
import time

class InvalidCurrencyError(Exception):
    pass

class InvalidAmountError(Exception):
    pass

#Abstract
class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        pass

#Observer Pattern for update rates
class OnlineRateProvider(ExchangeRateProvider):
    def __init__(self, supported_currencies: List[str]):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.supported_currencies = supported_currencies
        self.observers: List[Callable] = []  #Initialize observers list
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
        """Update rates periodically"""
        while True:
            time.sleep(interval)
            self.rates = self.fetch_rates()

    def start_auto_update(self, interval: int = 3600):
        """Start auto-updating rates in a separate thread"""
        thread = threading.Thread(target=self.update_rates, args=(interval,))
        thread.daemon = True
        thread.start()

#singleton for improve only on instance of ExchangeRateManager
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

class CurrencyConverter:
    def __init__(self, exchange_rate_manager: ExchangeRateManager):
        self.exchange_rate_manager = exchange_rate_manager

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero")
        rate = self.exchange_rate_manager.get_rate(from_currency, to_currency)
        return amount * rate

#Design Pattern Factory for create provider
class ExchangeRateProviderFactory:
    @staticmethod
    def create_provider(provider_type: str, supported_currencies: List[str]) -> ExchangeRateProvider:
        if provider_type == "online":
            return OnlineRateProvider(supported_currencies)
        # Add more provider types here if needed
        raise ValueError(f"Unknown provider type: {provider_type}")

if __name__ == "__main__":
    supported_currencies = ["USD", "BRL", "EUR", "GBP", "CNY"]
    provider = ExchangeRateProviderFactory.create_provider("online", supported_currencies)
    manager = ExchangeRateManager()
    manager.set_provider(provider)
    converter = CurrencyConverter(manager)
    # Example usage
    result = converter.convert(100, "USD", "EUR")
    print(f"100 USD = {result:.2f} EUR")
