import pandas as pd


class FintechTransformadorDatos:

    COLUMNAS_NUMERICAS = [
        "Total_Transactions",
        "Avg_Transaction_Value",
        "Max_Transaction_Value",
        "Min_Transaction_Value",
        "Total_Spent",
        "Active_Days"
    ]

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def limpieza_datos(self) -> "FintechTransformadorDatos":
        """Valida y limpia los datos antes de aplicar las métricas de negocio."""

        columnas_requeridas = [
            "Customer_ID",
            "Age",
            "Location",
            "Income_Level",
            "Total_Transactions",
            "Avg_Transaction_Value",
            "Max_Transaction_Value",
            "Min_Transaction_Value",
            "Total_Spent",
            "Active_Days"
        ]

        columnas_faltantes = [
            columna
            for columna in columnas_requeridas
            if columna not in self.df.columns
        ]

        if columnas_faltantes:
            raise ValueError(
                f"Faltan columnas requeridas: {columnas_faltantes}"
            )

        registros_iniciales = len(self.df)

        # Convertir columnas numéricas y detectar valores inválidos.
        for columna in self.COLUMNAS_NUMERICAS:
            self.df[columna] = pd.to_numeric(
                self.df[columna],
                errors="coerce"
            )

        self.df["Age"] = pd.to_numeric(
            self.df["Age"],
            errors="coerce"
        )

        # Eliminar registros con datos faltantes.
        self.df.dropna(inplace=True)

        # Los días activos deben ser mayores que cero
        # para poder calcular el gasto diario.
        self.df = self.df[self.df["Active_Days"] > 0]

        # Evitar identificadores vacíos.
        self.df = self.df[
            self.df["Customer_ID"].astype(str).str.strip() != ""
        ]

        # Mantener un único registro por cliente.
        self.df.drop_duplicates(
            subset=["Customer_ID"],
            keep="first",
            inplace=True
        )

        registros_finales = len(self.df)
        registros_eliminados = registros_iniciales - registros_finales

        print(
            f"-> Registros eliminados durante la limpieza: "
            f"{registros_eliminados:,}"
        )

        return self

    def agregar_metricas_negocio(self) -> "FintechTransformadorDatos":
        """Genera métricas y segmentos para análisis de clientes."""

        # Tasa de gasto diario.
        self.df["Daily_Spend_Rate"] = (
            self.df["Total_Spent"]
            / self.df["Active_Days"]
        ).round(2)

        # Diferencia entre el ticket máximo y mínimo.
        self.df["Ticket_Spread"] = (
            self.df["Max_Transaction_Value"]
            - self.df["Min_Transaction_Value"]
        ).round(2)

        # Percentiles utilizados como umbral de segmentación.
        p75_gastado = self.df["Total_Spent"].quantile(0.75)
        p75_activo = self.df["Active_Days"].quantile(0.75)

        def asignar_segmento(row):
            if (
                row["Total_Spent"] >= p75_gastado
                and row["Active_Days"] >= p75_activo
            ):
                return "VIP_ALTO_CONSUMO"

            elif (
                row["Total_Spent"] >= p75_gastado
                and row["Active_Days"] < p75_activo
            ):
                return "COMPRADOR_DE_BAJA_FRECUENCIA"

            elif row["Active_Days"] >= p75_activo:
                return "USUARIO_REGULAR"

            return "USUARIO_ESTANDAR"

        self.df["Customer_Segment"] = self.df.apply(
            asignar_segmento,
            axis=1
        )

        return self

    def datos_limpios(self) -> pd.DataFrame:
        """Devuelve el DataFrame procesado."""

        return self.df