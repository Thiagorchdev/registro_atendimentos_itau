import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página
st.set_page_config(page_title="Registro de Atendimentos Itaú", layout="centered")

# Acesso seguro via secrets.toml
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
gc = gspread.authorize(credentials)

SHEET_ID = st.secrets["sheets"]["sheet_id"]
worksheet = gc.open_by_key(SHEET_ID).sheet1

st.title("📋 Registro de Atendimentos Itaú")

# Formulário principal
st.subheader("Registrar atendimento")

col1, col2 = st.columns(2)
with col1:
    matricula = st.text_input("Matrícula do colaborador:")
with col2:
    nome_cliente = st.text_input("Nome do cliente:")

tipo_atendimento = st.selectbox(
    "Tipo de atendimento:",
    ["Dúvida", "Erro", "Solicitação", "Outro"]
)

descricao = st.text_area("Descrição do atendimento:")

# Pop-up de confirmação simulado
if st.button("Registrar atendimento"):
    if not matricula or not nome_cliente or not descricao:
        st.warning("Preencha todos os campos antes de registrar.")
    else:
        with st.container():
            st.markdown(
                """
                <div style="
                    background-color: #f9f9f9;
                    border: 2px solid #ccc;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                    text-align: center;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                ">
                    <h4>Confirmar registro?</h4>
                    <p>Tem certeza que deseja registrar este atendimento?</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ Confirmar"):
                    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    nova_linha = [data_hora, matricula, nome_cliente, tipo_atendimento, descricao]
                    worksheet.append_row(nova_linha)
                    st.success("Atendimento registrado com sucesso!")
            with col_cancel:
                st.button("❌ Cancelar")

# Mostrar registros existentes
st.subheader("📄 Últimos atendimentos registrados")

dados = worksheet.get_all_records()
if dados:
    df = pd.DataFrame(dados)
    st.dataframe(df.tail(10))
else:
    st.info("Nenhum atendimento registrado ainda.")
