import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy import stats
import os
from io import BytesIO
import dash_bootstrap_components as dbc
from load_data import load_filters, load_variable_data, combine_data_with_filters, load_multiple_variables

# Inicializando o app Dash com tema Bootstrap
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Função para carregar arquivos da seção
def load_section_files(area):
    section_path = f"../data/dw/{area}/"
    files = [f for f in os.listdir(section_path) if f.endswith('.xlsx')]
    return files

# Função para calcular estatísticas
def calculate_statistics(df, variavel, iqr_multiplier=1.5):
    stats_result = {}
    if variavel in df.columns:
        df[variavel] = pd.to_numeric(df[variavel], errors='coerce')
        df_clean = df[variavel].dropna()
        if not df_clean.empty:
            stats_result['mean'] = df_clean.mean()
            stats_result['median'] = df_clean.median()
            stats_result['std_dev'] = df_clean.std()
            stats_result['kurtosis'] = stats.kurtosis(df_clean, nan_policy='omit')
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
    dcc.Store(id='filtros-store'),
    dcc.Store(id='corr-data-store'),
    dcc.Location(id='url', refresh=False),
    dcc.Download(id="download-corr-matrix"),
    dcc.Download(id="download-raw-data"),

    # Navbar para dispositivos móveis
    dbc.NavbarSimple(
        children=[
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

# Layout da página de análise (Ambiental, Saúde, Geografia, Predição)
analysis_layout = dbc.Card([
    dbc.CardBody([
        html.H3("Gráfico 1"),
        dcc.Dropdown(id="ano-dropdown", multi=True, placeholder="Selecione os anos"),
        dcc.Dropdown(id="variavel-dropdown", placeholder="Selecione a variável"),
        dcc.Dropdown(id="municipio-dropdown", multi=True, placeholder="Selecione o município"),
        dcc.Dropdown(id="graph-type-dropdown-1", 
                     options=[
                         {'label': 'Barras', 'value': 'bar'},
                         {'label': 'Linhas', 'value': 'line'},
                         {'label': 'Boxplot', 'value': 'box'}
                     ], 
                     value='bar'),
        html.Label("Multiplicador do IQR para Cercas (padrão: 1.5):", 
                   title="Define a sensibilidade para identificar outliers. Valores menores detectam mais outliers, valores maiores são mais permissivos.",
                   className="mt-2"),
        dcc.Input(id="iqr-multiplier-1", type="number", value=1.5, min=0.1, step=0.1, className="mb-3"),
        dcc.Graph(id="grafico-1"),
        html.Div(id='estatisticas-1'),
        
        dbc.Button("Adicionar Segundo Gráfico", id="toggle-second-graph", n_clicks=0, color="primary", className="mt-3"),
        html.Div(id="second-graph-container", style={'display': 'none'}, children=[
            html.H3("Gráfico 2", className="mt-4"),
            dcc.Dropdown(id="ano-dropdown-2", multi=True, placeholder="Selecione os anos"),
            dcc.Dropdown(id="municipio-dropdown-2", multi=True, placeholder="Selecione o município"),
            dcc.Dropdown(id="graph-type-dropdown-2", 
                         options=[
                             {'label': 'Barras', 'value': 'bar'},
                             {'label': 'Linhas', 'value': 'line'},
                             {'label': 'Boxplot', 'value': 'box'}
                         ], 
                         value='bar'),
            html.Label("Multiplicador do IQR para Cercas (padrão: 1.5):", 
                       title="Define a sensibilidade para identificar outliers. Valores menores detectam mais outliers, valores maiores são mais permissivos.",
                       className="mt-2"),
            dcc.Input(id="iqr-multiplier-2", type="number", value=1.5, min=0.1, step=0.1, className="mb-3"),
            dcc.Graph(id="grafico-2"),
            html.Div(id='estatisticas-2'),
        ])
    ])
], className="mb-4")

# Layout da página de correlação
correlation_layout = dbc.Card([
    dbc.CardBody([
        html.H3("Análise de Correlação"),
        dcc.Dropdown(id="section-dropdown", placeholder="Selecione a seção"),
        dcc.Dropdown(id="variables-dropdown", multi=True, placeholder="Selecione as variáveis"),
        dcc.Dropdown(id="corr-ano-dropdown", multi=True, placeholder="Selecione os anos"),
        dcc.Dropdown(id="corr-municipio-dropdown", multi=True, placeholder="Selecione os municípios"),
        dcc.Dropdown(id="corr-method-dropdown", 
                     options=[
                         {'label': 'Pearson', 'value': 'pearson'},
                         {'label': 'Spearman', 'value': 'spearman'},
                         {'label': 'Kendall', 'value': 'kendall'}
                     ], 
                     value='pearson', 
                     placeholder="Selecione o método de correlação"),
        dbc.Row([
            dbc.Col(dbc.Button("Exportar Matriz de Correlação", id="export-corr-matrix", color="primary", className="mt-3"), md=6),
            dbc.Col(dbc.Button("Exportar Dados Brutos", id="export-raw-data", color="primary", className="mt-3"), md=6),
        ]),
        dcc.Graph(id="corr-heatmap"),
        html.Div(id='corr-table'),
        dcc.Graph(id="corr-scatter"),
    ])
], className="mb-4")

# Callback para atualizar o conteúdo da página
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    section = pathname.strip('/')
    if section in ['ambiental', 'saude', 'geografia', 'predicao']:
        return analysis_layout
    elif section == 'correlacao':
        return correlation_layout
    return html.Div("Página não encontrada")

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
    Output('variavel-dropdown', 'options'),
    [Input('url', 'pathname')]
)
def update_variable_dropdown(pathname):
    section = pathname.strip('/')
    if section in ['ambiental', 'saude', 'geografia', 'predicao']:
        files = load_section_files(section)
        variable_options = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
        return variable_options
    return []

# Callback para atualizar dropdown de anos (análise)
@app.callback(
    [Output('ano-dropdown', 'options'), Output('ano-dropdown-2', 'options')],
    [Input('url', 'pathname'), Input('filtros-store', 'data')]
)
def update_ano_dropdown(pathname, filtros_json):
    if not filtros_json:
        return [], []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    anos = filtros_df['ANO'].unique()
    ano_options = [{'label': str(ano), 'value': ano} for ano in sorted(anos)]
    
    return ano_options, ano_options

# Callback para atualizar dropdown de municípios (análise)
@app.callback(
    [Output('municipio-dropdown', 'options'), Output('municipio-dropdown-2', 'options')],
    [Input('url', 'pathname'), Input('ano-dropdown', 'value'), 
     Input('ano-dropdown-2', 'value'), Input('filtros-store', 'data')]
)
def update_cidade_dropdown(pathname, years_1, years_2, filtros_json):
    if not filtros_json:
        return [], []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    
    city_options_1 = []
    if years_1:
        df_filtered = filtros_df[filtros_df['ANO'].isin(years_1)]
        city_options_1 = [{'label': city, 'value': city} for city in df_filtered['NM_MUN'].unique()]
    
    city_options_2 = []
    if years_2:
        df_filtered = filtros_df[filtros_df['ANO'].isin(years_2)]
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

# Callback para atualizar gráficos e estatísticas (análise)
@app.callback(
    [Output('grafico-1', 'figure'), Output('estatisticas-1', 'children'),
     Output('grafico-2', 'figure'), Output('estatisticas-2', 'children')],
    [Input('url', 'pathname'), Input('ano-dropdown', 'value'), 
     Input('variavel-dropdown', 'value'), Input('municipio-dropdown', 'value'),
     Input('ano-dropdown-2', 'value'), Input('municipio-dropdown-2', 'value'),
     Input('graph-type-dropdown-1', 'value'), Input('graph-type-dropdown-2', 'value'),
     Input('iqr-multiplier-1', 'value'), Input('iqr-multiplier-2', 'value'),
     Input('filtros-store', 'data')]
)
def update_graph_and_statistics(pathname, years_1, variavel, municipios_1, 
                               years_2, municipios_2, graph_type_1, graph_type_2, 
                               iqr_multiplier_1, iqr_multiplier_2, filtros_json):
    section = pathname.strip('/')
    
    fig_1, stats_1 = {}, ""
    fig_2, stats_2 = {}, ""
    
    if not section or not variavel or not filtros_json:
        return fig_1, stats_1, fig_2, stats_2

    filtros_df = pd.read_json(filtros_json, orient='split')
    variable_df = load_variable_data(section, variavel)
    
    if years_1 and municipios_1:
        combined_df_1 = combine_data_with_filters(filtros_df, variable_df, years=years_1, municipios=municipios_1)
        
        if not combined_df_1.empty:
            stats_1 = calculate_statistics(combined_df_1, 'VALOR', iqr_multiplier=iqr_multiplier_1 or 1.5)
            if graph_type_1 == 'bar':
                fig_1 = px.bar(combined_df_1, x='NM_MUN_filtros', y='VALOR', color='ANO',
                              title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_1))})',
                              barmode='group')
                # Destacar outliers
                outliers = combined_df_1[
                    (combined_df_1['VALOR'] < stats_1['lower_fence']) | 
                    (combined_df_1['VALOR'] > stats_1['upper_fence'])
                ]
                if not outliers.empty:
                    fig_1.add_scatter(x=outliers['NM_MUN_filtros'], y=outliers['VALOR'], 
                                     mode='markers', marker=dict(color='red', size=10), 
                                     name='Outliers')
            elif graph_type_1 == 'line':
                fig_1 = px.line(combined_df_1, x='NM_MUN_filtros', y='VALOR', color='ANO',
                               title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_1))})')
                if not outliers.empty:
                    fig_1.add_scatter(x=outliers['NM_MUN_filtros'], y=outliers['VALOR'], 
                                     mode='markers', marker=dict(color='red', size=10), 
                                     name='Outliers')
            elif graph_type_1 == 'box':
                fig_1 = px.box(combined_df_1, x='NM_MUN_filtros', y='VALOR', color='ANO',
                              title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_1))})')
            
            # Estatísticas e tabela de outliers
            stats_text_1 = [
                html.Div(f"Média: {stats_1['mean']:.2f}" if stats_1['mean'] is not None else "Média: Dados insuficientes"),
                html.Div(f"Mediana: {stats_1['median']:.2f}" if stats_1['median'] is not None else "Mediana: Dados insuficientes"),
                html.Div(f"Desvio Padrão: {stats_1['std_dev']:.2f}" if stats_1['std_dev'] is not None else "Desvio Padrão: Dados insuficientes"),
                html.Div(f"Curtose: {stats_1['kurtosis']:.2f}" if stats_1['kurtosis'] is not None else "Curtose: Dados insuficientes"),
                html.Div(f"Cerca Inferior: {stats_1['lower_fence']:.2f}" if stats_1['lower_fence'] is not None else "Cerca Inferior: Dados insuficientes"),
                html.Div(f"Cerca Superior: {stats_1['upper_fence']:.2f}" if stats_1['upper_fence'] is not None else "Cerca Superior: Dados insuficientes"),
            ]
            # Adicionar tabela de outliers
            if not outliers.empty:
                stats_text_1.append(
                    html.Div([
                        html.H5("Outliers Identificados:", className="mt-3"),
                        dbc.Table.from_dataframe(
                            outliers[['NM_MUN_filtros', 'ANO', 'VALOR']].rename(
                                columns={'NM_MUN_filtros': 'Município', 'ANO': 'Ano', 'VALOR': 'Valor'}
                            ),
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True
                        )
                    ])
                )
            stats_1 = stats_text_1
    
    if years_2 and municipios_2:
        combined_df_2 = combine_data_with_filters(filtros_df, variable_df, years=years_2, municipios=municipios_2)
        
        if not combined_df_2.empty:
            stats_2 = calculate_statistics(combined_df_2, 'VALOR', iqr_multiplier=iqr_multiplier_2 or 1.5)
            if graph_type_2 == 'bar':
                fig_2 = px.bar(combined_df_2, x='NM_MUN_filtros', y='VALOR', color='ANO',
                              title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_2))})',
                              barmode='group')
                # Destacar outliers
                outliers = combined_df_2[
                    (combined_df_2['VALOR'] < stats_2['lower_fence']) | 
                    (combined_df_2['VALOR'] > stats_2['upper_fence'])
                ]
                if not outliers.empty:
                    fig_2.add_scatter(x=outliers['NM_MUN_filtros'], y=outliers['VALOR'], 
                                     mode='markers', marker=dict(color='red', size=10), 
                                     name='Outliers')
            elif graph_type_2 == 'line':
                fig_2 = px.line(combined_df_2, x='NM_MUN_filtros', y='VALOR', color='ANO',
                               title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_2))})')
                if not outliers.empty:
                    fig_2.add_scatter(x=outliers['NM_MUN_filtros'], y=outliers['VALOR'], 
                                     mode='markers', marker=dict(color='red', size=10), 
                                     name='Outliers')
            elif graph_type_2 == 'box':
                fig_2 = px.box(combined_df_2, x='NM_MUN_filtros', y='VALOR', color='ANO',
                              title=f'{variavel} - {section} (Anos: {", ".join(map(str, years_2))})')
            
            # Estatísticas e tabela de outliers
            stats_text_2 = [
                html.Div(f"Média: {stats_2['mean']:.2f}" if stats_2['mean'] is not None else "Média: Dados insuficientes"),
                html.Div(f"Mediana: {stats_2['median']:.2f}" if stats_2['median'] is not None else "Mediana: Dados insuficientes"),
                html.Div(f"Desvio Padrão: {stats_2['std_dev']:.2f}" if stats_2['std_dev'] is not None else "Desvio Padrão: Dados insuficientes"),
                html.Div(f"Curtose: {stats_2['kurtosis']:.2f}" if stats_2['kurtosis'] is not None else "Curtose: Dados insuficientes"),
                html.Div(f"Cerca Inferior: {stats_2['lower_fence']:.2f}" if stats_2['lower_fence'] is not None else "Cerca Inferior: Dados insuficientes"),
                html.Div(f"Cerca Superior: {stats_2['upper_fence']:.2f}" if stats_2['upper_fence'] is not None else "Cerca Superior: Dados insuficientes"),
            ]
            # Adicionar tabela de outliers
            if not outliers.empty:
                stats_text_2.append(
                    html.Div([
                        html.H5("Outliers Identificados:", className="mt-3"),
                        dbc.Table.from_dataframe(
                            outliers[['NM_MUN_filtros', 'ANO', 'VALOR']].rename(
                                columns={'NM_MUN_filtros': 'Município', 'ANO': 'Ano', 'VALOR': 'Valor'}
                            ),
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True
                        )
                    ])
                )
            stats_2 = stats_text_2
    
    return fig_1, stats_1, fig_2, stats_2

# Callback para atualizar dropdown de seção (correlação)
@app.callback(
    Output('section-dropdown', 'options'),
    [Input('url', 'pathname')]
)
def update_section_dropdown(pathname):
    sections = ['ambiental', 'saude', 'geografia', 'predicao']
    return [{'label': section.capitalize(), 'value': section} for section in sections]

# Callback para atualizar dropdown de variáveis (correlação)
@app.callback(
    Output('variables-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def update_variables_dropdown(section):
    if section:
        files = load_section_files(section)
        variable_options = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
        return variable_options
    return []

# Callback para atualizar dropdown de anos (correlação)
@app.callback(
    Output('corr-ano-dropdown', 'options'),
    [Input('filtros-store', 'data')]
)
def update_corr_ano_dropdown(filtros_json):
    if not filtros_json:
        return []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    anos = filtros_df['ANO'].unique()
    ano_options = [{'label': str(ano), 'value': ano} for ano in sorted(anos)]
    
    return ano_options

# Callback para atualizar dropdown de municípios (correlação)
@app.callback(
    Output('corr-municipio-dropdown', 'options'),
    [Input('corr-ano-dropdown', 'value'), Input('filtros-store', 'data')]
)
def update_corr_cidade_dropdown(years, filtros_json):
    if not filtros_json or not years:
        return []
    
    filtros_df = pd.read_json(filtros_json, orient='split')
    df_filtered = filtros_df[filtros_df['ANO'].isin(years)]
    city_options = [{'label': city, 'value': city} for city in df_filtered['NM_MUN'].unique()]
    
    return city_options

# Callback para atualizar heatmap, tabela e armazenar dados
@app.callback(
    [Output('corr-heatmap', 'figure'), Output('corr-table', 'children'), Output('corr-data-store', 'data')],
    [Input('section-dropdown', 'value'), Input('variables-dropdown', 'value'),
     Input('corr-ano-dropdown', 'value'), Input('corr-municipio-dropdown', 'value'),
     Input('corr-method-dropdown', 'value'), Input('filtros-store', 'data')]
)
def update_correlation_analysis(section, variables, years, municipios, method, filtros_json):
    heatmap_fig = go.Figure()
    table = html.Div("Selecione seção, variáveis, anos e municípios para calcular a correlação.")
    data_json = None
    
    if not section or not variables or len(variables) < 2 or not years or not municipios or not filtros_json:
        return heatmap_fig, table, data_json
    
    # Carregar dados combinados
    df = load_multiple_variables(section, variables, years=years, municipios=municipios)
    
    # Calcular matriz de correlação
    corr_matrix = df[variables].corr(method=method)
    
    # Criar heatmap
    heatmap_fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        title=f'Matriz de Correlação ({method.capitalize()})'
    )
    
    # Criar tabela de correlação
    table = dbc.Table.from_dataframe(
        corr_matrix.round(3),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )
    
    # Armazenar dados no store
    data_json = df.to_json(date_format='iso', orient='split')
    
    return heatmap_fig, table, data_json

# Callback para atualizar scatter plot com base em clique no heatmap
@app.callback(
    Output('corr-scatter', 'figure'),
    [Input('corr-heatmap', 'clickData'), Input('corr-data-store', 'data'),
     Input('variables-dropdown', 'value')]
)
def update_scatter_plot(click_data, data_json, variables):
    scatter_fig = go.Figure()
    
    if not data_json or not variables or len(variables) < 2:
        return scatter_fig
    
    df = pd.read_json(data_json, orient='split')
    
    # Selecionar o primeiro par de variáveis por padrão
    x_var, y_var = variables[0], variables[1]
    
    # Atualizar com base no clique no heatmap
    if click_data and 'points' in click_data:
        point = click_data['points'][0]
        x_idx, y_idx = point['x'], point['y']
        if isinstance(x_idx, str) and isinstance(y_idx, str) and x_idx in variables and y_idx in variables:
            x_var, y_var = x_idx, y_idx
    
    # Criar scatter plot
    scatter_fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        hover_data=['NM_MUN_filtros', 'ANO'],
        title=f'{x_var} vs {y_var}'
    )
    
    return scatter_fig

# Callback para exportar matriz de correlação
@app.callback(
    Output('download-corr-matrix', 'data'),
    [Input('export-corr-matrix', 'n_clicks')],
    [State('corr-data-store', 'data'), State('variables-dropdown', 'value'),
     State('corr-method-dropdown', 'value')]
)
def export_correlation_matrix(n_clicks, data_json, variables, method):
    if not n_clicks or not data_json or not variables or len(variables) < 2:
        return None
    
    df = pd.read_json(data_json, orient='split')
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

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)