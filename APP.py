import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Real")

# Leitura da planilha direto do GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df = pd.read_excel(URL_PEDIDOS)

# Exibe colunas e índices para checagem
st.write("Colunas e seus índices:")
for i, col in enumerate(df.columns):
    st.write(f"{i}: {col}")

# Cálculo com base nos índices: P (15), Q (16), N (13)
df["QUANTIDADE_REAL"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

# Seleção de colunas para exibir/salvar
colunas_exibir = df.columns[[0, 1, 15, 16, 13]].tolist()
colunas_exibir.append("QUANTIDADE_REAL")
df_resultado = df[colunas_exibir]

# Mostra os dados na tela
st.dataframe(df_resultado)

# Geração do arquivo Excel para download
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultado')
    output.seek(0)
    return output

arquivo_excel = converter_para_excel(df_resultado)

st.download_button(
    label="📥 Baixar Resultado em Excel",
    data=arquivo_excel,
    file_name="analise_pedidos_quantidade_real.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
