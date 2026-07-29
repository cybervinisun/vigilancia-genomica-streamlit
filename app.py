"""
Exemplo/teste: dashboard Streamlit com estatísticas básicas sobre um
conjunto de compostos (mesma estrutura do seu pipeline de curadoria).

Como rodar (WSL):
    pip install streamlit pandas plotly
    streamlit run app.py

Isso abre um servidor local (normalmente http://localhost:8501) que você
acessa pelo navegador do Windows normalmente -- o WSL2 expõe a porta
automaticamente pro Windows.

Para usar com o SEU csv real: troque o nome do arquivo na linha do
pd.read_csv() abaixo. As colunas usadas aqui (compound_id, Ki_nM, IC50_nM,
pKa_predito, MW, LogP, docking_score, receptor_subtype) são só um
exemplo -- ajuste os nomes para bater com o seu dataset.
"""
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Painel de Compostos - Teste", layout="wide")

st.title("Painel de Compostos — Estatísticas Básicas (exemplo)")
st.caption(
    "Dados sintéticos, gerados só para testar o app. Troque pelo seu CSV "
    "real (mesmas colunas) quando quiser rodar com dados de verdade."
)

# ---------- Carregar dados ----------
df = pd.read_csv("dados_exemplo_compostos.csv")

# ---------- Filtro na barra lateral ----------
st.sidebar.header("Filtros")
subtipos = sorted(df["receptor_subtype"].unique())
subtipo_selecionado = st.sidebar.multiselect(
    "Subtipo de receptor (GluN2x)", subtipos, default=subtipos
)
faixa_mw = st.sidebar.slider(
    "Faixa de massa molecular (MW)",
    float(df["MW"].min()), float(df["MW"].max()),
    (float(df["MW"].min()), float(df["MW"].max())),
)

df_filtrado = df[
    df["receptor_subtype"].isin(subtipo_selecionado)
    & df["MW"].between(*faixa_mw)
]

st.write(f"**{len(df_filtrado)}** compostos após o filtro (de {len(df)} no total).")

# ---------- Tabela ----------
with st.expander("Ver tabela de dados filtrados"):
    st.dataframe(df_filtrado, width='stretch')

# ---------- Estatísticas descritivas ----------
st.subheader("Estatísticas descritivas")
colunas_numericas = ["MW", "LogP", "pKa_predito", "Ki_nM", "IC50_nM", "docking_score"]
st.dataframe(df_filtrado[colunas_numericas].describe().round(2), width='stretch')

# ---------- Distribuição ----------
st.subheader("Distribuição de uma variável")
variavel = st.selectbox("Escolha a variável", colunas_numericas, index=4)  # Ki_nM
fig_hist = px.histogram(
    df_filtrado, x=variavel, color="receptor_subtype", nbins=30,
    marginal="box", title=f"Distribuição de {variavel}"
)
st.plotly_chart(fig_hist, width='stretch')

# ---------- Correlação ----------
st.subheader("Correlação entre variáveis numéricas")
corr = df_filtrado[colunas_numericas].corr(numeric_only=True)
fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
st.plotly_chart(fig_corr, width='stretch')

# ---------- Dispersão simples ----------
st.subheader("Dispersão: potência (Ki) x afinidade estrutural (docking)")
fig_scatter = px.scatter(
    df_filtrado, x="docking_score", y="Ki_nM", color="receptor_subtype",
    log_y=True, hover_data=["compound_id"],
)
st.plotly_chart(fig_scatter, width='stretch')
