from fastapi import FastAPI
from .auth import auth_router
from .ticket import ticket_router

def register_controllers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(ticket_router, prefix="/tickets", tags=["tickets"])