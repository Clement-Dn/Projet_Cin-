

import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression




#############################################################
#############################################################
#############################################################
#############################################################  Comparaisons des notes des spectateurs et notes de la presse
#############################################################
#############################################################
#############################################################




def get_degre_optimal(X, Y, degre_max=6, cv=5):
    """
    Retourne le degré optimal du polynôme de la régression (teste de 1 à 5 degrés par défaut)
    par cross validation (par défaut à 5)

    X : variable en asbcisse
    Y : variable en ordonnée
    degre_max : degré maximal testé des polynômes
    cv : nb de folds poru la validation croisée 

    """
    # Stockage des MSE
    liste_mse = []  
    
    # Boucle sur chaque degré testé
    for degree in range(1, degre_max + 1):

        poly = PolynomialFeatures(degree)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        
        # Validation croisée pour estimer la MSE
        mse = -cross_val_score(model, X_poly, Y, cv=cv, scoring='neg_mean_squared_error').mean()

        liste_mse.append(mse)
    
    # récupération du degré associé à la plus faible MSE
    degre_opt = np.argmin(liste_mse) + 1  

    return degre_opt
