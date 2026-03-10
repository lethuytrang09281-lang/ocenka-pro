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
