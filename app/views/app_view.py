from pathlib import Path
import sys
import streamlit as st
from sqlalchemy.exc import IntegrityError

# Garante que ache o caminho certo do arquivo.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models.models import Base, Chamados, Equipamento, SessionLocal, Usuario, engine


# Cria as tabelas no banco caso elas ainda nao existam.
Base.metadata.create_all(bind=engine)


def get_db():
    # Abre uma sessao com o banco para executar o CRUD.
    return SessionLocal()


def notify_success(message):
    # Mostra uma mensagem e recarrega a tela para atualizar os dados.
    st.success(message)
    st.rerun()


def notify_error(error):
    # Mostra uma mensagem de erro amigavel.
    st.error(f"Nao foi possivel concluir a operacao: {error}")


# Configuracao inicial da pagina Streamlit.
st.set_page_config(
    page_title="SmartHelp",
    page_icon="SH",
    layout="wide",
)

st.title("SmartHelp")
st.caption("Base do sistema de Helpdesk Inteligente com controle de estoque")

db = get_db()

try:
    # READ: busca os registros existentes no banco.
    usuarios = db.query(Usuario).order_by(Usuario.id).all()
    chamados = db.query(Chamados).order_by(Chamados.id.desc()).all()
    equipamentos = db.query(Equipamento).order_by(Equipamento.id).all()

    # Indicadores simples para apresentar um resumo do sistema.
    total_abertos = sum(1 for chamado in chamados if chamado.status.lower() == "aberto")
    total_andamento = sum(1 for chamado in chamados if chamado.status.lower() == "em andamento")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuarios", len(usuarios))
    col2.metric("Chamados", len(chamados))
    col3.metric("Abertos", total_abertos)
    col4.metric("Equipamentos", len(equipamentos))

    tab_chamados, tab_usuarios, tab_equipamentos = st.tabs(
        ["Chamados", "Usuarios", "Equipamentos"]
    )

    with tab_chamados:
        st.subheader("Novo chamado")

        # Formulario para criar um chamado ligado a um usuario.
        with st.form("form_criar_chamado", clear_on_submit=True):
            if not usuarios:
                st.warning("Cadastre um usuario antes de abrir chamados.")

            # Mostra id e nome na tela, mas salva somente o id do usuario no banco.
            usuario_opcoes = {f"{usuario.id} - {usuario.nome}": usuario.id for usuario in usuarios}
            usuario_label = st.selectbox("Solicitante", list(usuario_opcoes.keys()), disabled=not usuarios)
            titulo = st.text_input("Titulo", max_chars=100)
            descricao = st.text_area("Descricao", max_chars=500)
            prioridade = st.selectbox("Prioridade", ["baixa", "media", "alta", "critica"], index=1)
            status = st.selectbox("Status", ["aberto", "em andamento", "resolvido", "fechado"])
            criar_chamado = st.form_submit_button("Criar chamado", disabled=not usuarios)

            if criar_chamado:
                # CREATE: cria e salva um novo chamado.
                chamado = Chamados(
                    usuario_id=usuario_opcoes[usuario_label],
                    titulo=titulo,
                    descricao=descricao,
                    prioridade=prioridade,
                    status=status,
                )
                db.add(chamado)
                db.commit()
                notify_success("Chamado criado com sucesso.")

        st.subheader("Chamados cadastrados")
        if not chamados:
            st.info("Nenhum chamado cadastrado.")
        else:
            for chamado in chamados:
                # Cada chamado aparece em uma caixa expansivel.
                with st.expander(f"#{chamado.id} - {chamado.titulo}"):
                    st.write(f"Solicitante: {chamado.usuario.nome if chamado.usuario else 'Nao informado'}")
                    st.write(f"Descricao: {chamado.descricao}")

                    with st.form(f"form_editar_chamado_{chamado.id}"):
                        # Campos para alterar status e prioridade do chamado.
                        novo_status = st.selectbox(
                            "Status",
                            ["aberto", "em andamento", "resolvido", "fechado"],
                            index=["aberto", "em andamento", "resolvido", "fechado"].index(chamado.status)
                            if chamado.status in ["aberto", "em andamento", "resolvido", "fechado"]
                            else 0,
                            key=f"status_{chamado.id}",
                        )
                        nova_prioridade = st.selectbox(
                            "Prioridade",
                            ["baixa", "media", "alta", "critica"],
                            index=["baixa", "media", "alta", "critica"].index(chamado.prioridade)
                            if chamado.prioridade in ["baixa", "media", "alta", "critica"]
                            else 1,
                            key=f"prioridade_{chamado.id}",
                        )
                        salvar, excluir = st.columns(2)
                        salvar_chamado = salvar.form_submit_button("Salvar")
                        excluir_chamado = excluir.form_submit_button("Excluir")

                        if salvar_chamado:
                            # UPDATE: altera o chamado e confirma no banco.
                            chamado.status = novo_status
                            chamado.prioridade = nova_prioridade
                            db.commit()
                            notify_success("Chamado atualizado.")

                        if excluir_chamado:
                            # DELETE: remove o chamado do banco.
                            db.delete(chamado)
                            db.commit()
                            notify_success("Chamado excluido.")

    with tab_usuarios:
        st.subheader("Novo usuario")

        # Formulario para criar usuario.
        with st.form("form_criar_usuario", clear_on_submit=True):
            nome = st.text_input("Nome", max_chars=100)
            email = st.text_input("Email", max_chars=150)
            criar_usuario = st.form_submit_button("Criar usuario")

            if criar_usuario:
                # CREATE: salva usuario. IntegrityError trata email duplicado.
                usuario = Usuario(nome=nome, email=email)
                db.add(usuario)
                try:
                    db.commit()
                    notify_success("Usuario criado com sucesso.")
                except IntegrityError:
                    db.rollback()
                    notify_error("email ja cadastrado")

        st.subheader("Usuarios cadastrados")
        if not usuarios:
            st.info("Nenhum usuario cadastrado.")
        else:
            for usuario in usuarios:
                # Formulario para editar ou excluir cada usuario.
                with st.form(f"form_usuario_{usuario.id}"):
                    novo_nome = st.text_input("Nome", value=usuario.nome, key=f"nome_{usuario.id}")
                    novo_email = st.text_input("Email", value=usuario.email, key=f"email_{usuario.id}")
                    salvar, excluir = st.columns(2)
                    salvar_usuario = salvar.form_submit_button("Salvar")
                    excluir_usuario = excluir.form_submit_button("Excluir")

                    if salvar_usuario:
                        # UPDATE: altera nome/email do usuario.
                        usuario.nome = novo_nome
                        usuario.email = novo_email
                        try:
                            db.commit()
                            notify_success("Usuario atualizado.")
                        except IntegrityError:
                            db.rollback()
                            notify_error("email ja cadastrado")

                    if excluir_usuario:
                        # Regra simples: nao excluir usuario que tem chamados vinculados.
                        if usuario.chamados:
                            st.error("Nao e possivel excluir usuario com chamados vinculados.")
                        else:
                            db.delete(usuario)
                            db.commit()
                            notify_success("Usuario excluido.")

    with tab_equipamentos:
        st.subheader("Novo equipamento")

        # Formulario para criar equipamento/estoque.
        with st.form("form_criar_equipamento", clear_on_submit=True):
            nome = st.text_input("Nome do equipamento", max_chars=100)
            tipo = st.text_input("Tipo", max_chars=50)
            patrimonio = st.text_input("Patrimonio", max_chars=50)
            status = st.selectbox("Status", ["disponivel", "em uso", "manutencao", "descartado"])
            localizacao = st.text_input("Localizacao", max_chars=100)
            criar_equipamento = st.form_submit_button("Criar equipamento")

            if criar_equipamento:
                # CREATE: salva novo equipamento.
                equipamento = Equipamento(
                    nome=nome,
                    tipo=tipo,
                    patrimonio=patrimonio,
                    status=status,
                    localizacao=localizacao,
                )
                db.add(equipamento)
                try:
                    db.commit()
                    notify_success("Equipamento criado com sucesso.")
                except IntegrityError:
                    db.rollback()
                    notify_error("patrimonio ja cadastrado")

        st.subheader("Equipamentos cadastrados")
        if not equipamentos:
            st.info("Nenhum equipamento cadastrado.")
        else:
            for equipamento in equipamentos:
                # Formulario para editar ou excluir cada equipamento.
                with st.form(f"form_equipamento_{equipamento.id}"):
                    novo_nome = st.text_input("Nome", value=equipamento.nome, key=f"equip_nome_{equipamento.id}")
                    novo_tipo = st.text_input("Tipo", value=equipamento.tipo, key=f"equip_tipo_{equipamento.id}")
                    novo_patrimonio = st.text_input(
                        "Patrimonio",
                        value=equipamento.patrimonio,
                        key=f"equip_patrimonio_{equipamento.id}",
                    )
                    novo_status = st.selectbox(
                        "Status",
                        ["disponivel", "em uso", "manutencao", "descartado"],
                        index=["disponivel", "em uso", "manutencao", "descartado"].index(equipamento.status)
                        if equipamento.status in ["disponivel", "em uso", "manutencao", "descartado"]
                        else 0,
                        key=f"equip_status_{equipamento.id}",
                    )
                    nova_localizacao = st.text_input(
                        "Localizacao",
                        value=equipamento.localizacao or "",
                        key=f"equip_localizacao_{equipamento.id}",
                    )
                    salvar, excluir = st.columns(2)
                    salvar_equipamento = salvar.form_submit_button("Salvar")
                    excluir_equipamento = excluir.form_submit_button("Excluir")

                    if salvar_equipamento:
                        # UPDATE: altera os dados do equipamento.
                        equipamento.nome = novo_nome
                        equipamento.tipo = novo_tipo
                        equipamento.patrimonio = novo_patrimonio
                        equipamento.status = novo_status
                        equipamento.localizacao = nova_localizacao
                        try:
                            db.commit()
                            notify_success("Equipamento atualizado.")
                        except IntegrityError:
                            db.rollback()
                            notify_error("patrimonio ja cadastrado")

                    if excluir_equipamento:
                        # DELETE: remove o equipamento do banco.
                        db.delete(equipamento)
                        db.commit()
                        notify_success("Equipamento excluido.")
finally:
    # Fecha a sessao mesmo se acontecer algum erro durante a tela.
    db.close()
