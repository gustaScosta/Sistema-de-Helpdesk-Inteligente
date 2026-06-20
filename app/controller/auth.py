# app/controller/auth.py
from flask import Blueprint, request, jsonify, abort, session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login → autentica usuário.
    Espera JSON: { "username": "...", "password": "..." }
    (Para fins de estudo a senha está em texto plano; em produção use hash.)
    """
    data = request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        abort(400, description="username e password são obrigatórios")

    from ..models.user import User
    user = User.query.filter_by(username=data["username"]).first()
    if user is None or user.password != data["password"]:
        abort(401, description="Credenciais inválidas")

    # Armazena o id do usuário na sessão Flask (cookie de navegador)
    session["user_id"] = user.id
    return jsonify({"msg": "login ok", "user_id": user.id}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    POST /auth/logout → encerra a sessão.
    Remove o `user_id` da sessão.
    """
    session.pop("user_id", None)
    return jsonify({"msg": "logout ok"}), 200