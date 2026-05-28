import os
import uuid
import subprocess

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFrame,
    QHBoxLayout,
)

from parsers.diot_parser import DiotParser
from parsers.contabilidad_parser import ContabilidadParser
from core.conciliador import Conciliador


class DropZone(QFrame):

    def __init__(self, nombre, parent_window):

        super().__init__()

        self.nombre = nombre
        self.parent_window = parent_window

        self.setAcceptDrops(True)

        self.setMinimumHeight(100)

        self.setFrameShape(QFrame.Box)

        self.label = QLabel(f"{nombre}\n\nArrastra archivo aquí")

        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()

        layout.addWidget(self.label)

        self.setLayout(layout)

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        archivo = event.mimeData().urls()[0].toLocalFile()

        self.parent_window.archivos[self.nombre] = archivo

        self.label.setText(f"{self.nombre}\n\n" f"{os.path.basename(archivo)}")


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("DIOT Conciliador")

        self.resize(700, 600)

        self.archivos = {
            "DIOT": None,
            "IVA": None,
            "IEPS": None,
            "227": None,
        }

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()

        titulo = QLabel("Carga los archivos")

        titulo.setAlignment(Qt.AlignCenter)

        layout.addWidget(titulo)

        # =========================
        # ZONAS
        # =========================

        self.drop_diot = DropZone("DIOT", self)

        self.drop_iva = DropZone("IVA", self)

        self.drop_ieps = DropZone("IEPS", self)

        self.drop_227 = DropZone("227", self)

        layout.addWidget(self.drop_diot)
        layout.addWidget(self.drop_iva)
        layout.addWidget(self.drop_ieps)
        layout.addWidget(self.drop_227)

        # =========================
        # BOTONES
        # =========================

        botones_layout = QHBoxLayout()

        boton_buscar = QPushButton("Buscar archivo")

        boton_buscar.clicked.connect(self.buscar_archivo)

        botones_layout.addWidget(boton_buscar)

        boton_conciliar = QPushButton("Conciliar")

        boton_conciliar.clicked.connect(self.conciliar)

        botones_layout.addWidget(boton_conciliar)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

    # =========================
    # BUSCAR ARCHIVO
    # =========================

    def buscar_archivo(self):

        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", "Excel (*.xlsx)"
        )

        if not archivo:
            return

        nombre = os.path.basename(archivo).lower()

        if "diot" in nombre:

            self.archivos["DIOT"] = archivo

            self.drop_diot.label.setText(f"DIOT\n\n" f"{os.path.basename(archivo)}")

        elif "iva" in nombre:

            self.archivos["IVA"] = archivo

            self.drop_iva.label.setText(f"IVA\n\n" f"{os.path.basename(archivo)}")

        elif "ieps" in nombre:

            self.archivos["IEPS"] = archivo

            self.drop_ieps.label.setText(f"IEPS\n\n" f"{os.path.basename(archivo)}")

        elif "227" in nombre:

            self.archivos["227"] = archivo

            self.drop_227.label.setText(f"227\n\n" f"{os.path.basename(archivo)}")

        else:

            QMessageBox.warning(
                self, "Archivo inválido", "No se pudo detectar el tipo de archivo"
            )

    # =========================
    # VALIDAR
    # =========================

    def validar_archivos(self):

        faltantes = []

        for tipo, ruta in self.archivos.items():

            if not ruta:
                faltantes.append(tipo)

        if faltantes:

            QMessageBox.warning(
                self, "Faltan archivos", "Faltan:\n\n" + "\n".join(faltantes)
            )

            return False

        return True

    # =========================
    # CONCILIAR
    # =========================

    def conciliar(self):

        if not self.validar_archivos():
            return

        try:

            diot_df = DiotParser(self.archivos["DIOT"]).parse()

            iva_df = ContabilidadParser(self.archivos["IVA"]).parse()

            ieps_df = ContabilidadParser(self.archivos["IEPS"]).parse()

            df_227 = ContabilidadParser(self.archivos["227"]).parse()

            conciliador = Conciliador(diot_df, iva_df, ieps_df, df_227)

            resultado = conciliador.conciliar()

            # =========================
            # NOMBRE ARCHIVO
            # =========================

            nombre_archivo = f"resultado_" f"{uuid.uuid4().hex[:8]}.xlsx"

            home = os.path.expanduser("~")

            # Windows
            if os.name == "nt":

                escritorio = os.path.join(home, "Desktop")

            # Linux
            else:

                escritorio = os.path.join(home, "Escritorio")

            # Fallback
            if not os.path.exists(escritorio):

                escritorio = home

            ruta_salida = os.path.join(escritorio, nombre_archivo)

            # =========================
            # EXPORTAR
            # =========================

            resultado.to_excel(ruta_salida, index=False)

            # =========================
            # ABRIR ARCHIVO
            # =========================

            if os.name == "nt":

                os.startfile(ruta_salida)

            else:

                subprocess.Popen(["xdg-open", ruta_salida])

            QMessageBox.information(
                self, "Proceso terminado", f"Archivo generado:\n\n" f"{ruta_salida}"
            )

        except Exception as e:

            QMessageBox.critical(self, "Error", str(e))
