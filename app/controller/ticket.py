from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ..models.models import SessionLocal, Chamados, Usuario

ticket_router = APIRouter()


class ChamadoCreate(BaseModel):
    titulo: str
    descricao: str
    usuario_id: int
    prioridade: Optional[str] = "media"


class ChamadoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None


def _to_dict(c: Chamados) -> dict:
    return {
        "id": c.id,
        "titulo": c.titulo,
        "descricao": c.descricao,
        "status": c.status,
        "prioridade": c.prioridade,
        "usuario_id": c.usuario_id,
    }


@ticket_router.get("/")
def list_tickets():
    db = SessionLocal()
    try:
        chamados = db.query(Chamados).order_by(Chamados.id.desc()).all()
        return [_to_dict(c) for c in chamados]
    finally:
        db.close()


@ticket_router.get("/{ticket_id}")
def get_ticket(ticket_id: int):
    db = SessionLocal()
    try:
        chamado = db.query(Chamados).filter(Chamados.id == ticket_id).first()
        if not chamado:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        return _to_dict(chamado)
    finally:
        db.close()


@ticket_router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(body: ChamadoCreate):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.id == body.usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=400, detail="Usuario nao encontrado")
        chamado = Chamados(
            titulo=body.titulo,
            descricao=body.descricao,
            usuario_id=body.usuario_id,
            status="aberto",
            prioridade=body.prioridade,
        )
        db.add(chamado)
        db.commit()
        db.refresh(chamado)
        return _to_dict(chamado)
    finally:
        db.close()


@ticket_router.put("/{ticket_id}")
def update_ticket(ticket_id: int, body: ChamadoUpdate):
    db = SessionLocal()
    try:
        chamado = db.query(Chamados).filter(Chamados.id == ticket_id).first()
        if not chamado:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(chamado, field, value)
        db.commit()
        db.refresh(chamado)
        return _to_dict(chamado)
    finally:
        db.close()


@ticket_router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int):
    db = SessionLocal()
    try:
        chamado = db.query(Chamados).filter(Chamados.id == ticket_id).first()
        if not chamado:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        db.delete(chamado)
        db.commit()
    finally:
        db.close()