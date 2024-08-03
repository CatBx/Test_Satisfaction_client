import psycopg2
import os

# Variables d'environnement pour la connexion PostgreSQL
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')

# Fichier SQL à charger
SQL_FILE_PATH = '/app/load_db.sql'

# Connexion à la base de données
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PWD,
        host=DB_HOST,
        port=DB_PORT
        )

    cursor = conn.cursor()
except psycopg2.OperationalError as e:
    print(f"Erreur de connexion à la base de données : {e}")
    exit;

# Lecture et exécution du script SQL
with open(SQL_FILE_PATH, 'r') as f:
    sql = f.read()
    cursor.execute(sql)
    conn.commit()

# Fermeture de la connexion
cursor.close()
conn.close()

print("Chargement OK !")

