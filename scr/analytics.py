def calculate_rolling_limit(transactions, limits, year, month):
    """Рассчитать лимит на месяц по принципу скользящего бюджета."""
    key = (year, month)

    if key in limits and limits[key].get("total") is not None:
        print(f"📌 Используем ручной лимит: {limits[key]['total']:.2f} руб.")
        return limits[key]["total"]

    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    total_expense = 0
    for t in transactions:
        if t.get("year") == prev_year and t.get("month") == prev_month and t.get("type") == "расход":
            total_expense += t.get("amount", 0)

    if total_expense > 0:
        print(f"🔄 Скользящий бюджет: лимит на {month}.{year} = {total_expense:.2f} руб.")
        print(f"   (расходы за {prev_month}.{prev_year})")
        if key not in limits:
            limits[key] = {"total": None, "categories": {}, "is_manual": False}
        limits[key]["total"] = total_expense
        limits[key]["is_manual"] = False
        return total_expense

    print(f"⚠️ Нет данных за прошлый месяц ({prev_month}.{prev_year}).")
    while True:
        try:
            manual_limit = float(input(f"Введите примерный лимит на {month}.{year}: "))
            if manual_limit <= 0:
                print("Лимит должен быть положительным!")
                continue
            break
        except ValueError:
            print("Ошибка! Введите число.")

    if key not in limits:
        limits[key] = {"total": None, "categories": {}, "is_manual": False}
    limits[key]["total"] = manual_limit
    limits[key]["is_manual"] = True
    print(f"✅ Ручной лимит установлен: {manual_limit:.2f} руб.")
    return manual_limit


def get_balance(transactions, year, month):
    """Вернуть доходы, расходы и баланс за указанный месяц"""
    income = 0
    expense = 0
    for t in transactions:
        if t.get("year") == year and t.get("month") == month:
            if t["type"] == "доход":
                income += t["amount"]
            else:
                expense += t["amount"]
    return income, expense, income - expense


def get_expenses_by_category(transactions, year, month):
    """Вернуть словарь расходов по категориям за указанный месяц"""
    result = {}
    for t in transactions:
        if t.get("year") == year and t.get("month") == month and t["type"] == "расход":
            cat = t["category"]
            result[cat] = result.get(cat, 0) + t["amount"]
    return result


def build_text_chart(transactions, year, month):
    """Построить текстовую диаграмму расходов за месяц"""
    expenses = get_expenses_by_category(transactions, year, month)
    if not expenses:
        return "Нет расходов за этот месяц."

    max_amount = max(expenses.values())
    max_width = 30
    lines = [f"\n--- Диаграмма расходов за {month}.{year} ---"]
    for cat, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((amount / max_amount) * max_width) if max_amount > 0 else 0
        bar = "█" * bar_len
        lines.append(f"{cat:<15} | {bar} {amount:.2f} руб.")
    return "\n".join(lines)


def forecast_balance(transactions, limits, year, month):
    """Прогноз остатка на конец месяца"""
    key = (year, month)
    monthly_limit = limits.get(key, {}).get("total")
    if monthly_limit is None:
        return "⚠️ Лимит на месяц не установлен. Сначала установите лимит."

    income, expense, balance = get_balance(transactions, year, month)
    remaining = monthly_limit - expense
    return f"""
--- Прогноз на {month}.{year} ---
💰 Лимит месяца: {monthly_limit:.2f} руб.
💸 Потрачено: {expense:.2f} руб.
📊 Остаток бюджета: {remaining:.2f} руб.
📈 Итоговый баланс (с учётом доходов): {balance:.2f} руб.
"""


def close_month(transactions, limits, year, month):
    """
    Закрыть текущий месяц:
    - рассчитать расходы за месяц
    - перенести их как лимит на следующий месяц
    """
    total_expense = 0
    for t in transactions:
        if t.get("year") == year and t.get("month") == month and t.get("type") == "расход":
            total_expense += t.get("amount", 0)

    if total_expense == 0:
        return "⚠️ Нет расходов за этот месяц. Закрытие невозможно."

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    key = (next_year, next_month)

    if key not in limits:
        limits[key] = {"total": None, "categories": {}, "is_manual": False}
    limits[key]["total"] = total_expense
    limits[key]["is_manual"] = False

    from storage import save_limits
    save_limits(limits)

    return f"""
✅ МЕСЯЦ {month}.{year} ЗАКРЫТ!

📊 Расходы за месяц: {total_expense:.2f} руб.
🔄 Лимит на {next_month}.{next_year} установлен: {total_expense:.2f} руб.
"""



def check_category_limits(transactions, limits, year, month):

    key = (year, month)
    warnings = []

    # Если нет лимитов по категориям — возвращаем пустой список
    if key not in limits or "categories" not in limits[key]:
        return warnings

    category_limits = limits[key]["categories"]

    # Считаем расходы по категориям за месяц
    expenses = get_expenses_by_category(transactions, year, month)

    # Проверяем каждую категорию
    for cat, limit in category_limits.items():
        spent = expenses.get(cat, 0)
        if spent > limit:
            warnings.append(f"🔴 КАТЕГОРИЯ '{cat}': ПРЕВЫШЕНИЕ! Потрачено {spent:.2f} из {limit:.2f} руб.")
        elif spent >= limit * 0.8:
            warnings.append(f"🟡 КАТЕГОРИЯ '{cat}': Внимание! Потрачено {spent:.2f} из {limit:.2f} руб. (почти лимит)")

    return warnings


def get_category_limit(limits, year, month, category):

    key = (year, month)
    if key in limits and "categories" in limits[key]:
        return limits[key]["categories"].get(category)
    return None