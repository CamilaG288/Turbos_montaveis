import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura da planilha do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade real: Qtde. Abe - (Qtde. Separ - Qtde. Ate)
df["QUANTIDADE_REAL"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

# Filtra apenas linhas com QUANTIDADE_REAL > 0
df_filtrado = df[df["QUANTIDADE_REAL"] > 0]

# Seleciona colunas para exibir e exportar (usa nomes reais das colunas)
colunas_exibir = [
    "Cliente", "Produto", "Pedido", "Descricao",
    "Qtde.Ate", "Qtde. Separ", "Qtde. Abe", "QUANTIDADE_REAL"
]
df_resultado = df_filtrado[colunas_exibir]

# Exibe no painel
st.dataframe(df_resultado)

# Função para converter em Excel
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    return output

# Arquivo para download
arquivo_excel = converter_para_excel(df_resultado)

# Botão de download
st.download_button(
    label="📥 Baixar Resultado em Excel",
    data=arquivo_excel,
    file_name="analise_pedidos_quantidade_real.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
