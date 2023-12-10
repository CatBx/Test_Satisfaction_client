from bs4 import BeautifulSoup as bs
import requests 
import re
import pandas as pd

#==============================================================
# Initialisation des variables
#==============================================================
ListeNoms, ListeScores, ListeSites , ListeReviews, ListeMails, ListeTels, ListeAdr = [],[],[],[],[],[],[]
i=0 #compteur pages
page="INIT"

#==============================================================
# Boucle sur toutes les pages
#==============================================================
while i<3 :
#while page:
    i=i+1
    if i==1 :
        url = "https://www.trustpilot.com/categories/general_restaurants?country=GB"
    else :
        url="https://www.trustpilot.com/categories/general_restaurants?country=GB&page="+str(i)
    print(url)
    page=requests.get(url)
    print(page.status_code)
    soup=bs(page.content,"lxml")

    #==============================================================
    # Boucle sur tous les restaurants de la page
    #==============================================================
    liste_restaurants = soup.find_all('div', attrs = {'class': "paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2"})

    for restaurant in liste_restaurants : 
    
        # Récupération du nom des restaurants
        nom = restaurant.find('p',class_='typography_heading-xs__jSwUz typography_appearance-default__AAY17 styles_displayName__GOhL2').text.strip()
        ListeNoms.append(nom)

        #Récupération du TrustScore
        if (restaurant.find('span',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_trustScore__8emxJ') is  None) :
            ListeScores.append("")
        else :
            score = restaurant.find('span',class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_trustScore__8emxJ').text.strip()
            ListeScores.append(score)

        # Récupération page spéciale affectée au restaurant
        page_ref=restaurant.find('a').get('href')
        url_resto="https://www.trustpilot.com"+page_ref
        page_resto=requests.get(url_resto)
        soup_resto=bs(page_resto.content,"lxml")
                                                
        # Récupération du nombre d'avis
        if (soup_resto.find('p', attrs = {'class':'typography_body-l__KUYFJ typography_appearance-default__AAY17', 'data-reviews-count-typography':'true'}) is  None) :
            ListeReviews.append("")
        else :
            nb_reviews=soup_resto.find('p', attrs = {'class':'typography_body-l__KUYFJ typography_appearance-default__AAY17', 'data-reviews-count-typography':'true'}).text.strip()
            ListeReviews.append(nb_reviews)

        # Récupération des contacts
        # Adresse mail
        if (soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}) is  None) :
            ListeMails.append("")
        else :
            contact=soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'})
            mail=soup_resto.find('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}).text.strip()
            #test si @
            if '@' in mail :
                ListeMails.append(mail)
            else :
                ListeMails.append("")
                if re.search('[a-zA-Z]', mail):
                    ListeAdr.append(mail)
                    ListeTels.append("")
                else :
                    ListeTels.append(mail)


        # Telephone
        if (contact.find_next('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}) is  None) :
            ListeTels.append("")
        else :
            tel=contact.find_next('li', attrs = {'class':'styles_contactInfoElement__SxlS3'}).text.strip()
            if re.search('[a-zA-Z]', tel):
                ListeTels.append("")
                ListeAdr.append(tel)
            else:
                ListeTels.append(tel)

print(ListeNoms)
print(ListeScores)
print(ListeReviews)
print(ListeMails)
print(ListeTels)
print(ListeAdr)
print(len(ListeNoms))
print(len(ListeScores))
print(len(ListeReviews))
print(len(ListeMails))
print(len(ListeTels))
print(len(ListeAdr))

