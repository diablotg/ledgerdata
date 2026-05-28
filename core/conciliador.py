import pandas as pd


class Conciliador:

    def __init__(self, diot_df, iva_df, ieps_df, df_227):

        self.diot_df = diot_df
        self.iva_df = iva_df
        self.ieps_df = ieps_df
        self.df_227 = df_227

    def agrupar_contabilidad(self, df, nombre):

        grouped = df.groupby("CEGAP", as_index=False).agg(
            {
                "IMPORTE": "sum",
                "POLIZA": lambda x: ", ".join(x.astype(str).unique()[:10]),
                "FECHA": lambda x: ", ".join(x.astype(str).unique()[:10]),
            }
        )

        grouped = grouped.rename(
            columns={
                "IMPORTE": f"IMPORTE_{nombre}",
                "POLIZA": f"POLIZA_{nombre}",
                "FECHA": f"FECHA_{nombre}",
            }
        )

        return grouped

    def generar_estado(self, row, tipo):

        diot = round(row[f"DIOT_{tipo}"], 2)

        importe = round(row[f"IMPORTE_{tipo}"], 2)

        poliza = row.get(f"POLIZA_{tipo}", "")

        fecha = row.get(f"FECHA_{tipo}", "")

        # Limpiar NaN
        if pd.isna(poliza):
            poliza = ""

        if pd.isna(fecha):
            fecha = ""

        # OK
        if diot == importe:
            return "OK"

        # Existe en DIOT
        # pero no en contabilidad
        if diot != 0 and importe == 0:

            return "No registrado " "en contabilidad"

        # Existe en contabilidad
        # pero no en DIOT
        if diot == 0 and importe != 0:

            return (
                f"No registrado en DIOT | "
                f"Poliza(s): {poliza} | "
                f"Fecha(s): {fecha}"
            )

        # Diferencia normal
        return f"Diferencia {tipo} | " f"Poliza(s): {poliza} | " f"Fecha(s): {fecha}"

    def conciliar(self):

        print("Agrupando IVA...")

        iva_grouped = self.agrupar_contabilidad(self.iva_df, "IVA")

        print("Agrupando IEPS...")

        ieps_grouped = self.agrupar_contabilidad(self.ieps_df, "IEPS")

        print("Agrupando 227...")

        df_227_grouped = self.agrupar_contabilidad(self.df_227, "227")

        print("Realizando merges...")

        # =========================
        # MERGE PRINCIPAL
        # =========================

        result = self.diot_df.copy()

        result = pd.merge(result, iva_grouped, on="CEGAP", how="outer")

        result = pd.merge(result, ieps_grouped, on="CEGAP", how="outer")

        result = pd.merge(result, df_227_grouped, on="CEGAP", how="outer")

        tipos = ["IVA", "IEPS", "227"]

        # =========================
        # VALIDAR COLUMNAS
        # =========================

        for tipo in tipos:

            if f"IMPORTE_{tipo}" not in result.columns:
                result[f"IMPORTE_{tipo}"] = 0

            if f"POLIZA_{tipo}" not in result.columns:
                result[f"POLIZA_{tipo}"] = ""

            if f"FECHA_{tipo}" not in result.columns:
                result[f"FECHA_{tipo}"] = ""

        print("Calculando diferencias...")

        # =========================
        # DIFERENCIAS
        # =========================

        for tipo in tipos:

            result[f"DIOT_{tipo}"] = result[f"DIOT_{tipo}"].fillna(0).round(2)

            result[f"IMPORTE_{tipo}"] = result[f"IMPORTE_{tipo}"].fillna(0).round(2)

            result[f"DIFERENCIA_{tipo}"] = (
                result[f"DIOT_{tipo}"] - result[f"IMPORTE_{tipo}"]
            ).round(2)

        print("Generando estados...")

        # =========================
        # ESTADOS
        # =========================

        for tipo in tipos:

            result[f"ESTADO_{tipo}"] = result.apply(
                lambda row: self.generar_estado(row, tipo), axis=1
            )

        # =========================
        # ORDEN COLUMNAS
        # =========================

        result = result[
            [
                "CEGAP",
                "DIOT_IVA",
                "DIOT_IEPS",
                "DIOT_227",
                "POLIZA_IVA",
                "IMPORTE_IVA",
                "DIFERENCIA_IVA",
                "ESTADO_IVA",
                "POLIZA_IEPS",
                "IMPORTE_IEPS",
                "DIFERENCIA_IEPS",
                "ESTADO_IEPS",
                "POLIZA_227",
                "IMPORTE_227",
                "DIFERENCIA_227",
                "ESTADO_227",
            ]
        ]

        print("Generando fila TOTAL...")

        # =========================
        # TOTAL DIFERENCIAS
        # =========================

        total_row = {
            "CEGAP": "TOTAL",
            "DIFERENCIA_IVA": result["DIFERENCIA_IVA"].sum(),
            "DIFERENCIA_IEPS": result["DIFERENCIA_IEPS"].sum(),
            "DIFERENCIA_227": result["DIFERENCIA_227"].sum(),
        }

        result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

        return result
