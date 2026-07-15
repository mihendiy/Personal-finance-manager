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
.
├── src/
│ ├── init.py
│ ├── main.py 
│ ├── storage.py 
│ └── analytics.py 
├── tests/
│ ├── init.py
│ ├── test_analytics.py 
│ └── test_integration.py 
├── data/
│ ├── transactions.csv 
│ ├── categories.csv 
│ ├── limits.csv 
│ └── piggy_bank.csv 
├── Dockerfile
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md

text

---

## Установка и запуск

### Локально

```bash
# 1. Клонировать репозиторий
git clone https://github.com/mihendiy/finance-manager.git
cd finance-manager

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить
python src/main.py
В Docker
bash
# Собрать образ
docker build -t finance-manager .

# Запустить
docker run --rm finance-manager

# Запустить с монтированием папки data (для сохранения данных)
docker run --rm -v "$(pwd)/data:/app/data" finance-manager
Параметры запуска
Параметр	Описание	По умолчанию
—	Программа запускается без аргументов командной строки	—
Запуск тестов
bash
python -m pytest tests/ -v
Ожидаемый результат:

text
tests/test_analytics.py ............ [70%]
tests/test_integration.py ....      [100%]
==================== 17 passed in 0.08s ====================
Зависимости
Python ≥ 3.10

pytest == 7.4.0