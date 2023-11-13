SELECT 
    timestamp,
    external_temperature_c,
    wind_speed_unmuted_m_s,
    wind_speed_m_s,
    wind_direction_degrees,
    radiation_intensity_unmuted_w_m2,
    radiation_intensity_w_m2,
    standard_radiation_intensity_w_m2,
    radiation_sum_j_cm2,
    radiation_from_plant_w_m2,
    precipitation,
    relative_humidity_perc,
    moisture_deficit_g_kg,
    moisture_deficit_g_m3,
    dew_point_temperature_c,
    abs_humidity_g_kg,
    enthalpy_kj_kg,
    enthalpy_kj_m3,
    atmospheric_pressure_hpa
FROM 
    weather
ORDER BY 
    timestamp DESC
LIMIT 1;