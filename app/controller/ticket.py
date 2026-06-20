# app/controller/ticket.py
from flask import Blueprint, jsonify, request, abort
from ..models.ticket import Ticket, db                # modelo SQLAlchemy e objeto db
from ..models.user import User                      # para validar o criador

# Cria um blueprint chamado "ticket". O nome interno não precisa ser único na URL.
ticket_bp = Blueprint("ticket", __name__)

# ---------- Helpers ----------
def _ticket_to_dict(ticket: Ticket) -> dict:
    """
    Converte um objeto Ticket (linha do BD) em um dicionário JSON.
    Isso facilita a resposta da API.
    """
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "creator_id": ticket.creator_id,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
    }

# ---------- Rotas ----------
@ticket_bp.route("/", methods=["GET"])
def list_tickets():
    """GET /tickets/ → devolve a lista completa de tickets."""
    tickets = Ticket.query.all()
    return jsonify([_ticket_to_dict(t) for t in tickets]), 200


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id: int):
    """GET /tickets/<id> → devolve um ticket específico."""
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(_ticket_to_dict(ticket)), 200


@ticket_bp.route("/", methods=["POST"])
def create_ticket():
    """
    POST /tickets/ → cria um ticket.
    Espera JSON contendo: title, description, creator_id
    """
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON body required")

    # Verifica se os campos obrigatórios foram enviados
    required = {"title", "description", "creator_id"}
    if not required.issubset(data):
        missing = required - data.keys()
        abort(400, description=f"Campos faltando: {', '.join(missing)}")

    # Garante que o usuário informado realmente existe (FK)
    user = User.query.get(data["creator_id"])
    if not user:
        abort(400, description="Creator (user) not found")

    ticket = Ticket(
        title=data["title"],
        description=data["description"],
        creator_id=data["creator_id"],
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify(_ticket_to_dict(ticket)), 201


@ticket_bp.route("/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id: int):
    """
    PUT /tickets/<id> → altera título, descrição ou status.
    Recebe JSON com qualquer combinação de: title, description, status
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json(silent=True) or {}

    updatable = {"title", "description", "status"}
    for key in updatable.intersection(data):
        setattr(ticket, key, data[key])

    db.session.commit()
    return jsonify(_ticket_to_dict(ticket)), 200


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id: int):
    """DELETE /tickets/<id> → remove o ticket."""
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return "", 204