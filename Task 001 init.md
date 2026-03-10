# ЗАДАЧА Claude Code — TASK-001: Инициализация проекта Оценка Pro

## Контекст
Создаём новый проект на том же VPS где живёт Fedresurs Pro.
Отдельная директория, отдельная БД, отдельные контейнеры.
Часть файлов копируем из Fedresurs Pro (API-клиенты, утилиты).

## Что сделать

### 1. Создать структуру директорий

```bash
mkdir -p /root/ocenka-pro/{src/{database,modules/{npa,market,finance,tax,calc,report,realty,cost,equipment,intangible,business,bankruptcy,receivables,quick,cadastral,benchmark},api,services,utils},templates,data,design-system,alembic,.planning/{phase-OP01-npa,phase-OP02-market}}

touch /root/ocenka-pro/src/__init__.py
touch /root/ocenka-pro/src/database/__init__.py
touch /root/ocenka-pro/src/modules/__init__.py
touch /root/ocenka-pro/src/api/__init__.py
touch /root/ocenka-pro/src/services/__init__.py
touch /root/ocenka-pro/src/utils/__init__.py

# __init__.py для каждого модуля
for dir in npa market finance tax calc report realty cost equipment intangible business bankruptcy receivables quick cadastral benchmark; do
  touch /root/ocenka-pro/src/modules/$dir/__init__.py
done
```

### 2. Скопировать файлы из fedr

```bash
# API клиенты (копия, не симлинк)
cp /root/fedr/src/services/rosreestr_client.py /root/ocenka-pro/src/services/
cp /root/fedr/src/services/checko_client.py /root/ocenka-pro/src/services/

# Утилиты
cp /root/fedr/src/utils/resource_monitor.py /root/ocenka-pro/src/utils/

# Database base (будет адаптирован)
cp /root/fedr/src/database/base.py /root/ocenka-pro/src/database/
```

### 3. Адаптировать base.py

В `/root/ocenka-pro/src/database/base.py`:
- Заменить `fedresurs_db` → `ocenka_db` в DATABASE_URL
- Убрать лишние импорты если есть
- Убедиться что engine и session factory работают

### 4. Создать requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-dotenv==1.0.1
httpx==0.27.0
aiohttp==3.9.3
numpy==1.26.4
pandas==2.2.0
python-docx==1.1.0
pydantic==2.6.0
pydantic-settings==2.1.0
```

### 5. Создать .env.example

```
DATABASE_URL=postgresql://postgres:postgres@ocenka-db:5432/ocenka_db
CHECKO_API_KEY=your_key_here
APP_PORT=8001
DEBUG=true
```

### 6. Создать .gitignore

```
__pycache__/
*.pyc
.env
data/
*.egg-info/
.venv/
```

### 7. Создать docker-compose.yml

```yaml
version: '3.8'

services:
  ocenka-app:
    build: .
    container_name: ocenka-app
    ports:
      - "8001:8001"
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - ocenka-db
    restart: unless-stopped

  ocenka-db:
    image: postgres:15
    container_name: ocenka-db
    environment:
      POSTGRES_DB: ocenka_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - ocenka_pgdata:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    restart: unless-stopped

volumes:
  ocenka_pgdata:
```

ВАЖНО: PostgreSQL на порту 5433 снаружи (5432 занят Fedresurs).

### 8. Создать Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

### 9. Создать src/main.py

```python
from fastapi import FastAPI

app = FastAPI(
    title="Оценка Pro",
    description="SaaS-платформа для автоматизации отчётов об оценке",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"status": "ok", "project": "ocenka-pro"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 10. Создать .env (на основе .env.example)

```bash
cp /root/ocenka-pro/.env.example /root/ocenka-pro/.env
# Вставить реальный CHECKO_API_KEY из Fedresurs:
grep CHECKO_API_KEY /root/fedr/.env >> /root/ocenka-pro/.env
```

### 11. Скопировать файлы состояния

Файлы Claude.md, TASKS.md, ROADMAP.md будут предоставлены @ui.

### 12. Git init

```bash
cd /root/ocenka-pro
git init
git add -A
git commit -m "init: project structure, Docker, FastAPI skeleton"
```

### 13. Запуск и проверка

```bash
cd /root/ocenka-pro
docker-compose up -d --build
```

## Как проверить

```bash
# Контейнеры запущены
docker ps | grep ocenka

# FastAPI отвечает
curl -s http://localhost:8001/ | python3 -m json.tool

# Swagger UI
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs

# БД доступна
docker exec ocenka-db psql -U postgres -d ocenka_db -c "SELECT 1;"

# Файлы из Fedresurs на месте
ls -la /root/ocenka-pro/src/services/rosreestr_client.py
ls -la /root/ocenka-pro/src/services/checko_client.py
ls -la /root/ocenka-pro/src/utils/resource_monitor.py
```

## НЕ ТРОГАТЬ
- /root/fedr/ — Fedresurs Pro, другой проект
- Порт 8000 — занят Fedresurs Pro
- Порт 5432 — занят Fedresurs PostgreSQL