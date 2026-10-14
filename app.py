import streamlit as st
import pandas as pd
import plotly.express as px

# Seiten-Konfiguration
st.set_page_config(page_title="TravelTide Rewards Dashboard", layout="wide")

st.title("✈️ TravelTide - Customer Rewards & Cohort Dashboard")
st.markdown("Interaktive Analyse der **Perk-Zuordnungen** nach Demografie & Geografie.")

# 1. Daten laden
@st.cache_data
def load_data():
  df_perks = pd.read_csv('data/perk_assignments.csv')
  df_demo = pd.read_csv('data/travel_tide_cohort_users_with_states.csv')
  df_merged = df_perks.merge(df_demo, on='user_id')

  # 1. Datum in Datetime umwandeln
  df_merged['birthdate'] = pd.to_datetime(df_merged['birthdate'])
  today = pd.to_datetime('today')

  # 2. Exaktes Alter vektoriell berechnen
  has_not_had_birthday = (
      df_merged['birthdate'].dt.dayofyear > today.dayofyear
  ).astype(int)

  df_merged['Alter'] = (
      today.year - df_merged['birthdate'].dt.year - has_not_had_birthday
  )
  return df_merged

df = load_data()

# 2. Sidebar / Filter
st.sidebar.header("Filter-Optionen")
selected_perks = st.sidebar.multiselect(
    "Wähle Perk(s):",
    options=df['assigned_perk'].unique(),
    default=df['assigned_perk'].unique()
)

marital_filter = st.sidebar.radio("Familienstand:", ["Alle", "Nur Verheiratet", "Nur Single"])

# Filtern der Daten
df_filtered = df[df['assigned_perk'].isin(selected_perks)]
if marital_filter == "Nur Verheiratet":
    df_filtered = df_filtered[df_filtered['married'] == True]
elif marital_filter == "Nur Single":
    df_filtered = df_filtered[df_filtered['married'] == False]

# 3. KPI-Metriken anzeigen
col1, col2, col3 = st.columns(3)
col1.metric("Ausgewählte Kunden", f"{len(df_filtered):,}")
col2.metric("Anzahl Perks", f"{df_filtered['assigned_perk'].nunique()}")
col3.metric("Anzahl Bundesstaaten", f"{df_filtered['home_state'].nunique()}")

st.divider()

# 4. Diagramme (Visualisierung)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Verteilung der Perks")
    fig_perks = px.bar(
        df_filtered['assigned_perk'].value_counts().reset_index(),
        x='assigned_perk', y='count',
        labels={'assigned_perk': 'Perk', 'count': 'Anzahl User'},
        color='assigned_perk'
    )
    st.plotly_chart(fig_perks, use_container_width=True)

with col_right:
    st.subheader("Altersverteilung nach Perk")
    fig_age = px.histogram(
            df_filtered,
            x='Alter',
            color='assigned_perk',
            barmode='stack',
            nbins=15,
            labels={'Alter': 'Alter (Jahre)', 'count': 'Anzahl Kunden'},
    )
    st.plotly_chart(fig_age, use_container_width=True)