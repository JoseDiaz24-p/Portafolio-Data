import pandas as pd 

def transformar_clima(datos_crudos):
    
    #-------------------------------------------------------------------
    #Datos Generales 
    #-------------------------------------------------------------------
    latitud = datos_crudos["latitude"]
    longitud = datos_crudos["longitude"]
    zona_horaria = datos_crudos["timezone"]
    
    #-------------------------------------------------------------------
    #Datos Horarios
    #-------------------------------------------------------------------
    
    tiempo = datos_crudos["hourly"]["time"]
    temperatura= datos_crudos["hourly"]["temperature_2m"]
    humedad_relativa =datos_crudos["hourly"]["relative_humidity_2m"]
    temperatura_aparente = datos_crudos["hourly"]["apparent_temperature"]
    precipitacion = datos_crudos["hourly"]["precipitation"]
    codigo_tiempo = datos_crudos["hourly"]["weather_code"]
    presion_nivel_mar = datos_crudos["hourly"]["pressure_msl"]
    presion_superficie = datos_crudos["hourly"]["surface_pressure"]
    nubosidad = datos_crudos["hourly"]["cloud_cover"]
    visibilidad = datos_crudos["hourly"]["visibility"]
    velocidad_viento_10m = datos_crudos["hourly"]["wind_speed_10m"]
    rafaga_viento = datos_crudos["hourly"]["wind_gusts_10m"]
    temperatura_80m = datos_crudos["hourly"]["temperature_80m"]
    probabilidad_precipitacion = datos_crudos["hourly"]["precipitation_probability"]
    
    #-------------------------------------------------------------------
    #CreacionDataFrames
    #-------------------------------------------------------------------

    df = pd.DataFrame({
            "latitud": latitud,
            "longitud": longitud,
            "zona_horaria": zona_horaria,
            "hora_observacion": tiempo,
            "temperatura_2m": temperatura,
            "humedad_relativa": humedad_relativa,
            "temperatura_aparente" : temperatura_aparente,
            "precipitacion" :precipitacion,
            "codigo_tiempo" : codigo_tiempo,
            "presion_nivel_mar" : presion_nivel_mar,
            "presion_superficie" :presion_superficie,
            "nubosidad" : nubosidad,
            "visibilidad" : visibilidad,
            "velocidad_viento_10m" : velocidad_viento_10m,
            "rafaga_viento" : rafaga_viento,
            "temperatura_80m" : temperatura_80m,
            "probabilidad_precipitacion" : probabilidad_precipitacion
            })
    
    
    #-------------------------------------------------------------------
    #Conversion De Tipos
    #-------------------------------------------------------------------
    
    df["hora_observacion"] = pd.to_datetime(
        df["hora_observacion"],
        errors="coerce"
        )
    
    columnas_numericas =[
            "temperatura_2m",
            "humedad_relativa",
            "temperatura_aparente",
            "precipitacion",
            "codigo_tiempo",
            "presion_nivel_mar",
            "presion_superficie",
            "nubosidad",
            "visibilidad",
            "velocidad_viento_10m",
            "rafaga_viento",
            "temperatura_80m",
            "probabilidad_precipitacion"
        ]
        
    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
            )
    
    
    #-------------------------------------------------------------------
    #Eliminar Registros Sin Fecha
    #-------------------------------------------------------------------
    df = df.dropna(
        subset=["hora_observacion"]
        )
    
    #-------------------------------------------------------------------
    #Eliminar Duplicados
    #-------------------------------------------------------------------
    
    df = df.drop_duplicates(
        subset=[
            "latitud",
            "longitud",
            "hora_observacion"
            ]
        )
    return df
    