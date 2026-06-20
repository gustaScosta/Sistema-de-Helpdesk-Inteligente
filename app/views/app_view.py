import os
import streamlit as st
import requests

# URL base da API (local ou variavel de ambiente do Render)
API_URL = os.getenv("API_URL", "http://localhost:8000")


def notify_success(message):
    st.success(message)
    st.rerun()


def notify_error(error):
    st.error(f"Nao foi possivel concluir a operacao: {error}")


# Configuracao da pagina
st.set_page_config(
    page_title="SmartHelp",
    page_icon="SH",
    layout="wide",
)

st.title("SmartHelp")
st.caption("Painel visual integrado com a API REST")

# Busca os dados via API
try:
    res_users = requests.get(f"{API_URL}/users/")
    usuarios = res_users.json() if res_users.status_code == 200 else []
    
    res_tickets = requests.get(f"{API_URL}/tickets/")
    chamados = res_tickets.json() if res_tickets.status_code == 200 else []
    
    res_equips = requests.get(f"{API_URL}/equipments/")
    equipamentos = res_equips.json() if res_equips.status_code == 200 else []

    total_abertos = sum(1 for c in chamados if c.get("status", "").lower() == "aberto")
    total_andamento = sum(1 for c in chamados if c.get("status", "").lower() == "em andamento")

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

        with st.form("form_criar_chamado", clear_on_submit=True):
            if not usuarios:
                st.warning("Cadastre um usuario antes de abrir chamados.")

            usuario_opcoes = {f"{u['id']} - {u['nome']}": u['id'] for u in usuarios}
            usuario_label = st.selectbox("Solicitante", list(usuario_opcoes.keys()), disabled=not usuarios)
            titulo = st.text_input("Titulo", max_chars=100)
            descricao = st.text_area("Descricao", max_chars=500)
            prioridade = st.selectbox("Prioridade", ["baixa", "media", "alta", "critica"], index=1)
            criar_chamado = st.form_submit_button("Criar chamado", disabled=not usuarios)

            if criar_chamado:
                payload = {
                    "titulo": titulo,
                    "descricao": descricao,
                    "usuario_id": usuario_opcoes[usuario_label],
                    "prioridade": prioridade
                }
                res = requests.post(f"{API_URL}/tickets/", json=payload)
                if res.status_code in [200, 201]:
                    notify_success("Chamado criado com sucesso via API.")
                else:
                    detail = res.json().get("detail", res.text)
                    notify_error(detail)

        st.subheader("Chamados cadastrados")
        if not chamados:
            st.info("Nenhum chamado cadastrado.")
        else:
            for chamado in chamados:
                with st.expander(f"#{chamado['id']} - {chamado['titulo']}"):
                    # Acha o nome do usuario na lista local
                    user_nome = "Nao informado"
                    for u in usuarios:
                        if u["id"] == chamado["usuario_id"]:
                            user_nome = u["nome"]
                            break
                    
                    st.write(f"Solicitante: {user_nome}")
                    st.write(f"Descricao: {chamado['descricao']}")

                    with st.form(f"form_editar_chamado_{chamado['id']}"):
                        novo_status = st.selectbox(
                            "Status",
                            ["aberto", "em andamento", "resolvido", "fechado"],
                            index=["aberto", "em andamento", "resolvido", "fechado"].index(chamado["status"])
                            if chamado["status"] in ["aberto", "em andamento", "resolvido", "fechado"]
                            else 0,
                            key=f"status_{chamado['id']}",
                        )
                        nova_prioridade = st.selectbox(
                            "Prioridade",
                            ["baixa", "media", "alta", "critica"],
                            index=["baixa", "media", "alta", "critica"].index(chamado["prioridade"])
                            if chamado["prioridade"] in ["baixa", "media", "alta", "critica"]
                            else 1,
                            key=f"prioridade_{chamado['id']}",
                        )
                        salvar, excluir = st.columns(2)
                        salvar_chamado = salvar.form_submit_button("Salvar")
                        excluir_chamado = excluir.form_submit_button("Excluir")

                        if salvar_chamado:
                            payload = {"status": novo_status, "prioridade": nova_prioridade}
                            res = requests.put(f"{API_URL}/tickets/{chamado['id']}", json=payload)
                            if res.status_code == 200:
                                notify_success("Chamado atualizado via API.")
                            else:
                                notify_error(res.json().get("detail", res.text))

                        if excluir_chamado:
                            res = requests.delete(f"{API_URL}/tickets/{chamado['id']}")
                            if res.status_code in [200, 204]:
                                notify_success("Chamado excluido via API.")
                            else:
                                notify_error(res.json().get("detail", res.text))

    with tab_usuarios:
        st.subheader("Novo usuario")

        with st.form("form_criar_usuario", clear_on_submit=True):
            nome = st.text_input("Nome", max_chars=100)
            email = st.text_input("Email", max_chars=150)
            criar_usuario = st.form_submit_button("Criar usuario")

            if criar_usuario:
                payload = {"nome": nome, "email": email, "senha": ""}
                res = requests.post(f"{API_URL}/users/", json=payload)
                if res.status_code in [200, 201]:
                    notify_success("Usuario criado via API.")
                else:
                    notify_error(res.json().get("detail", res.text))

        st.subheader("Usuarios cadastrados")
        if not usuarios:
            st.info("Nenhum usuario cadastrado.")
        else:
            for usuario in usuarios:
                with st.form(f"form_usuario_{usuario['id']}"):
                    novo_nome = st.text_input("Nome", value=usuario["nome"], key=f"nome_{usuario['id']}")
                    novo_email = st.text_input("Email", value=usuario["email"], key=f"email_{usuario['id']}")
                    salvar, excluir = st.columns(2)
                    salvar_usuario = salvar.form_submit_button("Salvar")
                    excluir_usuario = excluir.form_submit_button("Excluir")

                    if salvar_usuario:
                        payload = {"nome": novo_nome, "email": novo_email}
                        res = requests.put(f"{API_URL}/users/{usuario['id']}", json=payload)
                        if res.status_code == 200:
                            notify_success("Usuario atualizado via API.")
                        else:
                            notify_error(res.json().get("detail", res.text))

                    if excluir_usuario:
                        res = requests.delete(f"{API_URL}/users/{usuario['id']}")
                        if res.status_code in [200, 204]:
                            notify_success("Usuario excluido via API.")
                        else:
                            notify_error(res.json().get("detail", res.text))

    with tab_equipamentos:
        st.subheader("Novo equipamento")

        with st.form("form_criar_equipamento", clear_on_submit=True):
            nome = st.text_input("Nome do equipamento", max_chars=100)
            tipo = st.text_input("Tipo", max_chars=50)
            patrimonio = st.text_input("Patrimonio", max_chars=50)
            status = st.selectbox("Status", ["disponivel", "em uso", "manutencao", "descartado"])
            localizacao = st.text_input("Localizacao", max_chars=100)
            criar_equipamento = st.form_submit_button("Criar equipamento")

            if criar_equipamento:
                payload = {
                    "nome": nome,
                    "tipo": tipo,
                    "patrimonio": patrimonio,
                    "status": status,
                    "localizacao": localizacao
                }
                res = requests.post(f"{API_URL}/equipments/", json=payload)
                if res.status_code in [200, 201]:
                    notify_success("Equipamento criado via API.")
                else:
                    notify_error(res.json().get("detail", res.text))

        st.subheader("Equipamentos cadastrados")
        if not equipamentos:
            st.info("Nenhum equipamento cadastrado.")
        else:
            for equip in equipamentos:
                with st.form(f"form_equipamento_{equip['id']}"):
                    novo_nome = st.text_input("Nome", value=equip["nome"], key=f"equip_nome_{equip['id']}")
                    novo_tipo = st.text_input("Tipo", value=equip["tipo"], key=f"equip_tipo_{equip['id']}")
                    novo_patrimonio = st.text_input(
                        "Patrimonio",
                        value=equip["patrimonio"],
                        key=f"equip_patrimonio_{equip['id']}",
                    )
                    novo_status = st.selectbox(
                        "Status",
                        ["disponivel", "em uso", "manutencao", "descartado"],
                        index=["disponivel", "em uso", "manutencao", "descartado"].index(equip["status"])
                        if equip["status"] in ["disponivel", "em uso", "manutencao", "descartado"]
                        else 0,
                        key=f"equip_status_{equip['id']}",
                    )
                    nova_localizacao = st.text_input(
                        "Localizacao",
                        value=equip["localizacao"] or "",
                        key=f"equip_localizacao_{equip['id']}",
                    )
                    salvar, excluir = st.columns(2)
                    salvar_equipamento = salvar.form_submit_button("Salvar")
                    excluir_equipamento = excluir.form_submit_button("Excluir")

                    if salvar_equipamento:
                        payload = {
                            "nome": novo_nome,
                            "tipo": novo_tipo,
                            "patrimonio": novo_patrimonio,
                            "status": novo_status,
                            "localizacao": nova_localizacao
                        }
                        res = requests.put(f"{API_URL}/equipments/{equip['id']}", json=payload)
                        if res.status_code == 200:
                            notify_success("Equipamento atualizado via API.")
                        else:
                            notify_error(res.json().get("detail", res.text))

                    if excluir_equipamento:
                        res = requests.delete(f"{API_URL}/equipments/{equip['id']}")
                        if res.status_code in [200, 204]:
                            notify_success("Equipamento excluido via API.")
                        else:
                            notify_error(res.json().get("detail", res.text))

except Exception as e:
    st.error(f"Erro ao conectar com a API: {e}")
    st.info(f"Verifique se a API esta rodando no endereco: {API_URL}")