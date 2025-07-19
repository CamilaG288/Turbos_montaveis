import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Resumo de Componentes", layout="wide")
st.title("📦 Resumo Consolidado - Necessidades por Componente (Nível 1 e 2)")

def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resumo")
    output.seek(0)
    return output

# --- ETAPA 1: CARREGAR PEDIDOS ---

URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade a produzir
df_pedidos["Quantidade_Produzir"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])

# Normalização
df_pedidos["Descricao"] = df_pedidos["Descricao"].astype(str).str.upper()
df_pedidos["Tp.Doc"] = df_pedidos["Tp.Doc"].astype(str).str.strip().str.upper()

# Filtros de exclusão
desc_excluir_pedidos = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
tipos_doc_excluir = ["PCONS", "PEF"]

df_pedidos_filtrados = df_pedidos[
    (df_pedidos["Quantidade_Produzir"] > 0) &
    (~df_pedidos["Descricao"].str.contains("|".join(desc_excluir_pedidos))) &
    (~df_pedidos["Tp.Doc"].isin(tipos_doc_excluir))
].copy()

# --- ETAPA 2: CARREGAR ESTRUTURA ---

URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Normalização
df_estrutura.iloc[:, 1] = df_estrutura.iloc[:, 1].astype(str).str.strip()  # Pai final
df_estrutura.iloc[:, 15] = df_estrutura.iloc[:, 15].astype(str).str.strip()  # Filho
df_estrutura.iloc[:, 22] = (
    df_estrutura.iloc[:, 22]
    .astype(str).str.replace(",", ".", regex=False)
    .astype(float)
)

# Limpa fantasmas e nulos
df_estrutura_limpa = df_estrutura[
    (df_estrutura.iloc[:, 19] != "S") & (df_estrutura.iloc[:, 15].notna())
].copy()

# Dicionário pai → [(filho, qtd)]
estrutura_dict = {}
for _, row in df_estrutura_limpa.iterrows():
    pai = row.iloc[1]
    filho = row.iloc[15]
    qtd = row.iloc[22]
    if pd.notna(pai) and pd.notna(filho) and pd.notna(qtd):
        estrutura_dict.setdefault(pai, []).append((filho, qtd))

# Exclusões por descrição de componentes
desc_excluir_componentes = [
    "SACO PLASTICO", "CAIXA", "PLAQUETA", "REBITE", "ETIQUETA", "CERTIFICADO", "CINTA PLASTICA"
]

estrutura_final = []

for _, pedido in df_pedidos_filtrados.iterrows():
    pai_final = str(pedido["Produto"]).strip()
    qtd_produzir = pedido["Quantidade_Produzir"]
    filhos_n1 = estrutura_dict.get(pai_final, [])

    for filho1, qtd1 in filhos_n1:
        desc1 = df_estrutura_limpa[df_estrutura_limpa.iloc[:, 15] == filho1].iloc[0, 17].upper()
        if any(p in desc1 for p in desc_excluir_componentes):
            continue

        if filho1.endswith("P"):
            filhos_p = estrutura_dict.get(filho1, [])
            for filho2, qtd2 in filhos_p:
                desc2 = df_estrutura_limpa[df_estrutura_limpa.iloc[:, 15] == filho2].iloc[0, 17].upper()
                if any(p in desc2 for p in desc_excluir_componentes):
                    continue
                estrutura_final.append({
                    "Pai Final": pai_final,
                    "Componente": filho2,
                    "Nível": 2,
                    "Qtd por Unidade": qtd1 * qtd2,
                    "Qtd Produzir": qtd_produzir,
                    "Qtd Necessária": qtd_produzir * qtd1 * qtd2
                })
        else:
            estrutura_final.append({
                "Pai Final": pai_final,
                "Componente": filho1,
                "Nível": 1,
                "Qtd por Unidade": qtd1,
                "Qtd Produzir": qtd_produzir,
                "Qtd Necessária": qtd_produzir * qtd1
            })

df_estrutura_n2 = pd.DataFrame(estrutura_final)

# --- ETAPA 3: RESUMO AGRUPADO ---

# Agrupamento consolidado
df_resumo = df_estrutura_n2.groupby(
    ["Pai Final", "Componente", "Nível"]
).agg({
    "Qtd por Unidade": "first",
    "Qtd Produzir": "sum",
    "Qtd Necessária": "sum"
}).reset_index()

# Buscar descrição do componente
df_descricoes = df_estrutura[[df_estrutura.columns[15], df_estrutura.columns[17]]].drop_duplicates()
df_descricoes.columns = ["Componente", "Descricao_Componente"]

# Junta no resumo
df_resumo = pd.merge(df_resumo, df_descricoes, on="Componente", how="left")

# Reorganizar colunas
df_resumo = df_resumo[
    ["Pai Final", "Componente", "Descricao_Componente", "Nível", "Qtd por Unidade", "Qtd Produzir", "Qtd Necessária"]
]

# --- EXIBIÇÃO ---

st.subheader("📊 Consolidado - Componentes por Produto Final")
st.dataframe(df_resumo)

st.download_button(
    label="📥 Baixar Resumo Consolidado",
    data=converter_para_excel(df_resumo),
    file_name="resumo_componentes_consolidado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
