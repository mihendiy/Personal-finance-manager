import sys
import os

# Добавляем папку src в пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from analytics import (
    calculate_rolling_limit,
    get_balance,
    get_expenses_by_category,
    build_text_chart,
    forecast_balance,
    close_month_auto,
    check_category_limits,
    get_category_limit
)


# ===== 1. Тесты для get_balance =====

def test_get_balance_ok():
    transactions = [
        {"category": "зарплата", "amount": 50000, "type": "доход", "year": 2026, "month": 1},
        {"category": "еда", "amount": 5000, "type": "расход", "year": 2026, "month": 1},
        {"category": "транспорт", "amount": 3000, "type": "расход", "year": 2026, "month": 1},
    ]
    income, expense, balance = get_balance(transactions, 2026, 1)
    assert income == 50000
    assert expense == 8000
    assert balance == 42000

def test_get_balance_empty():
    transactions = []
    income, expense, balance = get_balance(transactions, 2026, 1)
    assert income == 0
    assert expense == 0
    assert balance == 0


# ===== 2. Тесты для get_expenses_by_category =====

def test_get_expenses_by_category_ok():
    transactions = [
        {"category": "еда", "amount": 5000, "type": "расход", "year": 2026, "month": 1},
        {"category": "еда", "amount": 3000, "type": "расход", "year": 2026, "month": 1},
        {"category": "транспорт", "amount": 2000, "type": "расход", "year": 2026, "month": 1},
        {"category": "зарплата", "amount": 50000, "type": "доход", "year": 2026, "month": 1},
    ]
    result = get_expenses_by_category(transactions, 2026, 1)
    assert result["еда"] == 8000
    assert result["транспорт"] == 2000
    assert "зарплата" not in result

def test_get_expenses_by_category_empty():
    transactions = []
    result = get_expenses_by_category(transactions, 2026, 1)
    assert result == {}


# ===== 3. Тесты для calculate_rolling_limit =====

def test_calculate_rolling_limit_manual():
    transactions = []
    limits = {(2026, 1): {"total": 20000, "categories": {}, "is_manual": True}}
    result = calculate_rolling_limit(transactions, limits, 2026, 1)
    assert result == 20000

def test_calculate_rolling_limit_from_previous():
    transactions = [
        {"category": "еда", "amount": 15000, "type": "расход", "year": 2025, "month": 12},
    ]
    limits = {}
    result = calculate_rolling_limit(transactions, limits, 2026, 1)
    assert result == 15000
    assert limits[(2026, 1)]["total"] == 15000
    assert limits[(2026, 1)]["is_manual"] == False

def test_calculate_rolling_limit_no_previous(monkeypatch):
    transactions = []
    limits = {}
    monkeypatch.setattr('builtins.input', lambda _: "10000")
    result = calculate_rolling_limit(transactions, limits, 2026, 1)
    assert result == 10000
    assert limits[(2026, 1)]["total"] == 10000
    assert limits[(2026, 1)]["is_manual"] == True


# ===== 4. Тесты для check_category_limits =====

def test_check_category_limits_ok():
    transactions = [{"category": "еда", "amount": 3000, "type": "расход", "year": 2026, "month": 1}]
    limits = {(2026, 1): {"total": 20000, "categories": {"еда": 5000}, "is_manual": True}}
    warnings = check_category_limits(transactions, limits, 2026, 1)
    assert warnings == []

def test_check_category_limits_warning():
    transactions = [{"category": "еда", "amount": 4500, "type": "расход", "year": 2026, "month": 1}]
    limits = {(2026, 1): {"total": 20000, "categories": {"еда": 5000}, "is_manual": True}}
    warnings = check_category_limits(transactions, limits, 2026, 1)
    assert len(warnings) == 1
    assert "почти лимит" in warnings[0]

def test_check_category_limits_exceed():
    transactions = [{"category": "еда", "amount": 6000, "type": "расход", "year": 2026, "month": 1}]
    limits = {(2026, 1): {"total": 20000, "categories": {"еда": 5000}, "is_manual": True}}
    warnings = check_category_limits(transactions, limits, 2026, 1)
    assert len(warnings) == 1
    assert "ПРЕВЫШЕНИЕ" in warnings[0]


# ===== 5. Тесты для close_month_auto =====

def test_close_month_auto_with_remainder():
    transactions = [
        {"category": "зарплата", "amount": 50000, "type": "доход", "year": 2026, "month": 1},
        {"category": "еда", "amount": 15000, "type": "расход", "year": 2026, "month": 1},
    ]
    limits = {(2026, 1): {"total": 20000, "categories": {}, "is_manual": True}}
    piggy_balance = 0.0
    result, new_piggy = close_month_auto(transactions, limits, piggy_balance, 2026, 1)

    assert new_piggy == 35000
    assert limits[(2026, 2)]["total"] == 15000
    assert "35000" in result          # проверяем число (а не точный текст)
    assert "Остаток" in result        # проверяем, что слово "Остаток" есть
    assert "Доходы за месяц: 50000" in result
    assert "Расходы за месяц: 15000" in result



def test_close_month_auto_no_remainder():
    transactions = [
        {"category": "зарплата", "amount": 10000, "type": "доход", "year": 2026, "month": 1},
        {"category": "еда", "amount": 15000, "type": "расход", "year": 2026, "month": 1},
    ]
    limits = {(2026, 1): {"total": 20000, "categories": {}, "is_manual": True}}
    piggy_balance = 0.0
    result, new_piggy = close_month_auto(transactions, limits, piggy_balance, 2026, 1)
    assert new_piggy == 0
    assert limits[(2026, 2)]["total"] == 15000

def test_close_month_auto_no_limit():
    transactions = [{"category": "зарплата", "amount": 50000, "type": "доход", "year": 2026, "month": 1}]
    limits = {}
    piggy_balance = 0.0
    result, new_piggy = close_month_auto(transactions, limits, piggy_balance, 2026, 1)
    assert "Лимит на этот месяц не установлен" in result
    assert new_piggy == 0