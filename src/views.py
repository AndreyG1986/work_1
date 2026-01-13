from typing import Any
import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import json
from datetime import datetime

from src.utils import read_user_settings, get_user_lists, get_us_stocks_alpha_vantage, filter_by_date, greeting_func, read_excel_file

load_dotenv()
API_KEY = os.getenv("API_KEY_APILAYER")
TCS_TOKEN = os.getenv("API_TOKEN_TINKOFF")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SETTINGS_PATH = DATA_DIR / "user_settings.json"
excel_path = DATA_DIR / "operations.xlsx"
# Читаем операции
operations = read_excel_file(excel_path)


def receive_currencies(currencies: list[str]) -> dict:
    """
    Преобразуем список валют в формат:
    {"currency_rates": [{"currency": "USD", "rate": 0.0}, ...]}
    """
    return {
        "currency_rates": [
            {"currency": c, "rate": 0.0} for c in currencies
        ]
    }


def convert_to_rubles(currencies: list[str], api_key: str | None) -> list[float]:
    """
    Для каждого кода валюты возвращаем курс в рублях (float).
    Если валюта == "RUB" -> 1.0
    В случае ошибки возвращаем 0.0 для этой валюты (чтобы список остался корректной длины).
    """
    list_of_rates: list[float] = []

    if not api_key:

        for cur in currencies:
            list_of_rates.append(1.0 if cur == "RUB" else 0.0)
        return list_of_rates

    headers = {"apikey": api_key}

    for currency_from in currencies:
        if currency_from == "RUB":
            list_of_rates.append(1.0)
            continue


        url = (
            "https://api.apilayer.com/exchangerates_data/convert"
            f"?to=RUB&from={currency_from}&amount=1"
        )

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:

                print(f"Ошибка API для {currency_from}: {resp.status_code}")
                list_of_rates.append(0.0)
                continue

            data = resp.json()

            amount = float(data.get("result", 0.0))
            list_of_rates.append(amount)
        except Exception as e:
            print(f"Исключение при запросе курса {currency_from}: {e}")
            list_of_rates.append(0.0)

    return list_of_rates


def update_currencies(currencies_res: dict, cur_rates: list[float], cur_list: list[str]) -> dict:
    """
    Обновляем поля 'rate' у currencies_res по списку cur_rates.
    Корректно работает, даже если длины списков не совпадают.
    """

    n = min(len(cur_list), len(cur_rates))
    updated = {
        "currency_rates": [
            {"currency": cur_list[i], "rate": cur_rates[i]}
            for i in range(n)
        ]
    }
    return updated


def main(date: str) -> Any:
    """
    Собирает JSON-ответ для страницы "Главная".
    """
    # Пересчитываем filtered_ops, так как дата может различаться
    # Фильтруем по дате
    filtered_ops = filter_by_date(date, operations)

    # 1) читаем настройки
    settings = read_user_settings(SETTINGS_PATH)
    currencies_list, stocks_list = get_user_lists(settings)

    # 2) создаём "пустой" результат по валютам
    currencies_result = receive_currencies(currencies_list)

    # 3) получаем курсы в рублях
    rates = convert_to_rubles(currencies_list, API_KEY)

    # 4) обновляем словарь валют
    currencies_result = update_currencies(currencies_result, rates, currencies_list)

    # 5) получаем цены акций (если есть ключ)
    stocks_data = []
    if stocks_list and TCS_TOKEN:
        # вызываем функцию из utils, она сама делает запросы
        stocks_data = get_us_stocks_alpha_vantage(stocks_list, TCS_TOKEN)
    else:
        # если нет ключа или списка — заполним пустым списком
        stocks_data = []

    # 6) Собираем итоговый ответ
    response = {
        "greeting": greeting_func(datetime.now()),
        "date": date,
        "filtered_by_date_operations": filtered_ops,
        "currency_rates": currencies_result["currency_rates"],
        "stocks": stocks_data,
    }
    return response


if __name__ == "__main__":
    example_date = "2019-11-12 17:10:35"
    result = main(example_date)
    print(json.dumps(result, ensure_ascii=False, indent=2))

