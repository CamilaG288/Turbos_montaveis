import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Upload ou leitura do arquivo localmente ou via GitHub
url_pedidos = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(url_pedidos)

# Cálculo: Qtde. Abe - (Qtde. Separ - Qtde. Ate)
df["QUANTIDADE_REAL"] = df["P"] - (df["Q"] - df["N"])

# Exibe a tabela com a nova coluna
st.dataframe(df[["P", "Q", "N", "QUANTIDADE_REAL"]])

