import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from template import get_main_layout
from controllers import register_callbacks

# Inicializando o app Dash com tema Bootstrap
# app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # Necessário para Elastic Beanstalk

# Definir o layout principal
app.layout = get_main_layout()

# Registrar callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)


""" # Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True) """