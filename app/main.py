from fastapi import FastAPI
from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router

app = FastAPI(
    title="Healing Score Agent",
    version="0.1.0",
    description="Supportive dialogue and risk scoring prototype"
)

app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
def root():
    return {"message": "Healing Score Agent is running"}