import spacy
import pandas as pd
from textblob import TextBlob
nlp = spacy.load("en_core_web_sm")

#chargement des avis
df_resto = pd.read_csv("/home/ubuntu/projet/output/restaurants_avis.csv", sep ='#', index_col = "Id_Avis")
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
df_resto['Avis'] = df_resto['Avis'].astype(str).fillna('')

# Application de la fonction sur le DataFrame
df_resto['positive_points'] = df_resto['Avis'].apply(extract_positive_nouns)
df_resto['negative_points'] = df_resto['Avis'].apply(extract_negative_nouns)

df_resto.to_csv('/home/ubuntu/projet/output/avis_analyses.csv', sep='#')


