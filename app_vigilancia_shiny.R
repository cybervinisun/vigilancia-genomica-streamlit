# Amostra de "boas-vindas" em R Shiny -- versao paralela ao
# app_vigilancia_real.py, com os MESMOS dados reais e ao vivo de
# vigilancia epidemiologica de arboviroses (InfoDengue / Fiocruz-FGV).
#
# Diferenca de modelo mental em relacao ao Streamlit:
#   - Streamlit: o script inteiro reroda do zero a cada interacao.
#   - Shiny: voce separa "ui" (o layout/aparencia) de "server" (a logica),
#     e usa expressoes reativas (reactive({...})) que so recalculam
#     quando algo que elas dependem muda -- mais parecido com uma
#     planilha de Excel que recalcula so as celulas afetadas.
#
# Como rodar (no R/RStudio no Windows):
#   install.packages(c("shiny", "ggplot2", "dplyr"))
#   shiny::runApp("app_vigilancia_shiny.R")
# (ou abra o arquivo no RStudio e clique em "Run App")

library(shiny)
library(ggplot2)
library(dplyr)

# Geocode do IBGE das mesmas 6 capitais do exemplo em Python
CIDADES <- c(
  "Rio de Janeiro (RJ)" = 3304557,
  "Sao Paulo (SP)"      = 3550308,
  "Curitiba (PR)"       = 4106902,
  "Florianopolis (SC)"  = 4205407,
  "Belo Horizonte (MG)" = 3106200,
  "Recife (PE)"         = 2611606
)

DOENCAS <- c("Dengue" = "dengue", "Chikungunya" = "chikungunya", "Zika" = "zika")

# Busca os dados na API publica do InfoDengue -- mesma fonte do app em
# Python. read.csv() consegue ler direto de uma URL, sem precisar de
# nenhum pacote extra de HTTP.
buscar_dados <- function(geocode, doenca, ano_inicio, ano_fim) {
  url <- paste0(
    "https://info.dengue.mat.br/api/alertcity",
    "?geocode=", geocode,
    "&disease=", doenca,
    "&format=csv",
    "&ew_start=1&ew_end=53",
    "&ey_start=", ano_inicio,
    "&ey_end=", ano_fim
  )
  read.csv(url, stringsAsFactors = FALSE)
}

# ---------------- UI (aparencia/layout) ----------------
ui <- fluidPage(
  titlePanel("Vigilancia Epidemiologica de Arboviroses - dados reais (InfoDengue/Fiocruz)"),
  helpText("Dados publicos e ao vivo, via API do InfoDengue (parceria Fiocruz/FGV)."),

  sidebarLayout(
    sidebarPanel(
      selectInput("doenca", "Doenca", choices = names(DOENCAS)),
      checkboxGroupInput(
        "cidades", "Cidades",
        choices = names(CIDADES),
        selected = c("Rio de Janeiro (RJ)", "Curitiba (PR)", "Florianopolis (SC)")
      ),
      sliderInput("anos", "Periodo (anos)", min = 2020, max = 2026,
                  value = c(2024, 2026), step = 1, sep = "")
    ),

    mainPanel(
      tabsetPanel(
        tabPanel("Tabela", tableOutput("tabela")),
        tabPanel("Estatisticas descritivas", verbatimTextOutput("estatisticas")),
        tabPanel("Serie temporal", plotOutput("grafico_serie")),
        tabPanel("Incidencia por 100k", plotOutput("grafico_incidencia"))
      )
    )
  )
)

# ---------------- SERVER (logica/reatividade) ----------------
server <- function(input, output, session) {

  # reactive({...}) so roda de novo quando input$doenca, input$cidades
  # ou input$anos mudam -- e o resultado fica em cache ate la.
  dados <- reactive({
    req(input$cidades)  # nao faz nada se nenhuma cidade selecionada
    doenca_codigo <- DOENCAS[[input$doenca]]

    lista <- lapply(input$cidades, function(nome_cidade) {
      geocode <- CIDADES[[nome_cidade]]
      df <- tryCatch(
        buscar_dados(geocode, doenca_codigo, input$anos[1], input$anos[2]),
        error = function(e) NULL
      )
      if (!is.null(df)) df$cidade <- nome_cidade
      df
    })

    bind_rows(lista)
  })

  output$tabela <- renderTable({
    head(dados(), 50)
  })

  output$estatisticas <- renderPrint({
    colunas <- intersect(c("casos", "casos_est", "inc", "p_inc100k", "rt"), names(dados()))
    summary(dados()[, colunas, drop = FALSE])
  })

  output$grafico_serie <- renderPlot({
    df <- dados()
    df$data_iniSE <- as.Date(df$data_iniSE)
    ggplot(df, aes(x = data_iniSE, y = casos_est, color = cidade)) +
      geom_line(linewidth = 1) +
      labs(x = "Semana epidemiologica", y = "Casos estimados",
           title = paste("Casos estimados de", input$doenca)) +
      theme_minimal()
  })

  output$grafico_incidencia <- renderPlot({
    df <- dados()
    df$data_iniSE <- as.Date(df$data_iniSE)
    ggplot(df, aes(x = data_iniSE, y = p_inc100k, color = cidade)) +
      geom_line(linewidth = 1) +
      labs(x = "Semana epidemiologica", y = "Incidencia por 100 mil hab.") +
      theme_minimal()
  })
}

shinyApp(ui = ui, server = server)
