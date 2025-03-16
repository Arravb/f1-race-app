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
RACES = ["Australië GP", "China GP", "Japan GP", "Bahrein GP", "Saoedi-Arabië GP"]
COLUMNS = ["P" + str(i) for i in range(1, 21)] + ["Snelste Ronde"]

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

# Dropdown voor race selectie in de sidebar
selected_race = st.sidebar.selectbox("📅 Selecteer een Grand Prix", RACES)

if selected_race:
    st.subheader(selected_race)
    race_index = RACES.index(selected_race)
    for col in COLUMNS:
        df_races.at[race_index, col] = st.sidebar.selectbox(f"{col} ({selected_race})", ["Geen"] + SPELERS, key=f"{selected_race}_{col}", index=(["Geen"] + SPELERS).index(df_races.at[race_index, col] if pd.notna(df_races.at[race_index, col]) else "Geen"))

# Opslaan en berekenen
if st.sidebar.button("📥 Opslaan & Stand Berekenen"):
    df_races.replace("Geen", pd.NA, inplace=True)
    save_data(df_races)
    st.success("✅ Gegevens opgeslagen!")

# Toon de huidige ranglijst als lijst
df_stand = bereken_punten(df_races)
st.header("Huidige Stand")
for index, row in df_stand.iterrows():
    st.write(f"🏁 {row['Speler']} - {row['Totaal Punten']} punten")

# Podium visualisatie
st.subheader("🏆 Podium")
if len(df_stand) >= 3:
    podium_names = [df_stand.iloc[1]['Speler'], df_stand.iloc[0]['Speler'], df_stand.iloc[2]['Speler']]
    podium_colors = ["silver", "gold", "#cd7f32"]  # Zilver, Goud, Brons
    podium_positions = [2, 1, 3]  # Links, midden, rechts

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(podium_positions, [2, 3, 1], color=podium_colors, width=0.5)  # Simuleert een podium effect
    for i, txt in enumerate(podium_names):
        ax.text(podium_positions[i], [2, 3, 1][i] + 0.2, txt, ha='center', fontsize=12, fontweight='bold')

    ax.set_xticks(podium_positions)
    ax.set_xticklabels(["🥈", "🥇", "🥉"], fontsize=15)
    ax.set_yticks([])
    ax.set_frame_on(False)
    st.pyplot(fig)
else:
    st.write("Nog niet genoeg data om een podium te tonen.")
