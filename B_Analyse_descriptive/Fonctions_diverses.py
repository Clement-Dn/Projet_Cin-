

# Importation des librairies
import pandas as pd
from IPython.display import display, HTML
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm



###########################################################         Notes presse et spectateurs par genre de film

def classement_genres_preferes(dataframe, individus):
    ''' 
    Retourne le classsement des genres de films préférés par les INDIVIDUS (avec le nombre de films pris en compte)

    '''

    notes_moyennes = dataframe.rename(columns={'genre1': 'genre'})
    notes_moyennes = notes_moyennes.groupby('genre').agg(
        Note_Moyenne=(individus, 'mean'),
        Nombre_de_Films=(individus, 'size'))

    # On ne considère que les genres de films présents au moins 50 fois
    notes_moyennes = notes_moyennes[notes_moyennes['Nombre_de_Films'] >= 50]
    notes_moyennes['Note_Moyenne'] = notes_moyennes['Note_Moyenne'].round(2)

    return notes_moyennes.sort_values(by='Note_Moyenne', ascending=False)




def comparaison_preferences(dataframe):
    ''' 
    Met côte à côte le classement des genres préférés pour les spectateurs et pour la presse
    '''
    preferences_spect = classement_genres_preferes(dataframe, 'spectators_rating')
    preferences_presse = classement_genres_preferes(dataframe, 'press_rating')
    
    # Affichage côte à côte
    html_content = f"""
    <div style="display:flex;">
        <div style="flex:1; margin-right:20px;">
            {preferences_spect.to_html()}
        </div>
        <div style="flex:1;">
            {preferences_presse.to_html()}
        </div>
    </div>
    """
    display(HTML(html_content))




def p_value_anova_h_vs_f(dataframe):
    '''
        Retourne la p-value du test d'ANOVA pour les notations par rapport au genre des réalisateurs
    '''

    dataframe = dataframe[dataframe['genre_ind'].isin(['f', 'm'])]
    model = ols('spectators_rating ~ C(genre_ind)', data=dataframe).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    return(f'P-value du test ANOVA: {anova_table.iloc[0]['PR(>F)']:.3f}')




def get_moyenne_par_modalite(dataframe, variable):

    """
    Retourne la moyenne des notes des spectateurs et de la presse par modalité de la VARIABLE en entrée
    """
    moyenne = dataframe.groupby(variable).agg(
    presse=('press_rating', "mean"),
    spectateur=('spectators_rating', "mean"))

    moyenne['presse'] = moyenne['presse'].round(2)
    moyenne['spectateur'] = moyenne['spectateur'].round(2)
    
    return moyenne




#################################################### Traitement et boxplot pour la durée de films


def categorisation_duree(dataframe, variable):
    ''' 
    Création d'une nouvelle variable catégorielle avec des intervalles de 9 mintues
    '''
        
    bins = range(0, int(dataframe[variable].max()) + 10, 10)
    labels = [f'{i}-{i+9}' for i in bins[:-1]]
    dataframe['duree_cat'] = pd.cut(dataframe[variable], bins=bins, labels=labels, right=False)

    return dataframe





def boxplot_duree(dataframe, variable):
    '''
    Crée un boxplot de la distribution des notes des spectateurs par catégorie de durée.

    '''
    # suppression des films ayant des valeurs de durées aberrantes (ce qui représente 27 films sur les 10837)
    dataframe = dataframe[dataframe['duration_min']<360]
    dataframe = categorisation_duree(dataframe, 'duration_min')


    # boxplot
    plt.figure(figsize=(12, 8))
    sns.boxplot(x=variable, y='spectators_rating', data=dataframe)
    plt.title('Distribution des notes des spectateurs par catégorie de durée')
    plt.xlabel('Durée en minutes')
    plt.ylabel('Note des spectateurs')
    plt.xticks(rotation=45)

    return


####################################################      




def diagramme_baton_genre_proportion(dataframe, variable) : 
    '''

    '''
    dataframe= dataframe[dataframe['genre_ind'].isin(['f', 'm', "f_coréalisé", "m_coréalisé" ])]

    # Calcul des comptages pour chaque combinaison de variable et genre_ind
    count_data = dataframe.groupby([variable, 'genre_ind']).size().reset_index(name='count')

    # Calcul du total par genre_ind (homme ou femme)
    total_genre = dataframe.groupby('genre_ind').size().reset_index(name='total')

    # Fusionner les données pour ajouter le total à chaque ligne
    count_data = pd.merge(count_data, total_genre, on='genre_ind')

    # Calcul des pourcentages
    count_data['percentage'] = (count_data['count'] / count_data['total']) 
    
 

    # Barplot 
    sns.barplot(data=count_data, x=variable, y='percentage', hue='genre_ind')

    plt.title('Proportions des films selon le sexe du réalisateur')
    plt.xlabel(variable)
    plt.ylabel('Proportion de films')
    plt.legend(title='Genre')
    plt.show()

