


# Importation des librairies
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler 
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt






def get_table_cluster(dataframe, data_presse):
    """
    Retourne une table avec les moyennes pour chaque presse les notes attibuées en fonction du genre du film
    """

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


    # colonnes communes  afin de gérer les presse qui n'évaluent pas les films de tous les genres
    df_cleaned_columns = table_type.loc[:, table_type.isnull().sum() <= 15]  
    df_cleaned_rows = df_cleaned_columns.loc[df_cleaned_columns.isnull().sum(axis=1) <= 0]

    common_columns = df_cleaned_rows.columns.intersection(table_genre.columns)
    result_combined = pd.concat([table_genre[common_columns], df_cleaned_rows[common_columns]])
    df_transposed = result_combined.T


    return df_transposed






def optimal_clusters(dataframe, max_clusters):
    """
    Calcul de l'inertie en fonction du nombre de clusters et affiche du graphique associé 
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

    print(f"Graphiquement le nombre optimal de clusters est : {nb_optimal}")
    
    return nb_optimal




def normalisation(dataframe):
    """
    Normalisation de toutes les données présentes dans le dataframe

    """
    scaler = StandardScaler()  
    return scaler.fit_transform(dataframe)




def clustering_K_means(dataframe, nb_clusters):
    """ 
    Clustering par la méthode KMeans en utilisant NB_CLUSTERS nombre de clusters et en normalisant les données en entrée
    """

    # Normalisation
    dataframe_normalise = normalisation(dataframe)

    # Clustering
    kmeans = KMeans(n_clusters=nb_clusters, random_state=0)
    dataframe['Cluster'] = kmeans.fit_predict(dataframe_normalise)

    return dataframe.groupby('Cluster').groups




def recuperer_clusters(dataframe, numero):
    """ 
    Recuperation de liste des presses dans chaque Cluster
    """

    cluster_liste = dataframe[numero].tolist()
    liste_formatee = ", ".join([f"'{element}'" for element in cluster_liste]) 

    return liste_formatee




def graphe_cluster(dataframe):
    """ 
    Visualisation au sein de chaque groupe (cluster) des notes moyennes pour chaque variable étudiée.

    """

    # Récupération des clusters
    clusters = clustering_K_means(dataframe,2)

    # Récupération des moyennes pour chaque cluster
    moyennes = dataframe.groupby('Cluster').mean().T
    
    plt.figure(figsize=(10, 6))
    bar_width = 0.5
    
    r1 = range(len(moyennes.index))
    r2 = [x + bar_width for x in r1]

    
    plt.bar(r1, moyennes[0], color='green', width=bar_width, label='Cluster 1')
    plt.bar(r2, moyennes[1], color='#ADD8E6', width=bar_width, label='Cluster 2')
    plt.xlabel('Variables étudiées', fontweight='bold')
    plt.xticks([r + bar_width/2 for r in range(len(moyennes.index))], moyennes.index)
    plt.ylabel('Notes')
    plt.title('Comparaison des notes moyennes par Cluster')
    plt.xticks(rotation=45)
    plt.legend()

    # Appel à une autre fonctionn pour récupérer la liste des presses au sein de chaque cluster
    plt.text(0.95, 0.60, f'Cluster 1 : {recuperer_clusters(clusters, 0)}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    plt.text(0.95, 0.40, f'Cluster 2 : {recuperer_clusters(clusters, 1)}', transform=plt.gcf().transFigure, horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

