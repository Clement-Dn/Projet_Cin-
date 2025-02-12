
# Importations des librairies
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import pandas as pd



#############################################################  Courbes pour l'évolution dans le tps nb de films h vs f

def evolution_f_h_cnc(dataframe, genre):
    """ 
    
    Affichage de l'évolution dans le temps du nombre de films en fonction du genre du rélisateurs pour un GENRE de film demandé (si non renseigné tous les genres sont pris en compte)
    
    """

    # Création de toutes les combinaisons (année,genre_ind) afin de pouvoir injecter par la suite les combinaisons manquantes     
    # Index de toutes les années et modalités
    all_years = dataframe['date'].unique()
    all_genres = dataframe['genre_ind'].unique()

    combinaisons = pd.MultiIndex.from_product([all_years, all_genres], names=['date', 'genre_ind'])
    combinaisons = pd.DataFrame(index=combinaisons).reset_index()
    combinaisons['initialisation'] = 0



    # Sélection du genre de film a prendre en compte
    if genre != 'Tous':
        dataframe = dataframe.loc[dataframe['genre'] == genre]
        titre = f'Nb de films par genre du/des réalisateur/s pour les films {genre}'
    else:
        titre = 'Nb de films par genre du/des réalisateur/s' 


    groupby = dataframe.groupby(['date', 'genre_ind']).size().reset_index(name='count')
    groupby_merged = combinaisons.merge(groupby, on=['date', 'genre_ind'], how='left').fillna(0)

    # Pivoter afin d'avoir les années en index et les modalités en colonnes
    transposee = groupby_merged.pivot(index='date', columns='genre_ind', values='count').fillna(0)

  
    # Courbes
    plt.figure(figsize=(10, 6))
    plt.plot(transposee.index, transposee['f'], label='F', marker='o')
    plt.plot(transposee.index, transposee['m'], label='M', marker='o')
    plt.plot(transposee.index, transposee['m_coréalisé'], label='M_coréalisé', marker='o')
    plt.plot(transposee.index, transposee['f_coréalisé'], label='F_coréalisé', marker='o')
    plt.title(titre)
    plt.xlabel('Année')
    plt.ylabel('Nombre de films')
    plt.legend(title='Genre du/des réalisateur/s')




def graphique_h_f_cnc(dataframe):
    """ 
    
    Graphique interactif du nombre de films par réalisateur f, m, ou bien avec plusieurs réalisateurs en fonction du type de film
    
    """
    # Annees considérées
    annee_conservees = list(range(2010, 2023))
    annees_string = [str(annee) for annee in annee_conservees]
    dataframe = dataframe[dataframe['date'].isin(annees_string)]


    # On ne conserve que les genres de films qui sont assez nombreux (fixé à > 20)
    modalites_presentes = dataframe['genre'].value_counts()
    modalites_suffisantes = list(modalites_presentes.index)
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
            evolution_f_h_cnc(dataframe, change['new'])


    # Associer le bouton à la fonction de mise à jour
    menu_deroulant.observe(update_genre_film)

    display(menu_deroulant)
    evolution_f_h_cnc(dataframe, menu_deroulant.value)

