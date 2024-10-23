import tkinter as tk
from tkinter import ttk, messagebox
from currency_converter import CurrencyConverter, InvalidCurrencyError, InvalidAmountError, ExchangeRateManager, ExchangeRateProviderFactory

class GUICurrencyConverter(tk.Tk):
    def __init__(self, converter: CurrencyConverter):
        super().__init__()

        self.converter = converter
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        self.current_language = "en"
        self.translations = {
            "en": {
                "title": "Currency Converter",
                "amount": "Amount:",
                "from": "From:",
                "to": "To:",
                "convert": "Convert",
                "switch_language": "Mudar para Português",
                "error": "Error",
                "invalid_number": "Please enter a valid number for the amount.",
                "invalid_amount": "Amount must be greater than zero",
                "invalid_currency": "Invalid currency",
                "USD": "US Dollar",
                "BRL": "Brazilian Real",
                "EUR": "Euro",
                "GBP": "British Pound",
                "CNY": "Chinese Yuan"
            },
            "pt": {
                "title": "Conversor de Moedas",
                "amount": "Valor:",
                "from": "De:",
                "to": "Para:",
                "convert": "Converter",
                "switch_language": "Switch to English",
                "error": "Erro",
                "invalid_number": "Por favor, insira um número válido para o valor.",
                "invalid_amount": "O valor deve ser maior que zero",
                "invalid_currency": "Moeda inválida",
                "USD": "Dólar Americano",
                "BRL": "Real Brasileiro",
                "EUR": "Euro",
                "GBP": "Libra Esterlina",
                "CNY": "Yuan Chinês"
            }
        }

        self.supported_currencies = ["USD", "BRL", "EUR", "GBP", "CNY"]
        self.currency_symbols = {"USD": "$", "BRL": "R$", "EUR": "€", "GBP": "£", "CNY": "¥"}
        self.create_widgets()
        self.update_language() 

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))

        # Title
        self.title_label = ttk.Label(self, text="", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=(20, 10))

        # Language switch button
        self.language_button = ttk.Button(self, text="", command=self.switch_language)
        self.language_button.pack(pady=(0, 20))

        # Currency selection frame
        currency_frame = ttk.Frame(self)
        currency_frame.pack(pady=10, padx=20, fill="x")

        # From currency dropdown
        self.from_label = ttk.Label(currency_frame, text="")
        self.from_label.pack(side="left")
        self.from_currency = ttk.Combobox(currency_frame, values=self.get_currency_options(), width=15)
        self.from_currency.pack(side="left", padx=(10, 20))
        self.from_currency.set("USD - US Dollar")

        # To currency dropdown
        self.to_label = ttk.Label(currency_frame, text="")
        self.to_label.pack(side="left")
        self.to_currency = ttk.Combobox(currency_frame, values=self.get_currency_options(), width=15)
        self.to_currency.pack(side="left", padx=(10, 0))
        self.to_currency.set("EUR - Euro")

        # Amount input and Convert button
        amount_frame = ttk.Frame(self)
        amount_frame.pack(pady=10, padx=20, fill="x")
        self.amount_label = ttk.Label(amount_frame, text="")
        self.amount_label.pack(side="left")

        self.amount_var = tk.StringVar()
        self.amount_var.trace("w", self.limit_amount_chars)

        self.amount_entry = ttk.Entry(amount_frame, width=15, textvariable=self.amount_var)
        self.amount_entry.pack(side="left", padx=(10, 5))
        ttk.Label(amount_frame, text="$").pack(side="left")
        
        self.convert_button = ttk.Button(amount_frame, text="", command=self.convert)
        self.convert_button.pack(side="right")

        # Result label
        self.result_label = ttk.Label(self, text="", font=("Arial", 14, "bold"), wraplength=380)
        self.result_label.pack(pady=10)

    def limit_amount_chars(self, *args):
        value = self.amount_var.get()
        if len(value) > 25:
            self.amount_var.set(value[:25])

    def get_currency_options(self):
        return [f"{code} - {self.translate(code)}" for code in self.supported_currencies]

    def translate(self, key):
        return self.translations[self.current_language][key]

    def switch_language(self):
        self.current_language = "pt" if self.current_language == "en" else "en"
        self.update_language()

    def update_language(self):
        self.title(self.translate("title")) 
        self.title_label.config(text=self.translate("title"))
        self.from_label.config(text=self.translate("from"))
        self.to_label.config(text=self.translate("to"))
        self.amount_label.config(text=self.translate("amount"))
        self.convert_button.config(text=self.translate("convert"))
        self.language_button.config(text=self.translate("switch_language"))
        self.from_currency.config(values=self.get_currency_options())
        self.to_currency.config(values=self.get_currency_options())

    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            from_curr = self.from_currency.get().split(" - ")[0]
            to_curr = self.to_currency.get().split(" - ")[0]

            result = self.converter.convert(amount, from_curr, to_curr)
            self.result_label.config(text=f"{self.currency_symbols[from_curr]}{amount:.2f} = {self.currency_symbols[to_curr]}{result:.2f}")
        except ValueError:
            messagebox.showerror(self.translate("error"), self.translate("invalid_number"))
        except InvalidAmountError:
            messagebox.showerror(self.translate("error"), self.translate("invalid_amount"))
        except InvalidCurrencyError:
            messagebox.showerror(self.translate("error"), self.translate("invalid_currency"))

if __name__ == "__main__":
    supported_currencies = ["USD", "BRL", "EUR", "GBP", "CNY"]
    provider = ExchangeRateProviderFactory.create_provider("online", supported_currencies)
    manager = ExchangeRateManager()
    manager.set_provider(provider)
    converter = CurrencyConverter(manager)
    
    app = GUICurrencyConverter(converter)
    app.mainloop()
