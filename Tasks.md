# TASKS.md — Оценка Pro

## 🟡 В РАБОТЕ

### TASK-001: Инициализация проекта на VPS
- **Статус:** 🟢 завершено
- **Агент:** Claude Code
- **Фаза:** инфра
- **Описание:**
  1. Создать структуру /root/ocenka-pro/
  2. Скопировать файлы из Fedresurs Pro (rosreestr_client.py, checko_client.py, resource_monitor.py, base.py)
  3. Адаптировать base.py (ocenka_db вместо fedresurs_db)
  4. Создать .gitignore, .env.example, requirements.txt
  5. Инициализировать git, первый коммит
- **Критерий:** `ls /root/ocenka-pro/src/services/` показывает rosreestr_client.py и checko_client.py

### TASK-002: Docker + FastAPI каркас
- **Статус:** 🟢 завершено
- **Агент:** Claude Code
- **Фаза:** инфра
- **Зависит от:** TASK-001
- **Описание:**
  1. docker-compose.yml (ocenka-app на :8001, ocenka-db на PostgreSQL)
  2. Dockerfile для Python 3.11
  3. src/main.py — минимальный FastAPI (/docs работает)
  4. Alembic init + первая миграция (пустая)
- **Критерий:** `curl http://localhost:8001/docs` возвращает Swagger UI

### TASK-003: Схема БД (ядро)
- **Статус:** 🟢 завершено
- **Агент:** Qwen3 Coder
- **Фаза:** инфра
- **Зависит от:** TASK-002
- **Описание:**
  Создать models.py с ключевыми таблицами:
  - users, companies
  - appraisal_orders (задание по ФСО IV)
  - appraisal_reports (статусы: черновик → расчёт → проверка → финал)
  - objects (тип: недвижимость/МиО/НМА/бизнес/дебиторка)
  - npa_registry (НПА с редакциями)
  - regional_tax_rates
  - market_data
  Создать миграцию Alembic.
- **Критерий:** `alembic upgrade head` без ошибок, таблицы в БД

### TASK-004: Ревью скрипта ОП.01 (npa_engine.py)
- **Статус:** 🟢 завершено
- **Агент:** — (ревью в чате Claude Opus)
- **Фаза:** ОП.01
- **Зависит от:** TASK-002
- **Описание:** @ui приносит скрипт от Gemini → ревью → финальная версия → ТЗ агенту
- **Критерий:** npa_engine.py в src/modules/npa/, импортируется без ошибок

### TASK-005: Ревью скрипта ОП.02 (market_context.py)
- **Статус:** 🟢 завершено
- **Агент:** — (ревью в чате Claude Opus)
- **Фаза:** ОП.02
- **Зависит от:** TASK-002
- **Описание:** @ui приносит скрипт от Gemini → ревью → финальная версия → ТЗ агенту
- **Критерий:** market_context.py в src/modules/market/, импортируется без ошибок

---

## 🔴 БЭКЛОГ (по мере необходимости)

### TASK-006: Настроить nginx для ocenka-pro
- **Фаза:** инфра
- **Описание:** Отдельный server block, порт :8001 → контейнер

### TASK-007: GitHub репозиторий
- **Фаза:** инфра
- **Описание:** Создать repo, настроить remote, первый push

### TASK-008: Skills / CLAUDE.md для агентов Kilo Code
- **Фаза:** инфра
- **Описание:** Файлы конфигурации для Qwen, DeepSeek, Kimi, MiniMax в Kilo Code

---

## ✅ ЗАВЕРШЕНО

### TASK-012: Размещение модуля ОП.06 (calc/ahp_engine)
- **Статус:** 🟢 завершено
- **Дата:** 2026-03-12
- **Агент:** Qwen3 Coder
- **Фаза:** ОП.06
- **Описание:**
  1. Добавить EvaluationApproach в src/common/types.py
  2. Создать src/modules/calc/ahp_engine.py
  3. Проверка импортов и тестов
- **Критерий:** `from src.modules.calc.ahp_engine import AHPEngine` работает

### TASK-011: Размещение модуля ОП.05 (tax)
- **Статус:** 🟢 завершено
- **Дата:** 2026-03-12
- **Агент:** Qwen3 Coder
- **Фаза:** ОП.05
- **Описание:**
  1. Создать src/modules/tax/calculator.py
  2. Создать src/modules/tax/compliance.py
  3. Проверка импортов и тестов
- **Критерий:** `from src.modules.tax.calculator import TaxCalculator` работает

### TASK-010: Размещение модуля ОП.04 (economic_analysis)
- **Статус:** 🟢 завершено
- **Дата:** 2026-03-12
- **Агент:** Qwen3 Coder
- **Фаза:** ОП.04
- **Описание:**
  1. Создать src/modules/finance/economic_analysis.py
  2. Проверка импортов и тестов
- **Критерий:** `from src.modules.finance.economic_analysis import EconomicAnalysisEngine` работает

### TASK-009: Размещение модуля ОП.03 (finance)
- **Статус:** 🟢 завершено
- **Дата:** 2026-03-12
- **Агент:** Qwen3 Coder
- **Фаза:** ОП.03
- **Описание:**
  1. Создать src/modules/finance/finance_engine.py
  2. Создать src/modules/finance/compliance.py
  3. Проверка импортов и тестов
- **Критерий:** `from src.modules.finance.finance_engine import FinanceEngine` работает

### TASK-003: Схема БД (ядро)
- **Статус:** 🟢 завершено
- **Дата:** 2026-03-12
- **Агент:** Qwen3 Coder
- **Фаза:** инфра
- **Описание:**
  1. Создать models.py с 8 таблицами
  2. Alembic миграция применена
- **Критерий:** `alembic upgrade head` без ошибок, 9 таблиц в БД


TASK-012 выполнена. ✅

Созданные/обновлённые файлы:

Файл	Описание
src/common/types.py	Добавлен EvaluationApproach (3 подхода к оценке)
src/modules/calc/ahp_engine.py	AHPEngine: метод анализа иерархий Саати
Функции модуля ОП.06 (МАИ/AHP):

AHPEngine:

calculate_priority_vector() — вектор приоритетов (среднее геометрическое)
check_consistency() — проверка согласованности (ОС ≤ 0.10)
reconcile() — финальный синтез: согласование 3 подходов к оценке
Результаты теста (торговый павильон ЗАО «МИФ»):

Веса подходов:
  Затратный подход: 0.1485
  Сравнительный подход: 0.4534
  Доходный подход: 0.3982
ОС: 0.003 (согласовано)
Итоговая стоимость: 17 719 006,39 руб.
Проверка:

✅ Импорт EvaluationApproach работает
✅ Импорт AHPEngine работает
✅ Тесты прошли
✅ Git push выполнен
Обновлено:

TASKS.md — TASK-012 добавлен в ✅ ЗАВЕРШЕНО
Claude.md — добавлен ОП.06 в готовые модули