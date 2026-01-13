import pandas as pd
from typing import Optional
from datetime import datetime, timedelta


df = pd.read_excel("../data/operations.xlsx")

def df_filtered_by_date(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Фильтрует транзакции за последние 90 дней от указанной даты.
    Дата операции в формате '01.11.2019 10:45:29' преобразуется в дату.
    """
    # Получаем дату "90 дней назад" в формате datetime
    if date is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(date, "%Y.%m.%d")

    start_date = target_date - timedelta(days=90)

    # Преобразуем строковые даты в dataframe в datetime
    # Важно: используем dayfirst=True, так как дата начинается с дня
    transactions_dates = pd.to_datetime(
        transactions["Дата операции"],
        format="%d.%m.%Y %H:%M:%S",
        errors='coerce'
    )

    # Фильтруем: дата операции должна быть между start_date и target_date
    mask = (transactions_dates >= start_date) & (transactions_dates <= target_date)
    filtered_df_by_date = transactions.loc[mask]

    # Сортируем по дате (новые сверху)
    filtered_df_by_date = filtered_df_by_date.sort_values("Дата операции", ascending=False)

    return filtered_df_by_date

def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход:
    датафрейм с транзакциями,
    название категории,
    опциональную дату.
    Если дата не передана, то берется текущая дата.
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    filtered_df_by_cat = transactions.loc[transactions['Категория'] == category]
    filtered_df_by_cat_and_date = df_filtered_by_date(filtered_df_by_cat,date)
    return filtered_df_by_cat_and_date

if __name__ == "__main__":
    filtered_df = df_filtered_by_date(df, "2020.03.15")
    print(filtered_df)

    print(spending_by_category(df,"Переводы","2020.03.15"))

