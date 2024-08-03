from fastapi import FastAPI
from fastapi import Header
from typing import Optional
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import Request
import psycopg2
import os
import time
import csv
import pandas as pd

#===========================================================================================================================
# Variables d'environnement pour la connexion PostgreSQL
#===========================================================================================================================
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')

#===========================================================================================================================
# Dataframes globaux
#===========================================================================================================================
restaurants_df = pd.DataFrame()
avis_df = pd.DataFrame()

#===========================================================================================================================
# Définition des classes
#===========================================================================================================================
class RestaurantRanking(BaseModel):
    id_resto: int
    nom: str
    score: float
    classement: int

class Restaurants(BaseModel):
    id_resto: int
    nom: str
    contact: str
    nb_avis: int
    score: float

class Avis(BaseModel):
    id_avis: int
    id_resto: int
    auteur: str
    nb_notes: int
    note: int
    avis: str
    date_avis: str
    date_exp: str
    reply: str
    date_reply: str

class AvisStats(BaseModel):
    nb_note: int
    moyenne: float
    mediane: float

#===========================================================================================================================
#Définition des apis
#===========================================================================================================================
api = FastAPI(
        openapi_tags=[
            {
                'name': 'home',
                'description': 'Fonctionnalités d\'interrogation basiques'
                },
            {
                'name': 'statistiques',
                'description': 'Fonctionnalités statistiques sur les avis des restaurants'
                }
            ],
        title="DST Projet Satisfaction Clients",
        description="API utilisée pour interroger la base des avis clients sur les restaurants Britanniques et application de ML",
        version="1.0.1"
        )

@api.get('/',name="Test de fonctionnement basique de l'api", tags=['home'])
def get_index():
    """Point de terminaison pour valider que l'api est bien fonctionnelle
    """
    return {'Validité': 'OK'}

#===========================================================================================================================
# Gestion du chargement initial des avis et resto dans des dataframes
#===========================================================================================================================
def get_db_connection():
    conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PWD,
            host=DB_HOST,
            port=DB_PORT
            )
    return conn

def check_postgres():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM avis;")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count > 1000
        except psycopg2.OperationalError:
            return False

def clean_dataframe(df):
    # Remplacer les valeurs NaN, infinies par 0 ou une chaîne vide selon le contexte
    df = df.replace([float('inf'), float('-inf')], 0)
    df = df.fillna('')  # Remplacer NaN par une chaîne vide pour les colonnes de type string
    return df

def load_dataframes():
    global restaurants_df, avis_df
    conn = get_db_connection()

    # Charger les restaurants
    restaurants_query = "SELECT id_resto, nom, coalesce(contact,' ') contact, coalesce(nb_avis,0) nb_avis, coalesce(score,-1) score FROM restaurants"
    restaurants_df = pd.read_sql_query(restaurants_query, conn)

    # Charger les avis
    avis_query="SELECT id_avis, id_resto, auteur, coalesce(nb_notes,1) nb_notes, note, coalesce(avis,' ') avis, coalesce(date_avis,to_char(date_exp,'YYYY-MM-DD'),' ') date_avis, to_char(date_exp,'YYYY-MM-DD') date_exp, coalesce(reply,' ') reply, coalesce(to_char(date_reply,'YYYY-MM-DD'),' ') date_reply FROM avis;"
    avis_df = pd.read_sql_query(avis_query, conn)

    #Nettoyage des DF
    restaurants_df = clean_dataframe(restaurants_df)
    avis_df = clean_dataframe(avis_df)

    conn.close()

# Charger les dataframes au démarrage
@api.on_event("startup")
def on_startup():
    # Attente que le PG soit chargé
    while True:
        if check_postgres():
            print("Postgres OK")
            break
        else:
            print("Postgres pas encore disponible...")
            time.sleep(5)
    load_dataframes()

# Vérifier le nombre de restaurants chargés 
@api.get("/nb_restaurants", name="Nombre de restaurants chargés", tags=['home'])
def nb_restaurants():
        return {"Nb Restaurants chargés ": len(restaurants_df)}

# Vérifier le nombre d'avis chargés
@api.get("/nb_avis", name="Nombre d'avis chargés", tags=['home'])
def nb_avis():
    return {"Nb Avis chargés ": len(avis_df)}

# Liste des restaurants
@api.get("/liste_restaurants", response_model=List[Restaurants], name="Liste complète des restaurants",tags=['home'])
def liste_restaurants():
    return restaurants_df.to_dict(orient='records')

# Liste des avis
@api.get("/liste_avis", response_model=List[Avis], name="Liste complètes des avis",tags=['home'])
def liste_avis():
    return avis_df.to_dict(orient='records')

# Top 10 des restaurants les mieux classés
@api.get("/top_10_restaurants", response_model=List[Restaurants], name="Top 10 des restaurants les mieux classés", tags=['statistiques'])
def top_10_restaurants():
    sorted_restaurants = restaurants_df.sort_values(by='score', ascending=False)
    top_10 = sorted_restaurants.head(10)
    return top_10.to_dict(orient='records')

# Nb avis d'un restaurant (Id)
@api.get("/nb_avis/{id_resto}", response_model=List[Avis], name="Nombre d'avis pour un ID de restaurant donné", tags=['statistiques'])
def nb_avis_by_resto(id_resto: int):
    filtered_avis = avis_df[avis_df['id_resto'] == id_resto]
    return filtered_avis.to_dict(orient='records')

# Liste des avis d'un restaurant (Id)
@api.get("/avis/{id_resto}", response_model=List[Avis], name="Liste des avis pour un ID de restaurant donné", tags=['statistiques'])
def get_avis_by_resto(id_resto: int):
    filtered_avis = avis_df[avis_df['id_resto'] == id_resto]
    return filtered_avis.to_dict(orient='records')

# Nombre d'avis pour un restaurant donné
@api.get("/avis_count/{id_resto}", name="Nombre d'avis pour un restaurant donné", tags=['statistiques'])
def nb_avis_resto(id_resto: int):
    filtered_avis = avis_df[avis_df['id_resto'] == id_resto]
    return {"count": len(filtered_avis)}

@api.get("/restaurant_classement/{id_resto}", response_model=RestaurantRanking)
def get_restaurant_classement(id_resto: int):
    if id_resto not in restaurants_df['id_resto'].values:
        raise HTTPException(status_code=404, detail="ID Restaurant inconnu")
   
    # Trier les restaurants par score de manière décroissante
    sorted_restaurants = restaurants_df.sort_values(by='score', ascending=False)
    # Ajouter une colonne de classement
    sorted_restaurants['classement'] = range(1, len(sorted_restaurants) + 1)
    # Récupérer les informations du restaurant demandé
    restaurant_info = sorted_restaurants[sorted_restaurants['id_resto'] == id_resto].iloc[0]
    return RestaurantRanking(
            id_resto=restaurant_info['id_resto'],
            nom=restaurant_info['nom'],
            score=restaurant_info['score'],
            classement=restaurant_info['classement']
            )

# Moyenne + médiane des notes pour un restaurant donné
@api.get("/avis_stats/{id_resto}", response_model=AvisStats, name="Moyenne et médiane des notes pour un restaurant donné", tags=['statistiques'])
def get_avis_stats(id_resto: int):
    filtered_avis = avis_df[avis_df['id_resto'] == id_resto]
    print(avis_df.dtypes)
    print(filtered_avis)
    if filtered_avis.empty:
        raise HTTPException(status_code=404, detail="ID Restaurant inconnu")
    moyenne = filtered_avis['note'].mean()
    mediane = filtered_avis['note'].median()
    nb_note = filtered_avis['note'].count()
    return AvisStats(nb_note=nb_note, moyenne=moyenne, mediane=mediane)



