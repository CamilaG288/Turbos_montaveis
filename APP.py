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

# --- ETAPA 2: Componentes por Estrutura ---

# Leitura da estrutura de produtos
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Renomeia colunas importantes
df_estrutura = df_estrutura.rename(columns={
    "B": "COD_PAI",
    "P": "COD_FILHO",
    "W": "QTD_POR_UNIDADE",
    "S": "FANTASMA"
})

# Remove fantasmas e filhos nulos
df_estrutura = df_estrutura[(df_estrutura["FANTASMA"] != "S") & (df_estrutura["COD_FILHO"].notna())]

# Remove apenas os conjuntos com "P" como PAI (mas mantém os filhos vivos)
df_estrutura["COD_PAI"] = df_estrutura["COD_PAI"].astype(str)
df_estrutura["COD_FILHO"] = df_estrutura["COD_FILHO"].astype(str)
df_estrutura = df_estrutura[~df_estrutura["COD_PAI"].str.endswith("P")]

# Lista de componentes a gerar
componentes_lista = []

for _, pedido in df_pedidos_filtrados.iterrows():
    produto_final = str(pedido["Produto"]).strip()
    quantidade_real = pedido["QUANTIDADE_REAL"]

    # Busca componentes diretos (nível 1)
    filhos = df_estrutura[df_estrutura["COD_PAI"] == produto_final]

    for _, filho in filhos.iterrows():
        cod_componente = filho["COD_FILHO"]
        qtd_por_unidade = filho["QTD_POR_UNIDADE"]

        componentes_lista.append({
            "Produto Final": produto_final,
            "Componente": cod_componente,
            "Quantidade por Unidade": qtd_por_unidade,
            "Quantidade Real do Pedido": quantidade_real,
            "Qtde Necessária do Componente": quantidade_real * qtd_por_unidade,
            "Cliente": pedido["Cliente"],
            "Pedido": pedido["Pedido"]
        })

# Monta dataframe com os componentes
df_componentes = pd.DataFrame(componentes_lista)

# Exibir tabela de componentes
st.subheader("🧮 Componentes Necessários por Estrutura")
st.dataframe(df_componentes)

# Botão para baixar componentes
st.download_button(
    label="📥 Baixar Componentes Necessários",
    data=converter_para_excel(df_componentes),
    file_name="componentes_necessarios.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
