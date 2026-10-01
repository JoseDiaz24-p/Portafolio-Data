import pandas as pd


def validar_datos(df: pd.DataFrame):
    columnas_requeridas = [
            "VendorID",
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "passenger_count",
            "trip_distance",
            "RatecodeID",
            "store_and_fwd_flag",
            "PULocationID" ,
            "DOLocationID",
            "payment_type",
            "fare_amount",
            "extra",
            "mta_tax",
            "tip_amount",
            "tolls_amount" ,
            "improvement_surcharge",
            "total_amount",
            "congestion_surcharge",
            "Airport_fee",
            "cbd_congestion_fee"
        ]
    
    columnas_faltantes =[
            columna
            for columna in columnas_requeridas
            if columna not in df.columns
        ]
    
    if columnas_faltantes:
            raise ValueError(
                f"Faltan Columnas Requeridas: {columnas_faltantes}"
            )
    return columnas_requeridas
 
    

def limpiar_datos (df: pd.DataFrame, columnas_requeridas : list ) -> pd.DataFrame:
    columnas_fecha = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime"
        ]
    
    columnas_numericas = ["passenger_count",
        "RatecodeID","PULocationID","DOLocationID","payment_type",
        "trip_distance","fare_amount","extra","mta_tax",
                         "tip_amount","tolls_amount","improvement_surcharge",
                         "total_amount","congestion_surcharge","Airport_fee","cbd_congestion_fee"
        ]
    
    for columna in columnas_fecha:
            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )
    
    for columna in columnas_numericas:
            df[columna] = pd.to_numeric (
                df[columna],
                errors="coerce"
            )  

    df = df.drop_duplicates()
    df = df.dropna(
            subset=columnas_requeridas
        )

    return df


def enriquecer_datos(df: pd.DataFrame ) -> pd.DataFrame:
    df["Vendor_Name"] = df["VendorID"].map({
            1: "Creative Mobile Technologies, LLC",
            2: "Curb Mobility, LLC",
            6: "Myle Technologies Inc",
            7: "Helix"
        })
            
    
    df["Ratecode_Description"] = df["RatecodeID"].map({
            1 : "Standard rate",
            2 : "JF",
            3 : "Newark",
            4 : "Nassau or Westchester",
            5 : "Negotiated fare",
            6 : "Group ride",
            99 : "Null/unknown"
        })
    
    df["StoreAndFwd_Description"] = df["store_and_fwd_flag"].map({
           "Y": "store and forward ",
            "N": "not a store and forward trip"    
        })
    
    df["PaymentType_Description"] = df["payment_type"].map({
            0 : "Flex Fare trip",
            1 : "Credit card",
            2 : "Cash",
            3 : "No charge",
            4 : "Dispute",
            5 : "Unknown",
            6 : "Voided trip"
        })
    

    
    return df

def transformar_datos(df: pd.DataFrame ) -> pd.DataFrame:  

    validarDatos = validar_datos(df)
    limpiarDatos = limpiar_datos(df,validarDatos)
    enriquecerDatos = enriquecer_datos(limpiarDatos)

    return enriquecerDatos