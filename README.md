# Streamlit Analytics

## Description

Streamlit Analytics est un outil de diagnostic pour surveiller et analyser les données des dispositifs de suivi des bateaux. Il permet de visualiser les données de messages NMEA, de générer des QR codes, et de suivre la flotte globale des bateaux.

## Fonctionnalités

- **Analytics** : Affiche les données des 30 derniers jours pour un ID de dispositif donné, y compris la localisation la plus récente et les informations de l'utilisateur et du bateau.
- **QR Code Generator** : Génère des QR codes pour les dispositifs.
- **Global Fleet Tracker** : Affiche les données de tous les dispositifs connectés et les localisations sur une carte.

## Installation

### Prérequis

- Python 3.7+
- pip
- Un serveur SQL avec les bases de données appropriées

### Installation des dépendances

1. Clonez le dépôt :
    ```bash
    git clone https://gogs.dynamitsolutions.com:3000/Yacht_Sentinel/support_tooling.git
    cd support_tooling
    ```

2. Créez et activez un environnement virtuel :
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Assurez-vous que les informations de connexion à vos bases de données sont correctement définies dans le fichier `analytics.py`.

## Utilisation

1. Lancez l'application Streamlit :
    ```bash
    streamlit run analytics.py
    ```

2. Ouvrez votre navigateur web et accédez à l'URL affichée (généralement `http://localhost:8501`).

## Développement

### Structure du projet

- `analytics.py` : Contient le code principal de l'application Streamlit.
- `pages/` : Contient les pages supplémentaires de l'application.
  - `global_fleet_tracker.py` : Page de suivi global de la flotte.
  - `qr_code_generator.py` : Page de génération de QR code.
- `pgnDictionaries/` : Contient les dictionnaires de description des PGN.

### Ajout de fonctionnalités

Pour ajouter une nouvelle fonctionnalité ou une nouvelle page :

1. Créez un nouveau fichier dans le dossier `pages/`.
2. Ajoutez le contenu de la nouvelle page en utilisant les composants Streamlit.
3. Modifiez `analytics.py` pour inclure la nouvelle page dans la navigation.

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre les étapes ci-dessous pour contribuer :

1. Forkez le dépôt.
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/new-feature`).
3. Commitez vos changements (`git commit -m 'Add some feature'`).
4. Poussez votre branche (`git push origin feature/new-feature`).
5. Ouvrez une Pull Request.

## Aide

Si vous avez des questions ou des problèmes, veuillez ouvrir une issue sur le dépôt ou contacter l'administrateur du projet.

## Licence

Ce projet est sous licence MIT.
