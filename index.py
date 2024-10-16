from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

# Conexão com o banco de dados
DATABASE_URI = 'postgresql+psycopg2://postgres:123@localhost/projeto isaac'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def get_data_from_postgres():
    session = Session()
    
    query = "SELECT vin, modelname, askprice, brandname FROM cars WHERE askprice IS NOT NULL ORDER BY askprice DESC LIMIT 20"
    df = pd.read_sql(query, session.bind)
    
    session.close()
    
    return df

df = get_data_from_postgres()

app = Dash(__name__)

# Configuração de temas
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SOLAR
template_theme1 = 'morph'
template_theme2 = 'solar'

# Opções de marcas
opcoes = list(df['brandname'].unique())
opcoes.append("Todos os Carros")

# Gerando dicionário de marcas para usar no Slider
brand_options = {i: brand for i, brand in enumerate(df['brandname'].unique())}

# Layout do app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            html.H1(children='Previsão de Preço de Carros', style={'textAlign': 'center'}), 
            html.H3(children='Uma dashboard feita por Douglas Gobitsch, Cauã Guerreiro e Vinícius Raiol.',
                    style={'textAlign': 'center'})
        ])
    ]),

    # Dropdown para selecionar a marca
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(opcoes, value='Todos os Carros', id='brand-dropdown', placeholder="Selecione a marca"),
        ])
    ]),

    # Opções para selecionar o tipo de gráfico
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='chart-type',
                options=[
                    {'label': 'Gráfico de Dispersão', 'value': 'scatter'},
                    {'label': 'Gráfico de Colunas', 'value': 'bar'},
                    {'label': 'Gráfico de Pizza', 'value': 'pie'}  # Nova opção de gráfico de pizza
                ],
                value='scatter',  # Valor padrão
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ])
    ]),

    # Slider para selecionar marcas (visível apenas no gráfico de dispersão)
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                id='brand-slider',
                min=0,
                max=len(brand_options) - 1,
                value=0,  # Valor inicial
                marks=brand_options,  # Mapeia o índice para as marcas
                step=None,  # Passo fixo por marca
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], id='slider-container')  # Este contêiner será controlado pela callback para aparecer/desaparecer
    ]),

    # Gráfico
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='example-graph')
        ])
    ])
    
])

# Função de callback para atualizar o gráfico com base nas seleções do usuário
@app.callback(
    Output('example-graph', 'figure'),
    Output('slider-container', 'style'),  # Controla a visibilidade do slider
    Input('brand-dropdown', 'value'),
    Input('brand-slider', 'value'),
    Input('chart-type', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_graph(selected_brand, selected_slider_brand, chart_type, toggle):
    templates = template_theme1 if toggle else template_theme2

    # Filtrar dados com base na marca selecionada
    if selected_brand == "Todos os Carros":
        tabela_filtrada = df
    else:
        tabela_filtrada = df[df['brandname'] == selected_brand]

    # Se o tipo de gráfico for 'scatter', aplica o filtro do slider de marcas
    if chart_type == 'scatter':
        selected_brand_name = brand_options[selected_slider_brand]  # Pega o nome da marca selecionada no slider
        tabela_filtrada = tabela_filtrada[tabela_filtrada['brandname'] == selected_brand_name]
        fig = px.scatter(tabela_filtrada, x="modelname", y="askprice", color="brandname", template=templates)
        slider_style = {'display': 'block'}  # Mostra o controle deslizante

    # Se o tipo de gráfico for 'bar', exibe o gráfico de colunas (barras), sem filtrar por marca no slider
    elif chart_type == 'bar':
        fig = px.bar(tabela_filtrada, x="modelname", y="askprice", color="brandname", template=templates)
        slider_style = {'display': 'none'}  # Esconde o controle deslizante

    # Se o tipo de gráfico for 'pie', cria um gráfico de pizza
    elif chart_type == 'pie':
        fig = px.pie(tabela_filtrada, names='brandname', values='askprice', template=templates)
        slider_style = {'display': 'none'}  # Esconde o controle deslizante para o gráfico de pizza

    fig.update_layout(template=templates)
    
    return fig, slider_style

if __name__ == '__main__':
    app.run(debug=True)
