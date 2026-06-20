from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from ..models.models import SessionLocal, Usuario

user_router = APIRouter()


class UserCreate(BaseModel):
    nome: str
    email: str
    senha: Optional[str] = ""


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None


def _to_dict(u: Usuario) -> dict:
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        # Nao retornamos a senha por seguranca
    }


@user_router.get("/")
def list_users():
    db = SessionLocal()
    try:
        users = db.query(Usuario).order_by(Usuario.id).all()
        return [_to_dict(u) for u in users]
    finally:
        db.close()


@user_router.get("/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return _to_dict(user)
    finally:
        db.close()


@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.email == body.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="Email ja cadastrado")
        user = Usuario(nome=body.nome, email=body.email, senha=body.senha)
        db.add(user)
        db.commit()
        db.refresh(user)
        return _to_dict(user)
    finally:
        db.close()


@user_router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        
        # Se for mudar o email, verifica se ja nao existe outro
        if body.email and body.email != user.email:
            existente = db.query(Usuario).filter(Usuario.email == body.email).first()
            if existente:
                raise HTTPException(status_code=400, detail="Email ja cadastrado por outro usuario")
        
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(user, field, value)
            
        db.commit()
        db.refresh(user)
        return _to_dict(user)
    finally:
        db.close()


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        
        # Nao permite deletar usuario com chamados abertos
        if len(user.chamados) > 0:
            raise HTTPException(status_code=400, detail="Nao e possivel excluir usuario com chamados vinculados")
            
        db.delete(user)
        db.commit()
    finally:
        db.close()