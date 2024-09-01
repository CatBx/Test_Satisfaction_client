import requests
import spacy
import pandas as pd
from textblob import TextBlob
import nltk
from nltk.data import find
nlp = spacy.load("en_core_web_sm")

# répertoire des données NLTK
nltk.data.path.append('/usr/local/nltk_data')


# Vérification et téléchargement du corpus 'punkt' et 'punkt_tab'
try:
    find('tokenizers/punkt')
    print("Le corpus 'punkt' est déjà téléchargé.")
except LookupError:
    print("Le corpus 'punkt' n'est pas présent. Téléchargement en cours...")
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
    print("Le corpus 'punkt_tab' est déjà téléchargé.")
except LookupError:
    print("Le corpus 'punkt_tab' n'est pas présent. Téléchargement en cours...")
    nltk.download('punkt_tab')



# Vérifier que les ressources TextBlob sont installées
def check_textblob_resources():
    from textblob import Word
    try:
        # Création d'un simple objet Word pour vérifier les données
        word = Word("example")
        print("Les corpus TextBlob sont présents.")
    except Exception as e:
        print(f"Erreur avec TextBlob: {e}")
        # Tenter de télécharger les données de TextBlob si nécessaire
        import subprocess
        subprocess.run(["python3", "-m", "textblob.download_corpora"], check=True)

check_textblob_resources()

#Textblob fonctionne ?
text = "This is a test sentence to verify TextBlob functionality."
blob = TextBlob(text)
print("Sentences:", blob.sentences)
#Spacy fonctionne ?
doc = nlp("This is a test sentence.")
print("Tokens:", [token.text for token in doc])



#chargement des avis
#URL de base de l'API FastAPI
BASE_URL = "http://fastapi:8000"
print(f"Début de l'analyse ...")

# Récupération de la liste des avis 
def get_avis():
    response = requests.get(f"{BASE_URL}/liste_avis")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

# Initialisation du DataFrame
df_avis = get_avis()
print(f"Nombre d'avis récupérés : {len(df_avis)}")
print("Colonnes du DataFrame df_avis :", df_avis.columns)
print(df_avis.head())

# Gestion des synonymes
synonyms_dict = {
    'price': ['price', 'prices', 'bill', 'cost'],
    'service': ['service', 'services'],
    'wait': ['wait', 'waiting', 'waits']
}

# Fonction pour mapper un synonyme à son mot principal
def map_to_main_word(word, synonyms_dict):
    for main_word, synonyms in synonyms_dict.items():
        if word in synonyms:
            return main_word
    return word

def extract_positive_nouns(review):
    blob = TextBlob(review)
    sentences = blob.sentences
    
    positive_sentences = []
    nouns = []
    
    for sentence in sentences:
        if sentence.sentiment.polarity > 0:  # Si le sentiment est positif
            positive_sentences.append(str(sentence))
    
    for sent in positive_sentences:
        doc = nlp(sent)
        for token in doc:
            if token.pos_ == 'NOUN':  # Extraire uniquement les noms communs
                main_word = map_to_main_word(token.lemma_, synonyms_dict)
                nouns.append(main_word)
    
    return list(set(nouns))  # Éliminer les doublons

def extract_negative_nouns(review):
    blob = TextBlob(review)
    sentences = blob.sentences
    
    negative_sentences = []
    nouns = []
    
    for sentence in sentences:
        if sentence.sentiment.polarity < 0:  # Si le sentiment est négatif
            negative_sentences.append(str(sentence))
    
    for sent in negative_sentences:
        doc = nlp(sent)
        for token in doc:
            if token.pos_ == 'NOUN':  # Extraire uniquement les noms communs
                main_word = map_to_main_word(token.lemma_, synonyms_dict)
                nouns.append(main_word)
    
    return list(set(nouns))  # Éliminer les doublons

# Convertir les avis en chaînes de caractères et gérer les valeurs manquantes
df_avis['avis'] = df_avis['avis'].astype(str).fillna('')

# Application de la fonction sur le DataFrame
df_avis['positive_points'] = df_avis['avis'].apply(extract_positive_nouns)
df_avis['negative_points'] = df_avis['avis'].apply(extract_negative_nouns)

print("Colonnes du DataFrame df_avis après analyse:", df_avis.columns)
print(df_avis.head())

# Sauvegarde de l'analyse en base 
print(f"Sauvegarde en base ...")
df_backup_analyse=df_avis[['id_avis','id_resto','positive_points','negative_points']]
print(df_backup_analyse.head())
# Convertir le DataFrame en liste de dictionnaires
data = df_backup_analyse.to_dict(orient='records')
dataload = {'data': data}
#URL de l'API pour backuper les sentiments
url = "http://fastapi:8000/save_analyses"
# Envoi de la requête POST
response = requests.post(url, json=dataload)
# Check retour
if response.status_code == 200:
    print("Données sauvegardées avec succès")
else:
    print(f"Erreur {response.status_code}: {response.text}")


