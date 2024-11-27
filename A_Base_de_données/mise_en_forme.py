


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