import streamlit as st
import pandas as pd
import os
import time

# F1 puntensysteem
PUNTEN_SYSTEEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# Spelerslijst
SPELERS = ["Arvin", "Roland", "Frank van Ofwegen", "Mahir", "Mario-VDH", "Nicky"]

# Bestandsnaam voor opslag
DATA_FILE = "races_data.csv"

# Races en kolommen
RACES = ["Australië GP", "China GP", "Japan GP", "Bahrein GP", "Saoedi-Arabië GP"]
COLUMNS = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "Snelste Ronde"]

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
        for pos in range(1, 11):
            speler = row.get(f'P{pos}')
            if pd.notna(speler) and speler in punten_telling:
                punten_telling[speler] += PUNTEN_SYSTEEM[pos]
        if pd.notna(row.get('Snelste Ronde')) and row['Snelste Ronde'] in punten_telling:
            punten_telling[row['Snelste Ronde']] += 1
    return pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Totaal Punten"]).sort_values(by="Totaal Punten", ascending=False)

# Laad de opgeslagen data
df_races = load_data()

# Streamlit UI
st.set_page_config(page_title="F1 Kampioenschap 2025", layout="wide")
st.title("🏎️ F1 Online Kampioenschap 2025")
st.write("Beheer de race-uitslagen en bekijk de actuele ranglijst. De gegevens worden opgeslagen en blijven bewaard.")

# Dropdown voor race selectie
selected_race = st.selectbox("📅 Selecteer een Grand Prix", ["Geen"] + RACES)

if selected_race != "Geen":
    st.subheader(selected_race)
    race_index = RACES.index(selected_race)
    for col in COLUMNS:
        df_races.at[race_index, col] = st.selectbox(f"{col} ({selected_race})", ["Geen"] + SPELERS, key=f"{selected_race}_{col}", index=(["Geen"] + SPELERS).index(df_races.at[race_index, col] if pd.notna(df_races.at[race_index, col]) else "Geen"))

# Opslaan en berekenen
if st.sidebar.button("📥 Opslaan & Stand Berekenen"):
    df_races.replace("Geen", pd.NA, inplace=True)
    save_data(df_races)
    st.success("✅ Gegevens opgeslagen!")

# Toon de huidige ranglijst
df_stand = bereken_punten(df_races)
st.header("🏆 Huidige Stand")

# Animatie: Podium presentatie
st.subheader("🏆 Podium")
for i in range(min(3, len(df_stand))):  # Zorgt ervoor dat het niet crasht bij minder dan 3 spelers
    time.sleep(0.5)
    st.write(f"🥇 {df_stand.iloc[i]['Speler']} - {df_stand.iloc[i]['Totaal Punten']} punten")

st.dataframe(df_stand, height=400, width=600)


