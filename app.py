import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy import stats
import os
from io import BytesIO
import dash_bootstrap_components as dbc
import unicodedata
from load_data import load_filters, load_variable_data, combine_data_with_filters, load_multiple_variables

# Inicializando o app Dash com tema Bootstrap
# app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Necessário para Elastic Beanstalk

# Função para normalizar texto (remover acentos)
def normalize_text(text):
    """Remove acentos e converte para minúsculas para comparação."""
    if not text:
        return ""
    # Normalizar para decompor caracteres acentuados (ex.: 'ã' -> 'a' + '~')
    normalized = unicodedata.normalize('NFKD', str(text))
    # Remover diacríticos (acentos) e converter para minúsculas
    return ''.join(c for c in normalized if not unicodedata.combining(c)).lower()

# # Função para carregar arquivos da seção
# def load_section_files(area):
#     section_path = f"../data/dw/{area}/"
#     files = [f for f in os.listdir(section_path) if f.endswith('.xlsx')]
#     return files

# Pega o diretório onde o script está rodando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'dw') # Aponta para a pasta correta

def load_section_files(area):
    """Carrega os nomes dos arquivos de uma determinada seção."""
    section_path = os.path.join(DATA_DIR, area) # Caminho agora é absoluto
    if not os.path.exists(section_path):
        print(f"Aviso: O diretório não foi encontrado: {section_path}")
        return []
    return [f for f in os.listdir(section_path) if f.endswith('.xlsx')]

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

# Função para calcular estatísticas
def calculate_statistics(df, variavel, iqr_multiplier=1.5):
### --- Código para validação das bibliotecas e do join no load_data.py --- ###

    # stats_result = {}
    # test_data = [0.1683943758618205, 0.1620977241191381, 0.163068919876716, 0.1681304393463355, 
    #              0.1801848566900228, 0.1861701572810068, 0.1911233408523403, 0.1960505982627124, 
    #              0.1873534914332561, 0.174532931273655, 0.1898552894342499, 0.1813390463457654, 
    #              0.1733742477811903, 0.1704589930843963, 0.1944022019148184, 0.07300360441573536, 
    #              0.1828029737904217, 0.0388038347042544, 0.09990405093895749, 0.0978581013179412, 
    #              0.08955969834464803, 0.09480092461753206, 0.1002783035770839]
    # df_clean = pd.Series(test_data)
    # print(f"Valores de teste: {df_clean.tolist()}")
    # print(f"Média: {df_clean.mean():.4f}, Desvio Padrão: {df_clean.std():.4f}")
    # stats_result['mean'] = df_clean.mean()
    # stats_result['median'] = df_clean.median()
    # stats_result['std_dev'] = df_clean.std()
    # kurtosis_scipy_pearson = stats.kurtosis(df_clean, nan_policy='omit', fisher=False)
    # kurtosis_scipy_fisher = stats.kurtosis(df_clean, nan_policy='omit', fisher=True)
    # kurtosis_pandas = df_clean.kurtosis()
    # print(f"Curtose (Scipy Pearson): {kurtosis_scipy_pearson:.2f}")
    # print(f"Curtose (Scipy Fisher): {kurtosis_scipy_fisher:.2f}")
    # print(f"Curtose (Pandas Fisher): {kurtosis_pandas:.2f}")
    # stats_result['kurtosis'] = kurtosis_scipy_pearson
    # q1 = df_clean.quantile(0.25)
    # q3 = df_clean.quantile(0.75)
    # iqr = q3 - q1
    # stats_result['lower_fence'] = q1 - iqr_multiplier * iqr
    # stats_result['upper_fence'] = q3 + iqr_multiplier * iqr
    # return stats_result

    ## Definição para as variáveis para calcular estatisticas
    stats_result = {}
    if variavel in df.columns:
        df[variavel] = pd.to_numeric(df[variavel], errors='coerce')
        df_clean = df[variavel].dropna()
        if not df_clean.empty:
            stats_result['mean'] = df_clean.mean()
            stats_result['median'] = df_clean.median()
            stats_result['std_dev'] = df_clean.std()
            stats_result['kurtosis'] = stats.kurtosis(df_clean, nan_policy='omit', fisher=False)
            # Calcular cercas
            q1 = df_clean.quantile(0.25)
            q3 = df_clean.quantile(0.75)
            iqr = q3 - q1
            stats_result['lower_fence'] = q1 - iqr_multiplier * iqr
            stats_result['upper_fence'] = q3 + iqr_multiplier * iqr
        else:
            stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']}
    else:
        stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']}
    return stats_result

# Layout do app
app.layout = dbc.Container([
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
            dbc.NavItem(dbc.NavLink("Sobre", href="/")),
            dbc.NavItem(dbc.NavLink("Ambiental", href="/ambiental")),
            dbc.NavItem(dbc.NavLink("Saúde", href="/saude")),
            dbc.NavItem(dbc.NavLink("Geografia", href="/geografia")),
            dbc.NavItem(dbc.NavLink("Predição", href="/predicao")),
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
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Ambiental", href="/ambiental", active="exact"),
                dbc.NavLink("Saúde", href="/saude", active="exact"),
                dbc.NavLink("Geografia", href="/geografia", active="exact"),
                dbc.NavLink("Predição", href="/predicao", active="exact"),
                dbc.NavLink("Correlação", href="/correlacao", active="exact"),
            ], vertical=True, pills=True),
        ], md=2, className="bg-light d-none d-md-block"),  # Mostrar apenas em desktops

        # Conteúdo principal
        dbc.Col([
            html.H1("Dashboard Interativo", className="text-center my-3"),
            html.Div(id='page-content')
        ], md=10)
    ])
], fluid=True)

# Layout da página Home/Inicial
sobre_layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.Div([
                html.H1("Bem-vindo ao Dashboard Interativo", className="text-primary text-center mt-4 mb-3"),
                html.P(
                    "Uma ferramenta para análise exploratória de dados ambientais, de saúde e geográficos.",
                    className="lead text-center"
                )
            ]),
            width=12
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
                dbc.NavLink("Objetivos do Projeto", href="#objetivos", external_link=True),
                dbc.NavLink("Funcionalidades", href="#funcionalidades", external_link=True),
                dbc.NavLink("Como Utilizar", href="#como-utilizar", external_link=True),
                dbc.NavLink("Cálculos Estatísticos", href="#calculos", external_link=True),
                dbc.NavLink("O que é o IQR?", href="#iqr", external_link=True),
                dbc.NavLink("Quem Somos", href="#quem-somos", external_link=True),
            ], vertical=True, pills=True, className="bg-light p-2 rounded"), # Estilo de "pílulas" para visual melhor
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

# Layout da página de análise (Ambiental, Saúde, Geografia, Predição)
analysis_layout = dbc.Card([
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

        dcc.Graph(id="grafico-1"),
        html.Div(id='estatisticas-1', className="mt-4"), # Margem acima dos KPIs

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

            dcc.Graph(id="grafico-2"),
            html.Div(id='estatisticas-2', className="mt-4"),

            dbc.Button("Exportar Dados do Gráfico", id="export-analysis-data-2", color="success", outline=True, className="mt-3 w-100", style={'display': 'none'}),
        ])
    ])
], className="mb-4")

# Layout da página de correlação
correlation_layout = dbc.Card([
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
            dcc.Graph(id="corr-scatter"),

            dbc.Row([
                dbc.Col(dbc.Button("Exportar Matriz de Correlação", id="export-corr-matrix", color="secondary", outline=True, className="w-100 mt-2"), md=6),
                dbc.Col(dbc.Button("Exportar Dados Brutos", id="export-raw-data", color="secondary", outline=True, className="w-100 mt-2"), md=6),
            ], className="mt-5"),
        ])
    ])
], className="mb-4")

                            ## -- INICIO DOS CALLBACKS DE CONTEÚDO -- ##

# Callback para atualizar o conteúdo da página
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    # Se o pathname for a raiz, mostre a página Sobre
    if pathname == '/':
        return sobre_layout
    
    # Remove a barra para checar as outras seções
    section = pathname.strip('/')
    
    if section == 'sobre':
        return sobre_layout
    elif section in ['ambiental', 'saude', 'geografia', 'predicao']:
        return analysis_layout
    elif section == 'correlacao':
        return correlation_layout
    
    # Se nenhuma página corresponder, mostre uma mensagem de erro
    return dbc.Alert(
        [
            html.H4("Erro 404: Página não encontrada", className="alert-heading"),
            html.P(f"O caminho '{pathname}' não foi reconhecido. Por favor, use o menu para navegar."),
        ],
        color="danger",
        className="mt-4"
    )

# Callback para carregar filtros em cache
@app.callback(
    Output('filtros-store', 'data'),
    [Input('url', 'pathname')]
)
def store_filters(pathname):
    filtros_df = load_filters()
    return filtros_df.to_json(date_format='iso', orient='split')

# Callback para atualizar variáveis no dropdown (análise)
@app.callback(
    [Output('variavel-dropdown', 'options'), Output('variavel-dropdown-2', 'options')],
    [Input('url', 'pathname')]
)
def update_variable_dropdown(pathname):
    section = pathname.strip('/')
    if section in ['ambiental', 'saude', 'geografia', 'predicao']:
        files = load_section_files(section)
        # Ordenar alfabeticamente, ignorando maiúsculas/minúsculas
        files = sorted(files, key=lambda x: str.lower(x))
        variable_options = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
        return variable_options, variable_options
    return [], []

# Callback para controlar visibilidade e habilitação dos dropdowns (Gráfico 1)
@app.callback(
    [
        Output('ano-slider-container-1', 'style'),
        Output('ano-rangeslider', 'disabled'),   
        Output('municipio-dropdown-container-1', 'style'),
        Output('municipio-dropdown', 'disabled'),
        Output('graph-type-dropdown-container-1', 'style'),
        Output('graph-type-dropdown-1', 'disabled'),
        Output('iqr-multiplier-container-1', 'style'),
        Output('iqr-multiplier-1', 'disabled'),
        Output('municipio-dropdown', 'value'),
        Output('graph-type-dropdown-1', 'value'),
        Output('iqr-multiplier-1', 'value')
    ],
    [
        Input('variavel-dropdown', 'value'),
        Input('ano-rangeslider', 'value'),      
        Input('municipio-dropdown', 'value'),
        Input('graph-type-dropdown-1', 'value')
    ],
    [
        State('municipio-dropdown', 'value'),
        State('graph-type-dropdown-1', 'value'),
        State('iqr-multiplier-1', 'value')
    ]
)
def control_dropdowns_1(variavel, anos, municipios, graph_type, 
                        current_municipios, current_graph_type, current_iqr):
    # Padrões iniciais
    ano_style = {'display': 'none'}
    ano_disabled = True
    municipio_style = {'display': 'none'}
    municipio_disabled = True
    graph_type_style = {'display': 'none'}
    graph_type_disabled = True
    iqr_style = {'display': 'none'}
    iqr_disabled = True
    reset_municipios = current_municipios
    reset_graph_type = current_graph_type
    reset_iqr = current_iqr

    triggered_input = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    # Lógica de hierarquia
    if variavel:
        ano_style, ano_disabled = {'display': 'block'}, False
        if triggered_input == 'variavel-dropdown':
             reset_municipios, reset_graph_type, reset_iqr = [], None, 1.5
        if anos:
            municipio_style, municipio_disabled = {'display': 'block'}, False
            if triggered_input == 'ano-rangeslider':
                 reset_municipios, reset_graph_type, reset_iqr = [], None, 1.5
            if municipios:
                graph_type_style, graph_type_disabled = {'display': 'block'}, False
                if triggered_input == 'municipio-dropdown':
                     reset_graph_type, reset_iqr = 'bar', 1.5
                if graph_type == 'box':
                    iqr_style, iqr_disabled = {'display': 'block'}, False

    return (ano_style, ano_disabled, municipio_style, municipio_disabled, 
            graph_type_style, graph_type_disabled, iqr_style, iqr_disabled,
            reset_municipios, reset_graph_type, reset_iqr)

# Callback para controlar visibilidade e habilitação dos dropdowns (Gráfico 2)
@app.callback(
    [
        Output('ano-slider-container-2', 'style'),
        Output('ano-rangeslider-2', 'disabled'), 
        Output('municipio-dropdown-container-2', 'style'),
        Output('municipio-dropdown-2', 'disabled'), 
        Output('graph-type-dropdown-container-2', 'style'),
        Output('graph-type-dropdown-2', 'disabled'),
        Output('iqr-multiplier-container-2', 'style'),
        Output('iqr-multiplier-2', 'disabled'),
        Output('municipio-dropdown-2', 'value'), 
        Output('graph-type-dropdown-2', 'value'),
        Output('iqr-multiplier-2', 'value')
    ],
    [
        Input('variavel-dropdown-2', 'value'),   
        Input('ano-rangeslider-2', 'value'),     
        Input('municipio-dropdown-2', 'value'),  
        Input('graph-type-dropdown-2', 'value')
    ],
    [
        State('municipio-dropdown-2', 'value'),  
        State('graph-type-dropdown-2', 'value'),
        State('iqr-multiplier-2', 'value')
    ]
)
def control_dropdowns_2(variavel, anos, municipios, graph_type,
                        current_municipios, current_graph_type, current_iqr):
    # Padrões iniciais
    ano_style = {'display': 'none'}
    ano_disabled = True
    municipio_style = {'display': 'none'}
    municipio_disabled = True
    graph_type_style = {'display': 'none'}
    graph_type_disabled = True
    iqr_style = {'display': 'none'}
    iqr_disabled = True
    reset_municipios = current_municipios
    reset_graph_type = current_graph_type
    reset_iqr = current_iqr

    # Usamos o callback_context para saber qual input disparou a função
    ctx = dash.callback_context
    if not ctx.triggered:
        triggered_input = 'No input yet'
    else:
        triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # Lógica de hierarquia
    if variavel:
        ano_style, ano_disabled = {'display': 'block'}, False
        if triggered_input == 'variavel-dropdown-2':
             reset_municipios, reset_graph_type, reset_iqr = [], 'bar', 1.5
        if anos:
            municipio_style, municipio_disabled = {'display': 'block'}, False
            if triggered_input == 'ano-rangeslider-2':
                 reset_municipios, reset_graph_type, reset_iqr = [], 'bar', 1.5
            if municipios:
                graph_type_style, graph_type_disabled = {'display': 'block'}, False
                if triggered_input == 'municipio-dropdown-2':
                     reset_graph_type, reset_iqr = 'bar', 1.5
                if graph_type == 'box':
                    iqr_style, iqr_disabled = {'display': 'block'}, False
                else: # Esconde o IQR se não for boxplot
                    iqr_style, iqr_disabled = {'display': 'none'}, True


    return (ano_style, ano_disabled, municipio_style, municipio_disabled, 
            graph_type_style, graph_type_disabled, iqr_style, iqr_disabled,
            reset_municipios, reset_graph_type, reset_iqr)

# Callback para atualizar e configurar os RangeSliders de ano
@app.callback(
    [Output('ano-rangeslider', 'min'), Output('ano-rangeslider', 'max'),
     Output('ano-rangeslider', 'marks'), Output('ano-rangeslider', 'value'),
     Output('ano-rangeslider-2', 'min'), Output('ano-rangeslider-2', 'max'),
     Output('ano-rangeslider-2', 'marks'), Output('ano-rangeslider-2', 'value')],
    [Input('filtros-store', 'data')]
)
def update_ano_slider(filtros_json):
    if not filtros_json:
        # Retorna valores vazios se não houver dados
        no_data = (None, None, {}, None) * 2
        return no_data
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    anos = sorted(filtros_df['ANO'].unique())
    
    if not anos:
        no_data = (None, None, {}, None) * 2
        return no_data

    min_ano, max_ano = int(anos[0]), int(anos[-1])
    
    # Criar marcas (labels) para cada ano no slider
    marks = {int(ano): {'label': str(ano), 'style': {'transform': 'rotate(45deg)'}} for ano in anos}
    
    # Define o valor inicial do slider (todo o intervalo selecionado)
    initial_value = [min_ano, max_ano]
    
    # Retorna os mesmos valores para ambos os sliders
    return min_ano, max_ano, marks, initial_value, min_ano, max_ano, marks, initial_value

# Callback para atualizar dropdown de municípios (análise)
@app.callback(
    [Output('municipio-dropdown', 'options'), Output('municipio-dropdown-2', 'options')],
    [Input('ano-rangeslider', 'value'),
     Input('ano-rangeslider-2', 'value'),
     Input('filtros-store', 'data')]
)
def update_cidade_dropdown(year_range_1, year_range_2, filtros_json):
    if not filtros_json:
        return [], []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    
    city_options_1 = []
    if year_range_1:
        # Gera a lista completa de anos a partir do intervalo [inicio, fim]
        all_years_1 = list(range(year_range_1[0], year_range_1[1] + 1))
        df_filtered = filtros_df[filtros_df['ANO'].isin(all_years_1)]
        cities = sorted(df_filtered['NM_MUN'].unique(), key=str.lower)
        city_options_1 = [{'label': city, 'value': city} for city in cities]
    
    city_options_2 = []
    if year_range_2:
        # Repete a lógica para o segundo slider
        all_years_2 = list(range(year_range_2[0], year_range_2[1] + 1))
        df_filtered = filtros_df[filtros_df['ANO'].isin(all_years_2)]
        cities = sorted(df_filtered['NM_MUN'].unique(), key=str.lower)
        city_options_2 = [{'label': city, 'value': city} for city in cities]
    
    return city_options_1, city_options_2

# Callback para mostrar/esconder segundo gráfico e atualizar texto do botão
@app.callback(
    [Output('second-graph-container', 'style'),
     Output('toggle-second-graph', 'children')],
    [Input('toggle-second-graph', 'n_clicks')]
)
def toggle_second_graph(n_clicks):
    # n_clicks é None na primeira vez que a página carrega
    if n_clicks is None:
        n_clicks = 0

    # Se o número de cliques for par, o gráfico está escondido
    if n_clicks % 2 == 0:
        style = {'display': 'none'}
        button_text = "Adicionar Segundo Gráfico"
    # Se for ímpar, o gráfico está visível
    else:
        style = {'display': 'block'}
        button_text = "Remover Segundo Gráfico"
        
    return style, button_text

# Callback para atualizar gráficos e estatísticas (análise)
@app.callback(
    [Output('grafico-1', 'figure'), Output('estatisticas-1', 'children'),
     Output('grafico-2', 'figure'), Output('estatisticas-2', 'children'),
     Output('analysis-data-store-1', 'data'),
     Output('analysis-data-store-2', 'data'),
     Output('export-analysis-data-1', 'style'),
     Output('export-analysis-data-2', 'style')
     ],
    [Input('variavel-dropdown', 'value'), 
     Input('ano-rangeslider', 'value'),
     Input('municipio-dropdown', 'value'), 
     Input('graph-type-dropdown-1', 'value'),
     Input('iqr-multiplier-1', 'value'), 
     Input('variavel-dropdown-2', 'value'), 
     Input('ano-rangeslider-2', 'value'),
     Input('municipio-dropdown-2', 'value'), 
     Input('graph-type-dropdown-2', 'value'),
     Input('iqr-multiplier-2', 'value'),
     Input('url', 'pathname'), 
     Input('filtros-store', 'data')]
)
def update_graph_and_statistics(variavel_1, year_range_1, municipios_1, graph_type_1, iqr_multiplier_1,
                                  variavel_2, year_range_2, municipios_2, graph_type_2, iqr_multiplier_2,
                                  pathname, filtros_json):

    years_1 = list(range(year_range_1[0], year_range_1[1] + 1)) if year_range_1 else None
    years_2 = list(range(year_range_2[0], year_range_2[1] + 1)) if year_range_2 else None
    section = pathname.strip('/')

    fig_1, stats_1_content = go.Figure(), []
    fig_2, stats_2_content = go.Figure(), []

    data_json_1, data_json_2 = None, None
    btn_style_1 = {'display': 'none'}
    btn_style_2 = {'display': 'none'}
    
    if not section or not filtros_json:
        return fig_1, stats_1_content, fig_2, stats_2_content, data_json_1, data_json_2, btn_style_1, btn_style_2

    filtros_df = pd.read_json(filtros_json, orient='split')
    graph_labels = {'NM_MUN': 'Município', 'VALOR': 'Valor', 'ANO': 'Ano'}
    kpi_titles = {
        "mean": "Média", "median": "Mediana", "std_dev": "Desvio Padrão",
        "kurtosis": "Curtose", "lower_fence": "Cerca Inferior", "upper_fence": "Cerca Superior"
    }

    # --- Processamento para o Gráfico 1 ---
    if variavel_1 and years_1 and municipios_1 and graph_type_1:
        variable_df_1 = load_variable_data(section, variavel_1) 
        combined_df_1 = combine_data_with_filters(filtros_df, variable_df_1, years=years_1, municipios=municipios_1)
        
        if not combined_df_1.empty:
            # Armazena o dataframe e torna o botão visível
            data_json_1 = combined_df_1.to_json(date_format='iso', orient='split')
            btn_style_1 = {'display': 'block'}

            # 1. DETECÇÃO INICIAL DE OUTLIERS (sempre acontece)
            all_outliers_1, stats_per_group_1 = [], []
            for municipality, group_df in combined_df_1.groupby('NM_MUN'):
                iqr_value = iqr_multiplier_1 if graph_type_1 == 'box' and iqr_multiplier_1 else 1.5
                stats_data = calculate_statistics(group_df.copy(), 'VALOR', iqr_multiplier=iqr_value)
                stats_data['Município'] = municipality
                stats_per_group_1.append(stats_data)
                if stats_data.get('lower_fence') is not None:
                    outliers_in_group = group_df[(group_df['VALOR'] < stats_data['lower_fence']) | (group_df['VALOR'] > stats_data['upper_fence'])]
                    if not outliers_in_group.empty:
                        all_outliers_1.append(outliers_in_group)
            
            outliers_df_1 = pd.concat(all_outliers_1) if all_outliers_1 else pd.DataFrame()
            stats_df_1 = pd.DataFrame(stats_per_group_1)
            
            # --- LÓGICA DE EXIBIÇÃO HÍBRIDA PARA ESTATÍSTICAS 1 ---
            if not stats_df_1.empty:
                if len(municipios_1) == 1:
                    # Caso 1: Apenas um município selecionado -> Mostrar KPI cards
                    single_stats = stats_df_1.iloc[0].to_dict()
                    kpi_cards = [create_kpi_card(title, single_stats.get(key)) for key, title in kpi_titles.items()]
                    stats_1_content.append(dbc.Row(kpi_cards, className="mt-4"))
                else:
                    # Caso 2: Múltiplos municípios -> Mostrar tabela detalhada
                    stats_1_content.append(html.H4("Estatísticas por Município", className="mt-4"))
                    cols_order = ['Município', 'mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']
                    stats_df_1_ordered = stats_df_1[[col for col in cols_order if col in stats_df_1.columns]]
                    stats_1_content.append(dbc.Table.from_dataframe(stats_df_1_ordered.rename(columns={
                        'mean': 'Média', 'median': 'Mediana', 'std_dev': 'Desvio Padrão',
                        'kurtosis': 'Curtose', 'lower_fence': 'Cerca Inf.', 'upper_fence': 'Cerca Sup.'
                    }).round(2), striped=True, bordered=True, hover=True, responsive=True))

            # Criação dos Gráficos
            title_1 = f'{variavel_1} - {section}'
            if graph_type_1 == 'bar': fig_1 = px.bar(combined_df_1, x='ANO', y='VALOR', color='NM_MUN', title=title_1, barmode='group', labels=graph_labels)
            elif graph_type_1 == 'line': fig_1 = px.line(combined_df_1, x='ANO', y='VALOR', color='NM_MUN', title=title_1, labels=graph_labels)
            elif graph_type_1 == 'box': fig_1 = px.box(combined_df_1, x='ANO', y='VALOR', color='NM_MUN', title=title_1, labels=graph_labels)
            
            if not outliers_df_1.empty and graph_type_1 != 'box':
                fig_1.add_trace(go.Scatter(x=outliers_df_1['ANO'], y=outliers_df_1['VALOR'], mode='markers', marker=dict(color='red', size=10, symbol='x'), name='Outliers', customdata=outliers_df_1['NM_MUN'], hovertemplate='Município: %{customdata}<br>Ano: %{x}<br>Valor: %{y}<extra></extra>'))
            
            if not outliers_df_1.empty:
                stats_1_content.append(html.H4("Outliers Identificados", className="mt-4"))
                stats_1_content.append(dbc.Table.from_dataframe(outliers_df_1[['NM_MUN', 'ANO', 'VALOR']].rename(columns={'NM_MUN': 'Município', 'ANO': 'Ano', 'VALOR': 'Valor'}), striped=True, bordered=True, hover=True, responsive=True))

    # --- Processamento para o Gráfico 2 (LÓGICA IDÊNTICA) ---
    if variavel_2 and years_2 and municipios_2 and graph_type_2:
        variable_df_2 = load_variable_data(section, variavel_2)
        combined_df_2 = combine_data_with_filters(filtros_df, variable_df_2, years=years_2, municipios=municipios_2)
        
        if not combined_df_2.empty:
            # Armazena o dataframe e torna o botão visível
            data_json_2 = combined_df_2.to_json(date_format='iso', orient='split')
            btn_style_2 = {'display': 'block'}

            all_outliers_2, stats_per_group_2 = [], []
            for municipality, group_df in combined_df_2.groupby('NM_MUN'):
                iqr_value = iqr_multiplier_2 if graph_type_2 == 'box' and iqr_multiplier_2 else 1.5
                stats_data = calculate_statistics(group_df.copy(), 'VALOR', iqr_multiplier=iqr_value)
                stats_data['Município'] = municipality
                stats_per_group_2.append(stats_data)
                if stats_data.get('lower_fence') is not None:
                    outliers_in_group = group_df[(group_df['VALOR'] < stats_data['lower_fence']) | (group_df['VALOR'] > stats_data['upper_fence'])]
                    if not outliers_in_group.empty:
                        all_outliers_2.append(outliers_in_group)
            
            outliers_df_2 = pd.concat(all_outliers_2) if all_outliers_2 else pd.DataFrame()
            stats_df_2 = pd.DataFrame(stats_per_group_2)

            # --- LÓGICA DE EXIBIÇÃO HÍBRIDA PARA ESTATÍSTICAS 2 ---
            if not stats_df_2.empty:
                if len(municipios_2) == 1:
                    single_stats = stats_df_2.iloc[0].to_dict()
                    kpi_cards = [create_kpi_card(title, single_stats.get(key), color="success") for key, title in kpi_titles.items()]
                    stats_2_content.append(dbc.Row(kpi_cards, className="mt-4"))
                else:
                    stats_2_content.append(html.H4("Estatísticas por Município", className="mt-4"))
                    cols_order = ['Município', 'mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']
                    stats_df_2_ordered = stats_df_2[[col for col in cols_order if col in stats_df_2.columns]]
                    stats_2_content.append(dbc.Table.from_dataframe(stats_df_2_ordered.rename(columns={'mean': 'Média', 'median': 'Mediana', 'std_dev': 'Desvio Padrão', 'kurtosis': 'Curtose', 'lower_fence': 'Cerca Inf.', 'upper_fence': 'Cerca Sup.'}).round(2), striped=True, bordered=True, hover=True, responsive=True))

            title_2 = f'{variavel_2} - {section}'
            if graph_type_2 == 'bar': fig_2 = px.bar(combined_df_2, x='ANO', y='VALOR', color='NM_MUN', title=title_2, barmode='group', labels=graph_labels)
            elif graph_type_2 == 'line': fig_2 = px.line(combined_df_2, x='ANO', y='VALOR', color='NM_MUN', title=title_2, labels=graph_labels)
            elif graph_type_2 == 'box': fig_2 = px.box(combined_df_2, x='ANO', y='VALOR', color='NM_MUN', title=title_2, labels=graph_labels)
            
            if not outliers_df_2.empty and graph_type_2 != 'box':
                fig_2.add_trace(go.Scatter(x=outliers_df_2['ANO'], y=outliers_df_2['VALOR'], mode='markers', marker=dict(color='red', size=10, symbol='x'), name='Outliers', customdata=outliers_df_2['NM_MUN'], hovertemplate='Município: %{customdata}<br>Ano: %{x}<br>Valor: %{y}<extra></extra>'))
            
            if not outliers_df_2.empty:
                stats_2_content.append(html.H4("Outliers Identificados", className="mt-4"))
                stats_2_content.append(dbc.Table.from_dataframe(outliers_df_2[['NM_MUN', 'ANO', 'VALOR']].rename(columns={'NM_MUN': 'Município', 'ANO': 'Ano', 'VALOR': 'Valor'}), striped=True, bordered=True, hover=True, responsive=True))
            
    return fig_1, stats_1_content, fig_2, stats_2_content, data_json_1, data_json_2, btn_style_1, btn_style_2

# Callback para atualizar dropdowns de seção
@app.callback(
    [Output('section-dropdown-1', 'options'), Output('section-dropdown-2', 'options')],
    [Input('url', 'pathname')]
)
def update_section_dropdown(pathname):
    if pathname == '/correlacao':
        sections = ['ambiental', 'saude', 'geografia', 'predicao']
        sections = sorted(sections, key=str.lower)
        section_options = [{'label': section.capitalize(), 'value': section} for section in sections]
        return section_options, section_options
    return [], []


## Callback para atualizar dropdowns de variáveis
# @app.callback(
#     [Output('variable-dropdown-1', 'options'), Output('variable-dropdown-2', 'options')],
#     [Input('section-dropdown-1', 'value'), Input('section-dropdown-2', 'value')]
# )
# def update_variables_dropdown(section_1, section_2):
#     variable_options_1 = []
#     variable_options_2 = []
    
#     if section_1:
#         files = load_section_files(section_1)
#         files = sorted(files, key=lambda x: str.lower(x))
#         variable_options_1 = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
    
#     if section_2:
#         files = load_section_files(section_2)
#         files = sorted(files, key=lambda x: str.lower(x))
#         variable_options_2 = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
    
#     return variable_options_1, variable_options_2

# Callback para atualizar dropdowns de variáveis (agora um só)
@app.callback(
    Output('variable-dropdown-multi', 'options'),
    [Input('section-dropdown-1', 'value'), Input('section-dropdown-2', 'value')]
)
def update_multi_variable_dropdown(section_1, section_2):
    all_options = []
    seen_labels = set()

    def add_options(section):
        if section:
            files = load_section_files(section)
            for file in sorted(files, key=str.lower):
                label = file.split('.')[0]
                # Evita duplicatas se a mesma variável estiver em ambas as seções
                if label not in seen_labels:
                    # O valor agora inclui a seção para carregamento correto dos dados
                    all_options.append({'label': f"{label} ({section})", 'value': f"{section}|{label}"})
                    seen_labels.add(label)

    add_options(section_1)
    add_options(section_2)
    
    return all_options


                            ## -- INICIO DOS CALLBACKS DE ANÁLISE -- ##

# Callback para exportar dados do Gráfico 1
@app.callback(
    Output('download-analysis-data-1', 'data'),
    [Input('export-analysis-data-1', 'n_clicks')],
    [State('analysis-data-store-1', 'data'),
     State('variavel-dropdown', 'value')] # Pega o nome da variável para o arquivo
)
def export_analysis_data_1(n_clicks, data_json, variavel):
    if not n_clicks or not data_json or not variavel:
        return None
    
    df = pd.read_json(data_json, orient='split')
    
    # Normaliza o nome do arquivo
    clean_variavel = normalize_text(variavel).replace(" ", "_")
    filename = f"dados_{clean_variavel}.xlsx"
    
    # Exportar para Excel em memória
    buffer = BytesIO()
    df.to_excel(buffer, engine='openpyxl', index=False)
    buffer.seek(0)
    
    return dcc.send_bytes(buffer.getvalue(), filename)

# Callback para exportar dados do Gráfico 2
@app.callback(
    Output('download-analysis-data-2', 'data'),
    [Input('export-analysis-data-2', 'n_clicks')],
    [State('analysis-data-store-2', 'data'),
     State('variavel-dropdown-2', 'value')] # Pega o nome da variável para o arquivo
)
def export_analysis_data_2(n_clicks, data_json, variavel):
    if not n_clicks or not data_json or not variavel:
        return None
    
    df = pd.read_json(data_json, orient='split')
    
    # Normaliza o nome do arquivo
    clean_variavel = normalize_text(variavel).replace(" ", "_")
    filename = f"dados_{clean_variavel}.xlsx"

    # Exportar para Excel em memória
    buffer = BytesIO()
    df.to_excel(buffer, engine='openpyxl', index=False)
    buffer.seek(0)
    
    return dcc.send_bytes(buffer.getvalue(), filename)

                                ## -- INICIO DA SEÇÃO DE CORRELAÇÃO -- ##


# Callback para atualizar dropdown de anos (correlação)
@app.callback(
    [Output('corr-ano-rangeslider', 'min'), Output('corr-ano-rangeslider', 'max'),
     Output('corr-ano-rangeslider', 'marks'), Output('corr-ano-rangeslider', 'value')],
    [Input('filtros-store', 'data')]
)
def update_corr_ano_slider(filtros_json):
    if not filtros_json:
        return None, None, {}, None
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    anos = sorted(filtros_df['ANO'].unique())
    
    if not anos:
        return None, None, {}, None

    min_ano, max_ano = int(anos[0]), int(anos[-1])
    
    marks = {int(ano): {'label': str(ano), 'style': {'transform': 'rotate(45deg)'}} for ano in anos}
    
    initial_value = [min_ano, max_ano]
    
    return min_ano, max_ano, marks, initial_value

# Callback para atualizar dropdown de municípios (correlação)
@app.callback(
    Output('corr-municipios-dropdown', 'options'),
    [Input('corr-ano-rangeslider', 'value'), Input('filtros-store', 'data')]  # Input MODIFICADO
)
def update_corr_cidade_dropdown(year_range, filtros_json): # Argumento MODIFICADO
    if not filtros_json or not year_range:
        return []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    
    # Lógica MODIFICADA para lidar com um intervalo [inicio, fim]
    all_years = list(range(year_range[0], year_range[1] + 1))
    df_filtered = filtros_df[filtros_df['ANO'].isin(all_years)]
    
    cities = sorted(df_filtered['NM_MUN'].unique(), key=str.lower)
    city_options = [{'label': city, 'value': city} for city in cities]
    
    return city_options

# Callback para atualizar heatmap, tabela e armazenar dados
# @app.callback(
#     [Output('corr-heatmap', 'figure'), Output('corr-table', 'children'), Output('corr-data-store', 'data')],
#     [
#         Input('section-dropdown-1', 'value'), 
#         Input('section-dropdown-2', 'value'),
#         Input('variable-dropdown-1', 'value'),
#         Input('variable-dropdown-2', 'value'),
#         Input('corr-ano-rangeslider', 'value'),
#         Input('corr-municipios-dropdown', 'value'),
#         Input('corr-method-dropdown', 'value'), 
#         Input('filtros-store', 'data')
#     ]
# )
# def update_correlation_analysis(section_1, section_2, variable_1, variable_2, years_range, municipios, method, filtros_json): # Argumento MODIFICADO
#     heatmap_fig = go.Figure()
#     table = html.Div("Selecione seções, variáveis, anos e municípios para calcular a correlação.")
#     data_json = None
    
#     # Lógica MODIFICADA para verificar a nova entrada de anos
#     if not section_1 or not section_2 or not variable_1 or not variable_2 or not years_range or not municipios or not filtros_json:
#         return heatmap_fig, table, data_json
    
#     # Lógica ADICIONADA para criar a lista de anos a partir do intervalo
#     years = list(range(years_range[0], years_range[1] + 1))

#     # Criar lista de pares seção/variável
#     section_variable_pairs = [(section_1, variable_1), (section_2, variable_2)]
    
#     # Carregar dados combinados
#     df = load_multiple_variables(section_variable_pairs, years=years, municipios=municipios)
    
#     if df.empty or variable_1 not in df.columns or variable_2 not in df.columns:
#         return heatmap_fig, html.Div("Não há dados suficientes para as seleções feitas."), None

#     # Selecionar apenas as colunas das variáveis
#     variables = [variable_1, variable_2]
#     corr_matrix = df[variables].corr(method=method)
    
#     # Criar heatmap
#     heatmap_fig = px.imshow(
#         corr_matrix,
#         text_auto='.2f',
#         color_continuous_scale='RdBu_r',
#         zmin=-1,
#         zmax=1,
#         title=f'Matriz de Correlação ({method.capitalize()})'
#     )
    
#     # Criar tabela de correlação
#     table = dbc.Table.from_dataframe(
#         corr_matrix.round(3),
#         striped=True,
#         bordered=True,
#         hover=True,
#         responsive=True,
#         index=True # Garante que o índice (nomes das variáveis) seja exibido
#     )
    
#     # Armazenar dados no store
#     data_json = df.to_json(date_format='iso', orient='split')
    
#     return heatmap_fig, table, data_json

# Callback para atualizar a análise de correlação (heatmap, scatter e store)
@app.callback(
    [Output('corr-heatmap', 'figure'),
     Output('corr-data-store', 'data'),
     Output('scatter-x-axis-dropdown', 'options'),
     Output('scatter-y-axis-dropdown', 'options'),
     Output('scatter-x-axis-dropdown', 'value'),
     Output('scatter-y-axis-dropdown', 'value'),
     Output('correlation-results-container', 'style')],
    [Input('variable-dropdown-multi', 'value'),
     Input('corr-municipios-dropdown', 'value'),
     Input('corr-ano-rangeslider', 'value'),
     Input('corr-method-dropdown', 'value')]
)
def update_correlation_analysis(selected_variables, municipio, years_range, method):
    # Valores padrão para retorno
    heatmap_fig = go.Figure()
    scatter_options = []
    x_val, y_val = None, None
    data_json = None
    results_style = {'display': 'none'}

    # Condição de guarda: precisamos de ao menos 2 variáveis e todos os outros filtros
    if not selected_variables or len(selected_variables) < 2 or not municipio or not years_range:
        return heatmap_fig, data_json, scatter_options, scatter_options, x_val, y_val, results_style

    years = list(range(years_range[0], years_range[1] + 1))
    
    # Decodificar seção e variável do valor do dropdown
    section_variable_pairs = []
    clean_variable_names = []
    for val in selected_variables:
        section, variable_name = val.split('|')
        section_variable_pairs.append((section, variable_name))
        clean_variable_names.append(variable_name)

    # Carregar dados combinados
    df = load_multiple_variables(section_variable_pairs, years=years, municipios=[municipio])
    
    if df.empty or len(df.columns) < len(clean_variable_names):
        return heatmap_fig, data_json, scatter_options, scatter_options, x_val, y_val, results_style
    
    # Calcula matriz de correlação
    corr_matrix = df[clean_variable_names].corr(method=method)

    # Cirar Heatmap
    heatmap_fig = px.imshow(
        corr_matrix, text_auto='.2f', color_continuous_scale='RdBu_r', 
        zmin=-1, zmax=1, title=f'Matriz de Correlação ({method.capitalize()}) para {municipio}'
    )
    
    #Preparar dados para o próximo passo
    data_json = df.to_json(date_format='iso', orient='split')
    scatter_options = [{'label': var, 'value': var} for var in clean_variable_names]
    x_val, y_val = clean_variable_names[0], clean_variable_names[1]
    results_style = {'display': 'block'}
    return heatmap_fig, data_json, scatter_options, scatter_options, x_val, y_val, results_style


# Callback para atualizar scatter plot
# @app.callback(
#     Output('corr-scatter', 'figure'),
#     [
#         Input('corr-heatmap', 'clickData'), 
#         Input('corr-data-store', 'data'),
#         Input('variable-dropdown-1', 'value'),
#         Input('variable-dropdown-2', 'value')
#     ]
# )
# def update_scatter_plot(click_data, data_json, variable_1, variable_2):
#     scatter_fig = go.Figure()
    
#     if not data_json or not variable_1 or not variable_2:
#         return scatter_fig
    
#     df = pd.read_json(data_json, orient='split')
    
#     # Selecionar variáveis
#     x_var, y_var = variable_1, variable_2
    
#     # Atualizar com base no clique no heatmap
#     if click_data and 'points' in click_data:
#         point = click_data['points'][0]
#         x_idx, y_idx = point['x'], point['y']
#         if x_idx in [variable_1, variable_2] and y_idx in [variable_1, variable_2]:
#             x_var, y_var = x_idx, y_idx
    
#     # Criar scatter plot
#     scatter_fig = px.scatter(
#         df,
#         x=x_var,
#         y=y_var,
#         hover_data=['NM_MUN_filtros', 'ANO'],
#         title=f'{x_var} vs {y_var}'
#     )
    
#     return scatter_fig

# Callback para atualizar scatter plot com linha de tendência
@app.callback(
    Output('corr-scatter', 'figure'),
    [Input('corr-data-store', 'data'),
     Input('scatter-x-axis-dropdown', 'value'),
     Input('scatter-y-axis-dropdown', 'value')]
)
def update_scatter_plot(data_json, x_var, y_var):
    if not all([data_json, x_var, y_var]):
        return go.Figure()
    
    df = pd.read_json(data_json, orient='split')

    # Criar scatter plot com linha de tendência
    scatter_fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        hover_data=['ANO'],
        title=f'Dispersão: {y_var} vs. {x_var}',
        # Adiciona a linha de regressão linear
        trendline="ols",
        trendline_color_override="red"
    )
    
    return scatter_fig

# Callback para exportar matriz de correlação
@app.callback(
    Output('download-corr-matrix', 'data'),
    [Input('export-corr-matrix', 'n_clicks')],
    [
        State('corr-data-store', 'data'), 
        State('variable-dropdown-1', 'value'),
        State('variable-dropdown-2', 'value'),
        State('corr-method-dropdown', 'value')
    ]
)
def export_correlation_matrix(n_clicks, data_json, variable_1, variable_2, method):
    if not n_clicks or not data_json or not variable_1 or not variable_2:
        return None
    
    df = pd.read_json(data_json, orient='split')
    variables = [variable_1, variable_2]
    corr_matrix = df[variables].corr(method=method)
    
    # Exportar para Excel
    buffer = BytesIO()
    corr_matrix.to_excel(buffer, engine='openpyxl')
    buffer.seek(0)
    
    return dcc.send_bytes(buffer.getvalue(), "correlation_matrix.xlsx")

# Callback para exportar dados brutos
@app.callback(
    Output('download-raw-data', 'data'),
    [Input('export-raw-data', 'n_clicks')],
    [State('corr-data-store', 'data')]
)
def export_raw_data(n_clicks, data_json):
    if not n_clicks or not data_json:
        return None
    
    df = pd.read_json(data_json, orient='split')
    
    # Exportar para Excel
    buffer = BytesIO()
    df.to_excel(buffer, engine='openpyxl', index=False)
    buffer.seek(0)
    
    return dcc.send_bytes(buffer.getvalue(), "raw_data.xlsx")

                                    ## -- FIM DA SEÇÃO DE CORRELAÇÃO -- ##

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)


""" # Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True) """