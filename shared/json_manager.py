import json
import os


class GestorJSON:
    """Maneja la lectura y escritura de archivos JSON de forma segura."""

    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        if not os.path.exists(self.ruta_archivo):
            self.guardar([])

    def leer(self):
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def guardar(self, datos):
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False