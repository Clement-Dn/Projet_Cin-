
# Importations des librairies
import pandas as pd
import numpy as np






# Conversion durée en minutes
def duree_en_minutes(duree):
    ''' 
    Conversion en minutes
    
    ENTREE :
    - duree : chaine de caractère de la forme '2h 34min'

    SORTIE : 
    - Retourne la conversion en minutes de 'duree'

    '''
    parts = duree.split()

    heures = 0
    minutes = 0

    for part in parts:
        if 'h' in part:
            heures = int(part.replace('h', ''))
        elif 'min' in part:
            minutes = int(part.replace('min', ''))

    return heures * 60 + minutes



def mise_en_forme_decimale(valeur):
    ''' 
    Transforme les , en .
    '''

    return float(valeur.replace(',', '.'))


