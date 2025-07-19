import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura da planilha do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Cálculo usando os índices: Qtde. Abe (15), Qtde. Separ (16), Qtde. Ate (13)
df["QUANTIDADE_REAL"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

# Seleção de colunas para exibir e exportar
colunas_exibir = [
    "Cliente", "Produto", "Pedido", "Descricao", "Qtde.Ate", "Qtde. Separ", "Qtde. Abe", "QUANTIDADE_REAL"
]
df_resultado = df[colunas_exibir]

# Mostra a tabela no painel
st.dataframe(df_resultado)

# Função para gerar arquivo Excel
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultado')
    output.seek(0)
    return output

# Botão de download
arquivo_excel = converter_para_excel(df_resultado)

st.download_button(
    label="📥 Baixar Resultado em Excel",
    data=arquivo_excel,
    file_name="analise_pedidos_quantidade_real.xlsx",
