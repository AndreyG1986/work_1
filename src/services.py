from pathlib import Path
from src.utils import read_excel_file


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SETTINGS_PATH = DATA_DIR / "user_settings.json"
excel_path = DATA_DIR / "operations.xlsx"
# Читаем операции
operations = read_excel_file(excel_path)

# Простой поиск
def search_transactions(ops, cat):
    """Данная функция находит операции по ключу "Категория" и
    добавляет их в список, а затем возвращает этот список"""
    transactions=[]
    for op in ops:
        if op.get("Категория") == cat:
            transactions.append(op)

    return transactions


if __name__ == "__main__":
    print(search_transactions(operations,"Переводы"))