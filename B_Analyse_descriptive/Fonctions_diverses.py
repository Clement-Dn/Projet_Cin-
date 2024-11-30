

# Importation des librairies
import pandas as pd
from IPython.display import display, HTML
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm




###########################################################

def classement_genres_preferes(dataframe, individu):
    ''' 

    '''

    notes_moyennes = dataframe.rename(columns={'genre1': 'genre'})
    notes_moyennes = notes_moyennes.groupby('genre').agg(
        Note_Moyenne=(individu, 'mean'),
        Nombre_de_Films=(individu, 'size'))

    # On ne considère que les genres de films présents au moins 20 fois
    notes_moyennes = notes_moyennes[notes_moyennes['Nombre_de_Films'] >= 20]

    return notes_moyennes.sort_values(by='Note_Moyenne', ascending=False)




def comparaison_preferences(dataframe):
    ''' 

    '''
    preferences_spect = classement_genres_preferes(dataframe, 'spectateur')
    preferences_presse = classement_genres_preferes(dataframe, 'presse')
    
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
        retourne la p-value du test d'ANOVA pour les notations par rapport au genre des réalisateurs
    '''

    dataframe = dataframe[dataframe['genre_ind'].isin(['f', 'm'])]
    model = ols('spectateur ~ C(genre_ind)', data=dataframe).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    return(f'P-value du test ANOVA: {anova_table.iloc[0]['PR(>F)']:.3f}')





def boxplot_duree(dataframe, variable):
    '''

    '''
    plt.figure(figsize=(12, 8))
    sns.boxplot(x=variable, y='spectateur', data=dataframe)
    plt.title('Distribution des notes des spectateurs par catégorie de durée')
    plt.xlabel('Durée en minutes')
    plt.ylabel('Note des spectateurs')
    plt.xticks(rotation=45) 
    plt.show()