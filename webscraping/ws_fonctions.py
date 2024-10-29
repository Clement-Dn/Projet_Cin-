

# Importations des librairies

# Webscrapping
import requests
from io import BytesIO
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




def get_presse_vs_spect(annee, nb_pages, genre=None):
    """ 
    Notes Presse et notes Spectateurs pour divers films de périmètre (annee, genre)

    ENTREES
    - année : possible seulement de 2020 à 2029
    - nb_pages : nombre de pages de films considérés
    - genre : si non mentionné, tous les genres confondus sont récupérés


    SORTIE 
    - Dataframe avec les notes moyennes des spectateurs et de la presse 

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
        url = 'https://www.allocine.fr/films/genre-' + genre_numerique + '/decennie-2020/'+ 'annee-' + annee + '/'
    
    else:
        url = 'https://www.allocine.fr/films/decennie-2020/'+ 'annee-' + annee + '/'
    
    table_finale = pd.DataFrame()
    cols = ['Auteurs', 'Note']
    elements_a_scrapper = ['//span[contains(@class, " rating-title")]',\
'//span[@class="stareval-note"]']  
    uri_pages = '?page='

    # Récupération des données en utérant sur le nombre de pages souhaitées
    for i in range (nb_pages):

        table = get_donnees(url + uri_pages + str(i+1), elements_a_scrapper, cols)
        table_finale = pd.concat([table_finale, table], ignore_index=True)

    if genre is not None:
        table_finale['genre'] = genre

    return table_finale