from storage import (
    load_transactions, save_transactions,
    load_categories, save_categories,
    load_limits, save_limits,
    load_piggy_bank, save_piggy_bank
)
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

YEARS = [2026, 2027]

transactions = []
categories = {}
limits = {}
current_year = 2026
current_month = 1
piggy_balance = 0.0


# ---------- ВЫБОР ГОДА ----------

def show_years():
    print("\n" + "=" * 40)
    print("ВЫБОР ГОДА")
    print("=" * 40)
    for i, year in enumerate(YEARS, 1):
        print(f"{i}. {year}")
    print("0. Выход")
    print("=" * 40)


def choose_year():
    global current_year
    while True:
        show_years()
        choice = input("Выберите год (1-2) или 0 для выхода: ")
        if choice == "1":
            current_year = YEARS[0]
            choose_month()
        elif choice == "2":
            current_year = YEARS[1]
            choose_month()
        elif choice == "0":
            print("👋 До свидания!")
            save_transactions(transactions)
            save_limits(limits)
            save_piggy_bank(piggy_balance)
            return
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
    print(f"📊 ПЕРСОНАЛЬНЫЙ МЕНЕДЖЕР ФИНАНСОВ - {current_month}.{current_year}")
    print("=" * 50)

    print("\n📌 ОСНОВНЫЕ ДЕЙСТВИЯ")
    print("  1.  Добавить транзакцию")
    print("  2.  Показать все транзакции")

    print("\n📊 АНАЛИТИКА")
    print("  3.  Показать баланс")
    print("  4.  Текстовая диаграмма")
    print("  5.  Прогноз остатка")

    print("\n💰 БЮДЖЕТ")
    print("  6.  Установить лимит на месяц")
    print("  7.  Проверить общий лимит")
    print("  8.  Установить лимит на категорию")
    print("  9.  Проверить лимиты по категориям")

    print("\n🏦 КОПИЛКА")
    print("  10. Показать / пополнить / снять")

    print("\n📦 ЗАКРЫТИЕ")
    print("  11. Закрыть месяц")

    print("\n0.  Назад к выбору месяца")
    print("=" * 50)


def work_with_month():
    global piggy_balance
    piggy_balance = load_piggy_bank()

    while True:
        show_menu()
        choice = input("Выберите действие (0-11): ")
        if choice == "1":
            add_transaction()
        elif choice == "2":
            show_all_transactions()
        elif choice == "3":
            show_balance()
        elif choice == "4":
            show_chart()
        elif choice == "5":
            show_forecast()
        elif choice == "6":
            set_monthly_limit()
        elif choice == "7":
            check_limits()
        elif choice == "8":
            set_category_limit()
        elif choice == "9":
            check_category_limits_wrapper()
        elif choice == "10":
            piggy_bank_menu()
        elif choice == "11":
            close_current_month()
        elif choice == "0":
            save_piggy_bank(piggy_balance)
            return
        else:
            print("❌ Неверный ввод.")


# ---------- КОПИЛКА (ПОДМЕНЮ) ----------

def piggy_bank_menu():
    while True:
        print("\n" + "=" * 50)
        print("🏦 КОПИЛКА")
        print("=" * 50)
        print(f"💰 Текущий баланс копилки: {piggy_balance:.2f} руб.")
        print("=" * 50)
        print("1. Положить в копилку")
        print("2. Взять из копилки")
        print("3. Показать баланс копилки")
        print("0. Назад")
        print("=" * 50)

        choice = input("Выберите действие (0-3): ")
        if choice == "1":
            add_to_piggy()
        elif choice == "2":
            take_from_piggy()
        elif choice == "3":
            print(f"\n🐖 В копилке: {piggy_balance:.2f} руб.")
        elif choice == "0":
            return
        else:
            print("❌ Неверный ввод.")


# ---------- ТРАНЗАКЦИИ ----------

def add_transaction():
    global transactions, current_year, current_month
    print("\n--- Добавление транзакций ---")

    while True:
        print(f"📂 Доступные категории расходов: {', '.join(categories.get('расход', []))}")
        print(f"📂 Доступные категории доходов: {', '.join(categories.get('доход', []))}")

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

        more = input("\nДобавить ещё транзакцию? (да/нет): ").lower()
        if more != "да":
            print("✅ Возврат в меню.")
            return


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


def show_chart():
    print(build_text_chart(transactions, current_year, current_month))


def show_forecast():
    print(forecast_balance(transactions, limits, current_year, current_month))


# ---------- ЛИМИТЫ ----------

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


# ---------- ЛИМИТЫ ПО КАТЕГОРИЯМ ----------

def set_category_limit():
    global limits
    key = (current_year, current_month)

    print(f"\n--- Установка лимита на категорию ({current_month}.{current_year}) ---")

    expense_categories = categories.get("расход", [])
    if not expense_categories:
        print("⚠️ Нет категорий расходов.")
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


# ---------- ЗАКРЫТИЕ МЕСЯЦА ----------

def close_current_month():
    global limits, piggy_balance
    print("\n" + "=" * 50)
    print("📦 ЗАКРЫТИЕ МЕСЯЦА")
    print("=" * 50)

    # Проверяем, есть ли транзакции
    count = sum(1 for t in transactions if t.get("year") == current_year and t.get("month") == current_month)
    if count == 0:
        print("⚠️ Нет транзакций за этот месяц. Закрытие невозможно.")
        return

    # Проверяем, установлен ли лимит
    key = (current_year, current_month)
    if limits.get(key, {}).get("total") is None:
        print("⚠️ Лимит на этот месяц не установлен. Сначала установите лимит.")
        return

    # Подтверждение
    confirm = input(f"Вы действительно хотите закрыть {current_month}.{current_year}? (да/нет): ").lower()
    if confirm != "да":
        print("❌ Закрытие отменено.")
        return

    # Автоматическое закрытие
    result, piggy_balance = close_month_auto(
        transactions, limits, piggy_balance, current_year, current_month
    )
    print(result)


# ---------- КОПИЛКА ----------

def add_to_piggy():
    """Положить деньги в копилку (списывая с текущего баланса)"""
    global piggy_balance, transactions, current_year, current_month

    print("\n" + "=" * 50)
    print("🏦 ПОПОЛНЕНИЕ КОПИЛКИ")
    print("=" * 50)

    total_income = 0
    total_expense = 0
    for t in transactions:
        if t["type"] == "доход":
            total_income += t["amount"]
        else:
            total_expense += t["amount"]
    current_balance = total_income - total_expense

    print(f"💰 Ваш текущий баланс: {current_balance:.2f} руб.")
    print(f"🐖 В копилке сейчас: {piggy_balance:.2f} руб.")

    if current_balance <= 0:
        print("❌ У вас нет свободных средств для пополнения копилки!")
        return

    try:
        amount = float(input("Введите сумму для пополнения: "))
        if amount <= 0:
            print("❌ Сумма должна быть положительной!")
            return
    except ValueError:
        print("❌ Ошибка! Введите число.")
        return

    if amount > current_balance:
        print(f"❌ Недостаточно средств! У вас на балансе {current_balance:.2f} руб.")
        return

    transaction = {
        "category": "копилка",
        "amount": amount,
        "type": "расход",
        "year": current_year,
        "month": current_month
    }
    transactions.append(transaction)
    save_transactions(transactions)

    piggy_balance += amount
    save_piggy_bank(piggy_balance)

    print(f"✅ В копилку добавлено: {amount:.2f} руб.")
    print(f"💰 Новый баланс: {current_balance - amount:.2f} руб.")
    print(f"🐖 В копилке: {piggy_balance:.2f} руб.")


def take_from_piggy():
    """Взять деньги из копилки (добавляя к балансу)"""
    global piggy_balance, transactions, current_year, current_month

    print("\n" + "=" * 50)
    print("🏦 СНЯТИЕ ИЗ КОПИЛКИ")
    print("=" * 50)

    print(f"🐖 В копилке: {piggy_balance:.2f} руб.")

    if piggy_balance == 0:
        print("❌ Копилка пуста!")
        return

    try:
        amount = float(input("Введите сумму для снятия: "))
        if amount <= 0:
            print("❌ Сумма должна быть положительной!")
            return
    except ValueError:
        print("❌ Ошибка! Введите число.")
        return

    if amount > piggy_balance:
        print(f"❌ В копилке только {piggy_balance:.2f} руб.")
        return

    piggy_balance -= amount
    save_piggy_bank(piggy_balance)

    transaction = {
        "category": "копилка",
        "amount": amount,
        "type": "доход",
        "year": current_year,
        "month": current_month
    }
    transactions.append(transaction)
    save_transactions(transactions)

    total_income = 0
    total_expense = 0
    for t in transactions:
        if t["type"] == "доход":
            total_income += t["amount"]
        else:
            total_expense += t["amount"]
    current_balance = total_income - total_expense

    print(f"✅ Из копилки снято: {amount:.2f} руб.")
    print(f"💰 Новый баланс: {current_balance:.2f} руб.")
    print(f"🐖 В копилке осталось: {piggy_balance:.2f} руб.")


# ---------- ЗАПУСК ----------

def main():
    global transactions, categories, limits, piggy_balance
    print("=" * 50)
    print("📊 ПЕРСОНАЛЬНЫЙ МЕНЕДЖЕР ФИНАНСОВ")
    print("=" * 50)
    transactions = load_transactions()
    categories = load_categories()
    limits = load_limits()
    piggy_balance = load_piggy_bank()
    print(f"✅ Загружено: {len(transactions)} транзакций")
    print(f"🏦 В копилке: {piggy_balance:.2f} руб.")
    choose_year()
    print("👋 Программа завершена.")


if __name__ == "__main__":
    main()