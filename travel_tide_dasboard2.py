import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================================================
# 1. SEITEN-KONFIGURATION & LAYOUT-PARAMETER
# ==============================================================================
st.set_page_config(
    page_title="TravelTide Rewards & Cohort Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# PARAMETER: Schriftgrößen steuern
TITLE_FONT_SIZE = (
    "28px"  # Standard-Titelgröße (Standard in Streamlit ist ca. 40px)
)
# PARAMETER: Unterüberschriften (st.subheader) -> 2px kleiner
SUBHEADER_FONT_SIZE = "18px"  
# PARAMETER: Schriftgröße für die Kohorten-Informationen (ca. 1/3 kleiner als Standard)
INFO_FONT_SIZE = "14px"

# ==============================================================================
# 2. DATEN LADEN & SPALTEN BEREINIGEN
# ==============================================================================
@st.cache_data
def load_data():
  df_perks = pd.read_csv("data/perk_assignments.csv")
  df_demo = pd.read_csv("data/travel_tide_cohort_users_with_states.csv")
  df_merged = df_perks.merge(df_demo, on="user_id")

  # Alter vektoriell über dayofyear berechnen
  df_merged["birthdate"] = pd.to_datetime(df_merged["birthdate"])
  today = pd.to_datetime("today")

  has_not_had_birthday = (
      df_merged["birthdate"].dt.dayofyear > today.dayofyear
  ).astype(int)
  df_merged["Alter"] = (
      today.year - df_merged["birthdate"].dt.year - has_not_had_birthday
  )

  # Spaltennamen absichern / vereinheitlichen
  df_merged.rename(
      columns={"home_state": "Home State", "married": "Married"}, inplace=True
  )

  return df_merged


df = load_data()

# ==============================================================================
# 3. KONSISTENTE PERK-FARBPALETTE & CUSTOM CSS STYLING
# ==============================================================================
PERK_COLOR_MAP = {
    "free_checked_bag": "#4e79a7",  # Blau
    "exclusive_discounts": "#f28e2b",  # Orange
    "free_hotel_meal": "#59a14f",  # Grün
    "1_night_free_hotel_with_flight": "#e15759",  # Rot
    "no_cancellation_fees": "#76b7b2",  # Teal
}

all_perks = list(PERK_COLOR_MAP.keys())

# Dynamic CSS: Färbt Checkboxen ein und skaliert die Schriftgröße der Infoelemente
css_rules = [
   f"""
    /* Custom Schriftgröße für den Haupttitel (st.title) */
    h1 {{
        font-size: {TITLE_FONT_SIZE} !important;
        padding-top: 0rem !important;
        padding-bottom: 0.5rem !important;
    }}

    /* Unterüberschriften (st.subheader / h2) -> 2px kleiner als Titel */
    h2, div[data-testid="stSubheader"] {{
        font-size: {SUBHEADER_FONT_SIZE} !important;
        font-weight: 400 !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }}

    /* Custom Styling für Info-Boxen über den zentralen Parameter */
    .compact-info-header {{
        font-size: {INFO_FONT_SIZE} !important;
        font-weight: bold;
        margin-bottom: 8px;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: calc({INFO_FONT_SIZE} * 1.3) !important;
    }}
    div[data-testid="stMetricLabel"] p {{
        font-size: calc({INFO_FONT_SIZE} * 0.9) !important;
    }}
    """
]

for perk, color in PERK_COLOR_MAP.items():
  css_rules.append(f"""
    /* Custom Styling für Checkbox: {perk} */
    div[data-testid="stCheckbox"]:has(input[aria-label="{perk}"]) input:checked + div {{
        background-color: {color} !important;
        border-color: {color} !important;
    }}
    div[data-testid="stCheckbox"]:has(input[aria-label="{perk}"]) label span {{
        color: {color} !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }}
    """)

st.markdown(
    f"<style>{''.join(css_rules)}</style>",
    unsafe_allow_html=True,
)

# Haupttitel rendern
st.title("✈️ TravelTide - Customer Rewards & Cohort Dashboard")
st.markdown(
    "Interaktive Analyse der **Perk-Zuordnungen** nach Demografie, "
    "Altersstruktur und Geografie."
)

# ==============================================================================
# 4. FILTER & KOHORTEN-INFOS (3 PARALLELE ZELLEN IN EINEM BLOCK)
# ==============================================================================
st.subheader("🎯 Filter & Kennzahlen im Überblick")

col_filter_left, col_filter_mid, col_filter_right = st.columns(
    [1, 1, 1], gap="large"
)

# --- SPALTE 1: Perk-Checkboxen untereinander in Fettschrift ---
selected_perks = []
with col_filter_left:
  st.markdown("**Wähle Perk(s) aus:**")
  for perk in all_perks:
    is_checked = st.checkbox(
        perk,
        value=True,
        key=f"chk_{perk}",
    )
    if is_checked:
      selected_perks.append(perk)

# --- SPALTE 2: Familienstand-Filter ---
with col_filter_mid:
  st.markdown("**Familienstand Filter:**")
  marital_option = st.radio(
      "Familienstand auswählen:",
      ["Alle Kunden", "Nur Verheiratet", "Nur Single"],
      key="marital_radio",
  )

# Datensatz rechnerisch filtern
df_filtered = df[df["assigned_perk"].isin(selected_perks)]

if marital_option == "Nur Verheiratet":
  df_filtered = df_filtered[df_filtered["Married"] == True]
  user_kpi_label = "Verheiratete User"
elif marital_option == "Nur Single":
  df_filtered = df_filtered[df_filtered["Married"] == False]
  user_kpi_label = "Single User"
else:
  user_kpi_label = "Gesamte Kohorte (User)"

# --- SPALTE 3: Infoelemente in kleinerer Schriftgröße ---
with col_filter_right:
  st.markdown(
      f"<div class='compact-info-header'>Dynamische Kohorten-Informationen:</div>",
      unsafe_allow_html=True,
  )

  info_col1, info_col2 = st.columns(2)
  with info_col1:
    st.metric(user_kpi_label, f"{len(df_filtered):,} User")
    st.metric(
        "Ø Kundenalter",
        f"{df_filtered['Alter'].mean():.1f} Jahre"
        if not df_filtered.empty
        else "0 Jahre",
    )
  with info_col2:
    st.metric(
        "Aktive Perks",
        f"{df_filtered['assigned_perk'].nunique()} / {len(all_perks)}",
    )
    st.metric(
        "Abgedeckte States", f"{df_filtered['Home State'].nunique()}"
    )

st.divider()

# ==============================================================================
# 5. DIAGRAMME: PERK-VERTEILUNG & ALTERS-HISTOGRAMM
# ==============================================================================
col_chart_left, col_chart_right = st.columns(2, gap="large")

with col_chart_left:
  st.subheader("📊 Verteilung der zugewiesenen Perks")
  perk_counts = (
      df_filtered["assigned_perk"]
      .value_counts()
      .reindex(selected_perks)
      .fillna(0)
      .reset_index()
  )
  perk_counts.columns = ["assigned_perk", "count"]

  fig_perks = px.bar(
      perk_counts,
      x="assigned_perk",
      y="count",
      color="assigned_perk",
      color_discrete_map=PERK_COLOR_MAP,
      text_auto=True,
      labels={"assigned_perk": "Perk", "count": "Anzahl Kunden"},
  )
  fig_perks.update_layout(
      showlegend=False, xaxis_title="", yaxis_title="Anzahl Kunden"
  )
  st.plotly_chart(fig_perks, use_container_width=True)

with col_chart_right:
  st.subheader("🎂 Altersverteilung nach Perk")
  fig_age = px.histogram(
      df_filtered,
      x="Alter",
      color="assigned_perk",
      color_discrete_map=PERK_COLOR_MAP,
      barmode="stack",
      nbins=15,
      labels={
          "Alter": "Alter (Jahre)",
          "count": "Anzahl Kunden",
          "assigned_perk": "Perk",
      },
  )
  fig_age.update_layout(
      xaxis_title="Alter (Jahre)",
      yaxis_title="Anzahl Kunden",
      legend_title="Perk",
  )
  st.plotly_chart(fig_age, use_container_width=True)

st.divider()

# ==============================================================================
# 6. REGIONALE VERTEILUNG NACH BUNDESSTAATEN & PROVINZEN
# ==============================================================================
st.subheader(
    "🗺️ Verteilung nach US-Bundesstaaten & Kanadischen Provinzen"
)

if not df_filtered.empty:
  state_counts = (
      df_filtered.groupby(["Home State", "assigned_perk"])
      .size()
      .reset_index(name="Anzahl")
  )
  top_states = df_filtered["Home State"].value_counts().head(15).index
  df_states_top = state_counts[state_counts["Home State"].isin(top_states)]

  fig_states = px.bar(
      df_states_top,
      x="Home State",
      y="Anzahl",
      color="assigned_perk",
      color_discrete_map=PERK_COLOR_MAP,
      barmode="stack",
      labels={
          "Home State": "Bundesstaat / Provinz",
          "Anzahl": "Anzahl Kunden",
          "assigned_perk": "Perk",
      },
  )
  fig_states.update_layout(
      xaxis_title="Bundesstaat / Provinz (Top 15)",
      yaxis_title="Anzahl Kunden",
      legend_title="Perk",
  )
  st.plotly_chart(fig_states, use_container_width=True)
else:
  st.info(
      "Keine Daten für die aktuelle Filterkombination verfügbar.", icon="ℹ️"
  )