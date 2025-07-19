# Leitura da estrutura
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Converter para string e limpar espaços
df_estrutura.iloc[:, 1] = df_estrutura.iloc[:, 1].astype(str).str.strip()   # Coluna B - pai
df_estrutura.iloc[:, 15] = df_estrutura.iloc[:, 15].astype(str).str.strip() # Coluna P - filho

# Filtrar: remover fantasmas (coluna 19 == "S") e filhos nulos
df_estrutura_filtrada = df_estrutura[
    (df_estrutura.iloc[:, 19] != "S") & (df_estrutura.iloc[:, 15].notna())
]

# Ignorar pais terminados com "P"
df_estrutura_filtrada = df_estrutura_filtrada[~df_estrutura_filtrada.iloc[:, 1].str.endswith("P")]

# Construir lista de componentes
componentes_lista = []

for _, pedido in df_pedidos_filtrados.iterrows():
    produto_final = str(pedido["Produto"]).strip()
    quantidade_real = pedido["QUANTIDADE_REAL"]

    filhos = df_estrutura_filtrada[df_estrutura_filtrada.iloc[:, 1] == produto_final]

    for _, filho in filhos.iterrows():
        cod_componente = filho.iloc[15]  # Coluna P
        qtd_por_unidade = filho.iloc[23]  # Coluna W

        componentes_lista.append({
            "Produto Final": produto_final,
            "Componente": cod_componente,
            "Quantidade por Unidade": qtd_por_unidade,
            "Quantidade Real do Pedido": quantidade_real,
            "Qtde Necessária do Componente": quantidade_real * qtd_por_unidade,
            "Cliente": pedido["Cliente"],
            "Pedido": pedido["Pedido"]
        })

df_componentes = pd.DataFrame(componentes_lista)

# Exibe e permite download
st.subheader("🧮 Componentes Necessários por Estrutura")
st.dataframe(df_componentes)

st.download_button(
    label="📥 Baixar Componentes Necessários",
    data=converter_para_excel(df_componentes),
    file_name="componentes_necessarios.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
