import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def fetch_release_information(url):
    """
    Récupérer la page d'informations de version et l'analyser avec BeautifulSoup.
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Échec de la récupération de {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def extract_update_tables(soup):
    """
    Extraire les tableaux de mise à jour de la soupe HTML analysée.
    Retourne une liste de tuples contenant (version_name, table_soup).
    """
    update_tables = []
    tables = soup.find_all('table', {'id': re.compile(r'historyTable_\d+')})
    for table in tables:
        details_element = table.find_previous('details')
        version_name = table.find_previous('strong').get_text(strip=True)
        if details_element:
            summary_element = details_element.find('summary')
            if 'end of servicing' in summary_element.get_text(strip=True).lower():
                version_name += ' (EOL)'
            if summary_element:
                print(version_name)
                update_tables.append((version_name, table))
    return update_tables

def extract_updates_from_table(version_name, table):
    """
    Extraire les mises à jour d'un tableau donné.
    Retourne une liste de dictionnaires avec les clés : date, build, KB, eol.
    """
    updates = []
    # Trouver toutes les lignes dans le corps du tableau
    tbody = table.find('tbody')
    if not tbody:
        return updates
    rows = tbody.find_all('tr')
    if not rows:
        return updates
    # La première ligne est l'en-tête
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all('th')]
    # Mapper les en-têtes aux indices
    header_indices = {}
    for idx, header in enumerate(headers):
        if 'availability date' in header or 'release date' in header:
            header_indices['date'] = idx
        elif 'build' in header:
            header_indices['build'] = idx
        elif 'kb article' in header:
            header_indices['kb'] = idx
    # S'assurer que nous avons tous les en-têtes requis
    if not all(key in header_indices for key in ['date', 'build', 'kb']):
        return updates
    # Itérer sur les lignes de données
    for i, row in enumerate(rows[1:]):
        cells = row.find_all('td')
        if len(cells) < len(header_indices):
            continue
        date_cell = cells[header_indices['date']]
        build_cell = cells[header_indices['build']]
        kb_cell = cells[header_indices['kb']]
        # Extraire le texte et nettoyer
        date_text = date_cell.get_text(strip=True)
        build_text = build_cell.get_text(strip=True)
        kb_link = kb_cell.find('a', href=True)
        if kb_link:
            kb_text = kb_link.get_text(strip=True)
        else:
            kb_text = kb_cell.get_text(strip=True)
        # Déterminer la date de fin de vie (date de sortie de la mise à jour précédente)
        eol_text = None
        if i > 0:
            prev_row = rows[i]
            prev_date_cell = prev_row.find_all('td')[header_indices['date']]
            eol_text = prev_date_cell.get_text(strip=True)
        # Ajouter à la liste des mises à jour
        updates.append({
            'date': date_text,
            'build': build_text,
            'KB': kb_text,
            'eol': eol_text
        })
    return updates

def main():
    windows_versions = {
        'windows11': {
            'url': 'https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information',
            'output_prefix': 'windows_11_'
        },
        'windows10': {
            'url': 'https://learn.microsoft.com/en-us/windows/release-health/release-information',
            'output_prefix': 'windows_10_'
        },
        'windows_server': {
            'url': 'https://learn.microsoft.com/en-us/windows/release-health/windows-server-release-info',
            'output_prefix': 'windows_server_'
        }
    }
    
    # Créer le dossier 'windows/versions' s'il n'existe pas
    output_dir = 'windows/versions'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for win_version, info in windows_versions.items():
        print(f"Traitement de {win_version}...")
        soup = fetch_release_information(info['url'])
        if not soup:
            continue
        update_tables = extract_update_tables(soup)
        for version_name, table in update_tables:
            end_of_servicing = False
            if ('(EOL)' in version_name) or ('end of servicing' in version_name.lower()):
                end_of_servicing = True
            if 'server' in version_name.lower():
                version_name = version_name.lower().replace('version', '').strip().split(' ')[2]
            else:
                version_name = version_name.lower().replace('version', '').strip().split(' ')[0]
                
            print(version_name)
            # Nettoyer version_name pour créer un nom de fichier
            filename = 'windows/versions/' + info['output_prefix'] + version_name + '.json'
            updates = extract_updates_from_table(version_name, table)
            if not updates:
                print(f"Aucune mise à jour trouvée pour {version_name}")
                continue
            # Enregistrer les mises à jour dans un fichier JSON
            data = {
                "version": version_name,
                "end_of_servicing": end_of_servicing,
                "updates": updates
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            # Soyez poli et dormez entre les requêtes
            time.sleep(1)

if __name__ == "__main__":
    main()
