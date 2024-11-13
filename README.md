# PackageVersionDate

## Description

**PackageVersionDate** est un projet qui répertorie les versions des navigateurs (Chrome, Firefox) et des systèmes d'exploitation Windows (Windows 10, Windows 11, Windows Server), ainsi que leurs dates de fin de support (EOL).

Les informations sont mises à jour automatiquement chaque jour via GitHub Actions. 

---

## Arborescence

```
PackageVersionDate/
├── chrome/
│   ├── versions/
│   │   └── chrome_versions.json
│   └── get_chrome_versions.py
├── firefox/
│   ├── versions/
│   │   └── firefox_versions.json
│   └── get_firefox_versions.py
├── windows/
│   ├── versions/
│   │   ├── windows_10_20h1.json
│   │   └── windows_server_2019.json
│   │   └── ...
│   └── get_windows_versions.py
└── .github/
    └── workflows/
        └── update_versions.yml
```

---

## Exemple de Formats JSON

### Chrome et Firefox

```json
[
    {
        "version": "XX.XX.XXXX.XX",
        "published": "YYYY-MM-DD",
        "eol": "YYYY-MM-DD"
    }
]
```

### Windows

```json
{
    "version": "XXXX",
    "end_of_servicing": "true" or "false",
        "updates": [
        {
            "date": "YYYY-MM-DD",
            "build": "XXXX.XXXX",
            "KB": "KBXXXXXXX",
            "eol": "YYYY-MM-DD"
        }
    ]
}
```