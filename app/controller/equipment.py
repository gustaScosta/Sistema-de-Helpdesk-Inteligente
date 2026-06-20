from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ..models.models import SessionLocal, Equipamento

equipment_router = APIRouter()


class EquipmentCreate(BaseModel):
    nome: str
    tipo: str
    patrimonio: str
    status: str
    localizacao: Optional[str] = None


class EquipmentUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    patrimonio: Optional[str] = None
    status: Optional[str] = None
    localizacao: Optional[str] = None


def _to_dict(e: Equipamento) -> dict:
    return {
        "id": e.id,
        "nome": e.nome,
        "tipo": e.tipo,
        "patrimonio": e.patrimonio,
        "status": e.status,
        "localizacao": e.localizacao,
    }


@equipment_router.get("/")
def list_equipments():
    db = SessionLocal()
    try:
        equips = db.query(Equipamento).order_by(Equipamento.id).all()
        return [_to_dict(e) for e in equips]
    finally:
        db.close()


@equipment_router.get("/{equip_id}")
def get_equipment(equip_id: int):
    db = SessionLocal()
    try:
        equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
        if not equip:
            raise HTTPException(status_code=404, detail="Equipamento nao encontrado")
        return _to_dict(equip)
    finally:
        db.close()


@equipment_router.post("/", status_code=status.HTTP_201_CREATED)
def create_equipment(body: EquipmentCreate):
    db = SessionLocal()
    try:
        existente = db.query(Equipamento).filter(Equipamento.patrimonio == body.patrimonio).first()
        if existente:
            raise HTTPException(status_code=400, detail="Patrimonio ja cadastrado")
        equip = Equipamento(
            nome=body.nome,
            tipo=body.tipo,
            patrimonio=body.patrimonio,
            status=body.status,
            localizacao=body.localizacao
        )
        db.add(equip)
        db.commit()
        db.refresh(equip)
        return _to_dict(equip)
    finally:
        db.close()


@equipment_router.put("/{equip_id}")
def update_equipment(equip_id: int, body: EquipmentUpdate):
    db = SessionLocal()
    try:
        equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
        if not equip:
            raise HTTPException(status_code=404, detail="Equipamento nao encontrado")
        
        if body.patrimonio and body.patrimonio != equip.patrimonio:
            existente = db.query(Equipamento).filter(Equipamento.patrimonio == body.patrimonio).first()
            if existente:
                raise HTTPException(status_code=400, detail="Patrimonio ja cadastrado em outro equipamento")
                
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(equip, field, value)
            
        db.commit()
        db.refresh(equip)
        return _to_dict(equip)
    finally:
        db.close()


@equipment_router.delete("/{equip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equip_id: int):
    db = SessionLocal()
    try:
        equip = db.query(Equipamento).filter(Equipamento.id == equip_id).first()
        if not equip:
            raise HTTPException(status_code=404, detail="Equipamento nao encontrado")
        db.delete(equip)
        db.commit()
    finally:
        db.close()