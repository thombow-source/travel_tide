import pandas as pd

# 1. Pfade definieren
local_airports = 'data/airports.csv'
url_regions = 'https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv'
output_complete = 'data/airports-complete.csv'

# 2. Complete/OurAirports Datensatz mit ISO-Regionen laden
try:
  df_our = pd.read_csv(url_regions)
  print("OurAirports-Referenzliste online geladen.")
except Exception:
  df_our = pd.read_csv(local_airports)

# 3. Filtern auf US & CA
df_us_ca = df_our[df_our['iso_country'].isin(['US', 'CA'])].copy()

# 4. State Code abspalten (z. B. 'US-CA' -> 'CA', 'CA-ON' -> 'ON')
df_us_ca['state_code'] = df_us_ca['iso_region'].str.split('-').str[1]

# 5. Nur relevante Spalten für das Mapping behalten
df_complete = df_us_ca[[
    'iata_code',
    'name',
    'municipality',
    'iso_country',
    'state_code',
    'latitude_deg',
    'longitude_deg',
]]

# Datentyp-Aufräumung
df_complete = df_complete.dropna(subset=['iata_code']).drop_duplicates(
    subset=['iata_code']
)

# 6. Als dauerhafte vollständige CSV abspeichern
df_complete.to_csv(output_complete, index=False)
print(
    f"Erfolg! {len(df_complete):,} US/CA-Flughäfen in '{output_complete}'"
    " gespeichert."
)