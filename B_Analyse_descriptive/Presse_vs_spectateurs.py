

import numpy as np
import seaborn as sns 
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import ipywidgets as widgets
import matplotlib.pyplot as plt




#############################################################  Comparaisons des notes des spectateurs et notes de la presse





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






def plot_spec_vs_presse(dataframe, genre):
    """ 
    
    
    """

    if genre != 'Tous':
        dataframe = dataframe[dataframe['genre1']== genre]
        titre = f'Répartition des notes de presse et spectateurs pour les films {genre}'
            
    else:
        titre = 'Répartition des notes de presse et spectateurs sur tous les films'

    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=dataframe, x='spectateur', y='presse', alpha=0.7, linewidth=0.5, legend = False)

    # Ajout de la regression
    degre_optimal = get_degre_optimal(dataframe[['spectateur']], dataframe[['presse']])
    sns.regplot(data=dataframe, x='spectateur', y='presse', scatter=False, color='green', order=degre_optimal)

    plt.plot([0, 5], [0, 5], 'k--', label='x = y') 
    plt.xlim(0, 5)
    plt.ylim(0, 5)





def graphique_presse_vs_spect(dataframe):
    """


    """

    modalites_presentes = dataframe['genre1'].value_counts()

    # On ne représente que les modalités qui sont présentes en un nombre suffisant de fois (nombre fixé à 20 films)
    modalites_suffisantes = list(modalites_presentes[modalites_presentes >= 20].index) 
    modalites_suffisantes.append('Tous')


    # Boutons de sélection

    # Genre 1
    menu_deroulant = widgets.Dropdown(
        options=modalites_suffisantes,
        value='Tous',  # valeur initiale
        description='Genre :',
    )


    # Fonctions de mise à jour
    def update_genre(change):
        if change['type'] == 'change' and change['name'] == 'value':
            clear_output(wait=True) # suppression de l'ancien graphique pour pouvoir le remplacer

            display(menu_deroulant)

            plot_spec_vs_presse(dataframe, change['new'])

    

    # Association des menus déroulants à leur fonction de mise à jour
    menu_deroulant.observe(update_genre, names='value')


    # Affichage des menus déroulants et le graphe initial
    display(menu_deroulant)
    plot_spec_vs_presse(dataframe, menu_deroulant.value)
