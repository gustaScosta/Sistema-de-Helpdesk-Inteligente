from fastapi import FastAPI
from .auth import auth_router
from .ticket import ticket_router
from .user import user_router
from .equipment import equipment_router

def register_controllers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(ticket_router, prefix="/tickets", tags=["tickets"])
    app.include_router(user_router, prefix="/users", tags=["users"])
    app.include_router(equipment_router, prefix="/equipments", tags=["equipments"])