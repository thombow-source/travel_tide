import pandas as pd

# 1. Dateipfade definieren
#user_file = 'data/travel_tide_cohort_users_export.csv'
user_file = 'data/traveltide_user_aggregated_eda.csv'
airports_file = 'data/airports-complete.csv'
output_file = 'data/travel_tide_cohort_users_with_states.csv'

# 2. User & vollständige Flughafendaten lokal laden
df_users = pd.read_csv(user_file)
df_airports = pd.read_csv(airports_file)

# 3. Merge über home_airport (IATA)
df_enriched = df_users.merge(
    df_airports[['iata_code', 'state_code']],
    left_on='home_airport',
    right_on='iata_code',
    how='left',
)

# 4. Spalte umbenennen & aufräumen
df_enriched.rename(columns={'state_code': 'home_state'}, inplace=True)
if 'iata_code' in df_enriched.columns:
  df_enriched.drop(columns=['iata_code'], inplace=True)

# 5. Mismatch-Analyse im Terminal ausgeben
matched = df_enriched['home_state'].notna().sum()
mismatched = df_enriched['home_state'].isna().sum()

print("=== LOKALES MAPPING-ERGEBNIS ===")
print(f"Gesamtanzahl User:             {len(df_users):,}")
print(
    f"Gematchte User mit State:      {matched:,}"
    f" ({matched/len(df_users)*100:.2f}%)"
)
print(
    f"Mismatches (ohne US/CA-State): {mismatched:,}"
    f" ({mismatched/len(df_users)*100:.2f}%)\n"
)

# 6. Neue Datei exportieren
df_enriched.to_csv(output_file, index=False)
print(
    f"Erfolg! {len(df_enriched):,} User wurden erfolgreich in '{output_file}'"
    " gespeichert."
)