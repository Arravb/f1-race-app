import streamlit as st
import pandas as pd
import os

# ✅ Correcte F1 2025 racevolgorde
RACES = [
    "Australië GP", "China GP", "Japan GP", "Bahrein GP", "Saoedi-Arabië GP", "Miami GP",
    "Emilia-Romagna GP", "Monaco GP", "Canada GP", "Spanje GP", "Oostenrijk GP",
    "Groot-Brittannië GP", "Hongarije GP", "België GP", "Nederland GP", "Italië GP",
    "Azerbeidzjan GP", "Singapore GP", "Verenigde Staten GP", "Mexico GP",
    "Brazilië GP", "Las Vegas GP", "Qatar GP", "Abu Dhabi GP"
]

# ✅ Puntensysteem
PUNTEN_SYSTEEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
for i in range(11, 21):
    PUNTEN_SYSTEEM[i] = 0  # P11-P20 krijgen 0 punten

# ✅ Spelerslijst (alfabetisch gesorteerd)
SPELERS = sorted(["Arvin", "Frank van Ofwegen", "Mahir", "Mario-VDH", "Nicky", "Roland"])

# ✅ Bestandsnaam voor opslag
DATA_FILE = "races_data.csv"

# ✅ Kolomnamen
COLUMNS = ["P" + str(i) for i in range(1, 21)] + ["Snelste Ronde"]

# ✅ Functie om races_data.csv opnieuw te maken en correct te vullen
def reset_race_data():
    df = pd.DataFrame(columns=["Race"] + COLUMNS)
    df["Race"] = RACES
    save_data(df)

# ✅ Functie om opgeslagen data te laden en race reset correct te herstellen
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        reset_race_data()
    return pd.read_csv(DATA_FILE)

# ✅ Functie om data op te slaan
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ✅ Functie om punten te berekenen (Algemeen Klassement)
def bereken_punten(df):
    punten_telling = {speler: 0 for speler in SPELERS}
    race_telling = {speler: 0 for speler in SPELERS}  # Aantal races per speler

    for _, row in df.iterrows():
        for pos in range(1, 21):
            speler = row.get(f'P{pos}')
            if pd.notna(speler) and speler in punten_telling:
                punten_telling[speler] += PUNTEN_SYSTEEM[pos]
                race_telling[speler] += 1

        # Extra punt voor de snelste ronde
        if pd.notna(row.get('Snelste Ronde')) and row['Snelste Ronde'] in punten_telling:
            punten_telling[row['Snelste Ronde']] += 1

    df_stand = pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Totaal Punten"])
    df_stand["Aantal Races"] = df_stand["Speler"].map(race_telling)
    df_stand = df_stand.sort_values(by="Totaal Punten", ascending=False).reset_index(drop=True)

    return df_stand

# ✅ Functie om punten en posities te berekenen voor een specifieke race
def bereken_punten_race(race_data):
    punten_telling = {}

    for pos in range(1, 21):
        speler = race_data.get(f'P{pos}')
        if pd.notna(speler):
            punten_telling[speler] = PUNTEN_SYSTEEM[pos]

    # Extra punt voor de snelste ronde
    if pd.notna(race_data.get('Snelste Ronde')) and race_data['Snelste Ronde'] in punten_telling:
        punten_telling[race_data['Snelste Ronde']] += 1

    df_race_stand = pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Punten"])
    df_race_stand["Positie"] = range(1, len(df_race_stand) + 1)  # Positie toevoegen
    df_race_stand = df_race_stand[["Positie", "Speler", "Punten"]].sort_values(by="Positie").reset_index(drop=True)

    return df_race_stand

# ✅ Laad de opgeslagen data
df_races = load_data()

# ✅ Streamlit UI
st.set_page_config(page_title="F1 Kampioenschap 2025", layout="wide")
st.title("🏎️ F1 Online Kampioenschap 2025")

# -- Standaard CSS om ook de tabel onder het podium te centreren --
st.markdown("""
<style>
/* Container waarmee we de dataframe ook centreren, net als het podium */
.table-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ✅ Dropdown voor race selectie in de sidebar
selected_race = st.sidebar.selectbox("📅 Selecteer een Grand Prix", ["Huidig Klassement"] + RACES)

# 🏁 Sidebar: Posities én Snelste Ronde invoeren per GP
if selected_race != "Huidig Klassement":
    st.sidebar.subheader(f"🏁 Posities {selected_race}")

    race_index = df_races[df_races["Race"] == selected_race].index[0] if selected_race in df_races["Race"].values else None
    race_results = {}

    # Huidige posities
    for speler in SPELERS:
        existing_position = "Geen"
        if race_index is not None:
            for pos in range(1, 21):
                if df_races.at[race_index, f"P{pos}"] == speler:
                    existing_position = str(pos)
                    break

        race_results[speler] = st.sidebar.selectbox(
            f"{speler}",
            ["Geen"] + [str(i) for i in range(1, 21)],
            index=(["Geen"] + [str(i) for i in range(1, 21)]).index(existing_position) if existing_position != "Geen" else 0
        )

    # Huidige snelste ronde
    existing_fastest_lap = "Geen"
    if race_index is not None:
        current_fastest = df_races.at[race_index, "Snelste Ronde"]
        if pd.notna(current_fastest) and current_fastest in SPELERS:
            existing_fastest_lap = current_fastest

    fastest_lap_selected = st.sidebar.selectbox(
        "Snelste Ronde",
        ["Geen"] + SPELERS,
        index=(["Geen"] + SPELERS).index(existing_fastest_lap) if existing_fastest_lap != "Geen" else 0
    )

    if st.sidebar.button("📥 Opslaan"):
        if race_index is not None:
            # Posities opslaan
            for speler, positie in race_results.items():
                if positie != "Geen":
                    df_races.at[race_index, f"P{int(positie)}"] = speler

            # Snelste Ronde opslaan
            if fastest_lap_selected == "Geen":
                df_races.at[race_index, "Snelste Ronde"] = None
            else:
                df_races.at[race_index, "Snelste Ronde"] = fastest_lap_selected

            save_data(df_races)

        st.experimental_rerun()

# 🎖️ Podium weergave
def toon_podium(df_podium):
    """Toont alleen de top 3 in een 'podium-container' gecentreerd."""
    if len(df_podium) >= 3:
        podium = df_podium.iloc[:3]
        st.markdown(f"""
        <style>
            .podium-container {{
                display: flex;
                justify-content: center;
                align-items: flex-end;
                text-align: center;
                margin-bottom: 20px; /* iets kleinere marge zodat de tabel dichterbij staat */
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
            .gold {{
                background-color: gold;
                font-size: 30px;
                height: 160px;
            }}
            .silver {{
                background-color: silver;
                font-size: 26px;
                height: 120px;
            }}
            .bronze {{
                background-color: #cd7f32;
                font-size: 24px;
                height: 100px;
            }}
        </style>

        <div class="podium-container">
            <div class="podium-item silver">🥈 {podium.iloc[1]['Speler']}</div>
            <div class="podium-item gold">🥇 {podium.iloc[0]['Speler']}</div>
            <div class="podium-item bronze">🥉 {podium.iloc[2]['Speler']}</div>
        </div>
        """, unsafe_allow_html=True)

# 🔄 Algemene klassement (of specifieke GP)
if selected_race == "Huidig Klassement":
    st.subheader("🏆 Algemeen Klassement")
    df_stand = bereken_punten(df_races)
    toon_podium(df_stand)

    # De tabel in een extra container zodat hij ook gecentreerd is
    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
    st.dataframe(df_stand, hide_index=True, height=400, width=600)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.subheader(f"🏁 {selected_race} Resultaten")
    race_data = df_races[df_races["Race"] == selected_race].iloc[0]
    df_race_stand = bereken_punten_race(race_data)
    toon_podium(df_race_stand)

    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
    st.dataframe(df_race_stand, hide_index=True, height=400, width=600)
    st.markdown("</div>", unsafe_allow_html=True)

