import json
import os
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # Загружаем переменные окружения
TCS_TOKEN = os.getenv("API_TOKEN_TINKOFF")  # Ключ к API
DATA_DIR = BASE_DIR / "data"

def read_user_settings(path: Path) -> dict:
    """Чтение JSON-файла user_settings.json"""
    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Файл не найден")
        return {}
    except json.JSONDecodeError:
        print("Ошибка чтения JSON-файла")
        return {}

def get_user_lists(settings: dict):
    """Получаем списки валют и акций из настроек"""
    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])
    return currencies, stocks

def get_us_stocks_alpha_vantage(tickers: list[str], api_key: str) -> list[dict]:
    """
    Получаем цены акций через API Alpha Vantage
    (Не больше 5 запросов в минуту!)
    """
    stock_prices = []

    for ticker in tickers:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                price = float(data["Global Quote"]["05. price"])
                stock_prices.append({"ticker": ticker, "price": price})
            else:
                print(f"Нет данных для тикера {ticker}")
        except Exception as e:
            print(f"Ошибка при получении данных для {ticker}: {e}")

    return stock_prices


def read_excel_file(path: Path) -> list[dict]:
    """Считываем Excel-файл с операциями и возвращаем список словарей"""
    df = pd.read_excel(path)
    data = df.to_dict(orient="records")

    # заменяем NaN на None (чтобы JSON не падал)
    for record in data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return data


def read_date(date_str: str) -> datetime:
    """Читает дату в формате 'YYYY-MM-DD HH:MM:SS'"""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def filter_by_date(target_date: str, operations: list[dict]) -> list[dict]:
    """
    Фильтрует операции:
    Возвращает все операции с начала месяца до указанной даты включительно.
    """
    target = read_date(target_date)
    filtered = []

    for op in operations:
        try:
            op_date = datetime.strptime(op["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if (op_date.year == target.year and
                    op_date.month == target.month and
                    op_date <= target):
                filtered.append(op)
        except Exception:
            continue

    return filtered

def greeting_func(date_obj: datetime) -> str:
    """Возвращает приветствие по времени суток"""
    if date_obj.hour < 12 and date_obj.hour > 6:
        return "Доброе утро!"
    elif date_obj.hour < 17:
        return "Добрый день!"
    elif date_obj.hour > 0 and date_obj.hour < 6:
        return "Доброй ночи!"
    else:
        return "Добрый вечер!"

if __name__ == "__main__":
    # Пути к файлам
    settings_path = DATA_DIR / "user_settings.json"
    excel_path = DATA_DIR / "operations.xlsx"

    # Читаем настройки пользователя
    settings = read_user_settings(settings_path)
    currencies, stocks = get_user_lists(settings)

    print("Пользовательские акции:", stocks)
    print("Пользовательские валюты:", currencies)

    # Загружаем данные по акциям
    # if TCS_TOKEN and stocks:
    #     prices = get_us_stocks_alpha_vantage(stocks, TCS_TOKEN)
    #     print("Цены акций:", prices)

    # Читаем операции
    operations = read_excel_file(excel_path)
    print(f"Загружено операций: {len(operations)}")

    # Фильтруем по дате
    filtered_ops = filter_by_date("2019-11-12 17:10:35", operations)
    print(f"Найдено операций до даты: {len(filtered_ops)}")

    # Приветствие
    print(greeting_func(datetime.now()))
