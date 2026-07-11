# storage.py - работа с CSV-файлами

import os
import csv


def get_data_path(filename):
    """Вернуть правильный путь к файлу в папке data"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, "data", filename)


# ---------- ТРАНЗАКЦИИ ----------

def load_transactions():
    """Загрузить транзакции из CSV"""
    filename = get_data_path("transactions.csv")
    transactions = []
    try:
        with open(filename, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append({
                    "category": row["category"],
                    "amount": float(row["amount"]),
                    "type": row["type"],
                    "year": int(row["year"]),
                    "month": int(row["month"])
                })
        print("📂 Транзакции загружены.")
    except FileNotFoundError:
        print("📄 Файл транзакций не найден. Начинаем с пустого списка.")
    return transactions


def save_transactions(transactions):
    """Сохранить транзакции в CSV"""
    filename = get_data_path("transactions.csv")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["category", "amount", "type", "year", "month"])
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)
    print("💾 Транзакции сохранены.")


# ---------- КАТЕГОРИИ ----------

def load_categories():
    """Загрузить категории из CSV"""
    filename = get_data_path("categories.csv")
    categories = {"доход": [], "расход": []}
    try:
        with open(filename, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories[row["type"]].append(row["name"])
        print("📂 Категории загружены.")
    except FileNotFoundError:
        print("📄 Файл категорий не найден. Создаём категории по умолчанию.")
        categories = {
            "доход": ["зарплата", "премия", "подарок", "фриланс"],
            "расход": ["еда", "транспорт", "аренда", "развлечения", "коммунальные", "одежда"]
        }
        save_categories(categories)
    return categories


def save_categories(categories):
    """Сохранить категории в CSV"""
    filename = get_data_path("categories.csv")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "type"])
        writer.writeheader()
        for cat_type, names in categories.items():
            for name in names:
                writer.writerow({"name": name, "type": cat_type})
    print("💾 Категории сохранены.")


# ---------- ЛИМИТЫ ----------

def load_limits():
    """Загрузить лимиты из CSV"""
    filename = get_data_path("limits.csv")
    limits = {}
    try:
        with open(filename, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (int(row["year"]), int(row["month"]))
                if key not in limits:
                    limits[key] = {"total": None, "categories": {}, "is_manual": False}
                if row["category"] == "":
                    limits[key]["total"] = float(row["limit_amount"])
                    limits[key]["is_manual"] = row.get("is_manual", "False").lower() == "true"
                else:
                    limits[key]["categories"][row["category"]] = float(row["limit_amount"])
        print("📂 Лимиты загружены.")
    except FileNotFoundError:
        print("📄 Файл лимитов не найден. Начинаем с пустого словаря.")
    return limits


def save_limits(limits):
    """Сохранить лимиты в CSV"""
    filename = get_data_path("limits.csv")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["year", "month", "category", "limit_amount", "is_manual"])
        writer.writeheader()
        for (year, month), data in limits.items():
            if data.get("total") is not None:
                writer.writerow({
                    "year": year,
                    "month": month,
                    "category": "",
                    "limit_amount": data["total"],
                    "is_manual": str(data.get("is_manual", False))
                })
            for cat, amount in data.get("categories", {}).items():
                writer.writerow({
                    "year": year,
                    "month": month,
                    "category": cat,
                    "limit_amount": amount,
                    "is_manual": "True"
                })
    print("💾 Лимиты сохранены.")