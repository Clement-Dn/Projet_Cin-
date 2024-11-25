


##########################   Fonctions pour récupérer différentes informations sur internet    ###########################
##########################################################################################################################
##########################################################################################################################



# Importations des librairies

# Webscrapping
import requests
from bs4 import BeautifulSoup
import re
import lxml.html as lh
import io 

import asyncio
import aiohttp
import pandas as pd
import nest_asyncio

# Manipulation des données
import pandas as pd
import numpy as np







#############################################################
#############################################################
#############################################################
#############################################################  Récupération d'une série de films avec leurs notes associées 
#############################################################
#############################################################
#############################################################



def get_lien(annee, genre=None):
    """ 
    Construction du lien de la page d'accueil d'une liste de films :

    ENTREES  
    - année (int): année considérée des films (entre 2010 et 2029)
    - genre : si non mentionné, tous les genres confondus sont considérés

    SORTIE 
    - lien html

    """

    # Vérification de la validité de l'année
    if isinstance(annee, int):
        if annee > 2029 or annee < 2010:
            print(f"L'année '{annee}' n'est pas valide (doit être comprise entre 2010 et 2029)")
            return
    else:
        print(f"L'annee doit être un entier")
        return
    
    # récupération de la décennie correspondant sur le site AlloCine
    decennie = '2020'

    if annee < 2020:
        decennie = '2010'
     
    
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
        return 'https://www.allocine.fr/films/genre-' + genre_numerique + '/decennie-' + decennie + '/annee-' + annee + '/'
    
    else:
        return 'https://www.allocine.fr/films/decennie-' + decennie + '/annee-' + annee + '/'




def get_page_comparaison_notes(lien):
    """ 
    Récupération des notes Presse et notes Spectateurs pour tous les films se trouvant sur une page

    ENTREES
    - lien : lien html où les données sont à récupérer

    SORTIE 
    - Dataframe avec les notes moyennes des spectateurs et de la presse, ainsi que la durée, date et genre des films

    """
    try: 
        code_page = requests.get(lien)

        # Vérification que la requête est réussie
        if code_page.status_code != 200:
            print(f"Erreur lors du chargement de l'URL : {code_page.status_code}")
            return "fini"
    
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")

        return "fini"


    balises = BeautifulSoup(code_page.text, 'html.parser')
    films = balises.find_all('div', class_='card entity-card entity-card-list cf')


    nom_colonnes = ['titre','identifiant','date', 'durée','auteur', 'spectateur', 'presse', 'genre1','genre2','genre3']

    table_finale = pd.DataFrame(columns=nom_colonnes)

    # Boucle pour chaque film présent sur la page
    for film in films:
            

        meta_body = film.find('div', class_='meta-body-item meta-body-info')

        if meta_body:


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
            
            # Prise en compte des autres éléments que si la note SPECTATEURS et la note PRESSE sont présentes
            if presse_note is not None and spectateurs_note is not None:
            

                # Extraction de la date
                date = ""
                date_span = meta_body.find('span', class_='date')
                date = date_span.get_text(strip=True) if date_span else None   


                # Extraction de la durée
                duree = ""
                duree_text = meta_body.get_text(strip=True)
                duree_h_min = re.search(r'(\d+h \d+min)', duree_text)
                duree = duree_h_min.group(1) if duree_h_min else None   


                # Extraction de l'auteur
                auteur = ""
                meta_direction = film.find('div', class_='meta-body-item meta-body-direction')
                if meta_direction:
                    auteur_texte = meta_direction.find('span', class_='dark-grey-link')
                    auteur = auteur_texte.get_text(strip=True) if auteur_texte else None   


                # Extraction des genres du film
                genres_list = ['', '', '']
                genre_index = 0
                for genre in meta_body.find_all('span', class_='dark-grey-link'):
                    genre_text = genre.get_text(strip=True) if genre else None
                    if genre_index < 3:
                        genres_list[genre_index] = genre_text
                        genre_index += 1


                # Extraction du titre et de l'identifiant
                titre = ""
                identifiant = ""
                balise_titre = film.find('a', class_='meta-title-link')
                titre = balise_titre.get_text(strip=True) if balise_titre else None

                lien_film = balise_titre['href']
                numero = re.search(r'cfilm=(\d+)', lien_film)
                identifiant = numero.group(1)

                # Ajout de la ligne du film 
                new_row = pd.DataFrame([[titre, identifiant, date, duree , auteur, spectateurs_note, presse_note, genres_list[0],genres_list[1],genres_list[2]]], columns = nom_colonnes)
                table_finale = pd.concat([table_finale, new_row], ignore_index=True)
        
    return table_finale
        




def get_comparaison_notes(annee, genre=None):
    """ 
    Notes Presse et notes Spectateurs pour divers films de périmètre (annee, genre)

    ENTREES
    - année : possible seulement de 2010 à 2029
    - nb_pages : nombre de pages de films considérés
    - genre : si non mentionné, tous les genres confondus sont récupérés


    SORTIE 
    - Dataframe avec les films qui ont nécessairement les notes moyennes des spectateurs et de la presse.

    """
    url = get_lien(annee, genre)

    if not url:
        return

    table_finale = pd.DataFrame()

    # Récupération des données en itérant sur le nombre de pages souhaitées
    uri_pages = '?page='

    i = 0
    valide = True

    while valide == True:
    
        table = get_page_comparaison_notes(url + uri_pages + str(i+1))
        i = i + 1

        if not table.empty:
            table_finale = pd.concat([table_finale, table], ignore_index=True)
        else:
            valide = False

    print("nombre de films récupérés : ", len(table_finale))

    return table_finale




def get_base_films(annee1, annee2):
    """ 
    Récupérer les données de films entre l'annee1 et l'annee2

    """
    if not isinstance(annee1, int) or not isinstance(annee2, int):
        print("Les années doivent être des entiers")
    
    if annee2 > 2029 or annee1 < 2010:
        print(f"{annee1},{annee2} n'est pas valide (intervalle doit être compris entre 2010 et 2029)")
        return
    
    
    if annee1 <= annee2:

        table = pd.DataFrame()
        for i in range(annee1, annee2 + 1):

            table_intermediaire = get_comparaison_notes(i)
            
            table = pd.concat([table, table_intermediaire]) 
        
        # Suppression des doublons éventuels    
        table = table.drop_duplicates(subset='identifiant', keep='first')
        return table

        return table

    else:
        print('la première année doit être inférieure à la deuxième année')




def get_carac_film(base_film):
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main():
        async with aiohttp.ClientSession() as session:
            
            # On utilise identifiant pour créer des liens
            liens = ["https://www.allocine.fr/film/fichefilm_gen_cfilm=" + str(id) + ".html" for id in base_film['identifiant']]

            tasks = [fetch(session, url) for url in liens]
            responses = await asyncio.gather(*tasks)

            film_charac = []

            for i, response in enumerate(responses):

                soup = BeautifulSoup(response, 'html.parser')

                identifiant = re.findall(r'\d+', liens[i])[0]

                release_element = soup.find('span', class_='meta-release-type')
                release = release_element.text.strip() if release_element else ''

                # Extrait les données de la fiche technique
                fiche_tech = soup.find('section', class_='section ovw ovw-technical')
                if fiche_tech:
                    nationalite_span = fiche_tech.find('span', string='Nationalité')
                    nationalite = nationalite_span.find_next_sibling('span').text.strip() if nationalite_span else ''

                    date_sortie_dvd_span = fiche_tech.find('span', string='Date de sortie DVD')
                    date_sortie_dvd = date_sortie_dvd_span.find_next_sibling('span').text.strip() if date_sortie_dvd_span else ''

                    date_sortie_bluray_span = fiche_tech.find('span', string='Date de sortie Blu-ray')
                    date_sortie_bluray = date_sortie_bluray_span.find_next_sibling('span').text.strip() if date_sortie_bluray_span else ''

                    date_sortie_vod_span = fiche_tech.find('span', string='Date de sortie VOD')
                    date_sortie_vod = date_sortie_vod_span.find_next_sibling('span').text.strip() if date_sortie_vod_span else ''

                    type_film_span = fiche_tech.find('span', string='Type de film')
                    type_film = type_film_span.find_next_sibling('span').text.strip() if type_film_span else ''

                    budget_span = fiche_tech.find('span', string='Budget')
                    budget = budget_span.find_next_sibling('span').text.strip() if budget_span else ''

                    langues_span = fiche_tech.find('span', string='Langues')
                    langues = langues_span.find_next_sibling('span').text.strip() if langues_span else ''

                    format_production_span = fiche_tech.find('span', string='Format production')
                    format_production = format_production_span.find_next_sibling('span').text.strip() if format_production_span else ''

                    couleur_span = fiche_tech.find('span', string='Couleur')
                    couleur = couleur_span.find_next_sibling('span').text.strip() if couleur_span else ''

                    format_audio_span = fiche_tech.find('span', string='Format audio')
                    format_audio = format_audio_span.find_next_sibling('span').text.strip() if format_audio_span else ''

                    format_projection_span = fiche_tech.find('span', string='Format de projection')
                    format_projection = format_projection_span.find_next_sibling('span').text.strip() if format_projection_span else ''

                    num_visa_span = fiche_tech.find('span', string='N° de Visa')
                    num_visa = num_visa_span.find_next_sibling('span').text.strip() if num_visa_span else ''
                else:
                    nationalite = date_sortie_dvd = date_sortie_bluray = date_sortie_vod = type_film = budget = langues = format_production = couleur = format_audio = format_projection = num_visa = ''

                film_charac.append([identifiant, release, nationalite, date_sortie_dvd, date_sortie_bluray, date_sortie_vod, type_film, budget, langues, format_production, couleur, format_audio, format_projection, num_visa])

            # Créer un DataFrame pandas avec les numéros de films
            df_ws = pd.DataFrame(film_charac, columns=['identifiant', 'release', 'nationalite', 'date_sortie_dvd', 'date_sortie_bluray', 'date_sortie_vod', 'type_film', 'budget', 'langues', 'format_production', 'couleur', 'format_audio', 'format_projection', 'num_visa'])


            return pd.merge(base_film, df_ws, on='identifiant')

    return asyncio.run(main())





#############################################################
#############################################################
#############################################################
############################################################# Base prenom et récupération du genre
#############################################################
#############################################################
#############################################################


def base_prenom():
    """  

    Récupération sur data.gouv d'une BDD contenant 11 627 prénoms de plusieurs pays, et 
    pour lesquels leur genre (m/f/m,f/f,m est indiqué)   
    
    
    """

    # importation du csv avec 11 627 prénoms de différents pays
    url_prenom = "https://www.data.gouv.fr/fr/datasets/r/55cd803a-998d-4a5c-9741-4cd0ee0a7699"
        
    try:
        response = requests.get(url_prenom)

        # Vérification si la la requête a réussi
        response.raise_for_status()  #

        # Lire le fichier CSV à partir de la réponse
        table = pd.read_csv(io.StringIO(response.text), delimiter=';', encoding='utf-8')

    except Exception as e:
        print(f"Erreur inattendue : {e}")
    
    nom_colonnes = {
    '01_prenom': 'prenom',
    '02_genre': 'genre_ind',
    '03_langage': 'langage_ind'
    }

    table = table.rename(columns=nom_colonnes)

    return table
    


def get_genre_individuel(dataframe, colonne):
    """  
    
    Création d'une colonne 'prenom' à partir de la COLONNE d'un DATAFRAME. + ajout de l'argument de position (pour ajout base CNC des réalisateurs)
    
    """
    base_prenom_genre = base_prenom()
    base_prenom_genre = base_prenom_genre.drop(columns=['04_fréquence','langage_ind'])

    # transformation du prénom en minuscule afin de pouvoir merger sans problème de Majuscule
    dataframe['prenom'] = dataframe[colonne].str.split().str[0].str.lower()

    table = pd.merge(base_prenom_genre, dataframe, on='prenom', how='inner')
    table = table.drop(columns=['prenom'])
    
    return table



#############################################################
#############################################################
#############################################################
#############################################################  AUTRES RECUPERATOIN DE DONNEES ? 
#############################################################
#############################################################
#############################################################


