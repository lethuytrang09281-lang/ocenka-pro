# ОЦЕНКА PRO — СОСТОЯНИЕ

## Дата последнего обновления: 2026-03-12

## ✅ ЧТО РАБОТАЕТ
- [x] Инициализация проекта (TASK-001)
- [x] Docker + FastAPI каркас (TASK-002)
- [x] Схема БД: 8 таблиц + Alembic (TASK-003)
- [x] Модуль ОП.01 (npa): legal_logic.py, compliance.py
- [x] Модуль ОП.02 (market): market_context.py, compliance.py
- [x] Модуль ОП.03 (finance): finance_engine.py, compliance.py

## ❌ ЧТО СЛОМАНО
(пусто — проект новый)

## 🔄 ТЕКУЩАЯ ЗАДАЧА выполено
TASK-001: Инициализация проекта на VPS

## ➡️ СЛЕДУЮЩАЯ ЗАДАЧА выполено
TASK-002: Docker (app + db) + FastAPI каркас

## 📚 ТЕКУЩАЯ ФАЗА
ОП.01 + ОП.02 + ОП.03 — первые 3 дисциплины пройдены, модули размещены

## 📝 ЛОГ РЕШЁННЫХ ПРОБЛЕМ
(пусто — проект новый)

---

## 🖥️ ИНФРАСТРУКТУРА

```
VPS:            root@157.22.231.149 (тот же что Fedresurs Pro)
Проект:         /root/ocenka-pro/
БД:             ocenka_db (PostgreSQL, user: postgres)
Docker:         ocenka-app, ocenka-db
GitHub:         https://github.com/lethuytrang09281-lang/ocenka-pro
```

## 📁 СТРУКТУРА ПРОЕКТА

```
/root/ocenka-pro/
├── Claude.md
├── TASKS.md
├── ROADMAP.md
├── PROJECT.md
├── STATE.md
├── .planning/
│   ├── phase-OP01-npa/
│   └── phase-OP02-market/
├── src/
│   ├── main.py
│   ├── database/
│   │   ├── base.py              ← из Fedresurs Pro
│   │   └── models.py
│   ├── modules/
│   │   ├── npa/
│   │   ├── market/
│   │   ├── finance/
│   │   ├── tax/
│   │   ├── calc/
│   │   ├── report/
│   │   ├── realty/
│   │   ├── cost/
│   │   ├── equipment/
│   │   ├── intangible/
│   │   ├── business/
│   │   ├── bankruptcy/
│   │   ├── receivables/
│   │   ├── quick/
│   │   ├── cadastral/
│   │   └── benchmark/
│   ├── api/
│   ├── services/
│   │   ├── rosreestr_client.py  ← из Fedresurs Pro
│   │   ├── checko_client.py     ← из Fedresurs Pro
│   │   ├── cbr_client.py        ← написать
│   │   └── rosstat_client.py    ← написать
│   └── utils/
│       └── resource_monitor.py  ← из Fedresurs Pro
├── templates/
├── data/
├── design-system/
├── alembic/
├── docker-compose.yml
├── requirements.txt
├── .env
└── .gitignore
```

## 🔑 API (все бесплатные на старте)

```
Росреестр PKK   — rosreestr_client.py (из Fedresurs, безлимит)
Checko          — checko_client.py (из Fedresurs, ключ в .env)
ЦБ РФ           — cbr_client.py (написать, бесплатно)
Росстат/ЕМИСС   — rosstat_client.py (написать, бесплатно)
ФНС bo.nalog.ru — (этап 2)
ФССП            — (этап 2)
ЕФРСБ           — (этап 2)
```

## ⚠️ ВАЖНО

1. БД — `ocenka_db`, НЕ `fedresurs_db`
2. Это ОТДЕЛЬНЫЙ продукт от Fedresurs Pro
3. Общий VPS, но разные контейнеры, БД, репозитории
4. Порт FastAPI — :8001 (Fedresurs на :8000)
5. Модули заполняются по мере прохождения курса @ui