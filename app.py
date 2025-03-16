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

# 🏁 Sidebar: Posities invoeren per GP
if selected_race != "Huidig Klassement":
    st.sidebar.subheader(f"🏁 Posities {selected_race}")

    if selected_race in df_races["Race"].values:
        race_index = df_races[df_races["Race"] == selected_race].index[0]
    else:
        race_index = None

    race_results = {}

    for i, speler in enumerate(SPELERS, start=1):
        # Haal bestaande positie op, anders "Geen"
        existing_position = None
        for pos in range(1, 21):
            if race_index is not None and df_races.at[race_index, f"P{pos}"] == speler:
                existing_position = pos
                break

        # Dropdown voor positie-invoer
        pos = st.sidebar.selectbox(
            f"{speler}",
            ["Geen"] + list(range(1, 21)),
            index=["Geen"] + list(range(1, 21)).index(existing_position) if existing_position else 0,
        )
        race_results[speler] = pos

    # ✅ Direct opslaan & updaten bij klik op "Opslaan"
    if st.sidebar.button("📥 Opslaan"):
        if race_index is not None:
            df_races.loc[race_index, COLUMNS] = pd.NA  # Leegmaken voordat nieuwe data wordt ingevoerd
            for speler, positie in race_results.items():
                if positie != "Geen":
                    df_races.at[race_index, f"P{positie}"] = speler
        save_data(df_races)
        st.experimental_rerun()  # 🔄 Herlaad de app direct voor live update

# 🎖️ Podium weergave
def toon_podium(df_podium):
    if len(df_podium) >= 3:
        podium = df_podium.iloc[:3]
        st.markdown(f"""
        <style>
            .podium-container {{
                display: flex;
                justify-content: center;
                align-items: flex-end;
                text-align: center;
                margin-bottom: 40px;
            }}
            .podium-item {{
                border-radius: 10px;
                font-weight: bold;
                width: 180px;
                margin: 10px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 15px;
            }}
            .gold {{ background-color: gold; font-size: 30px; height: 160px; }}
            .silver {{ background-color: silver; font-size: 26px; height: 120px; }}
            .bronze {{ background-color: #cd7f32; font-size: 24px; height: 100px; }}
        </style>

        <div class="podium-container">
            <div class="podium-item silver">🥈 {podium.iloc[1]['Speler']}</div>
            <div class="podium-item gold">🥇 {podium.iloc[0]['Speler']}</div>
            <div class="podium-item bronze">🥉 {podium.iloc[2]['Speler']}</div>
        </div>
        """, unsafe_allow_html=True)

# 🔄 Live updates bij invoer en opslag
if selected_race == "Huidig Klassement":
    st.subheader("🏆 Algemeen Klassement")
    df_stand = bereken_punten(df_races)
    toon_podium(df_stand)
    st.subheader("📊 Huidige Stand")
    st.dataframe(df_stand.set_index("Speler"), height=400, width=600)

else:
    st.subheader(f"🏁 {selected_race} Resultaten")
    df_race_stand = bereken_punten(df_races[df_races["Race"] == selected_race])
    toon_podium(df_race_stand)
    st.subheader(f"📊 Stand {selected_race}")
    st.dataframe(df_race_stand.set_index("Speler"), height=400, width=600)
