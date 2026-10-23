WITH cohort_users AS (
    -- 1. Kompromiss-Kohorte: Kunden ab 04.01.2023 mit >= 4 Sessions UND >= 1 Buchung
    SELECT 
        user_id
    FROM sessions
    WHERE session_start >= '2023-01-05'
    GROUP BY user_id
    HAVING COUNT(DISTINCT session_id) >= 4 
       AND COUNT(DISTINCT trip_id) >= 1
),
valid_flights AS (
    -- 2. Nur gültige Flüge filtern
    SELECT *
    FROM flights
    WHERE base_fare_usd > 0 
      AND seats > 0 
      AND (return_time IS NULL OR return_time > departure_time)
),
valid_hotels AS (
    --- 3. Nur gültige Hotelbuchungen filtern
    SELECT *
    FROM hotels
    WHERE nights > 0
      AND hotel_per_room_usd > 0
      AND check_in_time IS NOT NULL 
      AND check_out_time IS NOT NULL
      AND check_out_time > check_in_time
)
SELECT 
    s.user_id,
    -- === DEMOGRAPHISCHE DATEN (aus users) ===
    u.birthdate,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.birthdate)) AS age,
    u.gender,
    u.married,
    u.has_children,
    u.home_airport,
    u.home_country,
    u.home_airport_lat,
    u.home_airport_lon,
    -- === METRIKEN AUS DEN SESSIONS ===
    COUNT(DISTINCT s.session_id) AS total_sessions,
    ROUND(AVG(s.page_clicks), 2) AS avg_page_clicks,
    -- Rabatt-Verhalten
    COUNT(CASE WHEN s.flight_discount = TRUE THEN 1 END) AS flight_discount_sessions,
    COUNT(CASE WHEN s.hotel_discount = TRUE THEN 1 END) AS hotel_discount_sessions,
    ROUND(AVG(s.flight_discount_amount), 4) AS avg_flight_discount_pct,
    ROUND(AVG(s.hotel_discount_amount), 4) AS avg_hotel_discount_pct,
    -- Buchungs- & Storno-Verhalten
    COUNT(DISTINCT s.trip_id) AS total_trips_booked,
    COUNT(CASE WHEN s.cancellation = TRUE THEN 1 END) AS total_cancellations,
    ROUND(100.0 * COUNT(CASE WHEN s.cancellation = TRUE THEN 1 END) / NULLIF(COUNT(DISTINCT s.trip_id), 0), 2) AS cancellation_rate_pct,
    -- === METRIKEN AUS DEN FLÜGEN ===
    COUNT(DISTINCT f.trip_id) AS total_flights_booked,
    SUM(f.seats) AS total_seats_booked,
    SUM(f.checked_bags) AS total_checked_bags,
    ROUND(AVG(f.checked_bags), 2) AS avg_checked_bags_per_flight,
    SUM(f.base_fare_usd) AS total_flight_spend_usd,
    ROUND(AVG(f.base_fare_usd), 2) AS avg_flight_price_usd,
    -- === METRIKEN AUS DEN HOTELS ===
    COUNT(DISTINCT h.trip_id) AS total_hotels_booked,
    SUM(h.nights) AS total_hotel_nights,
    ROUND(AVG(h.nights), 2) AS avg_hotel_nights,
    SUM(h.hotel_per_room_usd * h.nights) AS total_hotel_spend_usd,
    ROUND(AVG(h.hotel_per_room_usd), 2) AS avg_room_price_per_night_usd,
    -- === KOMBI-METRIK (Flug + Hotel) ===
    COUNT(DISTINCT CASE WHEN f.trip_id IS NOT NULL AND h.trip_id IS NOT NULL THEN s.trip_id END) AS combined_flight_and_hotel_trips
FROM sessions s
JOIN cohort_users cu ON s.user_id = cu.user_id
JOIN users u        ON s.user_id = u.user_id
LEFT JOIN valid_flights f ON s.trip_id = f.trip_id
LEFT JOIN valid_hotels h  ON s.trip_id = h.trip_id
WHERE s.session_start >= '2023-01-04'
  -- Qualitätsfilter: Verwirft Sessions mit ungültigen/Fehlerhaften Trips
  AND (s.trip_id IS NULL OR f.trip_id IS NOT NULL OR h.trip_id IS NOT NULL)
GROUP BY 
    s.user_id,
    u.birthdate,
    u.gender,
    u.married,
    u.has_children,
    u.home_airport,
    u.home_country,
    u.home_airport_lat,
    u.home_airport_lon;









