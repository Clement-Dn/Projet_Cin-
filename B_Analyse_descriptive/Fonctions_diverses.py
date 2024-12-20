

# Importation des librairies
import pandas as pd
from IPython.display import display, HTML
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm



###########################################################

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
    
    return moyenne



def boxplot_duree(dataframe, variable):
    '''
    Crée un boxplot de la distribution des notes des spectateurs par catégorie de durée.

    '''
    # On ne prend pas en compte les modalités présentes qu'une seule fois
    value_counts = dataframe[variable].value_counts()
    modalites_a_garder = value_counts[value_counts > 1].index
    dataframe_filtre = dataframe[dataframe[variable].isin(modalites_a_garder)]


    # boxplot
    plt.figure(figsize=(12, 8))
    sns.boxplot(x=variable, y='spectators_rating', data=dataframe_filtre)
    plt.title('Distribution des notes des spectateurs par catégorie de durée')
    plt.xlabel('Durée en minutes')
    plt.ylabel('Note des spectateurs')
    plt.xticks(rotation=45)
    plt.show()

    return



