import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================================================
# 1. SEITEN-KONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="TravelTide Rewards & Cohort Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("✈️ TravelTide - Customer Rewards & Cohort Dashboard")
st.markdown(
    "Interaktive Analyse der **Perk-Zuordnungen** nach Demografie, "
    "Altersstruktur und Geografie."
)


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
# 3. KONSISTENTE PERK-FARBPALETTE (HEX-CODES)
# ==============================================================================
PERK_COLOR_MAP = {
    "free_checked_bag": "#1f77b4",  # Blau
    "exclusive_discounts": "#ff7f0e",  # Orange
    "free_hotel_meal": "#2ca02c",  # Grün
    "1_night_free_hotel_with_flight": "#d62728",  # Rot
    "no_cancellation_fees": "#9467bd",  # Violett
}

all_perks = list(PERK_COLOR_MAP.keys())

# Dynamic CSS Injection: Färbt die jeweilige Checkbox bei Auswahl in der Perk-Farbe ein
css_rules = []
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

# ==============================================================================
# 4. FILTER-BEREICH (PARALLELE SPALTEN ON MAIN PAGE)
# ==============================================================================
st.subheader("🎯 Filter-Auswahl")

col_filter_left, col_filter_right = st.columns([1, 1], gap="large")

# --- LINKE SPALTE: Perk-Checkboxen untereinander ---
selected_perks = []
with col_filter_left:
  st.markdown("**Wähle Perk(s) aus:**")
  for perk in all_perks:
    # Die Checkbox erhält direkt den Namen des Perks ohne "Aktiv"
    is_checked = st.checkbox(
        perk,
        value=True,
        key=f"chk_{perk}",
    )
    if is_checked:
      selected_perks.append(perk)

# --- RECHTE SPALTE: Familienstand-Filter ---
with col_filter_right:
  st.markdown("**Familienstand Filter:**")
  marital_option = st.radio(
      "Familienstand auswählen:",
      ["Alle Kunden", "Nur Verheiratet", "Nur Single"],
      key="marital_radio",
  )

# ==============================================================================
# 5. DATENSATZ RECHNERISCH FILTERN & DYNAMISCHE KPI-METRIKEN
# ==============================================================================
df_filtered = df[df["assigned_perk"].isin(selected_perks)]

if marital_option == "Nur Verheiratet":
  df_filtered = df_filtered[df_filtered["Married"] == True]
  user_kpi_label = "Verheiratete User"
elif marital_option == "Nur Single":
  df_filtered = df_filtered[df_filtered["Married"] == False]
  user_kpi_label = "Single User"
else:
  user_kpi_label = "Gesamte Kohorte (User)"

st.divider()

# Dynamische KPI-Kacheln
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
col_kpi1.metric(user_kpi_label, f"{len(df_filtered):,} User")
col_kpi2.metric(
    "Aktive Perks",
    f"{df_filtered['assigned_perk'].nunique()} / {len(all_perks)}",
)
col_kpi3.metric(
    "Ø Kundenalter",
    f"{df_filtered['Alter'].mean():.1f} Jahre"
    if not df_filtered.empty
    else "0 Jahre",
)
col_kpi4.metric("Abgedeckte States", f"{df_filtered['Home State'].nunique()}")

st.divider()

# ==============================================================================
# 6. DIAGRAMME: PERK-VERTEILUNG & ALTERS-HISTOGRAMM
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
# 7. REGIONALE VERTEILUNG NACH BUNDESSTAATEN & PROVINZEN
# ==============================================================================
st.subheader(
    "🗺️ Regionale Verteilung nach US-Bundesstaaten & Kanadischen Provinzen"
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