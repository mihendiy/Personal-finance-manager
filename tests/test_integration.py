import sys
import os

# Добавляем папку src в пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import tempfile
import shutil
from storage import (
    load_transactions, save_transactions,
    load_categories, save_categories,
    load_limits, save_limits,
    load_piggy_bank, save_piggy_bank,
    get_data_path
)


# ===== 1. Транзакции =====

def test_save_and_load_transactions():
    test_data = [
        {"category": "еда", "amount": 500, "type": "расход", "year": 2026, "month": 1},
        {"category": "зарплата", "amount": 50000, "type": "доход", "year": 2026, "month": 1},
    ]
    # Сохраняем
    save_transactions(test_data)
    # Загружаем
    loaded = load_transactions()
    assert len(loaded) == len(test_data)
    assert loaded[0]["category"] == "еда"
    assert loaded[1]["amount"] == 50000


# ===== 2. Категории =====

def test_save_and_load_categories():
    test_data = {
        "доход": ["зарплата", "премия"],
        "расход": ["еда", "транспорт"]
    }
    save_categories(test_data)
    loaded = load_categories()
    assert loaded["доход"] == test_data["доход"]
    assert loaded["расход"] == test_data["расход"]


# ===== 3. Лимиты =====

def test_save_and_load_limits():
    test_data = {
        (2026, 1): {"total": 20000, "categories": {"еда": 5000}, "is_manual": True}
    }
    save_limits(test_data)
    loaded = load_limits()
    assert (2026, 1) in loaded
    assert loaded[(2026, 1)]["total"] == 20000
    assert loaded[(2026, 1)]["categories"]["еда"] == 5000


# ===== 4. Копилка =====

def test_save_and_load_piggy():
    test_balance = 15000.0
    save_piggy_bank(test_balance)
    loaded = load_piggy_bank()
    assert loaded == test_balance