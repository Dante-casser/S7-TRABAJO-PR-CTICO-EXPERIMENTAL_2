from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views_academico import (
    EstudianteController, DocenteController, MateriaController, MatriculaController
)


# =====================================================================
# POLIMORFISMO: un solo menú sirve para cualquier controlador académico
# =====================================================================
class MenuCRUD:
    """No sabe si maneja estudiantes o materias: solo habla con la interfaz CrudBase."""

    def __init__(self, controlador, titulo):
        self._controlador = controlador
        self._titulo = titulo
        self._activo = True
        self._opciones = {
            "1": (f"Crear {controlador.NOMBRE}", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "0": ("Volver", self.volver),
        }

    # ---------- utilidades estaticas ----------
    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        try:
            return int(input(etiqueta))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ---------- operaciones ----------
    def pedir_datos(self):
        datos = {}
        for campo in self._controlador.MODELO.CAMPOS:
            datos[campo] = input(f"{campo.replace('_', ' ').capitalize()}: ")
        return datos

    def crear(self):
        imprimir_titulo(f"CREAR {self._controlador.NOMBRE.upper()}")
        self.mostrar_resultado(*self._controlador.crear(self.pedir_datos()))
        self.pausa()

    def listar(self):
        imprimir_titulo(self._titulo.upper())
        objetos = self._controlador.listar()
        if not objetos:
            imprimir_info("No hay registros todavia.")
        else:
            for objeto in objetos:
                print(f"  {objeto}")
            imprimir_info(f"Total: {len(objetos)}")
        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self._controlador.NOMBRE.upper()}")
        termino = input("Termino: ")
        encontrados = self._controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Sin coincidencias para '{termino}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"VER {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {str(clave).capitalize():<14}: {valor}")
        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
            return self.pausa()

        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in self._controlador.MODELO.CAMPOS:
            actual = getattr(objeto, campo, "")
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo:
                cambios[campo] = nuevo

        self.mostrar_resultado(*self._controlador.actualizar(id_registro, cambios))
        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self._controlador.obtener(id_registro) if id_registro else None
        if objeto is None:
            imprimir_error("No encontrado")
            return self.pausa()

        imprimir_info(f"Se eliminara: {objeto.etiqueta()}")
        if confirmar("Confirma?"):
            self.mostrar_resultado(*self._controlador.eliminar(id_registro))
        else:
            imprimir_info("Operacion cancelada")
        self.pausa()

    def volver(self):
        self._activo = False

    # ---------- bucle ----------
    def mostrar_menu(self):
        imprimir_titulo(self._titulo)
        for tecla, (texto, _metodo) in self._opciones.items():
            print(f"  {tecla}. {texto}")
        print()

    def ejecutar(self):
        self._activo = True
        while self._activo:
            self.mostrar_menu()
            tecla = input("Opcion: ").strip()
            if tecla not in self._opciones:
                imprimir_error("Opcion no valida")
                self.pausa()
                continue
            self._opciones[tecla][1]()


# =====================================================================
# HERENCIA + SOBRESCRITURA: el menu de matriculas es un MenuCRUD con extras
# =====================================================================
class MenuMatriculas(MenuCRUD):

    def __init__(self, controlador):
        super().__init__(controlador, "MATRICULAS")
        self._opciones["1"] = ("Registrar matricula", self.crear)
        self._opciones["7"] = ("Agregar nota", self.agregar_nota)
        self._opciones["8"] = ("Ver boletin", self.ver_boletin)

    def crear(self):
        """Sobrescribe: una matricula necesita estudiante, materia y periodo."""
        imprimir_titulo("REGISTRAR MATRICULA")
        estudiante_id = self.pedir_entero("Id del estudiante: ")
        if estudiante_id is None:
            imprimir_error("El id debe ser un numero")
            return self.pausa()

        imprimir_info("Materias disponibles:")
        for materia in self._controlador.materias.listar():
            print(f"  {materia}")

        materia_id = self.pedir_entero("Id de la materia: ")
        if materia_id is None:
            imprimir_error("El id debe ser un numero")
            return self.pausa()

        periodo = input("Periodo (ej. 2026-1): ").strip() or "2026-1"

        self.mostrar_resultado(
            *self._controlador.crear({
                "estudiante_id": estudiante_id,
                "materia_id": materia_id,
                "periodo": periodo
            })
        )
        self.pausa()

    def agregar_nota(self):
        imprimir_titulo("AGREGAR NOTA A MATRICULA")
        matricula_id = self.pedir_entero("Id de la matricula: ")
        if matricula_id is None:
            imprimir_error("El id debe ser un numero")
            return self.pausa()

        print("Tipos de nota permitidos: deber, leccion, examen")
        tipo = input("Tipo de nota: ").strip().lower()

        try:
            valor = float(input("Valor de la nota (0 a 20): "))
        except ValueError:
            imprimir_error("El valor debe ser un numero valido")
            return self.pausa()

        peso_input = input("Peso de la nota [por defecto 1]: ").strip()
        peso = float(peso_input) if peso_input else 1.0

        exito, mensaje = self._controlador.agregar_nota(matricula_id, tipo, valor, peso)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_boletin(self):
        imprimir_titulo("BOLETIN DE ESTUDIANTE")
        estudiante_id = self.pedir_entero("Id del estudiante: ")
        texto = self._controlador.boletin(estudiante_id) if estudiante_id else None
        if texto is None:
            imprimir_error("No se encontro al estudiante o no tiene registros")
        else:
            print(texto)
        self.pausa()


# =====================================================================
class MenuPrincipal:

    def __init__(self):
        estudiantes = EstudianteController()
        docentes = DocenteController()
        materias = MateriaController(docentes)
        matriculas = MatriculaController(estudiantes, materias)

        self._activo = True
        self._menus = {
            "1": MenuCRUD(estudiantes, "ESTUDIANTES"),
            "2": MenuCRUD(docentes, "DOCENTES"),
            "3": MenuCRUD(materias, "MATERIAS"),
            "4": MenuMatriculas(matriculas),
        }

    def ejecutar(self):
        while self._activo:
            imprimir_titulo("SISTEMA ACADEMICO")
            print("  1. Estudiantes")
            print("  2. Docentes")
            print("  3. Materias")
            print("  4. Matriculas y Notas")
            print("  0. Salir\n")
            tecla = input("Opcion: ").strip()

            if tecla == "0":
                imprimir_info("Hasta luego!")
                self._activo = False
            elif tecla in self._menus:
                self._menus[tecla].ejecutar()
            else:
                imprimir_error("Opcion no valida")
                MenuCRUD.pausa()


if __name__ == "__main__":
    try:
        MenuPrincipal().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")