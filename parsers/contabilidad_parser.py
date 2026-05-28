import pandas as pd


class ContabilidadParser:

    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):

        # Leer únicamente columnas necesarias
        df = pd.read_excel(self.file_path, header=None, skiprows=3, usecols="B,C,J,O")

        # Renombrar columnas
        df.columns = ["POLIZA", "FECHA", "IMPORTE", "CEGAP"]

        # Limpiar CEGAP
        df["CEGAP"] = pd.to_numeric(df["CEGAP"], errors="coerce")

        # Eliminar CEGAP vacío
        df = df[df["CEGAP"].notna()]

        df["CEGAP"] = df["CEGAP"].astype(int).astype(str).str.strip()

        # NORMALIZAR IMPORTE
        df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce").fillna(0)

        df["POLIZA"] = df["POLIZA"].astype(str).str.strip()

        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce").dt.strftime(
            "%d/%m/%Y"
        )

        return df
