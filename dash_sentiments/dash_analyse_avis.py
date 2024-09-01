import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import requests

try:
    response = requests.get("http://fastapi:8000/liste_restaurants")
    response.raise_for_status()
    print("API FastAPI est accessible")
except requests.exceptions.RequestException as e:
    print(f"Erreur lors de l'accès à l'API FastAPI: {e}")


#URL de base de l'API FastAPI
BASE_URL = "http://fastapi:8000"

#  Récupération de la liste des Restaurants
def get_restaurants():
    response = requests.get(f"{BASE_URL}/liste_restaurants")
    if response.status_code == 200:
        df_r=pd.DataFrame(response.json())
        # on filtre les restaurants à ceux qui disposent d'avis
        df_r=df_r[df_r['nb_avis'] > 0]
        return df_r
    else:
        return pd.DataFrame()

# Récupération de la liste des avis 
def get_avis():
    response = requests.get(f"{BASE_URL}/liste_avis")
    if response.status_code == 200:
        df_a= pd.DataFrame(response.json())
        # on récupère uniquement les avis pour les resto renseignés dans df_restau
        df_a = df_a[df_a['id_resto'].isin(df_restau['id_resto'])]
        return df_a
    else:
        return pd.DataFrame()

# Récupération de la liste des sentiments 
def get_sentiments():
    response = requests.get(f"{BASE_URL}/liste_sentiments")
    if response.status_code == 200:
        df_s= pd.DataFrame(response.json())
        print(df_s.head())
        print(df_restau.head())
        # on récupère uniquement les sentiments pour les resto renseignés dans df_restau
        df_s = df_s[df_s['id_resto'].isin(df_restau['id_resto'])]
        return df_s
    else:
        return pd.DataFrame()

# Initialisation des DataFrames
df_restau = get_restaurants()
print(df_restau.head())
df_avis = get_avis()
df_avis['date_exp'] = pd.to_datetime(df_avis['date_exp'], errors='coerce')
print(df_avis.head())
df_sentiments = get_sentiments()
print(df_sentiments.head())

# Initialisation de l'application Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

# Créer la mise en page principale
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Mise en page de la page principale
index_page = html.Div([
    html.H1("Analyse des avis TrustPilot sur les restaurants Anglais"),
    dcc.Link('Comparatif de 2 restaurants', href='/comparatif'),
    html.Br(),
    dcc.Link('Analyse des avis', href='/analyse')
])

# Callback pour afficher la page appropriée
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/comparatif':
        return comparatif_layout
    elif pathname == '/analyse':
        return analyse_layout
    else:
        return index_page

# Layout pour la page de comparatif
comparatif_layout = html.Div([
    html.H1('Comparatif de 2 restaurants'),
    dcc.Link('Retour à la page principale', href='/'),
    html.Br(),
    dcc.Dropdown(
        id='score-filter',
        options=[
            {'label': 'MAUVAIS (Score < 2.5)', 'value': 'MAUVAIS'},
            {'label': 'MOYENS (2.5 <= Score <= 4)', 'value': 'MOYENS'},
            {'label': 'BONS (Score > 4)', 'value': 'BONS'}
        ],
        placeholder='Filtrer par score'
    ),
    dcc.Dropdown(
        id='resto1-dropdown',
        placeholder='Sélectionnez le premier restaurant'
    ),
    dcc.Dropdown(
        id='resto2-dropdown',
        placeholder='Sélectionnez le deuxième restaurant'
    ),
    html.Br(),
    #html.Button('Comparer les sentiments', id='compare-button', n_clicks=0),
    #html.Br(),
    html.Div(id='comparatif-table'),
    dcc.RangeSlider(
        id='date-slider',
        min=0,
        max=100,
        value=[0, 100],
        marks={},  # Les marques seront mises à jour dynamiquement
        tooltip={"placement": "bottom", "always_visible": False}
        ),
    html.Br()
])

# Callback pour mettre à jour les dropdowns selon le filtre de score
@app.callback(
    [Output('resto1-dropdown', 'options'),
     Output('resto2-dropdown', 'options')],
    [Input('score-filter', 'value')]
)
def set_restaurants_options(selected_score):
    if selected_score == 'MAUVAIS':
        filtered_df = df_restau[df_restau['score'] < 2.5]
    elif selected_score == 'MOYENS':
        filtered_df = df_restau[(df_restau['score'] >= 2.5) & (df_restau['score'] <= 4)]
    elif selected_score == 'BONS':
        filtered_df = df_restau[df_restau['score'] > 4]
    else:
        filtered_df = df_restau

    options = [{'label': f"{row['nom']} (Score: {row['score']})", 'value': row['id_resto']} for _, row in filtered_df.iterrows()]
    return options, options

# Callback pour afficher le tableau comparatif
@app.callback(
    Output('comparatif-table', 'children'),
    [Input('resto1-dropdown', 'value'),
     Input('resto2-dropdown', 'value'),
     Input('date-slider', 'value')]
)

def update_comparatif_table(resto1_id, resto2_id, date_range):
    if not resto1_id or not resto2_id:
                return "Sélectionnez 2 restaurants à comparer...."

    # Extraire les données pour chaque restaurant
    resto1 = df_restau[df_restau['id_resto'] == resto1_id]
    resto2 = df_restau[df_restau['id_resto'] == resto2_id]
    resto1_avis = df_avis[df_avis['id_resto'] == resto1_id]
    resto2_avis = df_avis[df_avis['id_resto'] == resto2_id]

    # dates limites pour le slider
    min_date = df_avis['date_exp'].min().year
    max_date = df_avis['date_exp'].max().year

    min_date,max_date=date_range

    # Filtrer les avis selon la plage de dates
    resto1_avis = df_avis[(df_avis['id_resto'] == resto1_id) & (df_avis['date_exp'].dt.year >= min_date) & (df_avis['date_exp'].dt.year <= max_date)]
    resto2_avis = df_avis[(df_avis['id_resto'] == resto2_id) & (df_avis['date_exp'].dt.year >= min_date) & (df_avis['date_exp'].dt.year <= max_date)]


    # Créer le tableau des caractéristiques des restaurants
    table_char = html.Table([
        html.Thead(html.Tr([html.Th("Restaurant"), html.Th("Caractéristiques")])),
        html.Tbody([
            html.Tr([html.Td(resto1['nom'].values[0]),html.Td(f"Nb Avis: {resto1['nb_avis'].values[0]}"), html.Td(f"Score: {resto1['score'].values[0]}")]),
            html.Tr([html.Td(resto2['nom'].values[0]),html.Td(f"Nb Avis: {resto2['nb_avis'].values[0]}"), html.Td(f"Score: {resto2['score'].values[0]}")])
            ])
        ])

    # Créer l'histogramme des notes
    def create_histogram(df, label):
        hist_data = df['note'].value_counts().sort_index()
        return go.Bar(
                x=hist_data.index,
                y=hist_data.values,
                name=label
                )

    # Créer les traces pour les histogrammes
    fig = go.Figure()
    fig.add_trace(create_histogram(resto1_avis, resto1['nom'].values[0]))
    fig.add_trace(create_histogram(resto2_avis, resto2['nom'].values[0]))

    fig.update_layout(
            barmode='group',
            title="Distribution des notes entre 1 et 5",
            xaxis_title="Note",
            yaxis_title="Nombre d'avis"
            )

    return html.Div([
        table_char,
        html.Br(),
        dcc.Graph(figure=fig)
        ])

#Callback pour mise a jour du slider
@app.callback(
        [Output('date-slider', 'min'),
            Output('date-slider', 'max'),
            Output('date-slider', 'value'),
            Output('date-slider', 'marks')],
        [Input('resto1-dropdown', 'value'),
            Input('resto2-dropdown', 'value')]
        )
def update_date_slider(resto1_id, resto2_id):
    if not resto1_id or not resto2_id:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
                    
    # Filtrer les avis pour les deux restaurants sélectionnés
    df_avis_filtered = df_avis[df_avis['id_resto'].isin([resto1_id, resto2_id])]

    # Obtenir les dates minimum et maximum
    min_date = df_avis_filtered['date_exp'].min().year
    max_date = df_avis_filtered['date_exp'].max().year


    # Créer les marques du slider
    marks = {year: str(year) for year in range(min_date, max_date + 1)}
    # Définir les valeurs du slider
    min_index = 0
    max_index = len(marks) - 1
    value = [min_date, max_date+1]
                
    #return min_index, max_index, value, marks
    return min_date, max_date, value, marks

# Callback pour rediriger vers la page d'analyse avec les restaurants sélectionnés
#@app.callback(
#        Output('url', 'href'),
#        [Input('compare-button', 'n_clicks')],
#        [Input('resto1-dropdown', 'value'),
#            Input('resto2-dropdown', 'value')
#            ]
#        )
#def redirect_to_analysis(n_clicks, resto1_id, resto2_id):
#    if n_clicks > 0 and resto1_id and resto2_id:
#        return f'/analyse?resto1={resto1_id}&resto2={resto2_id}'
#    return dash.no_update

# Layout pour la page d'analyse des avis
analyse_layout = html.Div([
    dcc.Location(id='url-analyse', refresh=True),
    html.H1('Analyse des avis'),
    dcc.Link('Retour à la page principale', href='/'),
    html.Br(),
    dcc.Dropdown(
        id='resto-analyse1-dropdown',
        placeholder='Sélectionnez le premier restaurant'
    ),
    dcc.Dropdown(
        id='resto-analyse2-dropdown',
        placeholder='Sélectionnez le deuxième restaurant (optionnel)'
    ),
    dcc.RadioItems(
        id='critere-radio',
        options=[
            {'label': 'Critères positifs', 'value': 'positifs'},
            {'label': 'Critères négatifs', 'value': 'negatifs'}
        ],
        value='positifs'
    ),
    dcc.Graph(id='avis-graph')
])

# Callback pour mettre à jour les dropdowns de l'analyse 
@app.callback(
        [Output('resto-analyse1-dropdown', 'options'),
            Output('resto-analyse2-dropdown', 'options'),
   #         Output('resto-analyse1-dropdown', 'value'),
   #         Output('resto-analyse2-dropdown', 'value')
        ],
        [Input('url-analyse', 'pathname')
         #,   Input('url-analyse', 'search')
        ]
        )
#def update_analysis_dropdowns_and_options(pathname, search):
def update_analysis_dropdowns_and_options(pathname):
    # Mise à jour des options des dropdowns
    options = [{'label': f"{row['nom']} (Score: {row['score']})", 'value': row['id_resto']} for _, row in df_restau.iterrows()]

    #resto1_id=None
    #resto2_id=None

    # Si des paramètres existent dans l'URL, on les extrait
    #if search:
      #  params = dict(param.split('=') for param in search[1:].split('&'))
      #  resto1_id = params.get('resto1')
      #  resto2_id = params.get('resto2')

    #return options, options, resto1_id, resto2_id
    return options, options

# Callback pour afficher le graphique des avis
@app.callback(
    Output('avis-graph', 'figure'),
    [Input('resto-analyse1-dropdown', 'value'),
     Input('resto-analyse2-dropdown', 'value'),
     Input('critere-radio', 'value')]
)

def update_avis_graph(resto1_id, resto2_id, critere):
    if not resto1_id:
        return {}
    
    def extract_keywords(df, critere_col):
        #suppression du null et transformation en chaine de caractères et en tableau la liste des mots
        keywords = df[critere_col].dropna().astype(str).loc[df[critere_col].astype(str).str.strip() != ''].str.replace(r"[\[\]']", '', regex=True).str.split(',').explode().str.strip()
        keywords = keywords[keywords != '']
        print(keywords.value_counts().head(20))
        return keywords.value_counts().head(20)

    # Création de la figure avec un ou 2 nuages de points selon la sélection
    fig = go.Figure()
    
    # Nuage de points pour le premier restaurant
    resto1_avis = df_sentiments[df_sentiments['id_resto'] == resto1_id]
    resto1_keywords = extract_keywords(resto1_avis, 'positive_points' if critere == 'positifs' else 'negative_points')

    fig.add_trace(go.Scatter(
        x=resto1_keywords.values,
        y=resto1_keywords.index,
        mode='markers',
        marker=dict(
            size=resto1_keywords.values,
            color='blue'  # Couleur fixe pour le restaurant 1
            ),
        name=df_restau[df_restau["id_resto"] == resto1_id]["nom"].values[0]
        ))

    # Ajouter les points pour le deuxième restaurant, si sélectionné
    if resto2_id:
        resto2_avis = df_sentiments[df_sentiments['id_resto'] == resto2_id]
        resto2_keywords = extract_keywords(resto2_avis, 'positive_points' if critere == 'positifs' else 'negative_points')

        fig.add_trace(go.Scatter(
            x=resto2_keywords.values,
            y=resto2_keywords.index,
            mode='markers',
            marker=dict(
                size=resto2_keywords.values,
                color='red'  # Couleur fixe pour le restaurant 2
                ),
            name=df_restau[df_restau["id_resto"] == resto2_id]["nom"].values[0]
            ))

    
    # mise en page
    fig.update_layout(
            title=f"Récurrence des termes utilisés par les clients ayant des connotations {'positifs' if critere == 'positifs' else 'négatifs'}",
            xaxis_title="Nombre d'occurrences",
            yaxis_title="Mot-clé",
            showlegend=True  # Afficher la légende avec les noms des restaurants
            )

    return fig


# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0",port=5001)



