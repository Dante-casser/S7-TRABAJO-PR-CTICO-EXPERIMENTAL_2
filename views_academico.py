from models_academico import Estudiante, Docente, Materia, Matricula
from views import CrudBase


class EstudianteController(CrudBase):
    """LISTO como ejemplo: cópialo y guíate con él para los demás."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    NOMBRE = "estudiante"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "carnet" in datos and str(datos["carnet"]).strip():
            carnet = str(datos["carnet"]).strip().upper()
            usados = {r["carnet"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if carnet in usados:
                return f"El carnet {carnet} ya está registrado"
        return None


class DocenteController(CrudBase):
    MODELO = Docente
    ARCHIVO = "data/docentes.json"
    NOMBRE = "docente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "especialidad")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "email" in datos and str(datos["email"]).strip():
            email = str(datos["email"]).strip().lower()
            usados = {r["email"].lower() for r in self.registros()
                      if r["id"] != id_actual}
            if email in usados:
                return "Ese email ya está registrado"
        return None


class MateriaController(CrudBase):
    MODELO = Materia
    ARCHIVO = "data/materias.json"
    NOMBRE = "materia"
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, docentes=None):
        super().__init__()
        self.docentes = docentes or DocenteController()

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "codigo" in datos and str(datos["codigo"]).strip():
            codigo = str(datos["codigo"]).strip().upper()
            usados = {r["codigo"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if codigo in usados:
                return f"Ya existe una materia con el código {codigo}"

        docente_id = datos.get("docente_id")
        if docente_id not in (None, "", "0"):
            try:
                doc_id = int(docente_id)
            except (TypeError, ValueError):
                return "docente_id inválido"
            if not self.docentes.existe(doc_id):
                return f"No existe un docente con id {doc_id}"

        return None

    def asignar_docente(self, materia_id, docente_id):
        if not self.existe(materia_id):
            return False, f"No existe materia con id {materia_id}"
        if docente_id not in (None, "", 0, "0"):
            try:
                doc_id = int(docente_id)
            except (TypeError, ValueError):
                return False, "docente_id inválido"
            if not self.docentes.existe(doc_id):
                return False, f"No existe un docente con id {doc_id}"
        return self.actualizar(materia_id, {"docente_id": docente_id})

    def materias_de_docente(self, docente_id):
        return [m for m in self.listar() if m.docente_id == docente_id]


class MatriculaController(CrudBase):
    """El equivalente académico del VentaController."""

    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matrícula"
    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None):
        super().__init__()
        self.estudiantes = estudiantes or EstudianteController()
        self.materias = materias or MateriaController()

    def validar(self, datos, id_actual=None):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números"

        if not self.estudiantes.existe(estudiante_id):
            return f"No existe un estudiante con id {estudiante_id}"

        if not self.materias.existe(materia_id):
            return f"No existe una materia con id {materia_id}"

        periodo = str(datos.get("periodo", "2026-1")).strip() or "2026-1"
        
        for reg in self.registros():
            if reg["id"] != id_actual:
                if (int(reg.get("estudiante_id", 0)) == estudiante_id and 
                    int(reg.get("materia_id", 0)) == materia_id and 
                    str(reg.get("periodo", "")).strip() == periodo):
                    return "El estudiante ya está matriculado en esta materia para el mismo periodo"

        return None

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        matricula = self.obtener(matricula_id)
        if matricula is None:
            return False, f"No existe matrícula con id {matricula_id}"
        try:
            matricula.agregar_nota(tipo, valor, peso)
        except ValueError as excepcion:
            return False, str(excepcion)
        
        registros = self.registros()
        for indice, registro in enumerate(registros):
            if registro["id"] == matricula_id:
                registros[indice] = matricula.a_diccionario()
                break
        self._gestor.guardar(registros)
        return True, f"Nota agregada correctamente. Nuevo promedio: {matricula.promedio}"

    def boletin(self, estudiante_id):
        estudiante = self.estudiantes.obtener(estudiante_id)
        if not estudiante:
            return None
        
        matriculas_est = [m for m in self.listar() if m.estudiante_id == estudiante_id]
        if not matriculas_est:
            return f"El estudiante {estudiante.nombre_completo} no tiene matrículas registradas."

        lineas = [
            f"BOLETÍN DE CALIFICACIONES",
            f"Estudiante: {estudiante.nombre_completo} (Carnet: {estudiante.carnet})",
            "-" * 50,
        ]

        promedios_totales = []
        for mat in matriculas_est:
            materia_obj = self.materias.obtener(mat.materia_id)
            nombre_mat = materia_obj.nombre if materia_obj else f"Materia ID {mat.materia_id}"
            
            lineas.append(f"Materia: {nombre_mat} [Periodo: {mat.periodo}]")
            lineas.append(f"Estado: {mat.estado} - Promedio: {mat.promedio}")
            lineas.append("Notas:")
            if mat.notas:
                for nota in mat.notas:
                    lineas.append(f"  - {nota.tipo} (peso {nota.peso}): {nota.valor}")
            else:
                lineas.append("  - Sin notas registradas")
            lineas.append("-" * 50)
            promedios_totales.append(mat.promedio)

        promedio_general = round(sum(promedios_totales) / len(promedios_totales), 2) if promedios_totales else 0
        lineas.append(f"PROMEDIO GENERAL ACUMULADO: {promedio_general}")
        
        return "\n".join(lineas)
