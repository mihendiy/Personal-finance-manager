WARNING_THRESHOLD = 0.8
CHART_MAX_WIDTH = 30


def calculate_rolling_limit(transactions, limits, year, month):
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
    result = {}
    for t in transactions:
        if t.get("year") == year and t.get("month") == month and t["type"] == "расход":
            cat = t["category"]
            result[cat] = result.get(cat, 0) + t["amount"]
    return result


def build_text_chart(transactions, year, month):
    expenses = get_expenses_by_category(transactions, year, month)
    if not expenses:
        return "Нет расходов за этот месяц."

    max_amount = max(expenses.values())
    lines = [f"\n--- Диаграмма расходов за {month}.{year} ---"]
    for cat, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((amount / max_amount) * CHART_MAX_WIDTH) if max_amount > 0 else 0
        bar = "█" * bar_len
        lines.append(f"{cat:<15} | {bar} {amount:.2f} руб.")
    return "\n".join(lines)


def forecast_balance(transactions, limits, year, month):
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
📈 Итоговый баланс: {balance:.2f} руб.
"""


def close_month_auto(transactions, limits, piggy_balance, year, month):
    """
    Автоматическое закрытие месяца:
    - остаток = доходы - расходы → переходит в копилку
    - лимит следующего месяца = расходы этого месяца
    """
    key = (year, month)

    # 1. Получаем текущий лимит
    current_limit = limits.get(key, {}).get("total")
    if current_limit is None:
        return "⚠️ Лимит на этот месяц не установлен.", piggy_balance

    # 2. Считаем доходы и расходы за месяц
    total_income = 0
    total_expense = 0
    for t in transactions:
        if t.get("year") == year and t.get("month") == month:
            if t["type"] == "доход":
                total_income += t["amount"]
            else:
                total_expense += t["amount"]

    # 3. Считаем остаток (реальные деньги, которые остались)
    remainder = total_income - total_expense

    # 4. Определяем следующий месяц
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    next_key = (next_year, next_month)

    # 5. Устанавливаем лимит на следующий месяц = расходы
    if next_key not in limits:
        limits[next_key] = {"total": None, "categories": {}, "is_manual": False}
    limits[next_key]["total"] = total_expense
    limits[next_key]["is_manual"] = False

    # 6. Если есть остаток — отправляем в копилку
    if remainder > 0:
        piggy_balance += remainder
        from storage import save_piggy_bank
        save_piggy_bank(piggy_balance)

    # 7. Сохраняем лимиты
    from storage import save_limits
    save_limits(limits)

    # 8. Формируем отчёт
    result = f"""
✅ МЕСЯЦ {month}.{year} ЗАКРЫТ!

💰 Лимит месяца: {current_limit:.2f} руб.
💵 Доходы за месяц: {total_income:.2f} руб.
💸 Расходы за месяц: {total_expense:.2f} руб.
📦 Остаток (доходы - расходы, перешёл в копилку): {remainder:.2f} руб.
🏦 В копилке теперь: {piggy_balance:.2f} руб.
🔄 Новый лимит на {next_month}.{next_year}: {total_expense:.2f} руб.
"""
    return result, piggy_balance

def check_category_limits(transactions, limits, year, month):
    key = (year, month)
    warnings = []

    if key not in limits or "categories" not in limits[key]:
        return warnings

    category_limits = limits[key]["categories"]
    expenses = get_expenses_by_category(transactions, year, month)

    for cat, limit in category_limits.items():
        spent = expenses.get(cat, 0)
        if spent > limit:
            warnings.append(f"🔴 КАТЕГОРИЯ '{cat}': ПРЕВЫШЕНИЕ! Потрачено {spent:.2f} из {limit:.2f} руб.")
        elif spent >= limit * WARNING_THRESHOLD:
            warnings.append(f"🟡 КАТЕГОРИЯ '{cat}': Внимание! Потрачено {spent:.2f} из {limit:.2f} руб. (почти лимит)")

    return warnings


def get_category_limit(limits, year, month, category):
    key = (year, month)
    if key in limits and "categories" in limits[key]:
        return limits[key]["categories"].get(category)
    return None