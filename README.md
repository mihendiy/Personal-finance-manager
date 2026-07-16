# Персональный менеджер финансов — учебная ознакомительная практика 2026

**Студент:** Косенков М.А.  
**Группа:** БИН-24-1  
**Вариант:** Б-01 — Персональный менеджер финансов  
**Язык:** Python 3.11

---

## Описание

Консольное приложение для учёта доходов и расходов по категориям. Реализованы категоризация транзакций, расчёт скользящего бюджета, лимиты по категориям с предупреждениями, текстовая диаграмма структуры расходов, прогноз остатка на конец периода, экспорт в CSV, а также автоматическое накопление средств в «Копилке».

---

## Структура репозитория

```
finance-manager/
├── src/
│   ├── __init__.py
│   ├── main.py             # точка входа, CLI-меню
│   ├── storage.py          # работа с CSV-файлами
│   └── analytics.py        # алгоритмическое ядро
├── tests/
│   ├── __init__.py
│   ├── test_analytics.py   # юнит-тесты алгоритмов
│   └── test_integration.py # интеграционные тесты
├── data/
│   ├── transactions.csv
│   ├── categories.csv
│   ├── limits.csv
│   └── piggy_bank.csv
├── Dockerfile
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```
## Установка и запуск
### Локально
```
# 1. Клонировать репозиторий
git clone https://github.com/mihendiy/Personal-finance-manager.git

# 2.Зайти в директорию с проектом
cd Personal-finance-manager

# 3. Установить зависимости
pip install -r requirements.txt

# 3. Запустить
python src/main.py
```
### В Docker 
```
1. Собрать образ
docker build -t finance-manager .

# 2. Запустить
docker run -it --rm finance-manager

# 3. Запустить с монтированием папки data (для сохранения изменений в файлах данных)
docker run -it --rm -v "%cd%/data:/app/data" finance-manager
```
## Запуск тестов

---
```
python -m pytest tests/ -v
```
## Зависимости

---
Python ≥ 3.10

pytest == 7.4.0
