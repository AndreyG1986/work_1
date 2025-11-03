# Главная и События
# views.py
# Курс валют.
# Стоимость акций из S&P500
from typing import Any
import os
from dotenv import load_dotenv
from src.utils import list_of_currencies, stocks
import requests
import json


load_dotenv()
API_KEY = os.getenv("API_KEY_APILAYER")
currency_to = "RUB"
PATH_TO_FILE_OPERATIONS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_settings.json")

def receive_currencies(currencies: list) -> dict:
    """преобразуем список к красивому формату, как в ТЗ
       {'currency_rates': [{'currency': 'USD', 'rate': 0.0}, {'currency': 'EUR', 'rate': 0.0}]}"""
    dict_of_currencies = {
        "currency_rates": [
            {"currency": currency, "rate": 0.0}
            for currency in currencies
        ]
    }
    return dict_of_currencies

currencies_result = receive_currencies(list_of_currencies)

def convert_to_rubles(currencies: list) -> list[float]:
    """Функция с помощью которой получаем список курсов в рублях"""
    list_of_rates = []
    for currency_from in currencies:
        amount = 1.0
        url = f"https://api.apilayer.com/exchangerates_data/convert?to={currency_to}&from={currency_from}&amount={amount}"
        payload = {}
        headers = {"apikey": f"{API_KEY}"}

        if currency_from == "RUB":
            list_of_rates.append(amount)
            return list_of_rates
        # elif currency_from == {}:
        #     return amount
        else:
            response = requests.request("GET", url, headers=headers, data=payload)
            status_code = response.status_code
            result = response.text

            if status_code == 200:

                python_response = json.loads(result)
                amount = float(python_response.get("result", 0))
                list_of_rates.append(amount)
    return list_of_rates

list_of_currency_rates = convert_to_rubles(list_of_currencies)

# Теперь вот тут нужно написать функции, которые будут заменять "rates"
# в нашем списке словариков currencies_result
def update_currencies(currencies_res: list[dict], cur_rates: list[float], cur_list: list[str]) -> list[dict]:
    """Заменяем значения по ключу "rate" в нашем словарике"""
    currencies_res = {
        "currency_rates": [
            {"currency": cur_list[i], "rate": cur_rates[i]}
            for i in range(len(cur_list))
        ]
    }
    return currencies_res



# def main(date: str) -> JSONType:
def main(date: str)-> Any:
    """Функция для страницы «Главная» принимает на вход строку с датой
    и временем в формате YYYY-MM-DD HH:MM:SS.
    Функция для страницы «Главная» отдает корректный JSON-ответ согласно ТЗ"""
    pass

# stocks_result = get_us_stocks_alpha_vantage(list_of_stocks, TCS_TOKEN)
cur_dict = update_currencies(currencies_result, list_of_currency_rates, list_of_currencies)
sum_of_dicts = cur_dict,stocks

if __name__ == "__main__":
    print(sum_of_dicts)
    # print(update_currencies(currencies_result, list_of_currency_rates, list_of_currencies))
    # print(list_of_currencies)
    # print(list_of_stocks)
    # print(convert_to_rubles(list_of_currencies))


