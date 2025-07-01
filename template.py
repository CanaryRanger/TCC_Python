import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Função para criar um card de KPI
def create_kpi_card(title, value, color="primary"):
    """
    Cria um dbc.Col com um dbc.Card para exibir um indicador (KPI).
    """
    # Formata o valor para exibição, tratando casos onde o dado não está disponível
    display_value = f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"
    
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H6(title, className="card-title text-center text-muted"),
                html.H4(display_value, className=f"card-text text-center text-{color}"),
            ]),
            className="shadow-sm p-2" # Adiciona uma sombra suave e padding
        ),
        # Define a responsividade do grid
        md=2,  # Em telas médias (desktops), ocupa 2 de 12 colunas (6 cards por linha)
        sm=4,  # Em telas pequenas (tablets), ocupa 4 de 12 colunas (3 cards por linha)
        xs=6,  # Em telas extra pequenas (celulares), ocupa 6 de 12 colunas (2 cards por linha)
        className="mb-3" # Margem inferior para espaçamento
    )

# Função para criar o layout principal
def get_main_layout():
# Layout do app
    return dbc.Container([
        # Stores
        dcc.Store(id='filtros-store'),
        dcc.Store(id='corr-data-store'),
        dcc.Store(id='analysis-data-store-1'),
        dcc.Store(id='analysis-data-store-2'),
        # Downloads
        dcc.Download(id="download-corr-matrix"),
        dcc.Download(id="download-raw-data"),
        dcc.Download(id="download-analysis-data-1"),
        dcc.Download(id="download-analysis-data-2"),
        # Localização
        dcc.Location(id='url', refresh=False),   

        # Navbar para dispositivos móveis
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Ambiental", href="/ambiental")),
                dbc.NavItem(dbc.NavLink("Saúde", href="/saude")),
                dbc.NavItem(dbc.NavLink("Geografia", href="/geografia")),
                dbc.NavItem(dbc.NavLink("Predição", href="")),
                dbc.NavItem(dbc.NavLink("Correlação", href="/correlacao")),
            ],
            brand="Menu",
            brand_href="#",
            color="primary",
            dark=True,
            className="d-md-none"  # Esconder em desktops
        ),

        dbc.Row([
            # Sidebar para desktops
            dbc.Col([
                html.H2("Menu", className="text-center"),
                dbc.Nav([
                    dbc.NavLink("Home", href="/", active="exact", className="my-3"),
                    dbc.NavLink("Ambiental", href="/ambiental", active="exact"),
                    dbc.NavLink("Saúde", href="/saude", active="exact"),
                    dbc.NavLink("Geografia", href="/geografia", active="exact"),
                    dbc.NavLink("Predição", href=""),
                    dbc.NavLink("Correlação", href="/correlacao", active="exact"),
                ], vertical=True, pills=True, className="p-3"),
            ], md=2, className="bg-light d-none d-md-block"),  # Mostrar apenas em desktops

            # Conteúdo principal
            dbc.Col([
                html.H1("", className="text-center my-3"),
                html.Div(id='page-content')
            ], md=10)
        ], className="flex-grow-1")
    ], fluid=True
     , className="vh-100 d-flex flex-column")

# Função para criar o layout da Home/Sobre page
def get_sobre_layout():
    return dbc.Container([
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H1("Bem-vindo ao Dashboard Brasil", className="text-primary text-center mt-4 mb-3"),
                    html.P(
                        "Uma ferramenta para análise exploratória de dados ambientais, de saúde e geográficos.",
                        className="lead text-center"
                    )
                ]),
                md=12
            )
        ),

        html.Hr(className="my-4"),

        dbc.Row([
            # Coluna da esquerda com o menu de seções
            dbc.Col([
                html.H4("Navegue pelas Seções"),
                # MUDANÇA: Trocado dbc.ListGroup por dbc.Nav para uma navegação mais limpa e funcional
                dbc.Nav([
                    # IMPORTANTE: external_link=True força a rolagem da página pelo navegador
                    dbc.NavLink("Objetivos do Projeto", href="#objetivos", external_link=True, className="text-white"),
                    dbc.NavLink("Funcionalidades", href="#funcionalidades", external_link=True, className="text-white"),
                    dbc.NavLink("Como Utilizar", href="#como-utilizar", external_link=True, className="text-white"),
                    dbc.NavLink("Cálculos Estatísticos", href="#calculos", external_link=True, className="text-white"),
                    dbc.NavLink("O que é o IQR?", href="#iqr", external_link=True, className="text-white"),
                    dbc.NavLink("Quem Somos", href="#quem-somos", external_link=True, className="text-white"),
                ], vertical=True, pills=True, className="bg-dark p-2 rounded"), # Estilo de "pílulas" para visual melhor
            ], md=3, className="mb-4"),

            # Coluna da direita com o conteúdo
            dbc.Col([
                html.H2("Objetivos do Projeto", id="objetivos"),
                dcc.Markdown("""
                    *Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.*
                """),

                html.H2("Funcionalidades do Dashboard", id="funcionalidades", className="mt-5"),
                dcc.Markdown("""
                    *Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.*
                """),

                html.H2("Como Utilizar", id="como-utilizar", className="mt-5"),
                dcc.Markdown("""
                    *Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.*
                """),

                html.H2("Cálculos Estatísticos", id="calculos", className="mt-5"),
                dcc.Markdown("""
                    Para fornecer insights valiosos, nosso dashboard calcula automaticamente um conjunto de métricas estatísticas essenciais para cada variável analisada. Essas métricas ajudam a compreender a tendência central, a dispersão e a forma da distribuição dos dados.

                    - **Média:** O valor médio do conjunto de dados. É útil para ter uma ideia geral, mas pode ser influenciado por valores muito altos ou muito baixos.
                    - **Mediana:** O valor do meio, que divide os dados exatamente em duas partes. É uma medida mais robusta que a média quando existem outliers.
                    - **Desvio Padrão:** Indica o quão espalhados os dados estão em torno da média. Um valor baixo significa que os dados são consistentes e próximos da média; um valor alto indica grande variabilidade.
                    - **Curtose:** Uma medida que nos diz sobre as "caudas" da distribuição. Um valor alto de curtose sugere que existem mais valores extremos (outliers) do que o esperado em uma distribuição normal.
                """),

                html.H2("O que é o IQR e como detectamos Outliers?", id="iqr", className="mt-5"),
                dcc.Markdown("""
                    Um **outlier** é um ponto de dado que se diferencia significativamente dos outros. Identificá-los é crucial para encontrar anomalias ou erros.

                    Nosso dashboard usa o método do **Intervalo Interquartil (IQR)**, um padrão ouro na estatística, para encontrar esses pontos.

                    1.  **Quartis:** Primeiro, ordenamos os dados e os dividimos em quatro partes iguais. O ponto que separa os primeiros 25% dos dados é o **Primeiro Quartil (Q1)**, e o que separa os primeiros 75% é o **Terceiro Quartil (Q3)**.
                    2.  **Cálculo do IQR:** O IQR é simplesmente a distância entre esses dois quartis: `IQR = Q3 - Q1`. Essa faixa contém os 50% centrais e mais "típicos" dos seus dados.
                    3.  **Definindo as Cercas:** Para encontrar os outliers, criamos "cercas" imaginárias acima e abaixo dos dados:
                        - **Cerca Inferior:** `Q1 - 1.5 * IQR`
                        - **Cerca Superior:** `Q3 + 1.5 * IQR`

                    Qualquer dado que esteja fora desses limites é sinalizado como um outlier. O multiplicador de **1.5** é o padrão da indústria, mas em nosso dashboard, **você pode ajustar esse valor** no filtro do gráfico de Boxplot para realizar análises mais ou menos rigorosas.
                """),

                html.H2("Quem Somos", id="quem-somos", className="mt-5"),
                dcc.Markdown("""
                    *Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.*
                """),

            ], md=9)
        ])
    ], fluid=True, className="mt-3")

# Função para criar o layout da página de análise (Ambiental, Saúde, Geografia, Predição)
def get_analysis_layout():
    return dbc.Card([
        dbc.CardBody([
            # Filtro de Variável
            html.Div(dcc.Dropdown(id="variavel-dropdown", placeholder="Selecione a variável"), className="mb-3"),
            
            # Filtro de Ano
            html.Div(id="ano-slider-container-1", style={'display': 'none'}, children=[
                html.Label("Selecione o Intervalo de Anos:"),
                dcc.RangeSlider(id='ano-rangeslider', step=1, disabled=True, allowCross=False, className="mt-1")
            ], className="mb-3"),
            
            # Filtro de Município
            html.Div(id="municipio-dropdown-container-1", style={'display': 'none'}, children=[
                dcc.Dropdown(id="municipio-dropdown", multi=True, placeholder="Selecione o município", 
                            searchable=True, disabled=True)
            ], className="mb-3"),

            # Filtro de Tipo de Gráfico
            html.Div(id="graph-type-dropdown-container-1", style={'display': 'none'}, children=[
                dcc.Dropdown(id="graph-type-dropdown-1", 
                            options=[
                                {'label': 'Barras', 'value': 'bar'},
                                {'label': 'Linhas', 'value': 'line'},
                                {'label': 'Boxplot', 'value': 'box'}
                            ], 
                            value='bar', 
                            placeholder="Selecione o tipo de gráfico", 
                            disabled=True)
            ], className="mb-3"),

            # Filtro de IQR
            html.Div(id="iqr-multiplier-container-1", style={'display': 'none'}, children=[
                html.Label("Multiplicador do IQR para Cercas (padrão: 1.5):", 
                        title="Define a sensibilidade para identificar outliers...",
                        className="form-label"), # Usando form-label para um estilo melhor
                dcc.Input(id="iqr-multiplier-1", type="number", value=1.5, min=0.1, step=0.1, disabled=True)
            ], className="mb-4"), # Margem um pouco maior antes do gráfico

            # Área de Gráficos e Estatísticas com Spinner
            html.Div([
                dbc.Spinner(
                    html.Div(id='loading-spinner-1', style={'display': 'none'}),  # Spinner para gráfico 1
                    size="md",
                    color="primary",
                    type="border",
                    fullscreen=False  # Não cobre toda a tela, apenas a área local
                ),
                dcc.Graph(id="grafico-1"),
                html.Div(id='estatisticas-1', className="mt-4"), # Margem acima dos KPIS
            ], className="position-relative"),  # Posicionamento relativo para o spinner

            # Botão de Exportação para o Gráfico 1
            dbc.Button("Exportar Dados do Gráfico", id="export-analysis-data-1", color="success", outline=True, className="mt-3 w-100", style={'display': 'none'}),    

            # Botão para adicionar o segundo gráfico
            dbc.Button("Adicionar Segundo Gráfico", id="toggle-second-graph", n_clicks=0, color="primary", className="mt-4 mb-3 w-100"), # w-100 para ocupar a largura toda
            
            # Container do Segundo Gráfico
            html.Div(id="second-graph-container", style={'display': 'none'}, children=[
                html.Hr(), # Adiciona uma linha divisória
                html.Div(dcc.Dropdown(id="variavel-dropdown-2", placeholder="Selecione a variável"), className="mb-3 mt-4"), # Margem acima e abaixo
                
                html.Div(id="ano-slider-container-2", style={'display': 'none'}, children=[
                    html.Label("Selecione o Intervalo de Anos:"),
                    dcc.RangeSlider(id='ano-rangeslider-2', step=1, disabled=True, allowCross=False, className="mt-1")
                ], className="mb-3"),
                
                html.Div(id="municipio-dropdown-container-2", style={'display': 'none'}, children=[
                    dcc.Dropdown(id="municipio-dropdown-2", multi=True, placeholder="Selecione o município", searchable=True, disabled=True)
                ], className="mb-3"),

                html.Div(id="graph-type-dropdown-container-2", style={'display': 'none'}, children=[
                    dcc.Dropdown(id="graph-type-dropdown-2", 
                                options=[
                                    {'label': 'Barras', 'value': 'bar'},
                                    {'label': 'Linhas', 'value': 'line'},
                                    {'label': 'Boxplot', 'value': 'box'}
                                ], 
                                value='bar', 
                                placeholder="Selecione o tipo de gráfico", 
                                disabled=True)
                ], className="mb-3"),
                
                html.Div(id="iqr-multiplier-container-2", style={'display': 'none'}, children=[
                    html.Label("Multiplicador do IQR para Cercas (padrão: 1.5):",
                            title="Define a sensibilidade para identificar outliers...",
                            className="form-label"),
                    dcc.Input(id="iqr-multiplier-2", type="number", value=1.5, min=0.1, step=0.1, disabled=True)
                ], className="mb-4"),

                # Mesma lógica de área de gráfico que 1.
                html.Div([
                    dbc.Spinner(
                        html.Div(id='loading-spinner-2', style={'display': 'none'}),  # Spinner para gráfico 2
                        size="md",
                        color="primary",
                        type="border",
                        fullscreen=False
                    ),
                    dcc.Graph(id="grafico-2"),
                    html.Div(id='estatisticas-2', className="mt-4"),
                ], className="position-relative"),

                dbc.Button("Exportar Dados do Gráfico", id="export-analysis-data-2", color="success", outline=True, className="mt-3 w-100", style={'display': 'none'}),
            ])
        ])
    ], className="mb-4")

# Função para criar o layout da página de correlação
def get_correlation_layout():
    return dbc.Card([
        dbc.CardBody([
            html.H3("Análise de Correlação", className="mb-4"),
            html.P("Para uma análise estatisticamente válida, selecione as variáveis de interesse para um único município ao longo do tempo.", className="text-muted"),

            # --- SEÇÃO DE FILTROS ---
            dbc.Row([
                dbc.Col([
                    html.Label("Seção 1"),
                    dcc.Dropdown(id="section-dropdown-1", placeholder="Selecione a seção 1")
                ], md=6),
                dbc.Col([
                    html.Label("Seção 2 (Opcional)"),
                    dcc.Dropdown(id="section-dropdown-2", placeholder="Para adicionar variáveis de outra seção")
                ], md=6)
            ], className="mb-3"),
            
            html.Label("Selecione 2 ou mais variáveis para a matriz", className="mt-2"),
            dcc.Dropdown(id="variable-dropdown-multi", multi=True, placeholder="Selecione as variáveis"),
            
            html.Label("Selecione o Município", className="mt-3"),
            dcc.Dropdown(id="corr-municipios-dropdown", multi=False, placeholder="Selecione o município"),
            
            html.Label("Selecione o Intervalo de Anos", className="mt-3"),
            dcc.RangeSlider(id='corr-ano-rangeslider', step=1, allowCross=False, className="mt-1"),

            html.Label("Método de Correlação", className="mt-3"),
            dcc.Dropdown(id="corr-method-dropdown", 
                        options=[
                            {'label': 'Pearson', 'value': 'pearson'},
                            {'label': 'Spearman', 'value': 'spearman'},
                            {'label': 'Kendall', 'value': 'kendall'}
                        ], 
                        value='pearson'),
            
            html.Hr(),

            # --- SEÇÃO DE RESULTADOS (Controlada por callback) ---
            html.Div([
                dbc.Spinner(
                html.Div(id='corr-spinner', style={'display': 'none'}),  # Spinner para gráfico 1
                    size="md",
                    color="primary",
                    type="border",
                    fullscreen=False  # Não cobre toda a tela, apenas a área local
                ),
            ], className="mt-4 position-relative"),
            html.Div(id='correlation-results-container', style={'display': 'none'}, children=[
                html.Div([
                    html.H4("Matriz de Correlação", className="text-center"),
                    dcc.Graph(id="corr-heatmap"),
                ], className="mt-4"),

                html.H4("Gráfico de Dispersão Detalhado", className="text-center mt-4"),
                html.P("Escolha duas variáveis da sua seleção para visualizar a dispersão e a linha de tendência.", className="text-center text-muted"),
                dbc.Row([
                    dbc.Col(dcc.Dropdown(id='scatter-x-axis-dropdown', placeholder='Selecione a variável do Eixo X'), md=6),
                    dbc.Col(dcc.Dropdown(id='scatter-y-axis-dropdown', placeholder='Selecione a variável do Eixo Y'), md=6)
                ], className="mt-2 mb-3"),
                html.Div([
                    dbc.Spinner(
                    html.Div(id='scat-spinner', style={'display': 'none'}),  # Spinner para gráfico 1
                    size="md",
                    color="primary",
                    type="border",
                    fullscreen=False  # Não cobre toda a tela, apenas a área local
                    ),
                    dcc.Graph(id="corr-scatter"),
                ], className="mt-4 position-relative"),
                

                dbc.Row([
                    dbc.Col(dbc.Button("Exportar Matriz de Correlação", id="export-corr-matrix", color="info", outline=True, className="w-100 mt-2"), md=6),
                    dbc.Col(dbc.Button("Exportar Dados Brutos", id="export-raw-data", color="warning", outline=True, className="w-100 mt-2"), md=6),
                ], className="mt-5"),
            ])
        ])
    ], className="mb-4")