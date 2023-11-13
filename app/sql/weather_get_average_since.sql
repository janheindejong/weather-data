SELECT 
    min(timestamp) timestamp,
    avg(external_temperature_c) external_temperature_c,
    avg(wind_speed_unmuted_m_s) wind_speed_unmuted_m_s,
    avg(wind_speed_m_s) wind_speed_m_s,
    avg(wind_direction_degrees) wind_direction_degrees,
    avg(radiation_intensity_unmuted_w_m2) radiation_intensity_unmuted_w_m2,
    avg(radiation_intensity_w_m2) radiation_intensity_w_m2,
    avg(standard_radiation_intensity_w_m2) standard_radiation_intensity_w_m2,
    avg(radiation_sum_j_cm2) radiation_sum_j_cm2,
    avg(radiation_from_plant_w_m2) radiation_from_plant_w_m2,
    avg(precipitation) precipitation,
    avg(relative_humidity_perc) relative_humidity_perc,
    avg(moisture_deficit_g_kg) moisture_deficit_g_kg,
    avg(moisture_deficit_g_m3) moisture_deficit_g_m3,
    avg(dew_point_temperature_c) dew_point_temperature_c,
    avg(abs_humidity_g_kg) abs_humidity_g_kg,
    avg(enthalpy_kj_kg) enthalpy_kj_kg,
    avg(enthalpy_kj_m3) enthalpy_kj_m3,
    avg(atmospheric_pressure_hpa) atmospheric_pressure_hpa
FROM 
    weather
WHERE 
    timestamp >= {timestamp_since}
;