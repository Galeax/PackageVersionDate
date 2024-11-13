import requests
import json
from datetime import datetime
import os

def main():
    try:
        # Récupérer les données de version depuis l'URL spécifiée
        url = "https://product-details.mozilla.org/1.0/firefox.json"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Erreur lors du décodage JSON: {e}")
        return

    # Extraire le dictionnaire 'releases'
    releases_data = data.get('releases', {})

    releases = []

    # Traiter chaque version
    for release_key, details in releases_data.items():
        category = details.get('category')
        if category in ['major', 'stability']:
            version = details.get('version')
            published = details.get('date')
            if published and version:
                try:
                    date_obj = datetime.strptime(published, '%Y-%m-%d')
                except ValueError:
                    print(f"Format de date invalide pour la version {version}: {published}")
                    continue  # Ignorer si le format de la date est invalide

                releases.append({
                    'version': version,
                    'published': published,
                    'date_obj': date_obj
                })

    # Trier les versions par date de publication
    releases.sort(key=lambda x: x['date_obj'])

    # Définir la date de fin de vie (EOL) comme la date de publication de la version suivante
    for i in range(len(releases)):
        if i < len(releases) - 1:
            eol_date = releases[i + 1]['published']
        else:
            eol_date = None  # Dernière version, date de fin de vie inconnue
        releases[i]['eol'] = eol_date

    # Supprimer 'date_obj' car il n'est plus nécessaire
    for release in releases:
        release.pop('date_obj')

    try:
        # Créer le répertoire si nécessaire
        os.makedirs('firefox/versions', exist_ok=True)
        
        # Exporter les données dans un fichier JSON
        with open('firefox/versions/firefox_versions.json', 'w') as f:
            json.dump(releases, f, indent=2)
        print("firefox_versions.json a été généré avec succès.")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier JSON: {e}")

if __name__ == "__main__":
    main()
