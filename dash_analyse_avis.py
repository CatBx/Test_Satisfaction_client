import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# Importation des données
df_avis = pd.read_csv("/home/ubuntu/projet/output/avis_analyses.csv",sep="#")
df_restau=pd.read_csv("/home/ubuntu/projet/output/restaurants.csv",sep="#")

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
            {'label': 'MAUVAIS', 'value': 'MAUVAIS'},
            {'label': 'MOYENS', 'value': 'MOYENS'},
            {'label': 'BONS', 'value': 'BONS'}
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
    html.Div(id='comparatif-table')
])

# Callback pour mettre à jour les dropdowns selon le filtre de score
@app.callback(
    [Output('resto1-dropdown', 'options'),
     Output('resto2-dropdown', 'options')],
    [Input('score-filter', 'value')]
)
def set_restaurants_options(selected_score):
    if selected_score == 'MAUVAIS':
        filtered_df = df_restau[df_restau['Score'] < 2.5]
    elif selected_score == 'MOYENS':
        filtered_df = df_restau[(df_restau['Score'] >= 2.5) & (df_restau['Score'] <= 4)]
    elif selected_score == 'BONS':
        filtered_df = df_restau[df_restau['Score'] > 4]
    else:
        filtered_df = df_restau

    options = [{'label': row['Nom'], 'value': row['Id_Resto']} for _, row in filtered_df.iterrows()]
    return options, options

# Callback pour afficher le tableau comparatif
@app.callback(
    Output('comparatif-table', 'children'),
    [Input('resto1-dropdown', 'value'),
     Input('resto2-dropdown', 'value')]
)
def update_comparatif_table(resto1_id, resto2_id):
    if resto1_id and resto2_id:
        resto1 = df_restau[df_restau['Id_Resto'] == resto1_id]
        resto2 = df_restau[df_restau['Id_Resto'] == resto2_id]

        return html.Table([
            html.Thead(html.Tr([html.Th(col) for col in resto1.columns])),
            html.Tbody([
                html.Tr([html.Td(resto1[col].values[0]) for col in resto1.columns]),
                html.Tr([html.Td(resto2[col].values[0]) for col in resto2.columns])
            ])
        ])
    return "Sélectionnez deux restaurants pour comparer."

# Layout pour la page d'analyse des avis
analyse_layout = html.Div([
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
     Output('resto-analyse2-dropdown', 'options')],
    [Input('url', 'pathname')]
)
def set_analysis_restaurants_options(pathname):
    options = [{'label': row['Nom'], 'value': row['Id_Resto']} for _, row in df_restau.iterrows()]
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
        keywords = df[critere_col].dropna().str.split(',').explode().str.strip()
        return keywords.value_counts().head(20)

    resto1_avis = df_avis[df_avis['Id_Resto'] == resto1_id]
    resto1_keywords = extract_keywords(resto1_avis, 'positive_points' if critere == 'positifs' else 'negative_points')

    fig = px.scatter(x=resto1_keywords.values, y=resto1_keywords.index, size=resto1_keywords.values, color=resto1_keywords.values, 
                     color_continuous_scale='Viridis', title=f'Mots-clés pour {df_restau[df_restau["Id_Resto"] == resto1_id]["Nom"].values[0]}')
    
    if resto2_id:
        resto2_avis = df_avis[df_avis['Id_Resto'] == resto2_id]
        resto2_keywords = extract_keywords(resto2_avis, 'positive_points' if critere == 'positifs' else 'negative_points')
        fig.add_scatter(x=resto2_keywords.values, y=resto2_keywords.index, mode='markers', marker=dict(size=resto2_keywords.values, color=resto2_keywords.values), 
                        name=df_restau[df_restau["Id_Resto"] == resto2_id]["Nom"].values[0])

    fig.update_layout(xaxis_title='Nombre d\'occurrences', yaxis_title='Mot-clé', coloraxis_colorbar=dict(title='Occurrences'))
    return fig

# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0",port=5001)



