import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Hierarquia Pai-Filho", layout="wide")
st.title("🔗 Hierarquia Completa: Pai, Filho e Neto")

# URL da planilha
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"

# Carregar planilha sem pular linhas
estrutura = pd.read_excel(URL_ESTRUTURA, header=None)

# Renomear colunas relevantes
estrutura['Pai_Final'] = estrutura[1].astype(str).str.strip()
estrutura['Componente'] = estrutura[15].astype(str).str.strip()
estrutura['Nivel'] = estrutura[16].astype(str).str.strip()
estrutura['Fantasma'] = estrutura[18].astype(str).str.upper().str.strip()

# Remover cabeçalhos e valores inválidos
estrutura = estrutura[
    (estrutura['Pai_Final'].str.len() > 1) &
    (~estrutura['Pai_Final'].str.contains("Produto", case=False))
]

# Filtrar fantasmas
estrutura = estrutura[estrutura['Fantasma'] != 'S']

# Separar níveis
n1 = estrutura[estrutura['Nivel'] == '1']
n2 = estrutura[estrutura['Nivel'] == '2']

hierarquia = []

# Construir relação
for _, row in n1.iterrows():
    pai_final = row['Pai_Final']
    filho = row['Componente']

    if filho.endswith('P'):
        filhos_do_conjunto = n2[n2['Pai_Final'] == filho]
        for _, neto in filhos_do_conjunto.iterrows():
            hierarquia.append({
                'Pai_Final': pai_final,
                'Pai_Imediato': filho,
                'Componente': neto['Componente'],
                'Nível': 'Neto'
            })
        hierarquia.append({
            'Pai_Final': pai_final,
            'Pai_Imediato': pai_final,
            'Componente': filho,
            'Nível': 'Filho (Conjunto)'
        })
    else:
        hierarquia.append({
            'Pai_Final': pai_final,
            'Pai_Imediato': pai_final,
            'Componente': filho,
            'Nível': 'Filho'
        })

# Criar DataFrame
df_hierarquia = pd.DataFrame(hierarquia)

st.subheader("📘 Estrutura Pai → Componente")
st.dataframe(df_hierarquia, use_container_width=True)

# Download Excel
buffer = BytesIO()
df_hierarquia.to_excel(buffer, index=False)
st.download_button("📥 Baixar Estrutura Hierárquica", buffer.getvalue(), file_name="estrutura_pai_filho.xlsx")
