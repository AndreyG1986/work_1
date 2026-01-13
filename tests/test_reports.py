import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.reports import df_filtered_by_date, spending_by_category


def test_df_filtered_by_date_simple(sample_data):
    """Простой тест фильтрации по дате"""
    result = df_filtered_by_date(sample_data, "2020.03.15")

    # Базовые проверки
    assert isinstance(result, pd.DataFrame)
    assert "Дата операции" in result.columns
    assert len(result) <= len(sample_data)


def test_spending_by_category_simple(sample_data):
    """Простой тест фильтрации по категории"""
    result = spending_by_category(sample_data, "Переводы", "2020.03.15")

    assert isinstance(result, pd.DataFrame)
    if len(result) > 0:
        assert all(result["Категория"] == "Переводы")


def test_spending_by_category_no_data(sample_data):
    """Тест когда категория не найдена"""
    result = spending_by_category(sample_data, "Несуществующая", "2020.03.15")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0