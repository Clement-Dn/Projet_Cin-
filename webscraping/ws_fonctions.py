

# Importations des librairies

# Webscrapping
import requests
from bs4 import BeautifulSoup
import re
import lxml.html as lh


# Manipulation des données
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




def get_donnees(url, elements_a_scrapper, cols):
    """
    Extraction des données d'une page web

    ENTREES 
    - url : url de la page concernée
    - elements_a_scrapper (liste) : balise des éléments à scrapper
    - cols (liste) : noms des colonnes dans le DataFrame final

    SORTIE 
    - DataFrame contenant les données scrappées d'une page


    """
    page = requests.get(url)

    # Vérification que l'URL est fonctionnelle
    if page.status_code != 200:
        print(f"Erreur lors du chargement de l'URL : {page.status_code}")
        return 
    
    # Objet arborescent pour extraire les éléments HTML
    doc = lh.fromstring(page.content)

    # Extraction des données  
    content = []
    for i in range(len(elements_a_scrapper)):
        content.append(doc.xpath(elements_a_scrapper[i]))


    # Création des DataFrame
    df_liste = []
    for j in range(len(elements_a_scrapper)):
        tmp = pd.DataFrame([content[j][i].text_content().strip() for i in range(len(content[i]))], columns=[cols[j]])
        tmp['key'] = tmp.index
        df_liste.append(tmp)


    # Jointure pour regrouper la note et le commentaire associé
    table = df_liste[0]
    for j in range(len(elements_a_scrapper)-1):
        table = table.join(df_liste[j+1], on='key', how='left', lsuffix='_l', rsuffix='_r')  
        del table['key_l']
        del table['key_r']

    return table.drop(columns=['key'])





def get_pages_comm(nb_pages, url):
    """ 
    Récupération des commentaires et notes CLIENTS sur plusieurs pages d'UN FILM

    ENTREES
    - url : url de la page principale du film
    - nb_pages : nombres de pages à scrapper


    SORTIE 
    - DataFrame contenant les données scrappées de TOUTES les pages demandées

    """

    table_finale = pd.DataFrame()
    cols = ['Note', 'Date','Description' ]
    elements_a_scrapper = ['//span[@class="stareval-note"]', \
'//span[@class="review-card-meta-date light"]', \
'//div[@class="content-txt review-card-content"]' ]
    uri_pages = '?page='

    for i in range (nb_pages):

        table_tmp = get_donnees(url + uri_pages + str(i+1), elements_a_scrapper, cols)
        table_finale = pd.concat([table_finale, table_tmp], ignore_index=True)

    return table_finale




def get_lien(annee, genre=None):
    """ 
    Construction du lien de la page d'accueil d'une liste de films :

    ENTREES  
    - année (int): année considérée des films (entre 2020 et 2029)
    - genre : si non mentionné, tous les genres confondus sont considérés

    SORTIE 
    - lien html

    """

    # Vérification de la validité de l'année
    if isinstance(annee, int):
        if annee > 2029 or annee < 2020:
            print(f"L'année '{annee}' n'est pas valide (doit être comprise entre 2020 et 2029)")
            return
    else:
        print(f"L'annee doit être un entier")
        return
    
    annee = str(annee)
     

    # Equivalence numérique du genre recherché
    genre_numerique = ''

    if genre is not None:

        genre_disponible = {
        "action": '13025',
        "animation": '13026',
        "aventure": '13001',
        "comedie" : '13005', 
        "drame": '13008',
        }
        if genre in genre_disponible:
            genre_numerique = genre_disponible[genre]
            
        else:
            print(f"Le genre '{genre}' n'est pas disponible.")
            return
   
        # Construction de l'URL
        return 'https://www.allocine.fr/films/genre-' + genre_numerique + '/decennie-2020/'+ 'annee-' + annee + '/'
    
    else:
        return 'https://www.allocine.fr/films/decennie-2020/'+ 'annee-' + annee + '/'




def get_page_comparaison_notes(lien):
    """ 
    Récupération des notes Presse et notes Spectateurs

    ENTREES
    - lien : lien html où les données sont à récupérer

    SORTIE 
    - Dataframe avec les notes moyennes des spectateurs et de la presse, ainsi que la durée, date et genre des films

    """
    
    code_page = requests.get(lien)


    # Vérification que l'URL est fonctionnelle
    if code_page.status_code != 200:
        print(f"Erreur lors du chargement de l'URL : {code_page.status_code}")
        return 
    
    soup = BeautifulSoup(code_page.text, 'html.parser')
    films = soup.find_all('div', class_='card entity-card entity-card-list cf')


    nom_colonnes = ['date', 'durée', 'spectateur', 'presse', 'genre1','genre2','genre3']
    table_finale = pd.DataFrame(columns=nom_colonnes)

    # Boucle pour chaque film présent sur la page
    for film in films:

        meta_body = film.find('div', class_='meta-body-item meta-body-info')


        # Extraction de la date
        date_span = meta_body.find('span', class_='date')
        date_text = date_span.get_text(strip=True)


        # Extraire de la durée
        duration_text = meta_body.get_text(strip=True)
        duration_match = re.search(r'(\d+h \d+min)', duration_text)
        duration = duration_match.group(1) if duration_match else None

        # Extraction des genres 
        genres_list = ['', '', '']
        genre_index = 0
        for genre in meta_body.find_all('span', class_='dark-grey-link'):
            genre_text = genre.get_text(strip=True)
            if genre_index < 3:
                genres_list[genre_index] = genre_text
                genre_index += 1



        # Extraction des notes
        avis = film.find_all('div', class_='rating-item')
        presse_note = None
        spectateurs_note = None

        for notation in avis:
            title = notation.find('span', class_='rating-title')
            title_text = title.get_text(strip=True) if title else None

            note = notation.find('span', class_='stareval-note')
            note_text = note.get_text(strip=True) if note else None
            
            if title_text == "Presse":
                presse_note = note_text
            elif title_text == "Spectateurs":
                spectateurs_note = note_text


        # Prise en compte du film si la note PRESSE et la note SPECTATEURS sont présentes
        if presse_note is not None and spectateurs_note is not None:
            new_row = pd.DataFrame([[date_text, duration, spectateurs_note, presse_note, genres_list[0],genres_list[1],genres_list[2]]], columns = nom_colonnes)
            table_finale = pd.concat([table_finale,new_row], ignore_index=True)
        
    return table_finale




def get_comparaison_notes(annee, nb_pages, genre=None):
    """ 
    Notes Presse et notes Spectateurs pour divers films de périmètre (annee, genre)

    ENTREES
    - année : possible seulement de 2020 à 2029
    - nb_pages : nombre de pages de films considérés
    - genre : si non mentionné, tous les genres confondus sont récupérés


    SORTIE 
    - Dataframe avec les notes moyennes des spectateurs et de la presse 

    """

    url = get_lien(annee, genre)
    if not url:
        return


    table_finale = pd.DataFrame()

    # Récupération des données en itérant sur le nombre de pages souhaitées
    uri_pages = '?page='
    for i in range (nb_pages):

        table = get_page_comparaison_notes(url + uri_pages + str(i+1))
        table_finale = pd.concat([table_finale, table], ignore_index=True)

    return table_finale