from unittest.mock import patch, MagicMock
from src.utils import read_excel_file


@patch("pandas.read_excel")
def test_read_excel_file(mock_read_excel, operation_from_excel):
    # Создаем mock DataFrame
    mock_df = MagicMock()
    mock_df.to_dict.return_value = operation_from_excel
    mock_read_excel.return_value = mock_df

    # Вызываем тестируемую функцию
    result = read_excel_file("test_path")