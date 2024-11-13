import requests
import json
from datetime import datetime
import os

def fetch_releases(platform, channels):
    releases = []

    for channel in channels:
        url = f"https://versionhistory.googleapis.com/v1/chrome/platforms/{platform}/channels/{channel}/versions/all/releases"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Échec de la récupération des données pour le canal '{channel}'. Erreur : {e}")
            continue

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON pour le canal '{channel}'. Erreur : {e}")
            continue

        channel_releases = data.get('releases', [])

        for release in channel_releases:
            version = release.get('version')
            serving = release.get('serving', {})
            start_time = serving.get('startTime')
            end_time = serving.get('endTime')
            if version and start_time:
                try:
                    date_obj = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    try:
                        date_obj = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        continue  # Ignorer si le format de la date est invalide

                releases.append({
                    'version': version,
                    'published': date_obj,
                    'eol': end_time,
                    'channel': channel
                })

    return releases

def main():
    # Plates-formes : 'win', 'mac', 'linux', etc.
    platform = 'win'

    # Canaux à inclure
    channels = ['stable', 'extended']

    # Récupérer les versions
    releases = fetch_releases(platform, channels)

    # Supprimer les doublons et trier les versions par date de publication
    unique_releases = {}
    for release in releases:
        version = release['version']
        if version not in unique_releases or release['published'] < unique_releases[version]['published']:
            unique_releases[version] = release

    releases = list(unique_releases.values())
    releases.sort(key=lambda x: x['published'])

    # Convertir toutes les dates 'published' en chaînes de caractères
    for release in releases:
        release['published'] = release['published'].strftime('%Y-%m-%d')
        
    # Créer le répertoire si nécessaire
    output_dir = 'chrome/versions'
    os.makedirs(output_dir, exist_ok=True)

    # Exporter les données dans un fichier JSON
    try:
        with open(os.path.join(output_dir, 'chrome_versions.json'), 'w') as f:
            json.dump(releases, f, indent=2)
        print("chrome_versions.json a été généré avec succès.")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier JSON. Erreur : {e}")

if __name__ == "__main__":
    main()
