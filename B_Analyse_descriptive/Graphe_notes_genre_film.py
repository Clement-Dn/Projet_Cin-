

import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
import seaborn as sns




#############################################################  Histogramme de la distribution des notes des spectateurs par type de film


def histogramme_genre_film(dataframe, genre1, genre2):
    """
    Génération d'un histogramme des notes des spectateurs par GENRE1 et GENRE2 de films

    """
    dataframe = dataframe.rename(columns={'genre1': 'genre'})

    if genre1 != 'Tous':

        if genre2 != ' ':
            dataframe = dataframe[dataframe['genre'].isin([genre1, genre2])]
            if genre1 != ' ':
                titre = f'Notes moyennes des spectateurs pour les films {genre1} et {genre2}'
            else:
                titre = f'Notes moyennes des spectateurs pour les films {genre2}'

        else:
            dataframe = dataframe.loc[dataframe['genre'] == genre1]
            titre = f'Notes moyenne des spectateurs pour les films {genre1}'

          
    else:
        if genre2 != ' ':
            print('Merci de choisir un Genre 1 pour comparer avec le Genre 2')
            
        titre = 'Notes moyennes des spectateurs par type de film'


    if genre1 != ' ' or genre2 != ' ':
        plt.figure(figsize=(8, 6))

        sns.histplot(data=dataframe, x='spectators_rating', hue='genre', bins=10, kde=True)
        plt.title(titre)
        plt.xlabel('Notes des spectateurs')
        plt.ylabel('Occurences')
        plt.xlim(0, 5)


        # Ajout du nombre de films pris en compte ainsi que la note moyenne des spectateurs
        if genre1 != 'Tous' and genre2 != ' ' and genre1 != genre2:
            
            nb_films_1 = len(dataframe.loc[dataframe['genre'] == genre1])
            moyenne_1 = dataframe.loc[dataframe['genre'] == genre1]['spectators_rating'].mean()

            nb_films_2 = len(dataframe.loc[dataframe['genre'] == genre2])
            moyenne_2 = dataframe.loc[dataframe['genre'] == genre2]['spectators_rating'].mean()
            
            if genre1 != ' ':
                plt.text(0.95, 0.75, f'Nombre de films {genre1} : {nb_films_1}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

                plt.figtext(0.95, 0.70, f'Note moyenne: {moyenne_1:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))

            plt.text(0.95, 0.60, f'Nombre de films {genre2} : {nb_films_2}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

            plt.figtext(0.95, 0.55, f'Note moyenne: {moyenne_2:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))


        else:
            nb_films = len(dataframe)
            moyenne = dataframe['spectators_rating'].mean()
            plt.text(0.95, 0.75, f'Nombre de films : {nb_films}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

            plt.figtext(0.95, 0.70, f'Note moyenne: {moyenne:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))




        # test ANOVA (singificativité de différence dans les moyennes de chaque type de films)
        if genre2 != ' ' or genre1 == 'Tous':
            if genre1 != ' 'and genre1 != genre2:
                model = ols('spectators_rating ~ C(genre)', data=dataframe).fit()
                anova_table = sm.stats.anova_lm(model, typ=2)
                # Affchage de la p-value
                plt.figtext(0.95, 0.40, f'P-value ANOVA: {anova_table.iloc[0]['PR(>F)']:.2f}', ha='left', va='top', bbox=dict(facecolor='white', alpha=0.5))
        





def graphique_genre_film(dataframe):
    """
    Créer une interface avec deux menus déroulants pour sélectionner les genres de films 
    dont on veut comparer la distribution des notes (visualisation histogramme)

    """

    modalites_presentes = dataframe['genre1'].value_counts()

    # On ne représente que les modalités qui sont présentes en un nombre suffisant de fois (nombre fixé à 50)
    modalites_suffisantes = list(modalites_presentes[modalites_presentes >= 50].index) 
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



