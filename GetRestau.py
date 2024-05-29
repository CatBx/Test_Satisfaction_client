from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from tabulate import tabulate #pip install tabulate

#==============================================================
# Initialisation des variables
#==============================================================
ListeMails, ListeNoms, ListeTotalReviews,ListeScores = [],[],[],[]
ListeIds,ListeIdRestoUnik,ListeAuteurAvis, ListeAuteurNotes, ListeAuteurNbNotes, ListeAvis, ListeDateAvis, ListeDateExp , ListeReply, ListeDateReply = [],[],[],[],[],[],[],[],[],[]
i=1 #compteur pages
idResto=0 #identifiant restaurant
page="INIT"

head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'refere': 'https://example.com'
        }


url = "https://www.trustpilot.com/categories/general_restaurants?country=GB"
page=requests.get(url,head)
print('debut')
#==============================================================
# Boucle sur toutes les pages
#==============================================================
#while i<3 :
while page:
    soup=bs(page.content,"lxml")
    print(str(page.status_code)+' : '+url)

    #==============================================================
    # Boucle sur tous les restaurants de la page
    #==============================================================
    liste_restaurants = soup.find_all('div', attrs = {'class': "paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2"})

    for restaurant in liste_restaurants :
        #Réinitialisation des listes
        #ListeIdRestoUnik,ListeAuteurAvis, ListeAuteurNotes, ListeAuteurNbNotes, ListeAvis, ListeDateAvis, ListeDateExp , ListeReply, ListeDateReply = [],[],[],[],[],[],[],[],[]

        # Récupération du nom des restaurants
        nom = restaurant.find('p',class_='typography_heading-xs__jSwUz typography_appearance-default__AAY17 styles_displayName__GOhL2').text.strip()
        print('     --> '+nom)
        ListeNoms.append(nom)
        idResto=idResto+1
        ListeIds.append(idResto)
		

        #Récupération du TrustScore
        if (restaurant.find('span',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_trustScore__8emxJ') is  None) :
            ListeScores.append("")
        else :
            score = restaurant.find('span',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_trustScore__8emxJ').text.strip()
            #ListeScores.append(score)
            ListeScores.append(score[11:])


        # Récupération page spéciale affectée au restaurant
        page_ref=restaurant.find('a').get('href')
        url_resto="https://www.trustpilot.com"+page_ref
        print('          '+url_resto)
        page_resto=requests.get(url_resto)
        soup_resto=bs(page_resto.content,"lxml")

        # Récupération du nombre d'avis
        if (soup_resto.find('p', attrs = {'class':'typography_body-l__KUYFJ typography_appearance-default__AAY17', 'data-reviews-count-typography':'true'}) is  None) :
            ListeTotalReviews.append("")
        else :
            nb_reviews=soup_resto.find('p', attrs = {'class':'typography_body-l__KUYFJ typography_appearance-default__AAY17', 'data-reviews-count-typography':'true'}).text.strip()
            #ListeTotalReviews.append(nb_reviews)
            ListeTotalReviews.append(nb_reviews[0:-6])

        # Récupération des contacts
        # Adresse mail
        if (soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}) is  None) :
            ListeMails.append("")
        else :
            contact=soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'})
            mail=soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}).text.strip()
            ListeMails.append(mail)


        #=========================================================================================
        # Boucle sur toutes les pages liées à ce restaurant pour récupérer l'ensemble des avis
        #=========================================================================================
        j=1
        #while j<3 :
        while page_resto:
            #traitement des reviews
            liste_avis = soup_resto.find_all('div', attrs = {'class': "styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ"})
            for avis in liste_avis :
                # Rattachement à l'Id Resto
                ListeIdRestoUnik.append(idResto)

                # Récupération du nom de l'auteur
                auteur_avis = avis.find('span',class_='typography_heading-xxs__QKBS8 typography_appearance-default__AAY17').text.strip()
				ListeAuteurAvis.append(auteur_avis)

                # Récupération de la date de l'avis
                if (avis.find('div', attrs = {'class':'typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_datesWrapper__RCEKH'}) is  None) :
                    ListeDateAvis.append("")
                else :
                    date_avis = avis.find('div',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_datesWrapper__RCEKH').text.strip()
                    ListeDateAvis.append(date_avis)

                # Récupération de la date de l'expérience
                #if (avis.find('b', attrs = {'class':'typography_body-m__xgxZ_ typography_appearance-default__AAY17 typography_weight-heavy__E1LTj'}) is  None) :
                if (avis.find('p', attrs = {'class':'typography_body-m__xgxZ_ typography_appearance-default__AAY17'}) is  None) :
                    ListeDateExp.append("")
                else :
                    date_exp = avis.find('p',class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17').text.strip()
                    date_exp = date_exp.split('Date of experience: ')[1]
                    ListeDateExp.append(date_exp)

                # Récupération de la note donnée
                auteur_note = avis.find('div',class_='styles_reviewHeader__iU9Px').get("data-service-review-rating")
                ListeAuteurNotes.append(auteur_note)

                # Récupération du nombre de notes données par l'auteur
                auteur_nb_note = avis.find('div',class_='styles_consumerExtraDetails__fxS4S').text.strip()
                auteur_nb_note = auteur_nb_note.split(' review')[0]
                ListeAuteurNbNotes.append(auteur_nb_note)

                # Récupération de l'avis
                if (avis.find('p', attrs = {'class':'typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn'}) is  None) :
                    ListeAvis.append("")
                else :
                    aut_avis = avis.find('p',class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn').text.strip()
                    ListeAvis.append(aut_avis)

                # Récupération du reply
                if (avis.find('p', attrs = {'class':'typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX','data-service-review-business-reply-text-typography':'true'}) is  None) :
                    ListeReply.append("")
                else :
                    reply = avis.find('p', attrs = {'class':'typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX','data-service-review-business-reply-text-typography':'true'}).text.strip()
                    ListeReply.append(reply)

                # Récupération de la date du reply
                if (avis.find('span', attrs = {'class':'styles_replyInfo__FYSje'}) is  None) :
                    ListeDateReply.append("")
                else :
                    #date_reply = avis.find('span',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_replyDate__Iem0_').text.strip()
                    date_reply = avis.find('span',class_='styles_replyInfo__FYSje').get('datetime')
                    ListeDateReply.append(date_reply)


            #Passage à la page d'avis suivante
            j=j+1
            url_resto_reviews=url_resto+'?page='+str(j)
            print('          '+url_resto_reviews)
            page_resto=requests.get(url_resto_reviews)
            soup_resto=bs(page_resto.content,"lxml")


        #Fin de la récupération des éléments relatifs au restaurant
        print('     [DF RESTO] id='+str(idResto))

        #df_resto = pd.DataFrame(list(zip(ListeNoms, ListeTotalReviews,ListeScores,ListeMails),list(zip(ListeIdRestoUnik,ListeAuteurAvis,ListeAuteurNbNotes,ListeAuteurNotes,ListeAvis,ListeDateAvis,ListeDateExp,ListeReply,ListeDateReply)), columns =['Id Resto', 'Auteur', 'Nb Notes','Note','Avis','Date Avis','Date Experience','Reply','Date Reply'])
        #print(tabulate(df_resto, headers='keys', tablefmt='fancy_grid')) 
        #df_resto.to_json('reviews/review_'+str(idResto)+'.json', orient = 'split', compression = 'infer', index = 'true')

    #Passage à la page suivante
    i=i+1
    url="https://www.trustpilot.com/categories/general_restaurants?country=GB&page="+str(i)
    page=requests.get(url,head)

#Fin programme : Impression du df des restaurants
print('[DF RESTO GLOBAL]')
df_resto_global = pd.DataFrame(list(zip(ListeIds, ListeNoms, ListeMails, ListeTotalReviews, ListeScores)), columns =['Id_Resto', 'Nom', 'Contact','Nb Avis','Score'])
df_reviews = pd.DataFrame(list(zip(ListeIdRestoUnik,ListeAuteurAvis,ListeAuteurNbNotes,ListeAuteurNotes,ListeAvis,ListeDateAvis,ListeDateExp,ListeReply,ListeDateReply)), columns =['Id_Resto', 'Auteur', 'Nb Notes','Note','Avis','Date Avis','Date Experience','Reply','Date Reply'])
#df_global=df_resto_global.merge(right=df_reviews,on = "Id_Resto", how='outer')
#on ne conserve que les restaus avec avis
df_global=df_resto_global.merge(right=df_reviews,on = "Id_Resto", how='inner')

#Gestion des NAN
#values_zero = {"Nb Avis": 0, "Nb Notes": 0}
#df_global.fillna(value=values_zero)


#print(tabulate(df_resto, headers='keys', tablefmt='fancy_grid')) 
df_global.to_json('gb_restaurants_avis.json', orient = 'split', compression = 'infer', index = 'true')
df_global.to_csv('gb_restaurants_avis.csv', sep=';',index=False)

#df_resto_global.to_json('restaurants.json', orient = 'split', compression = 'infer', index = 'true')
df_reviews.to_csv('restaurants_avis.csv', sep='#',index=False)
df_resto_global.to_csv('restaurants.csv', sep='#',index=False)
df_global.to_csv('gb_restaurants_avis.csv', sep=';',index=False)

#print(ListeNoms)
#print(ListeScores)
#print(ListeAuteurAvis)
#print(ListeAuteurNbNotes)
#print(ListeAuteurNotes)
#print(ListeAvis)
#print(ListeMails)
#print(ListeTels)
#print(len(ListeNoms))
#print(len(ListeScores))
#print(len(ListeMails))
#print(len(ListeTels))

#print(ListeDateExp)
#print(ListeDateAvis)
#print(ListeDateReply)
#print(ListeReply)
#print(len(ListeDateExp))
#print(len(ListeDateAvis))
#print(len(ListeDateReply))
#print(len(ListeReply))
#print(len(ListeAuteurAvis))
#print(len(ListeAuteurNbNotes))
#print(len(ListeAuteurNotes))
#print(len(ListeAvis))
print('Nb restaurants traités : '+str(len(ListeIds)))
