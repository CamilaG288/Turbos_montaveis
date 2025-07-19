import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Análise da Estrutura", layout="wide")
st.title("📦 Análise da Estrutura - Quantidade de Pais Finais")

# Caminho do arquivo
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar a planilha completa sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Visualizar as primeiras linhas para inspeção
st.subheader("👀 Primeiras linhas da estrutura bruta:")
st.dataframe(estrutura.head(10))

# Coluna B = index 1 => representa o Pai_Final
estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()

# 🔍 Tentar extrair apenas códigos válidos com regex (ex: 802925-01, RB6559-6)
estrutura['Pai_Final'] = estrutura['Pai_Final'].apply(lambda x: re.findall(r"[A-Z0-9]+-[0-9]+", x)[0] if re.findall(r"[A-Z0-9]+-[0-9]+", x) else None)

# Remover valores nulos após extração
estrutura_filtrada = estrutura[estrutura['Pai_Final'].notna()]

# Contar pais únicos válidos
pais_unicos = estrutura_filtrada['Pai_Final'].nunique()

st.subheader("🔍 Quantidade de Pais Finais Únicos Encontrados na Estrutura:")
st.metric(label="Pais Finais", value=pais_unicos)
