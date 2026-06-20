# app/main.py
from flask import Flask
from .models import db                    # objeto SQLAlchemy
from .controller import register_controllers   # função que criamos

def create_app():
    app = Flask(__name__)

    # Configurações do Flask – você pode mover para .env depois
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "super-secret-key"   # troque por algo aleatório!

    # Inicializa o ORM
    db.init_app(app)

    # Registra as rotas do controller
    register_controllers(app)

    # Cria as tabelas na primeira requisição (ou ao iniciar o app)
    @app.before_first_request
    def create_tables():
        db.create_all()

    return app

if __name__ == "__main__":
    create_app().run(debug=True)