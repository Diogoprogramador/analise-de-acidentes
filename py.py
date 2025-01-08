import pandas as pd
from dash import Dash, dcc, html
import dash_table
import plotly.express as px
import folium
from folium.plugins import HeatMap
from folium import Marker
from folium.features import CustomIcon
import base64

# Carregar os dados
df = pd.read_csv('cat_acidentes.csv', sep=';')
print(df)

# Remover NaN nas colunas de interesse
df = df.dropna(subset=['latitude', 'longitude', 'feridos', 'mortes'])

# Criar uma coluna de intensidade (soma de feridos e mortes)
df['intensidade'] = df['feridos'] + df['mortes']

# Calcular a porcentagem de feridos e mortes
df['percentual_feridos'] = (df['feridos'] / df['intensidade']) * 100
df['percentual_mortes'] = (df['mortes'] / df['intensidade']) * 100

# Criar mapa de calor com Folium, ajustando a intensidade
m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Definir dados de calor, onde a intensidade é mais pronunciada
heat_data = [[row['latitude'], row['longitude'], row['intensidade']] for index, row in df.iterrows()]

# Adicionar o HeatMap com ajustes para tornar as áreas de maior intensidade mais visíveis
HeatMap(heat_data, min_opacity=0.4, max_zoom=15, radius=15, blur=10).add_to(m)

# Adicionar setas nas áreas de maior intensidade
# Vamos adicionar setas nos 5 pontos com maior intensidade
top_acidentes = df.nlargest(5, 'intensidade')

for index, row in top_acidentes.iterrows():
    # Usando o CustomIcon para adicionar setas
    icon = CustomIcon(
        icon_image="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Arrow_down_right_3.svg/64px-Arrow_down_right_3.svg.png",
        icon_size=(30, 30),  # Ajuste o tamanho da seta
        icon_anchor=(15, 15)  # Posição da âncora da seta
    )
    # Criando o marcador com a seta
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=icon
    ).add_to(m)

# Salvar o mapa em um arquivo HTML
map_html = 'mapa_calor_com_setas.html'
m.save(map_html)

# Função para converter o mapa em uma imagem base64 para exibir no Dash
def render_map_as_base64(map_html):
    with open(map_html, 'rb') as f:
        map_data = f.read()
        return base64.b64encode(map_data).decode()

# Converter o mapa em base64
map_base64 = render_map_as_base64(map_html)

# Criar o gráfico de bolinhas para visualização de acidentes
fig_bolinhas = px.scatter(df, x='longitude', y='latitude',
                          size='intensidade', color='percentual_feridos',
                          hover_name='idacidente',
                          color_continuous_scale='Viridis',
                          title="Distribuição de Acidentes com Feridos e Mortes",
                          labels={'latitude': 'Latitude', 'longitude': 'Longitude', 'intensidade': 'Intensidade'})

# Criar o app Dash
app = Dash(__name__)

# Definir o layout do dashboard
app.layout = html.Div([

    # Título do Dashboard
    html.H1("Dashboard de Análise de Acidentes de Trânsito"),

    # Gráfico com Mapa de Calor
    html.Div([
        html.H2("Mapa de Calor dos Acidentes"),
        html.Img(src=f"data:image/png;base64,{map_base64}", style={"width": "100%", "height": "auto"})
    ]),

    # Tabela com os dados limpos
    html.Div([
        html.H2("Tabela de Dados"),
        dash_table.DataTable(
            id='tabela-dados',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'height': '400px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    ]),

    # Gráfico de Bolinhas
    html.Div([
        html.H2("Distribuição de Acidentes"),
        dcc.Graph(
            id='grafico-bolinhas',
            figure=fig_bolinhas
        )
    ])
])

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
