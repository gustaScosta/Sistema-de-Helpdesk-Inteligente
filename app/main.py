# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.models import Base, engine
from .controller import register_controllers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria todas as tabelas no banco ao iniciar a aplicacao.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SmartHelp - Helpdesk Inteligente",
    description="API REST para gerenciamento de chamados, usuarios e equipamentos.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_controllers(app)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "app": "SmartHelp API"}