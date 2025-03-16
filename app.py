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

# ✅ Functie om punten te berekenen
def bereken_punten(df):
    punten_telling = {speler: 0 for speler in SPELERS}

    for _, row in df.iterrows():
        for pos in range(1, 21):
            speler = row.get(f'P{pos}')
            if pd.notna(speler) and speler in punten_telling:
                punten_telling[speler] += PUNTEN_SYSTEEM[pos]

        if pd.notna(row.get('Snelste Ronde')) and row['Snelste Ronde'] in punten_telling:
            punten_telling[row['Snelste Ronde']] += 1

    df_stand = pd.DataFrame(list(punten_telling.items()), columns=["Speler", "Totaal Punten"]).sort_values(by="Totaal Punten", ascending=False)
    return df_stand

# ✅ Laad de opgeslagen data
df_races = load_data()

# ✅ Streamlit UI
st.set_page_config(page_title="F1 Kampioenschap 2025", layout="wide")
st.title("🏎️ F1 Online Kampioenschap 2025")

# ✅ Dropdown voor race selectie in de sidebar
selected_race = st.sidebar.selectbox("📅 Selecteer een Grand Prix", ["Huidig Klassement"] + RACES)

# 🏁 Sidebar: Posities invoeren per GP
if selected_race != "Huidig Klassement":
    st.sidebar.subheader(f"🏁 Posities {selected_race}")

    race_index = df_races[df_races["Race"] == selected_race].index[0] if selected_race in df_races["Race"].values else None
    race_results = {}

    for speler in SPELERS:
        existing_position = "Geen"
        if race_index is not None:
            for pos in range(1, 21):
                if df_races.at[race_index, f"P{pos}"] == speler:
                    existing_position = pos
                    break

        race_results[speler] = st.sidebar.selectbox(
            f"{speler}",
            ["Geen"] + list(range(1, 21)),
            index=(["Geen"] + list(range(1, 21))).index(str(existing_position)) if existing_position != "Geen" else 0
        )

    # ✅ Direct opslaan & updaten bij klik op "Opslaan"
    if st.sidebar.button("📥 Opslaan"):
        if race_index is not None:
            for speler, positie in race_results.items():
                if positie != "Geen":
                    df_races.at[race_index, f"P{positie}"] = speler
            save_data(df_races)

        # 🔄 Live update direct na opslaan
        st.experimental_rerun()

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
st.subheader("🏆 Algemeen Klassement")
df_stand = bereken_punten(df_races)
toon_podium(df_stand)
st.subheader("📊 Huidige Stand")
st.dataframe(df_stand.set_index("Speler"), height=400, width=600)
