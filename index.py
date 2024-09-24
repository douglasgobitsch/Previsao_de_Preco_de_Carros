from dash import Dash, dcc, html, Input, Output, callback 
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

# Configurações de conexão
DATABASE_URI = 'postgresql+psycopg2://postgres:123@localhost/projeto isaac'

# Criar uma engine de conexão
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Função para buscar os dados do PostgreSQL
def get_data_from_postgres():
    # Criar uma sessão
    session = Session()
    
    # Consultar a tabela com os dados do carro
    query = "SELECT vin, vf_ModelYear, askPrice, brandName FROM cars"
    df = pd.read_sql(query, session.bind)
    
    # Fechar a sessão
    session.close()
    
    return df

# Carregar os dados do PostgreSQL
df = get_data_from_postgres()

app = Dash(__name__)

# Definir temas para troca
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SOLAR
template_theme1 = 'morph'
template_theme2 = 'solar'

# Criar gráfico de barras padrão
fig = px.bar(df, x="vf_modelyear", y="askprice", color="brandname", barmode="group")

# Opções do dropdown: incluir marcas e o VIN (ID dos veículos)
opcoes = list(df['brandname'].unique())
opcoes.append("Todos os Carros")

# Adicionar VIN ao dropdown
opcoes_vin = list(df['vin'].unique())
opcoes_vin.append("Todos os VINs")

# Layout da página
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            html.H1(children='Previsão de Preço de Carros', style={'textAlign': 'center'}), 
            html.H3(children='Uma dashboard feita por Douglas Gobitsch, Cauã Guerreiro e Vinícius Raiol.',
                    style={'textAlign': 'center'})
        ])
    ]),
    # Dropdown de marcas
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(opcoes, value='Todos os Carros', id='brand-dropdown', placeholder="Selecione a marca"),
        ])
    ]),
    # Dropdown de VINs
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(opcoes_vin, value='Todos os VINs', id='vin-dropdown', placeholder="Selecione o VIN"),
        ])
    ]),
    # Gráfico de barras
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='example-graph', figure=fig)
        ])
    ])
])

# Callback para atualizar o gráfico com base na seleção de marca ou VIN
@app.callback(
    Output('example-graph', 'figure'),
    Input('brand-dropdown', 'value'),
    Input('vin-dropdown', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_graph(selected_brand, selected_vin, toggle):
    templates = template_theme1 if toggle else template_theme2
    
    # Se 'Todos os Carros' ou 'Todos os VINs' forem selecionados, mostrar todos os dados
    if selected_brand == "Todos os Carros" and selected_vin == "Todos os VINs":
        fig = px.bar(df, x="vf_modelyear", y="askprice", color="brandname", barmode="group", template=templates)
    
    # Se apenas uma marca for selecionada
    elif selected_brand != "Todos os Carros" and selected_vin == "Todos os VINs":
        tabela_filtrada = df.loc[df['brandname'] == selected_brand]
        fig = px.bar(tabela_filtrada, x="vf_modelyear", y="askprice", color="brandname", barmode="group", template=templates)
    
    # Se apenas um VIN for selecionado
    elif selected_brand == "Todos os Carros" and selected_vin != "Todos os VINs":
        tabela_filtrada = df.loc[df['vin'] == selected_vin]
        fig = px.bar(tabela_filtrada, x="vf_modelyear", y="askprice", color="brandname", barmode="group", template=templates)
    
    # Se tanto a marca quanto o VIN forem selecionados
    else:
        tabela_filtrada = df.loc[(df['brandname'] == selected_brand) & (df['vin'] == selected_vin)]
        fig = px.bar(tabela_filtrada, x="vf_modelyear", y="askprice", color="brandname", barmode="group", template=templates)
    
    # Atualizar layout com o template do tema selecionado
    fig.update_layout(template=templates)
    
    return fig

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)
