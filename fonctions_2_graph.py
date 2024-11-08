

import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import seaborn as sns



#############################################################
#############################################################
#############################################################
#############################################################  Histogramme de la distribution des notes des spectateurs par type de film
#############################################################
#############################################################
#############################################################



def histogramme_genre_film(dataframe, genre):
    """ 
    
    
    """
    
    
    if genre != 'Tous':
        dataframe = dataframe.loc[dataframe['genre1'] == genre]
        titre = f'Notes Spectateur pour les films {genre}'
    else:
        titre = 'Notes Spectateur par type de film' 

    plt.figure(figsize=(8, 6))
    
    sns.histplot(data=dataframe, x='spectateur', hue='genre1', bins=10, kde=True)
    plt.title(titre)
    plt.xlabel('Notes des spectateurs')
    plt.ylabel('Occurences')
    plt.xlim(0, 5) 



def graphique_genre_film(dataframe):
    """ 
    
    
    
    """

    modalites_presentes = dataframe['genre1'].value_counts()
    modalites_suffisantes = list(modalites_presentes[modalites_presentes >= 5].index)
    modalites_suffisantes.append('Tous')

    # Bouton de sélection 
    menu_deroulant = widgets.Dropdown(
        options=modalites_suffisantes,
        value='Tous',  # valeur initiale
        description='Genre :',
    )

    # Fonction de mise à jour
    def update_genre_film(change):
        if change['type'] == 'change' and change['name'] == 'value':

            clear_output(wait=True) # supprimer l'ancien graphe si un nouveau est demandé

            display(menu_deroulant)
            histogramme_genre_film(dataframe, change['new'])


    # Associer le bouton à la fonction de mise à jour
    menu_deroulant.observe(update_genre_film)


    
    display(menu_deroulant)
    histogramme_genre_film(dataframe, menu_deroulant.value)








#############################################################
#############################################################
#############################################################
#############################################################  Courbes pour l'évolution dans le tps nombre de films h vs f
#############################################################
#############################################################
#############################################################



def evolution_f_h(dataframe, genre):
    """ 
    
    
    """

    # Création de toutes les combinaisons (année,genre_ind) afin de pouvoir injecter par la suite les combinaisons manquantes     
    # Index de toutes les années et modalités
    all_years = dataframe['annee'].unique()
    all_genres = dataframe['genre_ind'].unique()

    combinaisons = pd.MultiIndex.from_product([all_years, all_genres], names=['annee', 'genre_ind'])
    combinaisons = pd.DataFrame(index=combinaisons).reset_index()
    combinaisons['initialisation'] = 0



    # Sélection du genre de film a prendre en compte
    if genre != 'Tous':
        dataframe = dataframe.loc[dataframe['genre1'] == genre]
        titre = f'Nb de films h vs f pour les films {genre}'
    else:
        titre = 'Nb de films h vs f' 


    groupby = dataframe.groupby(['annee', 'genre_ind']).size().reset_index(name='count')
    groupby_merged = combinaisons.merge(groupby, on=['annee', 'genre_ind'], how='left').fillna(0)

    # Pivoter afin d'avoir les années en index et les modalités en colonnes
    transposee = groupby_merged.pivot(index='annee', columns='genre_ind', values='count').fillna(0)

  
    # Courbes
    plt.figure(figsize=(10, 6))
    plt.plot(transposee.index, transposee['f'], label='F', marker='o')
    plt.plot(transposee.index, transposee['m'], label='M', marker='o')
    plt.title(titre)
    plt.xlabel('Année')
    plt.ylabel('Nombre de films')
    plt.legend(title='Genre du réalisateur')



def graphique_h_f(dataframe):
    """ 
    
    
    
    """

    modalites_presentes = dataframe['genre1'].value_counts()
    modalites_suffisantes = list(modalites_presentes[modalites_presentes >= 5].index)
    modalites_suffisantes.append('Tous')


    # Bouton de sélection 
    menu_deroulant = widgets.Dropdown(
        options=modalites_suffisantes,
        value='Tous',  # valeur initiale
        description='Genre du film :',
    )

    # Fonction de mise à jour
    def update_genre_film(change):
        if change['type'] == 'change' and change['name'] == 'value':

            clear_output(wait=True) # supprimer l'ancien graphe si un nouveau est demandé

            display(menu_deroulant)
            evolution_f_h(dataframe, change['new'])


    # Associer le bouton à la fonction de mise à jour
    menu_deroulant.observe(update_genre_film)

    display(menu_deroulant)
    evolution_f_h(dataframe, menu_deroulant.value)
