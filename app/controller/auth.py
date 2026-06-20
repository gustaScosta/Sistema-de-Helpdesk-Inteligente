from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ..models.models import SessionLocal, Usuario

auth_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    senha: str


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: UsuarioCreate):
    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.email == body.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="Email ja cadastrado")
        usuario = Usuario(nome=body.nome, email=body.email, senha=body.senha)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}
    finally:
        db.close()


@auth_router.post("/login")
def login(body: LoginRequest):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == body.email).first()
        if usuario is None or usuario.senha != body.senha:
            raise HTTPException(status_code=401, detail="Credenciais invalidas")
        return {"msg": "login ok", "user_id": usuario.id, "nome": usuario.nome}
    finally:
        db.close()