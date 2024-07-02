import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import json
from datetime import datetime
import folium
from streamlit_folium import st_folium

# Définir la configuration de la page en premier
st.set_page_config(layout="wide")

# Importer les nouvelles pages
from pages.global_fleet_tracker import show_global_fleet_tracker
from pages.qr_code_generator import show_qr_code_generator

# Charger le dictionnaire de descriptions de PGN
try:
    with open('pgnDictionaries/ys_dictionnary.json', 'r') as file:
        pgn_dict = json.load(file)
except FileNotFoundError:
    st.error("Le fichier 'pgn_descriptions.json' est introuvable.")
    pgn_dict = {}
for key in pgn_dict.keys():
     pgn_dict[key] = pgn_dict[key]['Description']

try:
    with open('pgnDictionaries/pgn_dict.json', 'r') as file:
        pgn_dict2 = json.load(file)
except FileNotFoundError:
    st.error("Le fichier 'pgn_descriptions.json' est introuvable.")
    pgn_dict2 = {}
for key in pgn_dict2.keys():
     pgn_dict[key] = pgn_dict2[key]

# Informations de connexion pour la base de données NMEA
AZUREUID_NMEA = 'abdel_test'
AZUREPWD_NMEA = 'cZ4A9mPqRRYA'
AZURESRV_NMEA = 'testdb.yacht-sentinel.com'
AZUREDB_NMEA = 'nmeadb'
TABLE = 'NmeaMessages'
DRIVER = 'ODBC Driver 17 for SQL Server'

connectionstring_template = 'mssql+pyodbc://{uid}:{password}@{server}:1433/{database}?driver={driver}'
connectionstring_nmea = connectionstring_template.format(
    uid=AZUREUID_NMEA,
    password=AZUREPWD_NMEA,
    server=AZURESRV_NMEA,
    database=AZUREDB_NMEA,
    driver=DRIVER.replace(' ', '+')
)

engn_nmea = create_engine(connectionstring_nmea)

# Informations de connexion pour la base de données principale
AZUREUID_MAIN = 'abdel.read_only'
AZUREPWD_MAIN = 'cZ4A9mPqRRYA'
AZURESRV_MAIN = 'yachtsentinel.database.windows.net'
AZUREDB_MAIN = 'yachtsentinel'

connectionstring_main = connectionstring_template.format(
    uid=AZUREUID_MAIN,
    password=AZUREPWD_MAIN,
    server=AZURESRV_MAIN,
    database=AZUREDB_MAIN,
    driver=DRIVER.replace(' ', '+')
)

engn_main = create_engine(connectionstring_main)

# Fonction pour récupérer les détails de l'abonnement pour un device_id donné
@st.cache_data(ttl=3600)
def get_user_boat_info(device_id):
    query = f'''
    SELECT TOP (1000)
        [User].[FullName] AS [Full Name],
        [User].[EmailAddress] AS [Email Address],
        [User].[MobileNumber] AS [Mobile Number],
        [UserSentinel].[Name] AS [Boat Name]
    FROM
        [dbo].[SubscriptionDetails]
    LEFT JOIN
        [dbo].[WhitelistedDevice] ON SubscriptionDetails.WhitelistedDeviceId = WhitelistedDevice.Id
    LEFT JOIN
        dbo.[User] ON SubscriptionDetails.TenantId = [User].TenantId
    LEFT JOIN
        dbo.[UserSentinel] ON SubscriptionDetails.TenantId = [UserSentinel].TenantId
    WHERE
        WhitelistedDevice.MacAddress = '{device_id}'
    AND 
        [SubscriptionDetails].[Status] = 1
    ORDER BY 
        WhitelistedDevice.MacAddress
    '''
    result = pd.read_sql_query(query, engn_main)
    return result

# Fonction pour récupérer les détails de l'abonnement pour un device_id donné
@st.cache_data(ttl=3600)
def get_subscription_details(device_id):
    query = f'''
    SELECT TOP (1000) 
        [STATUS],
        SubscriptionDetails.CreatedDate,
        SubscriptionDetails.ExpiryDate,
        SubscriptionType.[Name] as SubscriptionName,
        [Platform],
        [AppSchema]
    FROM 
        [dbo].[SubscriptionDetails]
    LEFT JOIN 
        [dbo].[WhitelistedDevice] ON SubscriptionDetails.WhitelistedDeviceId = WhitelistedDevice.Id
    LEFT JOIN 
        dbo.SubscriptionType on SubscriptionDetails.SubscriptionTypeId = SubscriptionType.Id
    WHERE 
        WhitelistedDevice.MacAddress = '{device_id}'
    AND 
        [SubscriptionDetails].[Status] = 1
    ORDER BY 
        WhitelistedDevice.MacAddress
    '''
    result = pd.read_sql_query(query, engn_main)
    return result

# Fonction pour récupérer les données des 30 derniers jours pour un device_id donné
@st.cache_data(ttl=3600)
def get_data(device_id):
    query = f'''
    SELECT 
        CAST(QueuedTime AS DATE) AS Date,
        Pgn,
        COUNT(*) AS message_count
    FROM 
        {TABLE}
    WHERE 
        SdKey = '{device_id}' AND
        QueuedTime >= DATEADD(day, -30, GETDATE())
    GROUP BY 
        CAST(QueuedTime AS DATE),
        Pgn
    ORDER BY 
        Date, Pgn;
    '''
    result = pd.read_sql_query(query, engn_nmea)
    return result

# Fonction pour récupérer la dernière localisation pour un device_id donné
@st.cache_data(ttl=3600)
def get_latest_location(device_id):
    query = f'''
    SELECT TOP 1 
        JSON_VALUE(Data, '$.Fields.Latitude') AS Latitude,
        JSON_VALUE(Data, '$.Fields.Longitude') AS Longitude,
        QueuedTime
    FROM 
        {TABLE}
    WHERE 
        SdKey = '{device_id}' AND
        JSON_VALUE(Data, '$.Fields.Latitude') IS NOT NULL AND
        JSON_VALUE(Data, '$.Fields.Longitude') IS NOT NULL
    ORDER BY 
        QueuedTime DESC;
    '''
    result = pd.read_sql_query(query, engn_nmea)
    if not result.empty:
        return result.iloc[0]
    return None

# Barre latérale avec logo en haut
with st.sidebar:
    st.image("logo.png", width=200)
    st.title("Boat Data Analytics")

    page = st.radio("Navigation", ["Analytics", "QR Code Generator", "Global Fleet Tracker"])

if page == "Analytics":
    st.header("Boat Data Analytics")
    st.write("Enter the Device ID to view the data.")
   
    # Widget pour saisir le numéro du device_id
    device_id = st.text_input("Enter Device ID", "8627710439*****")

    # Afficher les données si un device_id est saisi
    if device_id:
        user_boat_info = get_user_boat_info(device_id)
        if not user_boat_info.empty:
            st.markdown('<h4 style="color:grey;">User and Boat Information</h2>', unsafe_allow_html=True)
            st.write(user_boat_info)
        else:
            st.write("No user or boat information found for the given Device ID.")
        
    # Afficher les détails de l'abonnement
    subscription_data = get_subscription_details(device_id)
    if not subscription_data.empty:
            st.markdown('<h4 style="color:grey;">Subscription Details</h2>', unsafe_allow_html=True)
            st.write(subscription_data)
    else:
            st.write("No subscription details found for the given Device ID.")

    # Afficher les données si un device_id est saisi
    if device_id:
        data = get_data(device_id)
        if not data.empty:
            # Remplacer les numéros de PGN par les descriptions
            data['Pgn'] = data['Pgn'].apply(lambda x: pgn_dict.get(str(x), str(x)))
            
            # Pivoter les données
            pivot_table = data.pivot(index='Date', columns='Pgn', values='message_count').fillna(0)
            st.markdown('<h4 style="color:grey;">Data</h2>', unsafe_allow_html=True)
            st.write(pivot_table)

            # Optionnel : Créer des graphiques pour visualiser les données
            st.markdown('<h4 style="color:grey;">Number of messages per day and per PGN</h2>', unsafe_allow_html=True)
            st.bar_chart(pivot_table)
        else:
            st.write("No data found for the given Device ID.")
        
        # Récupérer la dernière localisation
        latest_location = get_latest_location(device_id)
        if latest_location is not None:
            st.markdown('<h4 style="color:grey;">Latest Location</h2>', unsafe_allow_html=True)
            st.write(f"Latitude: {latest_location['Latitude']}, Longitude: {latest_location['Longitude']}")
            st.write(f"Date and Time: {latest_location['QueuedTime']}")

            # Afficher la localisation sur une carte
            m = folium.Map(location=[latest_location['Latitude'], latest_location['Longitude']], zoom_start=12)
            folium.Marker([latest_location['Latitude'], latest_location['Longitude']], 
                        popup=f"Date and Time: {latest_location['QueuedTime']}").add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.write("No location data found for the given Device ID.")

elif page == "QR Code Generator":
    show_qr_code_generator()

elif page == "Global Fleet Tracker":
    show_global_fleet_tracker()
