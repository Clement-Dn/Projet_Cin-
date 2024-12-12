import requests
from bs4 import BeautifulSoup
import re
import lxml.html as lh
import io
import asyncio
import aiohttp
import pandas as pd
import nest_asyncio
import pandas as pd
import numpy as np
import csv
import time
import nest_asyncio


# Liste des 55 journaux
journaux = [
    "L’Écran fantastique", "Les Cahiers du cinéma", "Cinemateaser", "Les Inrocks", "Mad Movies", "Positif", "Première", "Télérama",
    "Transfuge", "À voir à lire", "Bande à part", "Critikat", "Culturebox", "Culturopoing", "Ecran large", "Filmsactu", "Journal du geek",
    "La Septième obsession", "LCI", "Les Fiches du cinéma", "IGN France", "20 minutes", "Charlie Hebdo", "CNews", "Les Dernières Nouvelles d’Alsace",
    "Les Echos", "L’Humanité", "La Croix", "La Voix du nord", "Le Dauphiné Libéré", "Le Figaro", "Le JDD", "Le Monde", "Le Parisien",
    "Le Point", "Libération", "Marianne", "Nouvel Obs", "Ouest France", "Sud-Ouest", "Biba", "Closer", "Elle", "Femme actuelle",
    "GQ", "Marie-Claire", "Paris Match", "Public", "Rolling Stone", "Télé 2 semaines", "Télé 7 jours", "Téléloisirs", "Voici"
]

def get_liens(annee, genre=None):
    """
    1 - Construction du lien menant à la page du site avec tous les films ayant le genre et
    l'année demandé.
    2 - Création du lien des différentes pages.
    3 - Extraction du lien des films
    4 - Extraction des infos sur les films

    ENTREES
    - année (int): année de production des films (entre 2010 et 2029)
    - genre : si non mentionné, tous les genres confondus sont considérés

    SORTIE
    - lien html

    """

    # Vérification de la validité de l'année
    if isinstance(annee, int):
        if annee > 2029 or annee < 2010:
            print(f"L'année '{annee}' n'est pas valide (doit être comprise entre 2010 et 2029)")
            return
    else:
        print(f"L'annee doit être un entier")
        return

    # récupération de la décennie correspondant sur le site AlloCine
    decennie = '2020'

    if annee < 2020:
        decennie = '2010'

    annee = str(annee)

    # Equivalence numérique du genre recherché
    genre_numerique = ''

    if genre is not None:

        genre_disponible = {
        "action": '13025',
        "animation": '13026',
        "aventure": '13001',
        "comedie" : '13005',
        "drame": '13008',
        }
        if genre in genre_disponible:
            genre_numerique = genre_disponible[genre]

        else:
            print(f"Le genre '{genre}' n'est pas disponible.")
            return

        # Construction de l'URL
        lien_maitre = 'https://www.allocine.fr/films/genre-' + genre_numerique + '/decennie-' + decennie + '/annee-' + annee + '/'

    else:
        lien_maitre = 'https://www.allocine.fr/films/decennie-' + decennie + '/annee-' + annee + '/'

    # Ws du nombre de page
    code_page = requests.get(lien_maitre)
    balises = BeautifulSoup(code_page.text, 'html.parser')
    liens = balises.find_all('a', href = True)
    nav = balises.find('nav', {"class" : 'pagination cf'})
    spans = nav.find_all('span')
    dernier = spans[-1].get_text()
    dernier = int(dernier)
    liens_pages = [f"{lien_maitre+"?page="}{i}" for i in range(1, dernier + 1)]

    # Fonction asynchrone pour récupérer les liens d'une page
    nest_asyncio.apply()

    async def fetch_links(session, url):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Trouver tous les divs avec la classe 'card entity-card entity-card-list cf'
                    entity_cards = soup.find_all('div', class_='card entity-card entity-card-list cf')

                    # Liste pour stocker les liens trouvés
                    links = []

                    # Parcourir chaque div trouvé
                    for card in entity_cards:
                        # Vérifier s'il y a un div avec la classe 'rating-holder rating-holder-3'
                        rating_holder = card.find('div', class_='rating-holder rating-holder-3')
                        if rating_holder:
                            # Chercher le lien avec la classe 'meta-title-link' dans le div parent
                            meta_title_link = card.find('a', class_='meta-title-link')
                            if meta_title_link:
                                # Ajouter le lien trouvé à la liste
                                links.append(meta_title_link['href'])


                    return links
                else:
                    print(f"Failed to retrieve the page. Status code: {response.status}")
                    return []
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return []
    # Fonction principale pour récupérer les liens de toutes les pages

    async def main(liens_pages):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in liens_pages:
                tasks.append(fetch_links(session, url))
            results = await asyncio.gather(*tasks)
            # Aplatir la liste des résultats
            flattened_results = [link for sublist in results for link in sublist]
            return flattened_results

    # Exécution de la fonction principale
    results = asyncio.run(main(liens_pages))

    # Création du nouveau DataFrame avec les liens récupérés
    new_data = pd.DataFrame({
        'links': results
    })
    new_data['links'] = new_data['links'].apply(lambda x: "https://www.allocine.fr" + x)

    return new_data

    # Pour chaque page on ws les liens des films

def get_carac_film(base_liens):
    nest_asyncio.apply()

    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main():
        async with aiohttp.ClientSession() as session:

            # On utilise identifiant pour créer des liens
            tasks = [fetch(session, url) for url in base_liens["links"]]
            responses = await asyncio.gather(*tasks)
            film_charac = []
            j = 0                 
            interval = len(base_liens) // 20  # Afficher l'avancement tous les 1%


            for i, response in enumerate(responses):
                # Calcul du pourcentage d'avancement
                if j % interval == 0: print(f"Avancement: {j / len(base_liens) * 100:.2f}%")
                j = j + 1
                soup = BeautifulSoup(response, 'html.parser')

                identifiant = re.search(r'\d+', base_liens["links"][i]).group()

                release_element = soup.find('span', class_='meta-release-type')
                release = release_element.text.strip() if release_element else ''

                duration_span = soup.find('span', class_='spacer')
                if duration_span:
                    duration = duration_span.find_next_sibling(text=True).strip()
                else:
                    duration = 'N/A'

                # Extraire les genres (maximum 3 genres)
                # Trouver tous les liens avec la classe 'dark-grey-link'
                meta_body = soup.find('div',class_='meta-body-item meta-body-info')
                genres = meta_body.find_all('span', class_='dark-grey-link')
                # Filtrer les liens pour ne garder que ceux avec un href de la forme '/films/genre-'
                genre_list = [genre.text.strip() for genre in genres]
                genre1 = genre_list[0] if len(genre_list) > 0 else ''
                genre2 = genre_list[1] if len(genre_list) > 1 else ''
                genre3 = genre_list[2] if len(genre_list) > 2 else ''

                # Extraire le réalisateur
                producer_span = soup.find('div', class_='meta-body-item meta-body-direction meta-body-oneline')
                producer_a = producer_span.find('span',class_='dark-grey-link') if producer_span else None
                director = producer_a.text.strip() if producer_a else 'N/A'

                # Extract press rating and number of reviews
                press_rating_element_div = soup.find('div', class_='rating-item-content')
                if press_rating_element_div:
                    press_rating = press_rating_element_div.find('span', class_='stareval-note').text if press_rating_element_div.find('span', class_='stareval-note') else ''
                    press_reviews = press_rating_element_div.find('span', class_='stareval-review').text.split()[0] if press_rating_element_div.find('span', class_='stareval-review') else ''
                else:
                    press_rating = ''
                    press_reviews = ''
                # Extract spectators rating and number of reviews
                spectators_rating_element = soup.find_all('div', class_='rating-item-content')
                spectators_rating = spectators_rating_element[1].find('span', class_='stareval-note').text if len(spectators_rating_element) > 1 and spectators_rating_element[1] else ''
                spectators_reviews_element = spectators_rating_element[1].find('span', class_='stareval-review') if len(spectators_rating_element) > 1 and spectators_rating_element[1] else None
                spectators_reviews = spectators_reviews_element.text.split()[0] if spectators_reviews_element else ''

                # Extraction des données de la fiche technique
                fiche_tech = soup.find('section', class_='section ovw ovw-technical')
                if fiche_tech:
                    nationalite_span = fiche_tech.find('span', string='Nationalité')
                    nationalite = nationalite_span.find_next_sibling('span').text.strip() if nationalite_span else ''

                    date_sortie_dvd_span = fiche_tech.find('span', string='Date de sortie DVD')
                    date_sortie_dvd = date_sortie_dvd_span.find_next_sibling('span').text.strip() if date_sortie_dvd_span else ''

                    date_sortie_bluray_span = fiche_tech.find('span', string='Date de sortie Blu-ray')
                    date_sortie_bluray = date_sortie_bluray_span.find_next_sibling('span').text.strip() if date_sortie_bluray_span else ''

                    date_sortie_vod_span = fiche_tech.find('span', string='Date de sortie VOD')
                    date_sortie_vod = date_sortie_vod_span.find_next_sibling('span').text.strip() if date_sortie_vod_span else ''

                    type_film_span = fiche_tech.find('span', string='Type de film')
                    type_film = type_film_span.find_next_sibling('span').text.strip() if type_film_span else ''

                    budget_span = fiche_tech.find('span', string='Budget')
                    budget = budget_span.find_next_sibling('span').text.strip() if budget_span else ''

                    langues_span = fiche_tech.find('span', string='Langues')
                    langues = langues_span.find_next_sibling('span').text.strip() if langues_span else ''

                    format_production_span = fiche_tech.find('span', string='Format production')
                    format_production = format_production_span.find_next_sibling('span').text.strip() if format_production_span else ''

                    couleur_span = fiche_tech.find('span', string='Couleur')
                    couleur = couleur_span.find_next_sibling('span').text.strip() if couleur_span else ''

                    format_audio_span = fiche_tech.find('span', string='Format audio')
                    format_audio = format_audio_span.find_next_sibling('span').text.strip() if format_audio_span else ''

                    format_projection_span = fiche_tech.find('span', string='Format de projection')
                    format_projection = format_projection_span.find_next_sibling('span').text.strip() if format_projection_span else ''
                   
                    recompenses_span = fiche_tech.find('span', string='Récompenses')
                    recompenses = recompenses_span.find_next_sibling('span').text.strip() if recompenses_span else ''

                    num_visa_span = fiche_tech.find('span', string='N° de Visa')
                    num_visa = num_visa_span.find_next_sibling('span').text.strip() if num_visa_span else ''
                else:
                    nationalite = date_sortie_dvd = date_sortie_bluray = date_sortie_vod = type_film = budget = langues = format_production = couleur = format_audio = format_projection = num_visa = ''

                # Extraction des critiques de la presse
                press_reviews_section = soup.find('div', class_='row reviews-press-list gd gd-xs-1 gd-m-2')
                press_reviews_list = {journal: '' for journal in journaux}
                if press_reviews_section:
                    items = press_reviews_section.find_all('li', class_='item')
                    # Parcourir chaque élément et extraire le journal et la critique
                    for item in items:
                        # Trouver l'élément <span> avec la classe "stareval-link-info"
                        journal_span = item.find('span', class_='stareval-link-info')
                        # Trouver l'élément <span> avec l'attribut "title"
                        critique_span = item.find('span', attrs={'title': True})

                        if journal_span and critique_span:
                            journal = journal_span.get_text(strip=True)
                            critique = critique_span['title']
                            if journal in press_reviews_list:
                                press_reviews_list[journal] = critique

                film_charac.append([
                    identifiant, release, nationalite, date_sortie_dvd, date_sortie_bluray, date_sortie_vod,
                    type_film, budget, langues, format_production, couleur, format_audio, format_projection,recompenses,
                    num_visa, duration, genre1, genre2, genre3, director, press_rating, press_reviews, spectators_rating, spectators_reviews
                ] + list(press_reviews_list.values()))

            return film_charac

    film_charac = asyncio.run(main())

    # Définir les colonnes du DataFrame
    columns = [
        'identifiant', 'release', 'nationalite', 'date_sortie_dvd', 'date_sortie_bluray', 'date_sortie_vod',
        'type_film', 'budget', 'langues', 'format_production', 'couleur', 'format_audio', 'format_projection',
        'recompenses',
        'num_visa', 'duration', 'genre1', 'genre2', 'genre3', 'director', 'press_rating', 'press_reviews',
        'spectators_rating', 'spectators_reviews'
    ] + journaux

    # Créer le DataFrame
    df = pd.DataFrame(film_charac, columns=columns)

    return df



def get_base_final(annee_debut, annee_fin):
    # Initialisation de la base finale comme un DataFrame vide
    base_final = pd.DataFrame()

    # Boucle sur chaque année de annee_debut à annee_fin (non inclus)
    for i in range(annee_debut, annee_fin):
        print(f"L'année en cours de WS est '{i}'.")

        # Mesure du temps de début
        start_time = time.time()

        # Obtention des caractéristiques des films pour l'année en cours
        base_annee_x = get_carac_film(get_liens(annee=i))
        print(f"Nombre de films trouvés {len(base_annee_x)}.")

        # Mesure du temps de fin
        end_time = time.time()

        # Calcul du temps pris
        elapsed_time = end_time - start_time
        print(f"Temps pris pour obtenir les caractéristiques des films pour l'année {i}: {elapsed_time:.2f} secondes")

        # Alignement des colonnes avant la concaténation
        if base_final.empty:
            base_final = base_annee_x
        else:
            # Ajout des colonnes manquantes avec des valeurs NaN
            for col in base_annee_x.columns:
                if col not in base_final.columns:
                    base_final[col] = pd.Series([float('nan')] * len(base_final))

            # Ajout des colonnes manquantes dans base_annee_x avec des valeurs NaN
            for col in base_final.columns:
                if col not in base_annee_x.columns:
                    base_annee_x[col] = pd.Series([float('nan')] * len(base_annee_x))

            # Concaténation des résultats à la base finale
            base_final = pd.concat([base_final, base_annee_x], ignore_index=True)

    return base_final

base_final = get_base_final(2010,2024)

