import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ======== CONFIGURAÇÃO ========
SENHA_GERENCIAL = "itau2025"

# Autenticação com Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
gc = gspread.authorize(credentials)
SHEET_ID = st.secrets["sheet_id"]
worksheet = gc.open_by_key(SHEET_ID).sheet1


# ======== FUNÇÕES ========
def carregar_base():
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def salvar_base(df):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def registrar_atendimento(matricula):
    df = carregar_base()

    if matricula not in df["MATRICULA"].values:
        st.error("❌ Matrícula não encontrada na base.")
        return

    idx = df.index[df["MATRICULA"] == matricula][0]
    nome = df.at[idx, "NOME"]
    setor = df.at[idx, "SETOR"]
    divisao = df.at[idx, "DIVISÃO"]
    atendimento_existente = df.at[idx, "ATENDIMENTO"]

    if atendimento_existente:
        st.info(f"ℹ️ {nome} ({setor}/{divisao}) já foi atendido em **{atendimento_existente}**.")
        return

    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.at[idx, "ATENDIMENTO"] = data_hora
    salvar_base(df)

    st.success(f"✅ Atendimento registrado para **{nome}** ({setor} / {divisao}) às {data_hora}.")


def exibir_relatorio():
    df = carregar_base()
    df = df.dropna(subset=["ATENDIMENTO"])

    if df.empty:
        st.info("Nenhum atendimento registrado ainda.")
        return

    df["ATENDIMENTO"] = pd.to_datetime(df["ATENDIMENTO"], errors="coerce")
    df_hoje = df[df["ATENDIMENTO"].dt.date == datetime.now().date()]

    st.header("📊 Relatório de Atendimentos do Dia")

    if not df_hoje.empty:
        total = len(df_hoje)
        media_por_hora = df_hoje.groupby(df_hoje["ATENDIMENTO"].dt.hour).size().mean()

        col1, col2 = st.columns(2)
        col1.metric("Total de atendimentos hoje", total)
        col2.metric("Média por hora", f"{media_por_hora:.2f}")

        st.subheader("🕓 Detalhamento de atendimentos de hoje")
        st.dataframe(df_hoje[["MATRICULA", "NOME", "SETOR", "DIVISÃO", "ATENDIMENTO"]])

        st.subheader("📅 Histórico completo")
        st.dataframe(df.sort_values(by="ATENDIMENTO", ascending=False))
    else:
        st.info("Nenhum atendimento registrado hoje ainda.")


# ======== INTERFACE ========
st.set_page_config(page_title="Controle de Atendimento", page_icon="🏦", layout="wide")

# ======== CSS PERSONALIZADO ========
st.markdown("""
<style>
.stApp {
    background-color: #f0f4fa;
}
.main-title {
    text-align: center;
    font-size: 50px;
    font-weight: 800;
    color: #002b5c;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    font-size: 24px;
    color: #003366;
    margin-top: 8px;
    margin-bottom: 50px;
}
.input-section {
    width: 50%;
    margin-left: 10%;
}
.input-label {
    text-align: left;
    font-size: 28px;
    font-weight: 700;
    color: #002b5c;
    margin-bottom: 10px;
}
div[data-baseweb="input"] > input {
    font-size: 36px !important;
    text-align: center !important;
    height: 90px !important;
    border: 3px solid #004a99 !important;
    border-radius: 14px !important;
    background-color: #ffffff !important;
    color: #002b5c !important;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
::placeholder {
    color: #444 !important;
    opacity: 1 !important;
}
div.stButton > button {
    font-size: 30px;
    font-weight: bold;
    background: linear-gradient(90deg, #0072ff, #0056b3);
    color: white;
    border-radius: 14px;
    height: 90px;
    width: 70%;
    border: none;
    text-align: left;
    box-shadow: 3px 3px 12px rgba(0,0,0,0.25);
    transition: all 0.2s ease-in-out;
    margin-top: 20px;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #0056b3, #004080);
    transform: scale(1.02);
}
.footer {
    text-align: center;
    color: #666;
    font-size: 14px;
    margin-top: 60px;
}
</style>
""", unsafe_allow_html=True)

# ======== CABEÇALHO ========
st.markdown('<h1 class="main-title">🏦 Atendimento Itaú Interno</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Digite sua matrícula para registrar seu atendimento</p>', unsafe_allow_html=True)

# ======== CAMPO DE ENTRADA ========
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown('<p class="input-label">Número da Matrícula</p>', unsafe_allow_html=True)

matricula_input = st.text_input(
    "",
    key="matricula",
    placeholder="Digite aqui",
    label_visibility="collapsed"
)

if st.button("Registrar Atendimento"):
    if matricula_input.strip():
        try:
            matricula = int(matricula_input)
            registrar_atendimento(matricula)
        except ValueError:
            st.error("Digite apenas números na matrícula.")
    else:
        st.warning("Informe uma matrícula antes de registrar.")

st.markdown('</div>', unsafe_allow_html=True)

# ======== ÁREA GERENCIAL ========
st.markdown("<div id='relatorio-area' style='display:none'>", unsafe_allow_html=True)
senha = st.text_input("🔒 Acesso:", type="password")

if senha == SENHA_GERENCIAL:
    exibir_relatorio()
elif senha:
    st.error("Senha incorreta.")

st.markdown("</div>", unsafe_allow_html=True)

# ======== RODAPÉ ========
st.markdown('<p class="footer">Marchesan</p>', unsafe_allow_html=True)
