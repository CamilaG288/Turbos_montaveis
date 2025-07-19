import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise da Estrutura", layout="wide")
st.title("📦 Análise da Estrutura - Quantidade de Pais Finais")

# Caminho do arquivo
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar a planilha completa sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Visualizar as primeiras linhas para entender a estrutura da planilha
st.subheader("👀 Primeiras linhas da estrutura bruta:")
st.dataframe(estrutura.head(10))

# Coluna B = index 1 => representa o Pai_Final
estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()

# Filtrar códigos válidos como pais finais (não vazios, com hífen, e tamanho mínimo)
estrutura_filtrada = estrutura[
    estrutura['Pai_Final'].notna() &
    estrutura['Pai_Final'].str.contains("-", na=False) &
    estrutura['Pai_Final'].str.len() >= 5
]

# Contar os pais finais únicos
pais_unicos = estrutura_filtrada['Pai_Final'].nunique()

st.subheader("🔍 Quantidade de Pais Finais Únicos Encontrados na Estrutura:")
st.metric(label="Pais Finais", value=pais_unicos)
