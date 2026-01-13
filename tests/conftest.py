import pytest


@pytest.fixture
def result_fixture():
  return {
  "greeting": "Добрый вечер!",
  "date": "2019-11-12 17:10:35",
  "filtered_by_date_operations": [{
    "date": "2019-11-12 17:10:35",
    "currency_rates": [
      {
        "currency": "USD",
        "rate": 81.299292
      },
      {
        "currency": "EUR",
        "rate": 94.242586
      }
    ],
    "stocks": [
      {
        "ticker": "AAPL",
        "price": 275.25
      },
      {
        "ticker": "AMZN",
        "price": 249.1
      },
      {
        "ticker": "GOOGL",
        "price": 291.31
      },
      {
        "ticker": "MSFT",
        "price": 508.68
      },
      {
        "ticker": "TSLA",
        "price": 439.62
      }
    ]
  }]}

@pytest.fixture
def operation_from_excel():
  return [{'Дата операции': '15.07.2019 16:50:10', 'Дата платежа': '17.07.2019', 'Номер карты': '*7197', 'Статус': 'OK', 'Сумма операции': -114.19, 'Валюта операции': 'RUB', 'Сумма платежа': -114.19, 'Валюта платежа': 'RUB', 'Кэшбэк': None, 'Категория': 'Супермаркеты', 'MCC': 5499.0, 'Описание': 'Колхоз', 'Бонусы (включая кэшбэк)': 2, 'Округление на инвесткопилку': 0, 'Сумма операции с округлением': 114.19}]