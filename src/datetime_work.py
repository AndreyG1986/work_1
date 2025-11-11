import pandas as pd
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import datetime
import re

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "user_settings.json"
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')
TCS_TOKEN = os.getenv('API_TOKEN_TINKOFF')


def read_user_settings(path):
    """Получение user_settings из json файла"""
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            user_data = json.load(f)
        # utils_logger.info("Файл %s успешно обработан", path)
        return user_data
    except FileNotFoundError:
        # utils_logger.error("Файл не найден: %s", path)
        print("Файл не найден")
        return []
    except json.JSONDecodeError as e:
        # utils_logger.error("Ошибка JSON в %s: %s", path, e)
        print("Запись содержит ошибки")
        return []

# Получаем набор настроек
settings = read_user_settings(PATH_TO_FILE)

def get_lists_of_settings(dict_of_settings: dict):
    """Получаем список валют и список акций"""
    # получаем список валют
    users_currencies = dict_of_settings.get('user_currencies')
    # получаем список акций
    users_stocks = dict_of_settings.get('user_stocks')
    return users_currencies, users_stocks

settings = get_lists_of_settings(settings)
# получаем список валют
list_of_currencies=settings[0]
# получаем список акций
list_of_stocks=settings[1]


def read_xl_file(path_to_file_xl: str)  -> str:
    """Функция для считывания excel файла.
    должна принимать путь например:
    "../data/transactions_excel.xlsx"/"""
    transactions_excel_data = pd.read_excel(path_to_file_xl)
    # Преобразуем DataFrame в список словарей
    list_of_dicts_xl = transactions_excel_data.to_dict(orient="records")

    # Преобразуем в JSON строку
    # json_data = json.dumps(list_of_dicts_xl, ensure_ascii=False, indent=2)

    # Заменяем pandas NaN на Python None
    for item in list_of_dicts_xl:
        for key, value in item.items():
            if pd.isna(value):
                item[key] = None

    return list_of_dicts_xl
    # return json_data

# получаем документ в json формате
operations_list = read_xl_file("../data/operations.xlsx")

# Заменяем NaN на null (который в Python станет None)
# cleaned_json = re.sub(r'\bNaN\b', 'null', json_string)
# operations_list = json.loads(cleaned_json)

my_date_object = datetime.datetime.now()
def greeting_func(date_obj):
    if date_obj.hour < 12:
        return "Доброе утро!"
    elif date_obj.hour < 17:
        return "Добрый день!"
    else:
        return "Добрый вечер!"

def iter_thru_ops(list_of_ops):
    """Итерируемся по списку операций и создаём список с нужными датами"""
    list_of_dates = []
    dates_strings = ""
    for operation in list_of_ops:
        dates_strings = operation["Дата операции"]
        list_of_dates.append(dates_strings)

    return list_of_dates

dates = iter_thru_ops(operations_list)

# Извлекаем день, месяц, год с помощью регулярных выражений
# date_pattern = r'(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})'
# match = re.match(date_pattern, dates)
#
# if match:
#     day = match.group(1)  # '01'
#     month = match.group(2)  # '01'
#     year = match.group(3)  # '2018'
#     hour = match.group(4)  # '12'
#     minute = match.group(5)  # '49'
#     second = match.group(6)  # '53'
#
#     print(f"День: {day}, Месяц: {month}, Год: {year}")
#     print(f"Время: {hour}:{minute}:{second}")

my_date_string = "2019-11-19 17:10:35"
def filter_by_date(date: str, operations):
    """Функция принимающую на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ со следующими данными:
    Данные для анализа и вывода на веб-страницах — это данные с начала месяца, на который
    выпадает входящая дата, по входящую дату.
    Если дата — 20.05.2020, то данные для анализа будут в диапазоне 01.05.2020-20.05.2020"""
    # берем строку с датой и забираем из неё месяц
    pass

if __name__ == "__main__":
    print(dates)
    # print(stocks)
    print()
    # print(read_user_settings(PATH_TO_FILE))
    # print(greeting_func(my_date_object))
    # print(list_of_currencies)
    # print(my_date_object.minute)
