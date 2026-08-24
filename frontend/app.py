import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Barbearia Vintage", page_icon="💈")

if "token" not in st.session_state:
    st.session_state.token = None


def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/logo_barbearia_semfundo.png", width=2000)
    st.subheader("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        resposta = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if resposta.status_code == 200:
            st.session_state.token = resposta.json()["token"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")


def aba_clientes():
    st.header("Clientes")
    token = st.session_state.token

    with st.expander("➕ Novo cliente"):
        name = st.text_input("Nome", key="novo_nome")
        email = st.text_input("Email", key="novo_email")
        notes = st.text_area("Observações", key="novo_notes")
        if st.button("Salvar cliente"):
            resposta = requests.post(
                f"{API_URL}/clients?token={token}",
                json={"name": name, "email": email, "notes": notes},
            )
            if resposta.status_code == 200:
                st.success("Cliente criado!")
                st.rerun()
            else:
                st.error("Erro ao criar cliente")

    resposta = requests.get(f"{API_URL}/clients?token={token}")
    clientes = resposta.json()

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    for cliente in clientes:
        with st.expander(f"{cliente['name']} (id {cliente['id']})"):
            novo_nome = st.text_input("Nome", value=cliente["name"], key=f"nome_{cliente['id']}")
            novo_email = st.text_input("Email", value=cliente["email"] or "", key=f"email_{cliente['id']}")
            novo_notes = st.text_area("Observações", value=cliente["notes"] or "", key=f"notes_{cliente['id']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Salvar alterações", key=f"salvar_{cliente['id']}"):
                    requests.put(
                        f"{API_URL}/clients/{cliente['id']}?token={token}",
                        json={"name": novo_nome, "email": novo_email, "notes": novo_notes},
                    )
                    st.success("Atualizado!")
                    st.rerun()
            with col2:
                if st.button("Remover", key=f"remover_{cliente['id']}"):
                    requests.delete(f"{API_URL}/clients/{cliente['id']}?token={token}")
                    st.success("Removido!")
                    st.rerun()


def aba_agendamentos():
    st.header("Agenda")
    token = st.session_state.token

    resposta_clientes = requests.get(f"{API_URL}/clients?token={token}")
    clientes = resposta_clientes.json()

    if not clientes:
        st.warning("Cadastre um cliente antes de criar agendamentos.")
        return

    nomes_clientes = {c["name"]: c["id"] for c in clientes}

    with st.expander("➕ Novo agendamento"):
        nome_selecionado = st.selectbox("Cliente", list(nomes_clientes.keys()))
        data = st.date_input("Data")
        hora = st.time_input("Horário")
        servico = st.text_input("Serviço", placeholder="Ex: Corte + Barba")

        if st.button("Salvar agendamento"):
            client_id = nomes_clientes[nome_selecionado]
            resposta = requests.post(
                f"{API_URL}/appointments?token={token}",
                json={
                    "client_id": client_id,
                    "date": str(data),
                    "time": hora.strftime("%H:%M"),
                    "service": servico,
                },
            )
            if resposta.status_code == 200:
                st.success("Agendamento criado!")
                st.rerun()
            else:
                st.error("Erro ao criar agendamento")

    resposta = requests.get(f"{API_URL}/appointments?token={token}")
    agendamentos = resposta.json()

    if not agendamentos:
        st.info("Nenhum agendamento ainda.")
        return

    ids_para_nomes = {c["id"]: c["name"] for c in clientes}

    for appt in agendamentos:
        nome_cliente = ids_para_nomes.get(appt["client_id"], "Cliente removido")
        with st.expander(f"{appt['date']} {appt['time']} - {nome_cliente} ({appt['status']})"):
            st.write(f"**Serviço:** {appt['service']}")

            novo_status = st.selectbox(
                "Status",
                ["agendado", "concluido", "cancelado", "nao_compareceu"],
                index=["agendado", "concluido", "cancelado", "nao_compareceu"].index(appt["status"]),
                key=f"status_{appt['id']}",
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Atualizar status", key=f"salvar_status_{appt['id']}"):
                    requests.put(
                        f"{API_URL}/appointments/{appt['id']}/status?token={token}",
                        json={"status": novo_status},
                    )
                    st.success("Status atualizado!")
                    st.rerun()
            with col2:
                if st.button("Remover", key=f"remover_appt_{appt['id']}"):
                    requests.delete(f"{API_URL}/appointments/{appt['id']}?token={token}")
                    st.success("Removido!")
                    st.rerun()


if st.session_state.token is None:
    tela_login()
else:
    st.sidebar.image("assets/logo_barbearia_semfundo.png", width=350)
    if st.sidebar.button("Sair"):
        st.session_state.token = None
        st.rerun()

    aba1, aba2 = st.tabs(["Clientes", "Agenda"])
    with aba1:
        aba_clientes()
    with aba2:
        aba_agendamentos()