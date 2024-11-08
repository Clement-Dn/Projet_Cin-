


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


# Manipulation des données
import pandas as pd
import numpy as np




#############################################################
#############################################################
#############################################################
############################################################# ????? PAS BESOIN DE CETTE PARTIE SI PAS NLP sur commentaires.....
#############################################################
#############################################################
#############################################################


def get_donnees(url, elements_a_scrapper, cols):   # Quand temps => mettre au propre cette fonction ! (si on l'utilise...sinon sup....)
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
    - Dataframe avec les notes moyennes des spectateurs et de la presse (si présente)

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
    
    
    if annee1 <= annee2:

        table = pd.DataFrame()
        for i in range(annee1, annee2 + 1):

            table_intermediaire = get_comparaison_notes(i)

            # # Si il y a une erreur (lien mauvais, une seule année non récupérable, etc), la boucle s'arrête et la fonction 
            # # s'arrête, de plus un message indiquant le problème s'affiche
            # if not table_intermediaire:
            #     return
            
            table = pd.concat([table, table_intermediaire]) 

        return table





#############################################################
#############################################################
#############################################################
############################################################# Base prenom et récupération du genre
#############################################################
#############################################################
#############################################################


def base_prenom():
    """  
    
    
    
    
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
    
    
    
    """
    base_prenom_genre = base_prenom()
    base_prenom_genre = base_prenom_genre.drop(columns=['04_fréquence'])

    # transformation du prénom en minuscule afin de pouvoir merger sans problème de Majuscule
    dataframe['prenom'] = dataframe[colonne].str.split().str[0].str.lower()


    return pd.merge(base_prenom_genre, dataframe, on='prenom', how='inner')



#############################################################
#############################################################
#############################################################
#############################################################  AUTRES RECUPERATOIN DE DONNEES ? 
#############################################################
#############################################################
#############################################################


