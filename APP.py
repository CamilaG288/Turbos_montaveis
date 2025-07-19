import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Produzir + Estrutura Nível 2")

def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    return output

# --- ETAPA 1: PEDIDOS ---

URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

# Quantidade a produzir
df_pedidos["Quantidade_Produzir"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])

# Palavras a excluir pela descrição (coluna 8)
desc_excluir_pedidos = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
df_pedidos["Descricao"] = df_pedidos["Descricao"].astype(str).str.upper()

df_pedidos_filtrados = df_pedidos[
    (df_pedidos["Quantidade_Produzir"] > 0) &
    (~df_pedidos["Descricao"].str.contains("|".join(desc_excluir_pedidos)))
].copy()

colunas_exibir = [
    "Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"
]
df_exibir = df_pedidos_filtrados[colunas_exibir]

st.subheader("📌 Pedidos com Quantidade a Produzir > 0")
st.dataframe(df_exibir)

st.download_button(
    label="📥 Baixar Pedidos com Qtde. Real > 0",
    data=converter_para_excel(df_exibir),
    file_name="pedidos_quantidade_produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- ETAPA 2: ESTRUTURA ---

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

# Filtrar fantasmas e filhos válidos
df_estrutura_limpa = df_estrutura[
    (df_estrutura.iloc[:, 19] != "S") & (df_estrutura.iloc[:, 15].notna())
].copy()

# Criar dicionário: pai → [(filho, qtd)]
estrutura_dict = {}
for _, row in df_estrutura_limpa.iterrows():
    pai = row.iloc[1]
    filho = row.iloc[15]
    qtd = row.iloc[22]
    if pd.notna(pai) and pd.notna(filho) and pd.notna(qtd):
        estrutura_dict.setdefault(pai, []).append((filho, qtd))

# Palavras para exclusão pela descrição dos componentes (coluna R = 17)
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
        if any(palavra in desc1 for palavra in desc_excluir_componentes):
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
                    "Qtd Necessária": qtd_produzir * qtd1 * qtd2,
                    "Cliente": pedido["Cliente"],
                    "Pedido": pedido["Pedido"]
                })
        else:
            estrutura_final.append({
                "Pai Final": pai_final,
                "Componente": filho1,
                "Nível": 1,
                "Qtd por Unidade": qtd1,
                "Qtd Produzir": qtd_produzir,
                "Qtd Necessária": qtd_produzir * qtd1,
                "Cliente": pedido["Cliente"],
                "Pedido": pedido["Pedido"]
            })

df_estrutura_n2 = pd.DataFrame(estrutura_final)

st.subheader("🧬 Estrutura Explodida Nível 1 e 2 (Itens válidos)")
st.dataframe(df_estrutura_n2)

st.download_button(
    label="📥 Baixar Estrutura Explodida Nível 2",
    data=converter_para_excel(df_estrutura_n2),
    file_name="estrutura_nivel_2_filtrada.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
