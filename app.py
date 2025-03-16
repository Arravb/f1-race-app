import streamlit as st
import pandas as pd
import os

# F1 puntensysteem
PUNTEN_SYSTEEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 
                  11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0}

# Spelerslijst
SPELERS = ["Arvin", "Roland", "Frank van Ofwegen", "Mahir", "Mario-VDH", "Nicky"]

# Bestandsnaam voor opslag
DATA_FILE = "races_data.csv"

# Races en kolommen
RACES = ["Australië GP", "China GP", "Japan GP", "Bahrein GP", "Saoedi-Arabië GP"]
COLUMNS = ["P" + str(i) for i in range(1, 21)] + ["Snelste Ronde"]

# Functie om opgeslagen data te laden
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Race"] + COLUMNS)
        df["Race"] = RACES
    # Zorg ervoor dat alle kolommen bestaan
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df

# Functie om data op te slaan
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Functie om punten te berekenen
def bereken_punten(df):
    punten_telling = {speler: 0 for speler in SPELERS}
    race_telling = {speler: 0 for speler in SPELERS}

    for _, row in df.iterrows():
        for pos in range(1, 21):
            speler = row.get(f'P{pos}')
            if pd.notna(speler) and speler in punten_telling:
                punten_telling[speler] += PUNTEN_SYSTEEM[pos]
                race_telling[speler] += 1

        if pd.notna(row.get('Snelste Ronde')) and row['Snelste Ronde'] in punten_telling:
            punten_telling[row['Snelste Ronde']] += 1

    df_stand = pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Totaal Punten"]).sort_values(by="Totaal Punten", ascending=False)
    df_stand["Aantal Races"] = df_stand["Speler"].map(race_telling)

    return df_stand

# Laad de opgeslagen data
df_races = load_data()

# Streamlit UI
st.set_page_config(page_title="F1 Kampioenschap 2025", layout="wide")
st.title("🏎️ F1 Online Kampioenschap 2025")

# Dropdown voor race selectie in de sidebar
selected_race = st.sidebar.selectbox("📅 Selecteer een Grand Prix", ["Huidig Klassement"] + RACES)

if selected_race == "Huidig Klassement":
    # Toon het algemene klassement
    st.subheader("🏆 Algemeen Klassement")
    df_stand = bereken_punten(df_races)
    
    # Toon podium met medailles
    if len(df_stand) >= 3:
        podium = df_stand.iloc[:3]
        st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <div style="text-align: center; margin: 20px;">
                <h1 style="color: gold;">🥇 {podium.iloc[0]['Speler']}</h1>
            </div>
        </div>
        <div style="display: flex; justify-content: center;">
            <div style="text-align: center; margin: 20px;">
                <h2 style="color: silver;">🥈 {podium.iloc[1]['Speler']}</h2>
            </div>
            <div style="text-align: center; margin: 20px;">
                <h2 style="color: #cd7f32;">🥉 {podium.iloc[2]['Speler']}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Toon de stand als tabel zonder index
    st.subheader("📊 Huidige Stand")
    st.dataframe(df_stand.set_index("Speler"), height=400, width=600)

else:
    # Toon de resultaten voor de geselecteerde race
    st.subheader(f"🏁 {selected_race} Resultaten")
    
    race_data = df_races[df_races["Race"] == selected_race].iloc[0]
    
    race_stand = []
    for pos in range(1, 21):
        if f"P{pos}" in race_data and pd.notna(race_data[f"P{pos}"]):
            speler = race_data[f"P{pos}"]
            race_stand.append((speler, PUNTEN_SYSTEEM[pos]))

    df_race_stand = pd.DataFrame(race_stand, columns=["Speler", "Punten"]).sort_values(by="Punten", ascending=False)

    # Podium per race
    if len(df_race_stand) >= 3:
        podium = df_race_stand.iloc[:3]
        st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <div style="text-align: center; margin: 20px;">
                <h1 style="color: gold;">🥇 {podium.iloc[0]['Speler']}</h1>
            </div>
        </div>
        <div style="display: flex; justify-content: center;">
            <div style="text-align: center; margin: 20px;">
                <h2 style="color: silver;">🥈 {podium.iloc[1]['Speler']}</h2>
            </div>
            <div style="text-align: center; margin: 20px;">
                <h2 style="color: #cd7f32;">🥉 {podium.iloc[2]['Speler']}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Stand voor deze race zonder index
    st.subheader(f"📊 Stand {selected_race}")
    st.dataframe(df_race_stand.set_index("Speler"), height=400, width=600)
