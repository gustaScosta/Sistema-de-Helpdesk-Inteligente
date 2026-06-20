import os
from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL nao encontrada. Configure a variavel de ambiente.")

# Corrige URL do Render/Neon que usa postgres:// ao inves de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(255), nullable=False, default="")

    chamados = relationship("Chamados", back_populates="usuario")


class Chamados(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False, default="aberto")
    prioridade = Column(String(20), nullable=False, default="media")

    usuario = relationship("Usuario", back_populates="chamados")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    patrimonio = Column(String(50), unique=True, nullable=False)
    status = Column(String(30), nullable=False)
    localizacao = Column(String(100), nullable=True)


# Tenta adicionar a coluna 'senha' caso a tabela 'usuarios' ja exista no Neon sem ela
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS senha VARCHAR(255) DEFAULT '';"))
        conn.commit()
        print("Migracao: Coluna 'senha' verificada/adicionada com sucesso!")
except Exception as e:
    # Se der erro (ex: SQLite local nao suporta ADD COLUMN IF NOT EXISTS), apenas ignora
    print("Aviso na migracao de banco:", e)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")