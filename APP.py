import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise da Estrutura", layout="wide")
st.title("📦 Análise da Estrutura - Quantidade de Pais Finais")

# Caminho do arquivo
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar a planilha completa sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Coluna B = index 1 => representa o Pai_Final
estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()

# Remover entradas nulas, vazias ou que são cabeçalho duplicado
estrutura_filtrada = estrutura[estrutura['Pai_Final'].str.len() > 1]
estrutura_filtrada = estrutura_filtrada[~estrutura_filtrada['Pai_Final'].str.contains("Produto", case=False)]

# Obter pais únicos válidos
pais_unicos_lista = estrutura_filtrada['Pai_Final'].drop_duplicates().sort_values().reset_index(drop=True)

st.subheader("🧾 Lista de Códigos dos Pais Finais:")
st.dataframe(pais_unicos_lista, use_container_width=True)

# Mostrar quantidade de pais únicos
st.subheader("🔍 Quantidade de Pais Finais Únicos Encontrados na Estrutura:")
st.metric(label="Pais Finais", value=len(pais_unicos_lista))
