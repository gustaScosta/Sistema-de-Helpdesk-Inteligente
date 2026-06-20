# app/main.py
from flask import Flask
from .models import db
from .controller import register_controllers

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "super-secret-key"

    db.init_app(app)
    register_controllers(app)

    # Cria as tabelas antes da primeira requisição
    @app.before_request
    def create_tables():
        db.create_all()

    return app

if __name__ == "__main__":
    create_app().run(debug=True)