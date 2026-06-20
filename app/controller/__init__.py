from flask import Flask
from .ticket import ticket_bp

from .auth import auth_bp

def registrer_controler(app: Flask) -> None:
    app.register_blueprint(ticket_bp, url_prefix="/tickets")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    