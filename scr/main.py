from storage import (
    load_transactions, save_transactions,
    load_categories, save_categories,
    load_limits, save_limits
)
from analytics import (
    calculate_rolling_limit,
    get_balance,
    get_expenses_by_category,
    build_text_chart,
    forecast_balance,
    close_month,
    check_category_limits,
    get_category_limit
)

# ---------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------
transactions = []
categories = {}
limits = {}
current_year = 2026
current_month = 1


# ---------- ВЫБОР ГОДА ----------

def show_years():
    print("\n" + "=" * 40)
    print("ВЫБОР ГОДА")
    print("=" * 40)
    print("1. 2026")
    print("2. 2027")
    print("0. Выход")
    print("=" * 40)


def choose_year():
    global current_year
    while True:
        show_years()
        choice = input("Выберите год (1-2) или 0 для выхода: ")
        if choice == "1":
            current_year = 2026
            choose_month()
        elif choice == "2":
            current_year = 2027
            choose_month()
        elif choice == "0":
            print("👋 До свидания!")
            save_transactions(transactions)
            save_limits(limits)
            exit()
        else:
            print("❌ Неверный ввод.")


# ---------- ВЫБОР МЕСЯЦА ----------

def show_months():
    print("\n" + "=" * 40)
    print(f"ВЫБОР МЕСЯЦА ({current_year})")
    print("=" * 40)
    print("1.  Январь    2.  Февраль    3.  Март")
    print("4.  Апрель    5.  Май        6.  Июнь")
    print("7.  Июль      8.  Август     9.  Сентябрь")
    print("10. Октябрь   11. Ноябрь     12. Декабрь")
    print("0. Назад")
    print("=" * 40)


def choose_month():
    global current_month, limits, transactions
    while True:
        show_months()
        choice = input("Выберите месяц (1-12) или 0 для выбора года: ")
        if choice == "0":
            return
        elif choice in [str(i) for i in range(1, 13)]:
            current_month = int(choice)
            monthly_limit = calculate_rolling_limit(transactions, limits, current_year, current_month)
            print(f"📊 Лимит на {current_month}.{current_year}: {monthly_limit:.2f} руб.")
            work_with_month()
        else:
            print("❌ Неверный ввод.")


# ---------- ГЛАВНОЕ МЕНЮ ----------

def show_menu():
    print("\n" + "=" * 50)
    print(f"ПЕРСОНАЛЬНЫЙ МЕНЕДЖЕР ФИНАНСОВ - {current_month}.{current_year}")
    print("=" * 50)
    print("1.  Добавить транзакцию")
    print("2.  Показать все транзакции")
    print("3.  Показать баланс")
    print("4.  Расходы по категориям")
    print("5.  Текстовая диаграмма")
    print("6.  Прогноз остатка")
    print("7.  Установить лимит на месяц")
    print("8.  Проверить общий лимит")
    print("9.  Закрыть месяц (перенос лимита)")
    print("10. Установить лимит на категорию")
    print("11. Проверить лимиты по категориям")
    print("0.  Назад к выбору месяца")
    print("=" * 50)


def work_with_month():
    while True:
        show_menu()
        choice = input("Выберите действие (1-11) или 0: ")
        if choice == "1":
            add_transaction()
        elif choice == "2":
            show_all_transactions()
        elif choice == "3":
            show_balance()
        elif choice == "4":
            show_expenses_by_category()
        elif choice == "5":
            show_chart()
        elif choice == "6":
            show_forecast()
        elif choice == "7":
            set_monthly_limit()
        elif choice == "8":
            check_limits()
        elif choice == "9":
            close_current_month()
        elif choice == "10":
            set_category_limit()
        elif choice == "11":
            check_category_limits_wrapper()
        elif choice == "0":
            return
        else:
            print("❌ Неверный ввод.")


# ---------- ТРАНЗАКЦИИ ----------

def add_transaction():
    global transactions, current_year, current_month
    print("\n--- Добавление транзакции ---")
    print(f"📂 Доступные категории расходов: {', '.join(categories.get('расход', []))}")
    print(f"📂 Доступные категории доходов: {', '.join(categories.get('доход', []))}")

    # Обработка пробелов и регистра
    category = input("Введите категорию: ").strip().lower()

    while True:
        try:
            amount = float(input("Введите сумму (в рублях): "))
            if amount <= 0:
                print("Сумма должна быть положительной!")
                continue
            break
        except ValueError:
            print("Ошибка! Введите число.")

    trans_type = input("Тип (доход/расход): ").lower()
    while trans_type not in ["доход", "расход"]:
        print("Введите 'доход' или 'расход'")
        trans_type = input("Тип (доход/расход): ").lower()

    # Если категория не найдена — добавляем автоматически
    if category not in categories.get(trans_type, []):
        print(f"🆕 Добавлена новая категория: '{category}'")
        categories[trans_type].append(category)
        save_categories(categories)

    transaction = {
        "category": category,
        "amount": amount,
        "type": trans_type,
        "year": current_year,
        "month": current_month
    }
    transactions.append(transaction)
    save_transactions(transactions)
    print(f"✅ Добавлено: {trans_type} {category} - {amount:.2f} руб.")


def show_all_transactions():
    print(f"\n--- Все транзакции за {current_month}.{current_year} ---")
    filtered = [t for t in transactions if t.get("year") == current_year and t.get("month") == current_month]
    if not filtered:
        print("Нет транзакций.")
        return
    print(f"{'№':<5} {'Категория':<15} {'Сумма':<10} {'Тип':<10}")
    print("-" * 45)
    for i, t in enumerate(filtered, 1):
        print(f"{i:<5} {t['category']:<15} {t['amount']:<10.2f} {t['type']:<10}")


def show_balance():
    income, expense, balance = get_balance(transactions, current_year, current_month)
    print(f"\n--- Баланс за {current_month}.{current_year} ---")
    print(f"💰 Доходы: {income:.2f} руб.")
    print(f"💸 Расходы: {expense:.2f} руб.")
    print(f"📊 Баланс: {balance:.2f} руб.")


def show_expenses_by_category():
    expenses = get_expenses_by_category(transactions, current_year, current_month)
    print(f"\n--- Расходы по категориям за {current_month}.{current_year} ---")
    if not expenses:
        print("Нет расходов.")
        return
    for cat, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat:<15} {amount:.2f} руб.")
    print(f"\nИТОГО: {sum(expenses.values()):.2f} руб.")


def show_chart():
    print(build_text_chart(transactions, current_year, current_month))


def show_forecast():
    print(forecast_balance(transactions, limits, current_year, current_month))


def set_monthly_limit():
    global limits
    key = (current_year, current_month)
    try:
        limit = float(input(f"Введите лимит на {current_month}.{current_year}: "))
        if limit < 0:
            print("Лимит не может быть отрицательным.")
            return
    except ValueError:
        print("Ошибка! Введите число.")
        return
    if key not in limits:
        limits[key] = {"total": None, "categories": {}, "is_manual": False}
    limits[key]["total"] = limit
    limits[key]["is_manual"] = True
    save_limits(limits)
    print(f"✅ Лимит установлен: {limit:.2f} руб.")


def check_limits():
    key = (current_year, current_month)
    limit = limits.get(key, {}).get("total")
    if limit is None:
        print("⚠️ Лимит на этот месяц не установлен.")
        return
    expenses = sum(get_expenses_by_category(transactions, current_year, current_month).values())
    print(f"\n--- Проверка лимитов за {current_month}.{current_year} ---")
    print(f"💰 Лимит: {limit:.2f} руб.")
    print(f"💸 Потрачено: {expenses:.2f} руб.")
    pct = (expenses / limit) * 100 if limit > 0 else 0
    print(f"📈 Использовано: {pct:.1f}%")
    if pct >= 100:
        print("🔴 ВНИМАНИЕ! Лимит превышен!")
    elif pct >= 80:
        print("🟡 Внимание! Лимит почти исчерпан.")
    else:
        print("🟢 Лимит в норме.")


def close_current_month():
    """Закрыть текущий месяц и перенести лимит"""
    global limits
    print("\n" + "=" * 50)
    print("ЗАКРЫТИЕ МЕСЯЦА")
    print("=" * 50)

    count = sum(1 for t in transactions if t.get("year") == current_year and t.get("month") == current_month)
    if count == 0:
        print("⚠️ Нет транзакций за этот месяц. Закрытие невозможно.")
        return

    confirm = input(f"Вы действительно хотите закрыть {current_month}.{current_year}? (да/нет): ").lower()
    if confirm != "да":
        print("❌ Закрытие отменено.")
        return

    result = close_month(transactions, limits, current_year, current_month)
    print(result)


# ---------- ЛИМИТЫ ПО КАТЕГОРИЯМ ----------

def set_category_limit():

    global limits
    key = (current_year, current_month)

    print(f"\n--- Установка лимита на категорию ({current_month}.{current_year}) ---")

    expense_categories = categories.get("расход", [])
    if not expense_categories:
        print("⚠️ Нет категорий расходов. Сначала добавьте категории через добавление транзакции.")
        return

    print(f"📂 Доступные категории расходов: {', '.join(expense_categories)}")

    category = input("Введите название категории: ").strip().lower()

    if category not in expense_categories:
        print(f"⚠️ Категория '{category}' не найдена в списке расходов.")
        return

    current_limit = get_category_limit(limits, current_year, current_month, category)
    if current_limit is not None:
        print(f"📌 Текущий лимит на '{category}': {current_limit:.2f} руб.")

    try:
        limit = float(input(f"Введите лимит на категорию '{category}' (в рублях): "))
        if limit < 0:
            print("Лимит не может быть отрицательным.")
            return
    except ValueError:
        print("Ошибка! Введите число.")
        return

    if key not in limits:
        limits[key] = {"total": None, "categories": {}, "is_manual": False}
    limits[key]["categories"][category] = limit

    save_limits(limits)
    print(f"✅ Лимит на категорию '{category}' установлен: {limit:.2f} руб.")


def check_category_limits_wrapper():

    print(f"\n--- Проверка лимитов по категориям за {current_month}.{current_year} ---")

    warnings = check_category_limits(transactions, limits, current_year, current_month)

    key = (current_year, current_month)
    if key in limits and "categories" in limits[key]:
        print("\n📋 Установленные лимиты по категориям:")
        expenses = get_expenses_by_category(transactions, current_year, current_month)
        for cat, limit in limits[key]["categories"].items():
            spent = expenses.get(cat, 0)
            status = "✅" if spent <= limit else "🔴"
            print(f"   {status} {cat}: {spent:.2f} / {limit:.2f} руб.")

    if not warnings:
        print("\n✅ Все лимиты по категориям в норме.")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРЕВЫШЕНИЯ:")
        for w in warnings:
            print(w)


# ---------- ЗАПУСК ----------

def main():
    global transactions, categories, limits
    print("=" * 50)
    print("ПЕРСОНАЛЬНЫЙ МЕНЕДЖЕР ФИНАНСОВ")
    print("=" * 50)
    transactions = load_transactions()
    categories = load_categories()
    limits = load_limits()
    print(f"✅ Загружено: {len(transactions)} транзакций")
    choose_year()


if __name__ == "__main__":
    main()