import json
import requests

# URL du fichier pgns.json
url = "https://raw.githubusercontent.com/canboat/canboat/master/analyzer/pgns.json"

# Récupérer les données JSON
response = requests.get(url)
try:
    data = response.json()
except json.JSONDecodeError as e:
    print(f"Erreur de décodage JSON: {e}")
    data = []

# Vérifier la structure des données
if isinstance(data, dict) and "PGNs" in data:
    pgn_list = data["PGNs"]
    pgn_dict = {}
    if isinstance(pgn_list, list):
        # Extraire le dictionnaire
        for item in pgn_list:
            if "PGN" in item.keys() and "Description" in item.keys():
                pgn_dict[str(item["PGN"])] = str(item["Description"]) 
        
        # Écrire le dictionnaire dans un fichier .json
        with open('pgn_dict.json', 'w') as json_file:
            json.dump(pgn_dict, json_file, indent=4)
        
        print("Les données ont été écrites dans le fichier pgn_dict.json")
    else:
        print("La clé 'PGNs' ne contient pas une liste.")
else:
    print("Les données ne sont pas dans le format de dictionnaire attendu ou la clé 'PGNs' est manquante.")

