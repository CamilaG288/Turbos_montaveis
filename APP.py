import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise da Estrutura", layout="wide")
st.title("📦 Análise da Estrutura - Hierarquia Pai-Filho")

# Caminho do arquivo
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar a planilha completa sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Coluna B = index 1 => representa o Pai_Final
# Coluna P = index 15 => Componente
# Coluna Q = index 16 => Nível
# Coluna S = index 18 => Fantasma

estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()
estrutura['Componente'] = estrutura[15].astype(str).str.strip()
estrutura['Nivel'] = estrutura[16].astype(str).str.strip()
estrutura['Fantasma'] = estrutura[18].astype(str).str.upper().str.strip()

# Remover entradas nulas ou com cabeçalho duplicado
estrutura = estrutura[
    (estrutura['Pai_Final'].str.len() > 1) &
    (~estrutura['Pai_Final'].str.contains("Produto", case=False))
]

# Eliminar componentes terminados em 'P' e fantasmas
estrutura = estrutura[
    ~estrutura['Componente'].str.endswith('P') &
    (estrutura['Fantasma'] != 'S')
]

# Criar hierarquia
hierarquia = []
for _, row in estrutura.iterrows():
    nivel = row['Nivel']
    if nivel == '1':
        hierarquia.append({
            'Pai_Final': row['Pai_Final'],
            'Pai_Imediato': row['Pai_Final'],
            'Componente': row['Componente'],
            'Nível': 'Filho'
        })
    elif nivel == '2':
        hierarquia.append({
            'Pai_Final': row['Pai_Final'],
            'Pai_Imediato': row['Componente'],
            'Componente': None,
            'Nível': 'Neto (componente do conjunto com P)'
        })

df_hierarquia = pd.DataFrame(hierarquia)

st.subheader("📘 Hierarquia Pai-Filho Completa")
st.dataframe(df_hierarquia, use_container_width=True)

# Mostrar quantidade de pais únicos
pais_unicos = df_hierarquia['Pai_Final'].drop_duplicates()
st.subheader("🔍 Quantidade de Pais Finais Únicos Encontrados na Estrutura:")
st.metric(label="Pais Finais", value=len(pais_unicos))
