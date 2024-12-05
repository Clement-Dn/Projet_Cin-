

# Importations des librairies
from unidecode import unidecode
import pandas as pd
import numpy as np
import requests
import io



#############################################################     cleaning de certaines informations



def mise_en_forme_decimale(valeur):
    ''' 
    Transforme les , en .
    
    '''
    if isinstance(valeur, str):
        return float(valeur.replace(',', '.'))

    else: 
        valeur_convertie = str(valeur)
        return float(valeur_convertie.replace(',', '.'))





#############################################################  Création des variables : annee, duree (en minutes) et catégorisation des durées


def get_annee(dataframe, colonne):
    ''' 
    création d'une colonne 'année' à partir de la date au format '01 janvier 1800' de la COLONNE d'un DATAFRAME.

    '''
    dataframe[colonne] = dataframe[colonne].astype('string')
    dataframe['annee'] = dataframe[colonne].str[-4:]

    return dataframe





def duree_en_minutes(duree):
    ''' 
    Conversion d'une durée en minutes
    
    ENTREE :
    - duree : chaine de caractère de la forme '2h 34min'

    SORTIE : 
    - Retourne la conversion en minutes de 'duree'

    '''
    if not pd.isna(duree):
        parts = duree.split() 

        heures = 0
        minutes = 0

        for part in parts:
            if 'h' in part:
                heures = int(part.replace('h', ''))
            elif 'min' in part:
                minutes = int(part.replace('min', ''))

        return heures * 60 + minutes
    return





def categorisation_duree(dataframe, variable):
    ''' 

    '''
        
    bins = range(0, int(dataframe[variable].max()) + 10, 10)
    labels = [f'{i}-{i+9}' for i in bins[:-1]]
    dataframe['duree_cat'] = pd.cut(dataframe[variable], bins=bins, labels=labels, right=False)

    return dataframe



############################################################# Traduction en valeur numérique des notes (Très bien, Pas mal, etc)



def equivalence_notes(dataframe):
    '''
    Renvoie le dataframe en donnant les équivalences en note.
    '''
   

    equivalences = {
        'Chef-d\'oeuvre': 5,
        'Très bien': 4,
        'Pas mal': 3,
        'Pas terrible': 2,
        'Très mauvais':1,
    }

    notes = dataframe.replace(equivalences)
    
    return notes


    




############################################################# Base prenom et récupération du genre



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

    # Suppression des accents pour améliorer les matching de prénoms
    base_prenom_genre['prenom'] = base_prenom_genre['prenom'].astype(str)
    base_prenom_genre['prenom'] = base_prenom_genre['prenom'].apply(unidecode)
    base_prenom_genre = base_prenom_genre.drop_duplicates(subset='prenom')

    # transformation du prénom en minuscule afin de pouvoir merger sans problème de Majuscule + suppression des accents
    dataframe['prenom'] = dataframe[colonne].str.split().str[0].str.lower()
    dataframe['prenom'] = dataframe['prenom'].astype(str)
    dataframe['prenom'] = dataframe['prenom'].apply(unidecode)

    table = pd.merge(base_prenom_genre, dataframe, on='prenom', how='right')
    table = table.drop(columns=['prenom'])
    
    return table


##########################################################################################  Traitement base CNC





def categorisation_devis(dataframe):
    ''' 
    categorisation du devis, en reprenant les critères de l'article
    [0,2000000] = "<2 m "
    [2000000,4000000] = "entre 2 et 4 m"
    [4000000,7000000] = "entre 4 et 7 m"
    [7000000,16000000] = "> à 7 m"

    '''
    dataframe["type_de_devis"] = pd.cut(dataframe.devis, [0,2000000,4000000,7000000, 16000000], right=False)
    dataframe["type_de_devis"]= dataframe["type_de_devis"].cat.rename_categories(["<2 m ", "entre 2 et 4 m", "entre 4 et 7 m", "> à 7 m"])
    
    return dataframe




def get_genre_prenom(prenom):
    """
    Retourne le genre associé au prénom donné

    """
    # Import de la base prénom
    base_prenom_genre = base_prenom()
    base_prenom_genre = base_prenom_genre.drop(columns=['04_fréquence', 'langage_ind'])
    base_prenom_genre['prenom'] = base_prenom_genre['prenom'].astype(str)
    base_prenom_genre['prenom'] = base_prenom_genre['prenom'].apply(unidecode)
    
    # Transformer le prénom en minuscule afin de pas avoir de pb de casse avec les majuscules
    prenom_formate = prenom.lower()
    prenom_formate = unidecode(prenom_formate)

    # Recherche du prénom dans la base
    genre = base_prenom_genre[base_prenom_genre['prenom'].str.lower() == prenom_formate]

    if not genre.empty:
        return genre['genre_ind'].values[0]
    else:
        return 'non trouvé'


def genres_multiple(liste):
    """
    A partir d'une liste de prénom + nom, retourne :
    - si une seule persone => si femme f, si homme h
    - si plusieurs personnes => mutiple + si il y a au moins une femme (f_coréalisé vs m_coréalisé)

    """
    if liste != None:
        prenoms = [individu.split()[-1] for individu in liste]

        if len(prenoms) > 1:
            for prenom in prenoms:
                if get_genre_prenom(prenom) == 'f':
                    return 'f_coréalisé'
                    return prenom
            return 'm_coréalisé'

        return get_genre_prenom(prenoms[0])
        
    return 'pas de realisateur'


def ajout_genre_multiple(dataframe, colonne):

    # # transformation de chaque élément de la colonne en liste pour faciliter la recherche de(s) genre(s)
    dataframe[colonne] = dataframe[colonne].str.split('/')

    # Parallélisation des CPU car sinon cela prend plusieurs minutes de parcourir les milliers de lignes
    dataframe['genre_ind'] = Parallel(n_jobs=-1)(delayed(genres_multiple)(realisateur) for realisateur in dataframe[colonne])

    return dataframe