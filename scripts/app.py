import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from scipy import stats
import os
from io import StringIO  # Adicionado para corrigir FutureWarning
from load_data import load_filters, load_variable_data, combine_data_with_filters

# Inicializando o app Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Função para carregar arquivos da seção
def load_section_files(area):
    section_path = f"../data/dw/{area}/"
    files = [f for f in os.listdir(section_path) if f.endswith('.xlsx')]
    return files

# Função para calcular estatísticas
def calculate_statistics(df, variavel):
    stats_result = {}
    if variavel in df.columns:
        df[variavel] = pd.to_numeric(df[variavel], errors='coerce')
        df_clean = df[variavel].dropna()
        if not df_clean.empty:
            stats_result['mean'] = df_clean.mean()
            stats_result['median'] = df_clean.median()
            stats_result['std_dev'] = df_clean.std()
            stats_result['kurtosis'] = stats.kurtosis(df_clean, nan_policy='omit')
        else:
            stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis']}
    else:
        stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis']}
    return stats_result

# Layout do app
app.layout = html.Div([
    dcc.Store(id='filtros-store'),
    dcc.Location(id='url', refresh=False),
    
    html.Div([
        html.H2("Menu"),
        dcc.Link("Ambiental", href="/ambiental", className="menu-item"),
        dcc.Link("Saúde", href="/saude", className="menu-item"),
        dcc.Link("Geografia", href="/geografia", className="menu-item"),
        dcc.Link("Predição", href="/predicao", className="menu-item"),
    ], className="sidebar"),

    html.Div([
        html.H1("Dashboard Interativo"),
        html.Div([
            html.H3("Gráfico 1"),
            dcc.Dropdown(id="ano-dropdown", multi=True, placeholder="Selecione o ano"),
            dcc.Dropdown(id="variavel-dropdown", placeholder="Selecione a variável"),
            dcc.Dropdown(id="municipio-dropdown", multi=True, placeholder="Selecione o município"),
            dcc.Dropdown(id="graph-type-dropdown-1", 
                         options=[
                             {'label': 'Barras', 'value': 'bar'},
                             {'label': 'Linhas', 'value': 'line'},
                             {'label': 'Boxplot', 'value': 'box'}
                         ], 
                         value='bar'),
            dcc.Graph(id="grafico-1"),
            html.Div(id='estatisticas-1'),
            
            html.Button("Adicionar Segundo Gráfico", id="toggle-second-graph", n_clicks=0),
            html.Div(id="second-graph-container", style={'display': 'none'}, children=[
                html.H3("Gráfico 2"),
                dcc.Dropdown(id="ano-dropdown-2", multi=True, placeholder="Selecione o ano"),
                dcc.Dropdown(id="municipio-dropdown-2", multi=True, placeholder="Selecione o município"),
                dcc.Dropdown(id="graph-type-dropdown-2", 
                             options=[
                                 {'label': 'Barras', 'value': 'bar'},
                                 {'label': 'Linhas', 'value': 'line'},
                                 {'label': 'Boxplot', 'value': 'box'}
                             ], 
                             value='bar'),
                dcc.Graph(id="grafico-2"),
                html.Div(id='estatisticas-2')
            ])
        ], className="content"),
    ], className="main-content")
])

# Callback para carregar filtros em cache
@app.callback(
    Output('filtros-store', 'data'),
    [Input('url', 'pathname')]
)
def store_filters(pathname):
    filtros_df = load_filters()
    return filtros_df.to_json(date_format='iso', orient='split')

# Callback para atualizar variáveis no dropdown
@app.callback(
    Output('variavel-dropdown', 'options'),
    [Input('url', 'pathname')]
)
def update_variable_dropdown(pathname):
    section = pathname.strip('/')
    if section:
        files = load_section_files(section)
        variable_options = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
        return variable_options
    return []

# Callback para atualizar dropdown de anos
@app.callback(
    [Output('ano-dropdown', 'options'), Output('ano-dropdown-2', 'options')],
    [Input('url', 'pathname'), Input('filtros-store', 'data')]
)
def update_ano_dropdown(pathname, filtros_json):
    if not filtros_json:
        return [], []
    
    filtros_df = pd.read_json(StringIO(filtros_json), orient='split')
    anos = filtros_df['ANO'].unique()
    ano_options = [{'label': str(ano), 'value': ano} for ano in sorted(anos)]
    
    return ano_options, ano_options

# Callback para atualizar dropdown de municípios
@app.callback(
    [Output('municipio-dropdown', 'options'), Output('municipio-dropdown-2', 'options')],
    [Input('url', 'pathname'), Input('ano-dropdown', 'value'), 
     Input('ano-dropdown-2', 'value'), Input('filtros-store', 'data')]
)
def update_cidade_dropdown(pathname, year_1, year_2, filtros_json):
    if not filtros_json:
        return [], []
    
    filtros_df = pd.read_json(StringIO(filtros_json), orient='split')
    
    city_options_1 = []
    if year_1:
        df_filtered = filtros_df[filtros_df['ANO'] == year_1]
        city_options_1 = [{'label': city, 'value': city} for city in df_filtered['NM_MUN'].unique()]
    
    city_options_2 = []
    if year_2:
        df_filtered = filtros_df[filtros_df['ANO'] == year_2]
        city_options_2 = [{'label': city, 'value': city} for city in df_filtered['NM_MUN'].unique()]
    
    return city_options_1, city_options_2

# Callback para mostrar/esconder segundo gráfico
@app.callback(
    Output('second-graph-container', 'style'),
    [Input('toggle-second-graph', 'n_clicks')]
)
def toggle_second_graph(n_clicks):
    if n_clicks % 2 == 0:
        return {'display': 'none'}
    return {'display': 'block'}

# Callback para atualizar gráficos e estatísticas
# Em app.py, callback update_graph_and_statistics
@app.callback(
    [Output('grafico-1', 'figure'), Output('estatisticas-1', 'children'),
     Output('grafico-2', 'figure'), Output('estatisticas-2', 'children')],
    [Input('url', 'pathname'), Input('ano-dropdown', 'value'), 
     Input('variavel-dropdown', 'value'), Input('municipio-dropdown', 'value'),
     Input('ano-dropdown-2', 'value'), Input('municipio-dropdown-2', 'value'),
     Input('graph-type-dropdown-1', 'value'), Input('graph-type-dropdown-2', 'value'),
     Input('filtros-store', 'data')]
)
def update_graph_and_statistics(pathname, year_1, variavel, municipios_1, 
                               year_2, municipios_2, graph_type_1, graph_type_2, filtros_json):
    section = pathname.strip('/')
    
    fig_1, stats_1 = {}, ""
    fig_2, stats_2 = {}, ""
    
    if not section or not variavel or not filtros_json:
        return fig_1, stats_1, fig_2, stats_2

    filtros_df = pd.read_json(StringIO(filtros_json), orient='split')
    variable_df = load_variable_data(section, variavel)
    
    if year_1 and municipios_1:
        combined_df_1 = combine_data_with_filters(filtros_df, variable_df, year=year_1, municipios=municipios_1)
        
        if not combined_df_1.empty:
            stats_1 = calculate_statistics(combined_df_1, 'VALOR')
            if graph_type_1 == 'bar':
                fig_1 = px.bar(combined_df_1, x='NM_MUN_filtros', y='VALOR', 
                              title=f'{variavel} - {section} ({year_1})')
            elif graph_type_1 == 'line':
                fig_1 = px.line(combined_df_1, x='NM_MUN_filtros', y='VALOR', 
                               title=f'{variavel} - {section} ({year_1})')
            elif graph_type_1 == 'box':
                fig_1 = px.box(combined_df_1, x='NM_MUN_filtros', y='VALOR', 
                              title=f'{variavel} - {section} ({year_1})')
            
            stats_text_1 = [
                html.Div(f"Média: {stats_1['mean']:.2f}" if stats_1['mean'] is not None else "Média: Dados insuficientes"),
                html.Div(f"Mediana: {stats_1['median']:.2f}" if stats_1['median'] is not None else "Mediana: Dados insuficientes"),
                html.Div(f"Desvio Padrão: {stats_1['std_dev']:.2f}" if stats_1['std_dev'] is not None else "Desvio Padrão: Dados insuficientes"),
                html.Div(f"Curtose: {stats_1['kurtosis']:.2f}" if stats_1['kurtosis'] is not None else "Curtose: Dados insuficientes")
            ]
            stats_1 = stats_text_1
    
    if year_2 and municipios_2:
        combined_df_2 = combine_data_with_filters(filtros_df, variable_df, year=year_2, municipios=municipios_2)
        
        if not combined_df_2.empty:
            stats_2 = calculate_statistics(combined_df_2, 'VALOR')
            if graph_type_2 == 'bar':
                fig_2 = px.bar(combined_df_2, x='NM_MUN_filtros', y='VALOR', 
                              title=f'{variavel} - {section} ({year_2})')
            elif graph_type_2 == 'line':
                fig_2 = px.line(combined_df_2, x='NM_MUN_filtros', y='VALOR', 
                               title=f'{variavel} - {section} ({year_2})')
            elif graph_type_2 == 'box':
                fig_2 = px.box(combined_df_2, x='NM_MUN_filtros', y='VALOR', 
                              title=f'{variavel} - {section} ({year_2})')
            
            stats_text_2 = [
                html.Div(f"Média: {stats_2['mean']:.2f}" if stats_2['mean'] is not None else "Média: Dados insuficientes"),
                html.Div(f"Mediana: {stats_2['median']:.2f}" if stats_2['median'] is not None else "Mediana: Dados insuficientes"),
                html.Div(f"Desvio Padrão: {stats_2['std_dev']:.2f}" if stats_2['std_dev'] is not None else "Desvio Padrão: Dados insuficientes"),
                html.Div(f"Curtose: {stats_2['kurtosis']:.2f}" if stats_2['kurtosis'] is not None else "Curtose: Dados insuficientes")
            ]
            stats_2 = stats_text_2
    
    return fig_1, stats_1, fig_2, stats_2

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)