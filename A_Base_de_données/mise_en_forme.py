


# Importations des librairies
import pandas as pd
import numpy as np







def mise_en_forme_decimale(valeur):
    ''' 
    Transforme les , en .
    
    '''
    if isinstance(valeur, str):
        return float(valeur.replace(',', '.'))

    else: 
        valeur_convertie = str(valeur)
        return float(valeur_convertie.replace(',', '.'))





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