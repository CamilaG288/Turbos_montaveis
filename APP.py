import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura da planilha do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade real: Qtde. Abe - (Qtde. Separ - Qtde. Ate)
df["QUANTIDADE_REAL"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

# Selecionar colunas para exibir/exportar
colunas_exibir = [
    "Cliente", "Produto",
