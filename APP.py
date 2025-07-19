import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Painel de Estoque", layout="wide")
st.title("📦 Consulta de Estoque Atual por Componente")

# Link da planilha de estoque e estrutura no GitHub
URL_ESTOQUE = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ALMOX102.xlsx"
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

@st.cache_data
def carregar_estoque():
    estoque = pd.read_excel(URL_ESTOQUE)
    return estoque

@st.cache_data
def carregar_estrutura():
    estrutura = pd.read_excel(URL_ESTRUTURA)  # Não pula linhas!
    estrutura.columns.values[15] = "Componente"
    estrutura = estrutura.rename(columns={
        "Produto": "Pai_Final",
        "Qtde. Líquida": "Qtde_Liquida",
        "Setup/Perda": "Setup",
        "Descrição do Produto": "Descricao",
        "Nível": "Nivel",
        "Fantasma": "Fantasma"
    })

    estrutura['Componente'] = estrutura['Componente'].astype(str).str.strip()
    estrutura['Pai_Final'] = estrutura['Pai_Final'].astype(str).str.strip()
    estrutura['Fantasma'] = estrutura['Fantasma'].astype(str).str.upper().str.strip()
    estrutura['Nivel'] = estrutura['Nivel'].astype(str).str.strip()

    estrutura = estrutura[estrutura['Nivel'].isin(["1", "2"])]
    estrutura = estrutura[~estrutura['Componente'].str.endswith("P")]
    estrutura = estrutura[estrutura['Fantasma'] != 'S']

    return estrutura[["Pai_Final", "Componente", "Descricao", "Nivel", "Qtde_Liquida"]]

# Carregando dados
estoque_raw = carregar_estoque()
estrutura_filtrada = carregar_estrutura()

# Processar estoque
estoque = estoque_raw.rename(columns={"Produto": "Componente", "Qtde Atual": "Quantidade"})
estoque['Componente'] = estoque['Componente'].astype(str).str.strip()
estoque_resumo = estoque.groupby("Componente", as_index=False)["Quantidade"].sum()

# Exibir Estoque
st.subheader("🔍 Estoque por Componente")
st.dataframe(estoque_resumo, use_container_width=True)

buffer = BytesIO()
estoque_resumo.to_excel(buffer, index=False)
st.download_button("📥 Baixar Estoque em Excel", data=buffer.getvalue(), file_name="estoque_resumo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Exibir Estrutura
st.title("🏗️ Estrutura Pai-Filho (Níveis 1 e 2)")
st.subheader("🔍 Estrutura Pai → Componente")
st.dataframe(estrutura_filtrada, use_container_width=True)

buffer_estrutura = BytesIO()
estrutura_filtrada.to_excel(buffer_estrutura, index=False)
st.download_button("📥 Baixar Estrutura Filtrada", data=buffer_estrutura.getvalue(), file_name="estrutura_filtrada.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
