from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
import psycopg2
import joblib
import numpy as np

# Conexão com o banco de dados
DATABASE_URI = 'postgresql+psycopg2://postgres:1408@localhost/cars_dataset'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Função para carregar dados do PostgreSQL
def get_data_from_postgres():
    session = Session()
    query = """
    WITH LatestCars AS (
        SELECT vin, brandname, modelname, msrp, askprice, vf_baseprice, firstseen, lastseen, vf_modelyear, 
        ROW_NUMBER() OVER (PARTITION BY modelname ORDER BY lastseen DESC) AS row_num 
        FROM cars
    )
    SELECT * 
    FROM LatestCars 
    WHERE row_num = 1 
    ORDER BY askprice DESC 
    LIMIT 30;
    """
    df_bar = pd.read_sql(query, session.bind)
    session.close()
    return df_bar

df_bar = get_data_from_postgres()

def get_data_from_postgres_pizza():
    session = Session() 
    query = "SELECT vin, modelname, askprice, brandname FROM cars WHERE askprice IS NOT NULL ORDER BY askprice DESC LIMIT 20"
    df_pizza = pd.read_sql(query, session.bind)
    
    session.close()
    
    return df_pizza

df_pizza = get_data_from_postgres_pizza()

def get_data_from_postgres_scatter():
    session = Session()
    query = """
    WITH MarcaTotalPreco AS (
        SELECT brandname, SUM(askprice) AS total_preco 
        FROM cars 
        GROUP BY brandname 
        ORDER BY total_preco DESC 
        LIMIT 15
    ),
    LatestCars AS (
        SELECT vin, brandname, modelname, msrp, askprice, vf_baseprice, firstseen, lastseen, vf_modelyear, 
        ROW_NUMBER() OVER (PARTITION BY modelname ORDER BY lastseen DESC) AS row_num 
        FROM cars WHERE askprice != 0
    ),
    RankedCars AS (
        SELECT *, RANK() OVER (PARTITION BY brandname ORDER BY askprice DESC) AS rank 
        FROM LatestCars 
        WHERE row_num = 1 
        AND brandname IN (SELECT brandname FROM MarcaTotalPreco)
    )
    SELECT * 
    FROM RankedCars 
    WHERE rank <= 15 
    ORDER BY brandname, askprice DESC;
    """
    df_scatter = pd.read_sql(query, session.bind)
    session.close()
    return df_scatter

df_scatter = get_data_from_postgres_scatter()

# Carregar o modelo de Machine Learning
model = joblib.load('modelo_previsao_veiculos_com_pipeline.pkl')

# Função para prever valorização ou depreciação com o modelo
def prever_valorizacao_ou_depreciacao(df):
    # Previsão com o modelo treinado
    X = df[['vf_modelyear', 'brandname']].copy()
    X['ano'] = pd.to_datetime(X['vf_modelyear'], errors='coerce').dt.year
    X['ano'] = X['ano'].fillna(X['ano'].mean())  # Preencher anos ausentes com a média
    X = X.rename(columns={'brandname': 'marca'})  # Renomear para atender ao pipeline
    y_pred = model.predict(X[['ano', 'marca']])  # Usar apenas as colunas necessárias
    df['previsao_preco'] = y_pred
    return df

df_valorizacao = prever_valorizacao_ou_depreciacao(df_scatter)

app = Dash(__name__)

# Configuração de temas
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SOLAR
template_theme1 = 'morph'
template_theme2 = 'solar'

# Opções de marcas
opcoes = list(df_pizza['brandname'].unique())
opcoes.append("Todos os Carros")

# Gerando dicionário de marcas para usar no Slider
brand_options = {i: brand for i, brand in enumerate(df_scatter['brandname'].unique())}

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
                    {'label': 'Gráfico de Pizza', 'value': 'pie'},
                    {'label': 'Valorização / Depreciação', 'value': 'valorizacao'}
                ],
                value='scatter',
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
                value=0,
                marks=brand_options,
                step=None,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], id='slider-container')
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
    Output('slider-container', 'style'),
    Input('brand-dropdown', 'value'),
    Input('brand-slider', 'value'),
    Input('chart-type', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_graph(selected_brand, selected_slider_brand, chart_type, toggle):
    templates = template_theme1 if toggle else template_theme2

    # Filtrar dados com base na marca selecionada
    if selected_brand == "Todos os Carros":
        tabela_filtrada_bar = df_bar
    else:
        tabela_filtrada_bar = df_bar[df_bar['brandname'] == selected_brand]

    if selected_brand == "Todos os Carros":
        tabela_filtrada_pizza = df_pizza
    else:
        tabela_filtrada_pizza = df_pizza[df_pizza['brandname'] == selected_brand]

    if selected_brand == "Todos os Carros":
        tabela_filtrada_scatter = df_scatter
    else:
        tabela_filtrada_scatter = df_scatter[df_scatter['brandname'] == selected_brand]

    # Gráfico de dispersão
    if chart_type == 'scatter':
        selected_brand_name = brand_options[selected_slider_brand]
        tabela_filtrada_scatter = tabela_filtrada_scatter[tabela_filtrada_scatter['brandname'] == selected_brand_name]
        fig = px.scatter(tabela_filtrada_scatter, x="modelname", y="askprice", color="brandname", template=templates)
        slider_style = {'display': 'block'}

    # Gráfico de barras
    elif chart_type == 'bar':
        fig = px.bar(tabela_filtrada_bar, x="modelname", y="askprice", color="brandname", template=templates)
        slider_style = {'display': 'none'}

    # Gráfico de pizza
    elif chart_type == 'pie':
        fig = px.pie(tabela_filtrada_pizza, names='brandname', values='askprice', template=templates)
        slider_style = {'display': 'none'}

    # Gráfico de valorização/depreciação
    elif chart_type == 'valorizacao':
        df_valorizacao = prever_valorizacao_ou_depreciacao(tabela_filtrada_scatter)
        fig = px.scatter(df_valorizacao, x="vf_modelyear", y="previsao_preco", color="brandname", template=templates)
        slider_style = {'display': 'none'}

    return fig, slider_style

if __name__ == '__main__':
    app.run_server(debug=True)
