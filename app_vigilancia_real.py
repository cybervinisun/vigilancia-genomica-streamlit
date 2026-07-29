"""
Amostra de "boas-vindas" com DADOS REAIS (não sintéticos!) de vigilância
epidemiológica de arboviroses no Brasil, via API pública do InfoDengue
(parceria Fiocruz/FGV) -- o mesmo tipo de sistema de vigilância que a
Rede Genômica Fiocruz usa/alimenta (ex.: o painel de variantes de dengue
lançado pela rede em 2024/2026).

Fonte dos dados: https://info.dengue.mat.br/services/api/doc (API pública,
sem necessidade de chave/autenticação).

Como rodar:
    source venv/bin/activate   # (o mesmo venv que você já criou)
    streamlit run app_vigilancia_real.py

Precisa de internet ativa no WSL pra puxar os dados na hora (a API é
consultada ao vivo, então os números mudam conforme a semana
epidemiológica mais recente publicada).
"""
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Vigilância de Arboviroses — InfoDengue/Fiocruz", layout="wide")

st.title("Vigilância Epidemiológica de Arboviroses — dados reais (InfoDengue/Fiocruz)")
st.caption(
    "Dados públicos e ao vivo, via API do InfoDengue (parceria Fiocruz/FGV). "
    "Mesmo tipo de vigilância que a Rede Genômica Fiocruz monitora (ex.: o "
    "painel de variantes de dengue lançado pela rede)."
)

# IBGE geocode de algumas capitais (fixo -- pode adicionar outras cidades
# se souber o geocode do IBGE)
CIDADES = {
    "Rio de Janeiro (RJ)": 3304557,
    "São Paulo (SP)": 3550308,
    "Curitiba (PR)": 4106902,
    "Florianópolis (SC)": 4205407,
    "Belo Horizonte (MG)": 3106200,
    "Recife (PE)": 2611606,
}

DOENCAS = {"Dengue": "dengue", "Chikungunya": "chikungunya", "Zika": "zika"}


@st.cache_data(ttl=3600, show_spinner="Buscando dados na API do InfoDengue...")
def buscar_dados(geocode, doenca, ey_start, ey_end):
    url = (
        "https://info.dengue.mat.br/api/alertcity"
        f"?geocode={geocode}&disease={doenca}&format=csv"
        f"&ew_start=1&ew_end=53&ey_start={ey_start}&ey_end={ey_end}"
    )
    df = pd.read_csv(url)
    return df


# ---------- Sidebar ----------
st.sidebar.header("Filtros")
doenca_nome = st.sidebar.selectbox("Doença", list(DOENCAS.keys()))
cidades_selecionadas = st.sidebar.multiselect(
    "Cidades", list(CIDADES.keys()), default=["Rio de Janeiro (RJ)", "Curitiba (PR)", "Florianópolis (SC)"]
)
ano_inicio, ano_fim = st.sidebar.select_slider(
    "Período (anos)", options=list(range(2020, 2027)), value=(2024, 2026)
)

if not cidades_selecionadas:
    st.warning("Selecione ao menos uma cidade na barra lateral.")
    st.stop()

# ---------- Buscar e juntar dados ----------
frames = []
erros = []
for nome_cidade in cidades_selecionadas:
    geocode = CIDADES[nome_cidade]
    try:
        df_cidade = buscar_dados(geocode, DOENCAS[doenca_nome], ano_inicio, ano_fim)
        df_cidade["cidade"] = nome_cidade
        frames.append(df_cidade)
    except Exception as e:
        erros.append(f"{nome_cidade}: {e}")

if erros:
    st.error(
        "Não consegui buscar dados para algumas cidades (provavelmente sem "
        "internet no momento, ou a API está fora do ar):\n" + "\n".join(erros)
    )

if not frames:
    st.stop()

df = pd.concat(frames, ignore_index=True)
df["data_iniSE"] = pd.to_datetime(df["data_iniSE"])

st.write(f"**{len(df)}** semanas epidemiológicas carregadas, para **{doenca_nome}** em {len(cidades_selecionadas)} cidade(s).")

with st.expander("Ver tabela de dados"):
    st.dataframe(df, width="stretch")

# ---------- Estatísticas descritivas ----------
st.subheader("Estatísticas descritivas")
colunas_numericas = ["casos", "casos_est", "inc", "p_inc100k", "rt"]
colunas_presentes = [c for c in colunas_numericas if c in df.columns]
st.dataframe(df[colunas_presentes].describe().round(2), width="stretch")

# ---------- Série temporal ----------
st.subheader(f"Casos estimados de {doenca_nome} ao longo do tempo")
fig_serie = px.line(
    df.sort_values("data_iniSE"), x="data_iniSE", y="casos_est", color="cidade",
    labels={"data_iniSE": "Semana epidemiológica", "casos_est": "Casos estimados"},
)
st.plotly_chart(fig_serie, width="stretch")

# ---------- Incidência por 100k ----------
if "p_inc100k" in df.columns:
    st.subheader("Incidência por 100 mil habitantes")
    fig_inc = px.line(
        df.sort_values("data_iniSE"), x="data_iniSE", y="p_inc100k", color="cidade",
    )
    st.plotly_chart(fig_inc, width="stretch")

# ---------- Nível de alerta ----------
if "nivel" in df.columns:
    st.subheader("Semanas por nível de alerta (1=verde ... 4=vermelho)")
    contagem_nivel = df.groupby(["cidade", "nivel"]).size().reset_index(name="semanas")
    fig_nivel = px.bar(
        contagem_nivel, x="cidade", y="semanas", color="nivel", barmode="stack",
        color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(fig_nivel, width="stretch")

st.caption("Fonte: InfoDengue (info.dengue.mat.br) — parceria Fiocruz / FGV EMAp.")
