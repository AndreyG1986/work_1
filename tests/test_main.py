from unittest.mock import patch, MagicMock
from src.views import main


@patch('src.views.TCS_TOKEN', 'test_token')  # Исправлено - должен быть в том же модуле, где используется
@patch('src.views.API_KEY', 'test_api_key')
@patch('src.views.SETTINGS_PATH', 'test_settings_path')
@patch('src.views.get_us_stocks_alpha_vantage')  # Если функция используется в views
@patch('src.views.update_currencies')
@patch('src.views.convert_to_rubles')
@patch('src.views.receive_currencies')
@patch('src.views.get_user_lists')  # Если функция используется в views
@patch('src.views.read_user_settings')  # Если функция используется в views
def test_main_function(
        mock_read_settings,
        mock_get_user_lists,
        mock_receive_currencies,
        mock_convert_to_rubles,
        mock_update_currencies,
        mock_get_stocks,
        result_fixture
):
    # Настраиваем моки
    mock_read_settings.return_value = {'some': 'settings'}
    mock_get_user_lists.return_value = (['USD', 'EUR'], ['AAPL', 'AMZN'])

    mock_receive_currencies.return_value = {
        "currency_rates": [
            {"currency": "USD", "rate": 0},
            {"currency": "EUR", "rate": 0}
        ]
    }

    mock_convert_to_rubles.return_value = {
        "USD": 81.299292,
        "EUR": 94.242586
    }

    mock_update_currencies.return_value = {
        "currency_rates": result_fixture["currency_rates"]
    }

    mock_get_stocks.return_value = result_fixture["stocks"]

    # Вызываем тестируемую функцию
    test_date = "2019-11-12 17:10:35"
    result = main(test_date)

    # Проверяем результат
    assert result == result_fixture

    # Проверяем вызовы зависимостей
    mock_read_settings.assert_called_once_with('test_settings_path')
    mock_get_user_lists.assert_called_once_with({'some': 'settings'})
    mock_receive_currencies.assert_called_once_with(['USD', 'EUR'])
    mock_convert_to_rubles.assert_called_once_with(['USD', 'EUR'], 'test_api_key')
    mock_update_currencies.assert_called_once()
    mock_get_stocks.assert_called_once_with(['AAPL', 'AMZN'], 'test_token')