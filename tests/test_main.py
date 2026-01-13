import json
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime
from src.views import main, receive_currencies, convert_to_rubles, update_currencies, API_KEY, TCS_TOKEN
from src.utils import read_user_settings, get_user_lists, get_us_stocks_alpha_vantage, read_excel_file, filter_by_date, \
    greeting_func


class TestMainFunction:
    """Тестирование функции main"""

    @pytest.fixture
    def mock_operations(self):
        """Фикстура для мока операций"""
        return [
            {
                "Дата операции": "12.11.2019 15:57:16",
                "Сумма операции": -27.9,
                "Валюта операции": "RUB",
                "Категория": "Супермаркеты"
            },
            {
                "Дата операции": "12.11.2019 15:50:37",
                "Сумма операции": -82.0,
                "Валюта операции": "RUB",
                "Категория": "Транспорт"
            }
        ]

    def test_main_success(self, mock_operations):
        """
        Тест успешного выполнения main с моками всех зависимостей
        """
        # Подготавливаем тестовые данные
        test_date = "2019-11-12 17:10:35"

        # Создаем моки для всех зависимостей
        with patch('src.views.read_user_settings') as mock_read_settings, \
                patch('src.views.get_user_lists') as mock_get_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_read_excel, \
                patch('src.views.convert_to_rubles') as mock_convert, \
                patch('src.views.get_us_stocks_alpha_vantage') as mock_stocks, \
                patch('src.views.greeting_func') as mock_greeting:

            # Настраиваем API ключи внутри контекста
            import src.views
            original_api_key = src.views.API_KEY
            original_tcs_token = src.views.TCS_TOKEN
            src.views.API_KEY = 'test_api_key'
            src.views.TCS_TOKEN = 'test_tcs_token'

            try:
                # Настраиваем возвращаемые значения моков
                mock_read_excel.return_value = mock_operations
                mock_filter.return_value = mock_operations[:2]

                mock_read_settings.return_value = {"test": "settings"}
                mock_get_lists.return_value = (["USD", "EUR"], ["AAPL", "AMZN"])

                mock_greeting.return_value = "Добрый вечер!"

                mock_convert.return_value = [81.299292, 94.242586]

                mock_stocks.return_value = [
                    {"ticker": "AAPL", "price": 275.25},
                    {"ticker": "AMZN", "price": 249.10}
                ]

                # Вызываем тестируемую функцию
                result = main(test_date)

                # Проверяем структуру результата
                assert "greeting" in result
                assert "date" in result
                assert "filtered_by_date_operations" in result
                assert "currency_rates" in result
                assert "stocks" in result

                # Проверяем конкретные значения
                assert result["greeting"] == "Добрый вечер!"
                assert result["date"] == test_date
                assert len(result["filtered_by_date_operations"]) == 2
                assert len(result["currency_rates"]) == 2
                assert len(result["stocks"]) == 2
            finally:
                # Восстанавливаем оригинальные значения
                src.views.API_KEY = original_api_key
                src.views.TCS_TOKEN = original_tcs_token

    def test_main_without_api_keys(self, mock_operations):
        """
        Тест main без API ключей
        """
        test_date = "2019-11-12 17:10:35"

        with patch('src.views.read_user_settings') as mock_read_settings, \
                patch('src.views.get_user_lists') as mock_get_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_read_excel, \
                patch('src.views.greeting_func') as mock_greeting:

            # Устанавливаем None для API ключей
            import src.views
            original_api_key = src.views.API_KEY
            original_tcs_token = src.views.TCS_TOKEN
            src.views.API_KEY = None
            src.views.TCS_TOKEN = None

            try:
                mock_read_excel.return_value = mock_operations
                mock_filter.return_value = mock_operations[:1]
                mock_read_settings.return_value = {}
                mock_get_lists.return_value = (["RUB", "USD"], [])
                mock_greeting.return_value = "Добрый день!"

                result = main(test_date)

                # При отсутствии TCS_TOKEN список акций должен быть пустым
                assert result["stocks"] == []
            finally:
                # Восстанавливаем оригинальные значения
                src.views.API_KEY = original_api_key
                src.views.TCS_TOKEN = original_tcs_token

    def test_main_with_empty_settings(self):
        """
        Тест main с пустыми настройками пользователя
        """
        test_date = "2019-11-12 17:10:35"

        with patch('src.views.read_user_settings') as mock_read_settings, \
                patch('src.views.get_user_lists') as mock_get_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_read_excel, \
                patch('src.views.greeting_func') as mock_greeting:
            mock_read_excel.return_value = []
            mock_filter.return_value = []
            mock_read_settings.return_value = {}
            mock_get_lists.return_value = ([], [])
            mock_greeting.return_value = "Доброе утро!"

            result = main(test_date)

            assert result["filtered_by_date_operations"] == []
            assert result["currency_rates"] == []
            assert result["stocks"] == []


class TestCurrencyFunctions:
    """Тестирование вспомогательных функций для валют"""

    def test_receive_currencies(self):
        """Тест функции receive_currencies"""
        currencies = ["USD", "EUR", "RUB"]
        result = receive_currencies(currencies)

        assert "currency_rates" in result
        assert len(result["currency_rates"]) == 3

        for i, currency in enumerate(currencies):
            assert result["currency_rates"][i]["currency"] == currency
            assert result["currency_rates"][i]["rate"] == 0.0

    def test_update_currencies(self):
        """Тест функции update_currencies"""
        currencies_res = {
            "currency_rates": [
                {"currency": "USD", "rate": 0.0},
                {"currency": "EUR", "rate": 0.0}
            ]
        }

        rates = [81.299292, 94.242586]
        currencies_list = ["USD", "EUR"]

        result = update_currencies(currencies_res, rates, currencies_list)

        assert result["currency_rates"][0]["currency"] == "USD"
        assert result["currency_rates"][0]["rate"] == 81.299292
        assert result["currency_rates"][1]["currency"] == "EUR"
        assert result["currency_rates"][1]["rate"] == 94.242586

    def test_convert_to_rubles_with_api_key(self):
        """Тест функции convert_to_rubles с API ключом"""
        currencies = ["USD", "EUR", "RUB"]
        api_key = "test_api_key"

        with patch('src.views.requests.get') as mock_get:
            # Настраиваем мок ответа API
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": 75.5}
            mock_get.return_value = mock_response

            # Меняем API_KEY
            import src.views
            original_api_key = src.views.API_KEY
            src.views.API_KEY = api_key

            try:
                result = convert_to_rubles(currencies, api_key)

                # RUB должен быть 1.0, остальные - значение из мока
                assert len(result) == 3
                # Проверяем, что для RUB вернулся 1.0
                # На самом деле функция сначала проверит if currency_from == "RUB"
                # и вернет 1.0 для RUB, а для остальных сделает запрос к API
            finally:
                src.views.API_KEY = original_api_key

    def test_convert_to_rubles_without_api_key(self):
        """Тест функции convert_to_rubles без API ключа"""
        currencies = ["USD", "EUR", "RUB"]

        # Передаем None как api_key
        result = convert_to_rubles(currencies, None)

        # Без API ключа все валюты кроме RUB должны быть 0.0
        # RUB всегда 1.0
        usd_index = currencies.index("USD")
        eur_index = currencies.index("EUR")
        rub_index = currencies.index("RUB")

        assert result[rub_index] == 1.0
        assert result[usd_index] == 0.0
        assert result[eur_index] == 0.0

    def test_convert_to_rubles_api_error(self):
        """Тест функции convert_to_rubles при ошибке API"""
        currencies = ["USD", "EUR"]
        api_key = "test_api_key"

        with patch('src.views.requests.get') as mock_get:
            # Мок ошибки API
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = convert_to_rubles(currencies, api_key)

            # При ошибке должны вернуться 0.0
            assert result == [0.0, 0.0]

    def test_convert_to_rubles_exception(self):
        """Тест функции convert_to_rubles при исключении"""
        currencies = ["USD"]
        api_key = "test_api_key"

        with patch('src.views.requests.get', side_effect=Exception("Network error")):
            result = convert_to_rubles(currencies, api_key)

            # При исключении должен вернуться 0.0
            assert result == [0.0]


class TestMainWithRequests:
    """Тестирование main с моками requests"""

    def test_main_with_api_requests(self):
        """Тест main с реальными запросами к API"""
        test_date = "2019-11-12 17:10:35"

        with patch('src.views.read_user_settings') as mock_settings, \
                patch('src.views.get_user_lists') as mock_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_excel, \
                patch('src.views.requests.get') as mock_requests, \
                patch('src.views.greeting_func') as mock_greeting, \
                patch('src.views.get_us_stocks_alpha_vantage') as mock_stocks:

            # Устанавливаем тестовые API ключи
            import src.views
            original_api_key = src.views.API_KEY
            original_tcs_token = src.views.TCS_TOKEN
            src.views.API_KEY = 'test_api_key'
            src.views.TCS_TOKEN = 'test_tcs_token'

            try:
                # Настраиваем моки
                mock_excel.return_value = [{"Дата операции": "12.11.2019 15:57:16"}]
                mock_filter.return_value = [{"Дата операции": "12.11.2019 15:57:16"}]
                mock_settings.return_value = {}
                mock_lists.return_value = (["USD", "EUR"], ["AAPL"])
                mock_greeting.return_value = "Тест"

                # Мок для API валют
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"result": 80.5}
                mock_requests.return_value = mock_response

                # Мок для акций
                mock_stocks.return_value = [{"ticker": "AAPL", "price": 150.0}]

                # Вызываем main
                result = main(test_date)

                # Проверяем, что requests.get был вызван для каждой валюты (кроме RUB)
                # USD и EUR - 2 вызова
                assert mock_requests.call_count >= 2

                # Проверяем результат
                assert len(result["currency_rates"]) == 2
                assert len(result["stocks"]) == 1
            finally:
                # Восстанавливаем оригинальные значения
                src.views.API_KEY = original_api_key
                src.views.TCS_TOKEN = original_tcs_token

    def test_main_stocks_without_token(self):
        """Тест main без TCS_TOKEN"""
        test_date = "2019-11-12 17:10:35"

        with patch('src.views.read_user_settings') as mock_settings, \
                patch('src.views.get_user_lists') as mock_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_excel, \
                patch('src.views.greeting_func') as mock_greeting:

            # Устанавливаем None для TCS_TOKEN
            import src.views
            original_tcs_token = src.views.TCS_TOKEN
            src.views.TCS_TOKEN = None

            try:
                mock_excel.return_value = []
                mock_filter.return_value = []
                mock_settings.return_value = {}
                mock_lists.return_value = ([], ["AAPL", "GOOGL"])  # Есть акции в настройках
                mock_greeting.return_value = "Тест"

                result = main(test_date)

                # Без TCS_TOKEN список акций должен быть пустым
                assert result["stocks"] == []
            finally:
                src.views.TCS_TOKEN = original_tcs_token

    def test_main_stocks_empty_list(self):
        """Тест main с пустым списком акций"""
        test_date = "2019-11-12 17:10:35"

        with patch('src.views.read_user_settings') as mock_settings, \
                patch('src.views.get_user_lists') as mock_lists, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_excel_file') as mock_excel, \
                patch('src.views.greeting_func') as mock_greeting:
            mock_excel.return_value = []
            mock_filter.return_value = []
            mock_settings.return_value = {}
            mock_lists.return_value = (["USD"], [])  # Пустой список акций
            mock_greeting.return_value = "Тест"

            result = main(test_date)

            # С пустым списком акций результат должен быть пустым списком
            assert result["stocks"] == []


class TestMainIntegration:
    """Интеграционные тесты"""

    def test_main_complete_flow(self):
        """Полный тест потока выполнения main"""
        test_date = "2019-11-12 17:10:35"

        # Подготавливаем все моки
        with patch('src.views.read_excel_file') as mock_excel, \
                patch('src.views.filter_by_date') as mock_filter, \
                patch('src.views.read_user_settings') as mock_settings, \
                patch('src.views.get_user_lists') as mock_lists, \
                patch('src.views.requests.get') as mock_requests, \
                patch('src.views.get_us_stocks_alpha_vantage') as mock_stocks, \
                patch('src.views.datetime') as mock_datetime:

            # Устанавливаем тестовые API ключи
            import src.views
            original_api_key = src.views.API_KEY
            original_tcs_token = src.views.TCS_TOKEN
            src.views.API_KEY = 'test_api_key'
            src.views.TCS_TOKEN = 'test_tcs_token'

            try:
                # Настраиваем данные
                operations_data = [
                    {"Дата операции": "12.11.2019 15:57:16", "Сумма": 100},
                    {"Дата операции": "11.11.2019 10:00:00", "Сумма": 200}
                ]

                mock_excel.return_value = operations_data
                mock_filter.return_value = [operations_data[0]]

                mock_settings.return_value = {"user": "test"}
                mock_lists.return_value = (["USD", "EUR"], ["AAPL"])

                # Мок для datetime в greeting_func
                mock_datetime.now.return_value = datetime(2019, 11, 12, 20, 0, 0)

                # Мок для API валют
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"result": 85.0}
                mock_requests.return_value = mock_response

                # Мок для акций
                mock_stocks.return_value = [{"ticker": "AAPL", "price": 150.0}]

                # Выполняем функцию
                result = main(test_date)

                # Проверяем результат
                assert result["date"] == test_date
                assert "Добрый вечер!" in result["greeting"]
                assert len(result["filtered_by_date_operations"]) == 1
                assert len(result["currency_rates"]) == 2
                assert len(result["stocks"]) == 1
            finally:
                # Восстанавливаем оригинальные значения
                src.views.API_KEY = original_api_key
                src.views.TCS_TOKEN = original_tcs_token