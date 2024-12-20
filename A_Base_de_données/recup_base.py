# # Si ne fonctionne pas 
url = "https://minio.lab.sspcloud.fr/roux/base_final_v2.csv"
import pandas as pd
table_films = pd.read_csv(url)

####### Nettoyage et mise en forme

# Conversion des notes en écriture décimale
table_films['spectators_rating'] = table_films['spectators_rating'].apply(mise_en_forme_decimale)
table_films['press_rating'] = table_films['press_rating'].apply(mise_en_forme_decimale)




######## Créations de variables

# Ajout du genre des réalisateurs (en se basant sur une base de plus de 11 627 prénoms de plusieurs pays dont le genre est mentionné)
table_films = get_genre_individuel(table_films, 'director')

# Différence de notation entre spectateur et presse
table_films['diff_notation'] = table_films['spectators_rating']-table_films['press_rating']

# Année du film
table_films = get_annee(table_films, 'date')

# Durée du film en minutes
table_films['duration'] = table_films['duration'].astype('string')
table_films['duration_min'] = table_films['duration'].apply(duree_en_minutes)

# Catégorisation par la durée des films
table_films = categorisation_duree(table_films, 'duration_min')

# Variable catégorielle du type de récompenses (prix, nomination, rien)
table_films['categorie_recompenses'] = table_films['recompenses'].apply(get_cat_recompenses)



# Création d'un dataframe, contenant les notes de chaque film par presse + Traduction des notes en numérique (Très bien => 4, etc)
presse = table_films.iloc[:, [1] + list(range(27, 80))]
presse_notes = equivalence_notes(presse)
presse_notes.set_index('identifiant', inplace=True)


# récupération de la base CNC par API
#Ici, j'importe les données du CNC en utilisant un API.
import requests
import pandas as pd
api_root = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/cnc-production-cinematographique-liste-des-films-agrees/exports/json?limit=-1"
response = requests.get(api_root)
films_cnc_brut = response.json() #je mets tout dans un dico json
print(response.content[:1000])

films_cnc = pd.json_normalize(films_cnc_brut) 
#films_cnc = films_cnc.set_index('visa')


base_allocine = table_films.drop(columns=['titre'])
base_cnc_agregee = pd.merge(films_cnc, base_allocine,left_on='visa', right_on='num_visa', how='inner')

print("allo")
print(base_cnc_agregee)