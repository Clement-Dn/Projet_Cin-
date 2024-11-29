


###########################################################


def classement_genres_preferes(dataframe):
    ''' 

    '''

    notes_moyennes = dataframe.rename(columns={'genre1': 'genre'})
    notes_moyennes = notes_moyennes.groupby('genre').agg(
        Note_Moyenne=('spectateur', 'mean'),
        Nombre_de_Films=('spectateur', 'size'))

    # On ne considère que les genres de films présents au moins 20 fois
    notes_moyennes = notes_moyennes[notes_moyennes['Nombre_de_Films'] >= 20]

    return notes_moyennes.sort_values(by='Note_Moyenne', ascending=False)