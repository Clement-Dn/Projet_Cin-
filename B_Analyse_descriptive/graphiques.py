

import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd



#############################################################
#############################################################
#############################################################
#############################################################  Histogramme de la distribution des notes des spectateurs par type de film
#############################################################
#############################################################
#############################################################


def histogramme_genre_film(dataframe, genre1, genre2):
    """
    Génération d'un histogramme des notes des spectateurs par GENRE1 et GENRE2 de films

    """
    dataframe = dataframe.rename(columns={'genre1': 'genre'})

    if genre1 != 'Tous':

        if genre2 != ' ':
            dataframe = dataframe[dataframe['genre'].isin([genre1, genre2])]
            titre = f'Notes moyennes des spectateurs pour les films {genre1} et {genre2}'

        else:
            dataframe = dataframe.loc[dataframe['genre'] == genre1]
            titre = f'Notes moyenne des spectateurs pour les films {genre1}'
            
    else:
        titre = 'Notes moyennes des spectateurs par type de film'


    plt.figure(figsize=(8, 6))

    sns.histplot(data=dataframe, x='spectateur', hue='genre', bins=10, kde=True)
    plt.title(titre)
    plt.xlabel('Notes des spectateurs')
    plt.ylabel('Occurences')
    plt.xlim(0, 5)



    if genre1 != 'Tous' and genre2 != ' ' and genre1 != genre2:
        nb_films_1 = len(dataframe.loc[dataframe['genre'] == genre1])
        moyenne_1 = dataframe.loc[dataframe['genre'] == genre1]['spectateur'].mean()

        nb_films_2 = len(dataframe.loc[dataframe['genre'] == genre2])
        moyenne_2 = dataframe.loc[dataframe['genre'] == genre2]['spectateur'].mean()
        

        plt.text(0.95, 0.75, f'Nombre de films {genre1} : {nb_films_1}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        plt.figtext(0.95, 0.70, f'Note moyenne: {moyenne_1:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))

        plt.text(0.95, 0.60, f'Nombre de films {genre2} : {nb_films_2}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        plt.figtext(0.95, 0.55, f'Note moyenne: {moyenne_2:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))


    else:
        nb_films = len(dataframe)
        moyenne = dataframe['spectateur'].mean()
        plt.text(0.95, 0.75, f'Nombre de films : {nb_films}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        plt.figtext(0.95, 0.70, f'Note moyenne: {moyenne:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))





def graphique_genre_film(dataframe):
    """
    Créer une interface avec deux menus déroulants pour sélectionner les genres de films 
    dont on veut comparer la distribution des notes (visualisation histogramme)

    """

    modalites_presentes = dataframe['genre1'].value_counts()
    modalites_suffisantes = list(modalites_presentes[modalites_presentes >= 5].index) ########################## QUEL NOMBRE METTRE ?????????????????????????
    modalites_suffisantes.append('Tous')
    modalites_suffisantes.append(' ')


    # Boutons de sélection

    # Genre 1
    menu_deroulant_1 = widgets.Dropdown(
        options=modalites_suffisantes,
        value='Tous',  # valeur initiale
        description='Genre 1 :',
    )

    # Genre 2
    menu_deroulant_2 = widgets.Dropdown(
        options=[genre for genre in modalites_suffisantes if genre != 'Tous'],
        value=' ',   # valeur initiale
        description='Genre 2 :',
    )



    # Fonctions de mise à jour
    def update_genre_1(change):

        if change['type'] == 'change' and change['name'] == 'value':
            print(f"Genre 1 changé en : {change['new']}")  
            clear_output(wait=True) # suppression de l'ancien graphique pour pouvoir le remplacer

            display(menu_deroulant_1)
            display(menu_deroulant_2)

            histogramme_genre_film(dataframe, change['new'], menu_deroulant_2.value)

    def update_genre_2(change):

        if change['type'] == 'change' and change['name'] == 'value':
            print(f"Genre 2 changé en : {change['new']}")  # Débogage
            clear_output(wait=True)

            display(menu_deroulant_1)
            display(menu_deroulant_2)
            
            histogramme_genre_film(dataframe, menu_deroulant_1.value, change['new'])



    # Association des menus déroulants à leur fonction de mise à jour
    menu_deroulant_1.observe(update_genre_1, names='value')
    menu_deroulant_2.observe(update_genre_2, names='value')



    # Affichage des menus déroulants et le graphe initial
    display(menu_deroulant_1)
    display(menu_deroulant_2)
    histogramme_genre_film(dataframe, menu_deroulant_1.value, menu_deroulant_2.value)









#############################################################
#############################################################
#############################################################
#############################################################  Courbes pour l'évolution dans le tps nombre de films h vs f
#############################################################
#############################################################
#############################################################



def evolution_f_h(dataframe, genre):
    """ 
    
    Affichage de l'évolution dans le temps du nombre de films en fonction du genre du rélisateurs pour un GENRE de film demandé (si non renseigné tous les genres sont pris en compte)
    
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
    
    Graphique intéractif du nombre de films par réalisateur f et h en fonction du type de film
    
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
