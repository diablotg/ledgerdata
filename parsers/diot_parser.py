import pandas as pd


class DiotParser:

    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):

        # Leer únicamente columnas necesarias
        df = pd.read_excel(
            self.file_path, header=None, skiprows=17, usecols="J,BB,EL,EX"
        )

        # Renombrar columnas
        df.columns = ["CEGAP", "DIOT_IVA", "DIOT_IEPS", "DIOT_227"]

        # Limpiar CEGAP
        df["CEGAP"] = pd.to_numeric(df["CEGAP"], errors="coerce")

        # Eliminar CEGAP vacío
        df = df[df["CEGAP"].notna()]

        df["CEGAP"] = df["CEGAP"].astype(int).astype(str).str.strip()

        # Convertir importes
        importe_cols = ["DIOT_IVA", "DIOT_IEPS", "DIOT_227"]

        for col in importe_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Agrupar por CEGAP
        df_grouped = df.groupby("CEGAP", as_index=False).sum()

        return df_grouped
