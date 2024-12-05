import requests
import json
from datetime import datetime
import os

def main():
    try:
        # Fetch version data from the specified URL
        url = "https://product-details.mozilla.org/1.0/firefox.json"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Extract the 'releases' dictionary
    releases_data = data.get('releases', {})

    releases = []
    major_releases = []

    # Process each version
    for release_key, details in releases_data.items():
        if 'esr' in release_key:
            continue
        category = details.get('category')
        if category in ['major', 'stability']:
            version = details.get('version')
            published = details.get('date')
            if published and version:
                try:
                    date_obj = datetime.strptime(published, '%Y-%m-%d')
                except ValueError:
                    print(f"Invalid date format for version {version}: {published}")
                    continue  # Skip if date format is invalid

                release_info = {
                    'version': version,
                    'published': published,
                    'date_obj': date_obj,
                    'category': category  # Keep track of the category
                }

                releases.append(release_info)

                # Collect major releases separately
                if category == 'major':
                    major_releases.append(release_info)

    # Sort the releases by publication date
    releases.sort(key=lambda x: x['date_obj'])
    major_releases.sort(key=lambda x: x['date_obj'])

    # For each major release, find the next major release date for EOL
    for release in releases:
        if release['category'] == 'major':
            release_date = release['date_obj']

            # Find the next major release after the current release
            next_major_release_date = None
            for major_release in major_releases:
                if major_release['date_obj'] > release_date:
                    next_major_release_date = major_release['published']
                    break

            release['eol'] = next_major_release_date  # Could be None if no next major release
        else:
            release['eol'] = None  # Non-major releases do not have EOL dates

        release['eol'] = next_major_release_date  # Could be None if no next major release

    # Remove 'date_obj' and 'category' as they're no longer needed
    for release in releases:
        release.pop('date_obj')
        release.pop('category')

    try:
        # Create the directory if it doesn't exist
        os.makedirs('firefox/versions', exist_ok=True)
        
        # Export the data to a JSON file
        with open('firefox/versions/firefox_versions.json', 'w') as f:
            json.dump(releases, f, indent=2)
        print("firefox_versions.json has been successfully generated.")
    except IOError as e:
        print(f"Error writing JSON file: {e}")

if __name__ == "__main__":
    main()
