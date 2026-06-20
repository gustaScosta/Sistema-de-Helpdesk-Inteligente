import os

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Carrega as variaveis do arquivo .env, incluindo a DATABASE_URL do Neon.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL nao encontrada. Verifique o arquivo .env.")

# Engine e a conexao principal do SQLAlchemy com o banco PostgreSQL.
engine = create_engine(DATABASE_URL)

# SessionLocal cria sessoes para consultar, inserir, atualizar e excluir dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base e a classe mae usada para transformar classes Python em tabelas.
Base = declarative_base()


class Usuario(Base):
    # Nome real da tabela no banco.
    __tablename__ = "usuarios"

    # Colunas da tabela usuarios.
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # Um usuario pode possuir varios chamados.
    chamados = relationship("Chamados", back_populates="usuario")


class Chamados(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, nullable=False)

    # Chave estrangeira que liga o chamado ao id de um usuario.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    status = Column(String, nullable=False)
    prioridade = Column(String, nullable=False)

    # Permite acessar os dados do usuario pelo chamado: chamado.usuario.nome.
    usuario = relationship("Usuario", back_populates="chamados")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    # Tabela para controlar os equipamentos/itens do estoque.
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    patrimonio = Column(String(50), unique=True, nullable=False)
    status = Column(String(30), nullable=False)
    localizacao = Column(String(100), nullable=True)


if __name__ == "__main__":
    # Cria no banco todas as tabelas definidas acima, se ainda nao existirem.
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
