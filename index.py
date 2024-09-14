from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
 
import pandas as pd

from app import *
from dash_bootstrap_templates import ThemeSwitchAIO

df = pd.read_csv('dataset_cars_novo.csv')
#lê o arquivo csv já tratado

app = Dash(__name__)

url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SOLAR
template_theme1 = 'morph'
template_theme2 = 'solar'
#define os temas do site pra que sejam aplicados com mais facilidade nos gráficos

fig = px.bar(df, x="vf_ModelYear", y="askPrice", color="brandName", barmode="group")
opcoes = list(df['brandName'].unique())
opcoes.append("Todos os Carros")
#define os valores do gráfico de barra e atribui os valores da coluna ao botão interativo

app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            ThemeSwitchAIO(aio_id = 'theme', themes = [url_theme1, url_theme2]),
            html.H1(children= 'Previsão de Preço de Carros',
            style={'textAlign' : 'center'}), 
            html.H3(children= 'Uma dashboard feita por Douglas Gobitsch, Cauã Guerreiro e Vinícius Raiol.',
            style={'textAlign' : 'center'})
        ])
    ]),
    #escreve o cabeçalho do site
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(opcoes, value='Todos os Carros', id='vin'),
        ])
    ]),
    #insere o botão dropdown
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='example-graph',
                figure=fig
            )
        ])
    ]),
    #insere o gráfico de barra
   
])
@app.callback(
    Output('example-graph', 'figure'),
    Input('vin', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
#faz interação da troca de temas e do botão
def bar(value, toggle):
    templates = template_theme1 if toggle else template_theme2
    
    if value == "Todos os Carros":
        fig = px.bar(df, x="vf_ModelYear", y="askPrice", color="brandName", barmode="group", template = templates)
    else:
        tabela_filtrada = df.loc[df['brandName']==value, :]
        fig = px.bar(tabela_filtrada, x="vf_ModelYear", y="askPrice", color="brandName", barmode="group", template = templates)
        
    fig.update_layout(template = templates)
    return fig
    #filtra os valores para que apareçam apenas valores de um só país e retorna esses valores atualizados


if __name__ == '__main__':
    app.run(debug=True)
#inicia o servidor do app no flask
