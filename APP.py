import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura da planilha direto do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Visualizar as colunas com índice (debug)
st.write("Colunas e seus índices:")
for i, col in enumerate(df.columns):
    st.write(f"{i}: {col}")

# Cálculo com base nos índices: P (15), Q (16), N (13)
df["QUANTIDADE_REAL"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

# Exibição de colunas relevantes
colunas_exibir = df.columns[[0, 1, 15, 16, 13]].tolist()  # por exemplo: pedido, produto + P, Q, N
colunas_exibir.append("QUANTIDADE_REAL")

st.dataframe(df[colunas_exibir])
