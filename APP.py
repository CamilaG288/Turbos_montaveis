import streamlit as st
import pandas as pd

st.set_page_config(page_title="Códigos Pai Final", layout="wide")
st.title("📦 Lista de Códigos Pai Final (Coluna B)")

# URL da planilha
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar a planilha completa sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Coluna B = index 1 => representa o Pai_Final
estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()

# Remover entradas vazias e cabeçalhos duplicados
estrutura = estrutura[
    (estrutura['Pai_Final'].str.len() > 1) &
    (~estrutura['Pai_Final'].str.contains("Produto", case=False))
]

# Selecionar os códigos únicos
codigos_pai_finais = estrutura['Pai_Final'].drop_duplicates().sort_values().reset_index(drop=True)

st.subheader(f"🔍 Total de Códigos Pai Final Únicos: {len(codigos_pai_finais)}")
st.dataframe(codigos_pai_finais, use_container_width=True)

# Exportar para Excel
from io import BytesIO
buffer = BytesIO()
codigos_pai_finais.to_frame(name="Pai_Final").to_excel(buffer, index=False)
st.download_button("📥 Baixar Lista em Excel", buffer.getvalue(), file_name="codigos_pai_final.xlsx")

