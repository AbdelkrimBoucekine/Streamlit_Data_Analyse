import streamlit as st
import pandas as pd
import time
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
import folium
from streamlit_folium import st_folium

# Charger le dictionnaire de descriptions de PGN
try:
    with open('pgnDictionaries/pgn_dict.json', 'r') as file:
        pgn_dict = json.load(file)
except FileNotFoundError:
    st.error("Le fichier 'pgn_descriptions.json' est introuvable.")
    pgn_dict = {}

# Informations de connexion
AZUREUID = 'xxxxxxxxxxx'
AZUREPWD = 'xxxxxxxxxxx'
AZURESRV = 'xxxxxxxxxxxxx'
AZUREDB = 'xxxxxxxxxxxxx'
TABLE = 'xxxxxxxxxxxxxxxxxx'
DRIVER = 'ODBC Driver 17 for SQL Server'

# Chaîne de connexion
connectionstring_template = 'mssql+pyodbc://{uid}:{password}@{server}:1433/{database}?driver={driver}'
connectionstring = connectionstring_template.format(
    uid=AZUREUID,
    password=AZUREPWD,
    server=AZURESRV,
    database=AZUREDB,
    driver=DRIVER.replace(' ', '+')
)

# Créer un moteur SQL Alchemy
engn_nmea = create_engine(connectionstring)

# Fonction pour récupérer les données des 30 derniers jours pour tous les devices
def get_device_message_count_30_days():
    date_30_days_ago = datetime.now() - timedelta(days=30)
    query = f'''
    SELECT 
        SdKey, 
        Pgn,
        COUNT(*) AS message_count
    FROM 
        {TABLE}
    WHERE 
        SdKey LIKE '8627710439%' AND
        QueuedTime >= '{date_30_days_ago.strftime('%Y-%m-%d')}'
    GROUP BY 
        SdKey, 
        Pgn
    '''
    result = pd.read_sql_query(query, engn_nmea)
    result['Pgn'] = result['Pgn'].astype(str)  # Convertir les noms de colonnes en chaînes de caractères
    return result

# Fonction pour récupérer les dernières localisations de tous les devices
@st.cache_data(ttl=3600)  # Cache les résultats pour une heure
def get_all_latest_locations():
    date_30_days_ago = datetime.now() - timedelta(days=30)
    query = f'''
    WITH LatestData AS (
        SELECT
            SdKey,
            Data,
            QueuedTime,
            ROW_NUMBER() OVER (PARTITION BY SdKey ORDER BY QueuedTime DESC) AS rn
        FROM
            {TABLE}
        WHERE
            SdKey LIKE '8627710439%' AND
            QueuedTime >= '{date_30_days_ago.strftime('%Y-%m-%d')}' AND
            JSON_VALUE(Data, '$.Fields.Latitude') IS NOT NULL AND
            JSON_VALUE(Data, '$.Fields.Longitude') IS NOT NULL
    )
    SELECT
        SdKey,
        JSON_VALUE(Data, '$.Fields.Latitude') AS Latitude,
        JSON_VALUE(Data, '$.Fields.Longitude') AS Longitude,
        QueuedTime
    FROM
        LatestData
    WHERE
        rn = 1
    '''
    print (query)
    start = time.time()
    result = pd.read_sql_query(query, engn_nmea)
    end = time.time()
    duration = end - start
    print (f"duration {str(duration)}")
    result['Latitude'] = result['Latitude'].astype(float)
    result['Longitude'] = result['Longitude'].astype(float)
    return result

def show_global_fleet_tracker():
    st.title("Global Fleet Tracker")
    
    # Récupérer les données des 30 derniers jours pour tous les devices
    data = get_device_message_count_30_days()
    
    if not data.empty:
        # Remplacer les numéros de PGN par les descriptions
        data['Pgn'] = data['Pgn'].apply(lambda x: pgn_dict.get(x, x))
        
        # Pivoter les données
        pivot_table = data.pivot(index='SdKey', columns='Pgn', values='message_count').fillna(0)
        pivot_table.columns = pivot_table.columns.astype(str)  # Convertir les noms de colonnes en chaînes de caractères
        pivot_table['Total'] = pivot_table.sum(axis=1)
        
        st.write("Message count for all devices in the last 30 days:")
        st.write(pivot_table)

        # Afficher le compteur de devices
        st.write(f"Total Devices: {data['SdKey'].nunique()}")

        # Récupérer les positions des devices
        locations = get_all_latest_locations()
        
        if not locations.empty:
            # Créer une carte
            m = folium.Map(location=[locations['Latitude'].mean(), locations['Longitude'].mean()], zoom_start=2)
            
            # Ajouter les points à la carte
            for _, row in locations.iterrows():
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=f"Device ID: {row['SdKey']}<br>Time: {row['QueuedTime']}"
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
        else:
            st.write("No location data available for any devices.")
    else:
        st.write("No data found for any devices in the last 30 days.")

