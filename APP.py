import streamlit as st
import pandas as pd
from io import BytesIO

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

# Eliminar fantasmas
estrutura = estrutura[estrutura['Fantasma'] != 'S']

# Construir hierarquia completa: pai -> filho -> neto (multi-nível)
hierarquia = []

# Dicionário de componentes para buscar filhos
estrutura_dict = estrutura.groupby([1, 'Nivel'])

for i in range(len(estrutura)):
    row = estrutura.iloc[i]
    pai_final = row['Pai_Final']
    pai_imediato = pai_final
    componente = row['Componente']
    nivel = row['Nivel']

    if nivel == '1':
        if componente.endswith('P'):
            # Filho é um conjunto, buscar seus filhos
            filhos_n2 = estrutura[(estrutura[1] == componente) & (estrutura['Nivel'] == '2')]
            for _, neto in filhos_n2.iterrows():
                hierarquia.append({
                    'Pai_Final': pai_final,
                    'Pai_Imediato': componente,
                    'Componente': neto['Componente'],
                    'Nível': 'Neto'
                })
            # Também registra o conjunto como filho direto
            hierarquia.append({
                'Pai_Final': pai_final,
                'Pai_Imediato': pai_final,
                'Componente': componente,
                'Nível': 'Filho (Conjunto)'
            })
        else:
            # Filho comum
            hierarquia.append({
                'Pai_Final': pai_final,
                'Pai_Imediato': pai_final,
                'Componente': componente,
                'Nível': 'Filho'
            })

# Criar DataFrame da hierarquia
df_hierarquia = pd.DataFrame(hierarquia)

st.subheader("📘 Hierarquia Pai-Filho Completa")
st.dataframe(df_hierarquia, use_container_width=True)

# Mostrar quantidade de pais únicos
pais_unicos = df_hierarquia['Pai_Final'].drop_duplicates()
st.subheader("🔍 Quantidade de Pais Finais Únicos Encontrados na Estrutura:")
st.metric(label="Pais Finais", value=len(pais_unicos))

# Download do Excel da hierarquia
buffer = BytesIO()
df_hierarquia.to_excel(buffer, index=False)
st.download_button("📥 Baixar Hierarquia em Excel", buffer.getvalue(), file_name="hierarquia_estrutura.xlsx")
