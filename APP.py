import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura do arquivo direto do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade real: P - (Q - N)
df["QUANTIDADE_REAL"] = df["P"] - (df["Q"] - df["N"])

# Exibir resultado com colunas relevantes
colunas_exibir = ["PEDIDO", "PRODUTO", "CLIENTE", "P", "Q", "N", "QUANTIDADE_REAL"]
colunas_exibir = [col for col in colunas_exibir if col in df.columns]  # Garante que existam

st.dataframe(df[colunas_exibir])
