import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Painel de Estoque", layout="wide")
st.title("📦 Consulta de Estoque Atual por Componente")

# Link da planilha de estoque no GitHub
URL_ESTOQUE = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ALMOX102.xlsx"

@st.cache_data
def carregar_estoque():
    estoque = pd.read_excel(URL_ESTOQUE)
    return estoque

# Carregando dados
tabela_estoque = carregar_estoque()

# Renomear e padronizar colunas
estoque = tabela_estoque.rename(columns={"Produto": "Componente", "Qtde Atual": "Quantidade"})
estoque['Componente'] = estoque['Componente'].astype(str).str.strip()

# Agrupar por componente e somar a quantidade disponível
estoque_resumo = estoque.groupby("Componente", as_index=False)["Quantidade"].sum()

# Exibir
st.subheader("🔍 Estoque por Componente")
st.dataframe(estoque_resumo, use_container_width=True)

# Download em Excel
buffer = BytesIO()
estoque_resumo.to_excel(buffer, index=False)
st.download_button("📥 Baixar Estoque em Excel", data=buffer.getvalue(), file_name="estoque_resumo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
