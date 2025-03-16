import streamlit as st
import pandas as pd
import os
import time
import matplotlib.pyplot as plt

# F1 puntensysteem
PUNTEN_SYSTEEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0}

# Spelerslijst
SPELERS = ["Arvin", "Roland", "Frank van Ofwegen", "Mahir", "Mario-VDH", "Nicky"]

# Bestandsnaam voor opslag
DATA_FILE = "races_data.csv"

# Races en kolommen
RACES = ["Australië GP", "China GP", "Japan GP", "Bahrein GP", "Saoedi-Arabië GP", "Monaco GP", "Canada GP", "Spanje GP", "Oostenrijk GP", "Groot-Brittannië GP", "Hongarije GP", "België GP", "Nederland GP", "Italië GP", "Singapore GP", "Japan GP", "Qatar GP", "Verenigde Staten GP", "Mexico GP", "Brazilië GP", "Las Vegas GP", "Abu Dhabi GP"]
COLUMNS = ["Naam"] + [f"P{i}" for i in range(1, 21)] + ["Snelste Ronde"]

# Functie om opgeslagen data te laden
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Race"] + COLUMNS)
        df["Race"] = RACES
        return df

# Functie om data op te slaan
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Functie om punten te berekenen
def bereken_punten(df):
    punten_telling = {speler: 1 for speler in SPELERS}  # Start bij 1 ipv 0
    for _, row in df.iterrows():
        for pos in range(1, 21):
            speler = row.get(f'P{pos}')
            if pd.notna(speler) and speler in punten_telling:
                punten_telling[speler] += PUNTEN_SYSTEEM[pos]
        if pd.notna(row.get('Snelste Ronde')) and row['Snelste Ronde'] in punten_telling:
            punten_telling[row['Snelste Ronde']] += 1
    df_stand = pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Totaal Punten"]).sort_values(by="Totaal Punten", ascending=False)
    return df_stand

# Laad de opgeslagen data
df_races = load_data()

# Streamlit UI
st.set_page_config(page_title="F1 Kampioenschap 2025", layout="wide")
st.title("🏎️ F1 Online Kampioenschap 2025")

# Sidebar voor GP selectie en invoer
selected_race = st.sidebar.selectbox("📅 Selecteer een Grand Prix", ["Geen"] + RACES)
if selected_race != "Geen":
    st.sidebar.subheader(selected_race)
    race_index = RACES.index(selected_race)
    for speler in SPELERS:
        df_races.at[race_index, speler] = st.sidebar.selectbox(f"Positie voor {speler}", list(range(1, 21)), key=f"{selected_race}_{speler}")
    df_races.at[race_index, "Snelste Ronde"] = st.sidebar.selectbox("🏁 Snelste Ronde", ["Geen"] + SPELERS, key=f"{selected_race}_SnelsteRonde")

# Opslaan en berekenen
if st.sidebar.button("📥 Opslaan & Stand Berekenen"):
    df_races.replace("Geen", pd.NA, inplace=True)
    save_data(df_races)
    st.success("✅ Gegevens opgeslagen!")

# Toon de huidige ranglijst
df_stand = bereken_punten(df_races)
st.header("Huidige Stand")
st.dataframe(df_stand.iloc[:, 1:], height=400, width=600)  # Eerste kolom verwijderen

# Podium visualisatie
st.subheader("🏆 Podium")
if len(df_stand) >= 3:
    podium_names = [df_stand.iloc[1]['Speler'], df_stand.iloc[0]['Speler'], df_stand.iloc[2]['Speler']]
    colors = ["silver", "gold", "#cd7f32"]  # Zilver, Goud, Brons
    medals = ["🥈", "🥇", "🥉"]

    for i in range(3):
        st.write(f"{medals[i]} {podium_names[i]}")
else:
    st.write("Nog niet genoeg data om een podium te tonen.")


