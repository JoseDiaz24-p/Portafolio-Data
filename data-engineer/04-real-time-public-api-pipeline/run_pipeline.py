from src.extract import extraer_clima
from src.transform import transformar_clima
from src.load import cargar_raw,cargar_limpios

def main():
    #santiago
    latitud = -33.4489
    longitud = -70.6693
    print("="*60)
    print("Canalizacion De Datos Meteorologicos")
    print("="*60)

    #--------------------------------------------------
    #1.Extraccion
    #--------------------------------------------------

    print("\n[1/4] Extrayendo Datos...")
    
    datos_crudos = extraer_clima(latitud, longitud)
    
    print("Datos Extraidos Correctamente.")
    
    #--------------------------------------------------
    #2.Carga Datos Sin Procesar
    #--------------------------------------------------

    print("\n[2/4] Guardando Datos Sin Procesar...")
    cargar_raw(datos_crudos)
    
    print("Datos Sin Procesar Guardados.")
    
    #--------------------------------------------------
    #3.TRansformar
    #--------------------------------------------------

    print("\n[3/4] Transformando Datos...")
    
    df = transformar_clima(datos_crudos)
    
    print(f"Registros Limpios: {len(df)}")
    
    
    #--------------------------------------------------
    #4.Cargar Datos Limpios
    #--------------------------------------------------

    print("\n[4/4] Cargando Datos limpios...")
    
    cargar_limpios(df)
    print("Datos Limpios Guardados.")
    print("\nPipeline Terminado")
    
    
    
    
if __name__ == "__main__":
    main()