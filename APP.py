import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real + Componentes Necessários")

# Função auxiliar para exportar Excel
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    return output

# --- ETAPA 1: Análise dos Pedidos ---

# Leitura da planilha de pedidos
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade real: Qtde. Abe - (Qtde. Separ - Qtde. Ate)
df_pedidos["QUANTIDADE_REAL"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])

# Filtrar pedidos com QUANTIDADE_REAL > 0
df_pedidos_filtrados = df_pedidos[df_pedidos["QUANTIDADE_REAL"] > 0].copy()

# Selecionar colunas úteis
colunas_exibir = [
    "Cliente", "Produto", "Pedido", "Descricao",
    "Qtde.Ate", "Qtde. Separ", "Qtde. Abe", "QUANTIDADE_REAL"
]
df_exibir = df_pedidos_filtrados[colunas_exibir]

# Exibir pedidos válidos
st.subheader("📌 Pedidos com Quantidade Real > 0")
st.dataframe(df_exibir)

# Botão para baixar pedidos filtrados
st.download_button(
    label="📥 Baixar Pedidos com Qtde. Real > 0",
    data=converter_para_excel(df_exibir),
    file_name="pedidos_quantidade_real.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- ETAPA 2: Componentes por Estrutura (corrigido) ---

# Leitura da estrutura de produtos
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Conversão e limpeza das colunas importantes
df_estrutura.iloc[:, 1] = df_estrutura.iloc[:, 1].astype(str).str.strip()    # Coluna B - p
