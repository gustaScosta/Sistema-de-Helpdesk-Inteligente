import os

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL nao encontrada. Verifique o arquivo .env.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    chamados = relationship("Chamados", back_populates="usuario")


class Chamados(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    status = Column(String, nullable=False)
    prioridade = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="chamados")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    patrimonio = Column(String(50), unique=True, nullable=False)
    status = Column(String(30), nullable=False)
    localizacao = Column(String(100), nullable=True)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
