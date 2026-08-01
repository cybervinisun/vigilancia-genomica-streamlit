# 📊 Vigilância Genômica e Epidemiológica — Dashboards

Dashboards interativos para visualização de dados de vigilância epidemiológica de arboviroses (dengue, chikungunya, zika) no Brasil, com dados reais e ao vivo via API pública do [InfoDengue](https://info.dengue.mat.br/) (parceria Fiocruz/FGV).

Projeto desenvolvido como demonstração de habilidades em ciência de dados aplicada à saúde pública, integrando visualização interativa, consumo de APIs e comparação entre frameworks (Python/Streamlit e R/Shiny).

## 🔗 Acesse os dashboards publicados

| App | Framework | Link |
|---|---|---|
| Vigilância de Arboviroses (dados reais) | Streamlit | **[Abrir no Streamlit Community Cloud](https://vigilancia-genomica-app-vvnutarygmjpgvncuxkvrw.streamlit.app)** |
| Vigilância de Arboviroses (dados reais) | R Shiny | **[Abrir no Posit Connect Cloud](https://connect.posit.cloud/bestaceleste/content/019fb8f5-6865-c13d-1c62-a77447b59fe9)** |

## 📁 Estrutura do repositório

- `app_vigilancia_real.py` — dashboard Streamlit com dados reais e ao vivo do InfoDengue (série temporal, incidência por 100k habitantes, nível de alerta por cidade).
- `app.R` — versão equivalente em R/Shiny do dashboard acima, usando os mesmos dados e a mesma fonte.
- `app.py` — exemplo/protótipo com dados sintéticos de compostos químicos, ilustrando a mesma estrutura de painel aplicada a outro domínio (triagem de candidatos a fármacos).
- `gerar_dados_exemplo.py` — script que gera o dataset sintético usado no `app.py`.

## 🛠️ Como rodar localmente

**Streamlit (Python):**
```bash
pip install -r requirements.txt
streamlit run app_vigilancia_real.py
```

**Shiny (R):**
```r
install.packages(c("shiny", "ggplot2", "dplyr"))
shiny::runApp("app.R")
```

## 📡 Fonte dos dados

Dados públicos e em tempo real via [API do InfoDengue](https://info.dengue.mat.br/services/api/doc) (parceria Fiocruz / FGV EMAp) — o mesmo tipo de sistema de vigilância utilizado pela Rede Genômica Fiocruz.

## 🧰 Stack

`Python` · `R` · `Streamlit` · `Shiny` · `Plotly` · `ggplot2` · `Pandas` · `dplyr`

---

**Autor:** Vinícius Nunes da Rocha — [Lattes](https://lattes.cnpq.br/5217191640471435) · [ORCID](https://orcid.org/0000-0002-2557-3871)
