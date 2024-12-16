


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt







def get_table_cluster(dataframe, data_presse):

    # récupération des moyennes par genre du réalisateur
    table_genre = pd.merge(dataframe[['identifiant', 'genre_ind']], data_presse, on = 'identifiant', how='left')
    table_genre = table_genre.drop(columns=table_genre.columns[0])

    note_columns = table_genre.columns
    note_columns = note_columns.drop('genre_ind')

    for col in note_columns:
        table_genre[col] = pd.to_numeric(table_genre[col], errors='coerce')

    table_genre = table_genre.groupby('genre_ind').mean().reset_index()
    table_genre = table_genre.set_index('genre_ind')



    # récupération des moyennes par type/genre de film
    table_type = pd.merge(dataframe[['identifiant','genre1']], data_presse, on = 'identifiant', how='left')
    table_type = table_type.drop(columns=table_type.columns[0])

    note_columns = table_type.columns
    note_columns = note_columns.drop('genre1')

    for col in note_columns:
        table_type[col] = pd.to_numeric(table_type[col], errors='coerce')

        
    table_type = table_type.groupby('genre1').mean().reset_index()
    table_type = table_type.set_index('genre1')


    # colonnes communes A GERER QUAND IL Y AURA LA BASE
    df_cleaned_columns = table_type.loc[:, table_type.isnull().sum() <= 12]  
    df_cleaned_rows = df_cleaned_columns.loc[df_cleaned_columns.isnull().sum(axis=1) <= 0]

    common_columns = df_cleaned_rows.columns.intersection(table_genre.columns)
    result_combined = pd.concat([table_genre[common_columns], df_cleaned_rows[common_columns]])
    df_cleaned = result_combined.drop(index=['m,f', 'f,m'])
    df_transposed = df_cleaned.T


    return df_transposed






def optimal_clusters(dataframe, max_clusters):
    """
    Methode du coude pour déterminer le nombre de clusters optimal
    """

    inertie = []
    k_range = range(1, max_clusters + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(dataframe)
        inertie.append(kmeans.inertia_)

    # Plot de la méthode du coude
    plt.figure(figsize=(8, 4))
    plt.plot(k_range, inertie, 'bo-')
    plt.xlabel('Nombre de clusters')
    plt.ylabel('Inertie')
    plt.title('Intertie en fonction du nombre de clusters (Méthode du coude pour déterminer le nombre optimal de clusters)')
    plt.show()

    return inertie



def normalisation(dataframe):
    """

    """
    scaler = StandardScaler()  
    return scaler.fit_transform(dataframe)



def determine_optimal_clusters(dataframe, max_clusters):
    """
    Détermine le nombre optimal de clusters en utilisant la méthode du coude.

    """
    # Normalisation
    dataframe = normalisation(dataframe)

    # Vecteur contenant les inerties
    inertie = optimal_clusters(dataframe, max_clusters)

    # Calcul des dérivées
    derivees = np.diff(inertie)

    # Recherche du coude
    second_differences = np.diff(derivees)
    nb_optimal = np.argmax(second_differences) + 2  

    print(f"Le nombre optimal de clusters est : {nb_optimal}")
    
    return nb_optimal




def clustering_K_means(dataframe, nb_clusters):
    """ 

    """

    # Normalisation
    dataframe_normalise = normalisation(dataframe)

    # Clustering
    kmeans = KMeans(n_clusters=nb_clusters, random_state=0)
    dataframe['Cluster'] = kmeans.fit_predict(dataframe_normalise)

    return dataframe.groupby('Cluster').groups