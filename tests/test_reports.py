# tests/test_reports.py
import pandas as pd
import pytest
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Мокаем pd.read_excel перед импортом модуля
with patch('pandas.read_excel'):
    from src.reports import df_filtered_by_date, spending_by_category

def test_df_filtered_by_date(sample_data):
    """Тест фильтрации по дате"""
    result = df_filtered_by_date(sample_data, "2020.03.15")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category(sample_data):
    """Тест фильтрации по категории"""
    result = spending_by_category(sample_data, "Переводы", "2020.03.15")
    assert isinstance(result, pd.DataFrame)
    if len(result) > 0:
        assert all(result["Категория"] == "Переводы")