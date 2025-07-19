import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Hierarquia Pai-Filho", layout="wide")
st.title("🔗 Hierarquia Completa: Pai, Filho, Neto e além")

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

# Construir hierarquia completa
hierarquia = []

# Mapeia estrutura pai-filho para múltiplos níveis
mapa_pai_filho = estrutura.groupby('Pai_Final')['Componente'].apply(list).to_dict()

# Função recursiva para percorrer todos os níveis
def construir_hierarquia(pai_final, pai_imediato, componente, nivel):
    hierarquia.append({
        'Pai_Final': pai_final,
        'Pai_Imediato': pai_imediato,
        'Componente': componente,
        'Nível': nivel
    })
    filhos = mapa_pai_filho.get(componente, [])
    for filho in filhos:
        construir_hierarquia(pai_final, componente, filho, f"Nível {int(nivel.split()[-1]) + 1}")

# Inicia com todos os pais finais
for _, row in estrutura.iterrows():
    if row['Nivel'] == '1':
        construir_hierarquia(row['Pai_Final'], row['Pai_Final'], row['Componente'], 'Nível 1')

# Criar DataFrame
df_hierarquia = pd.DataFrame(hierarquia)

st.subheader("📘 Estrutura Pai → Componente (Todos os Níveis)")
st.dataframe(df_hierarquia, use_container_width=True)

# Download Excel
buffer = BytesIO()
df_hierarquia.to_excel(buffer, index=False)
st.download_button("📥 Baixar Estrutura Hierárquica Completa", buffer.getvalue(), file_name="estrutura_pai_filho_completa.xlsx")
