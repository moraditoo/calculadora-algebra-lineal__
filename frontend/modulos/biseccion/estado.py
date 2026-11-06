# frontend/modulos/biseccion/estado.py
# Todo lo que el usuario escribe y calcula en el metodo de biseccion.
import math
from dataclasses import dataclass, field

from backend.metodos_numericos.analizador import ErrorFuncion, Funcion
from .ejemplos import EJEMPLOS

CRITERIOS = [
    {"valor": "absoluto", "titulo": "Ea < E", "detalle": "Error absoluto: |c nuevo − c anterior|"},
    {"valor": "relativo", "titulo": "Er < E", "detalle": "Error relativo: |(c nuevo − c anterior) / c nuevo|"},
    {"valor": "porcentual", "titulo": "Er % < E", "detalle": "Error relativo porcentual (· 100 %)"},
    {"valor": "funcion", "titulo": "|f(c)| < E", "detalle": "Valor de la función en el punto c"},
    {"valor": "intervalo", "titulo": "(b − a) < E", "detalle": "Longitud del intervalo que queda"},
]

NOMBRE_ERROR = {"absoluto": "Ea", "relativo": "Er", "porcentual": "Er %", "funcion": "|f(c)|", "intervalo": "b − a"}

PASOS = [
    (1, "Función"),
    (2, "Gráfica e intervalos"),
    (3, "Parámetros"),
    (4, "Iteraciones"),
    (5, "Conclusión"),
    (6, "Algoritmo"),
]


@dataclass
class Estado:
    # Paso 1: la funcion se guarda en LaTeX (editor matematico) o en texto.
    # Al abrir se carga el ejemplo de clase (EJEMPLOS[0]) con sus mismos datos.
    funcion: str = EJEMPLOS[0]["latex"]
    es_latex: bool = True
    formula: str | None = None
    error_funcion: str | None = None

    # Paso 2: grafica e intervalos
    x_min: str = EJEMPLOS[0]["x_min"]
    x_max: str = EJEMPLOS[0]["x_max"]
    subintervalos: str = EJEMPLOS[0]["subintervalos"]
    tabulacion: dict | None = None
    grafica_general: str | None = None
    intervalo_activo: int | None = None
    # Si la funcion cambio, al graficar se busca solo un rango donde se vean sus raices
    rango_automatico: bool = False
    aviso_rango: str | None = None
    vista_plano: tuple | None = None     # (x min, x max) que se ve en la grafica interactiva
    # Intervalo que se elige al graficar si aparece en la tabulacion (el de un ejemplo)
    intervalo_preferido: tuple | None = (EJEMPLOS[0]["a"], EJEMPLOS[0]["b"])

    # Paso 3: parametros
    a: str = ""
    b: str = ""
    tolerancia: str = EJEMPLOS[0]["tolerancia"]
    criterio: str = EJEMPLOS[0]["criterio"]
    max_iteraciones: str = "100"
    decimales: int = 5
    decimales_automaticos: bool = True   # se ajustan a E mientras el usuario no mueva el control

    # Pasos 4 y 5: resultado
    resultado: dict | None = None
    grafica_escalera: str | None = None
    grafica_error: str | None = None
    graficas_iteracion: dict = field(default_factory=dict)
    iteracion_vista: int = 1

    paso: int = 1
    _cache: tuple = (None, None, None)

    def funcion_lista(self):
        """La funcion analizada, o None si esta mal escrita (con cache)."""
        texto, latex, objeto = self._cache
        if texto != self.funcion or latex != self.es_latex:
            try:
                objeto, self.error_funcion = Funcion(self.funcion, latex=self.es_latex), None
            except ErrorFuncion as e:
                objeto, self.error_funcion = None, str(e)
            self._cache = (self.funcion, self.es_latex, objeto)
        return objeto

    def ajustar_decimales(self):
        """Muestra una cifra mas de las que pide E (E = 0.0001 -> 5 decimales, como en clase)."""
        if not self.decimales_automaticos:
            return
        try:
            precision = float(str(self.tolerancia).replace(",", "."))
        except ValueError:
            return
        if precision <= 0 or math.isinf(precision) or math.isnan(precision):
            return
        if self.criterio == "porcentual":
            precision /= 100
        self.decimales = max(4, min(15, math.ceil(-math.log10(precision) - 1e-9) + 1))

    def nueva_funcion(self, texto, es_latex):
        """La funcion la escribio el usuario: el rango y el intervalo anteriores ya no sirven."""
        self.funcion, self.es_latex = texto, es_latex
        self.formula = None
        self.a = self.b = ""
        self.intervalo_preferido = None
        self.rango_automatico = True
        self.limpiar_resultados()

    @classmethod
    def desde_ejemplo(cls, ejemplo):
        """Estado inicial de la vista: el primer ejemplo del metodo, listo para graficar."""
        estado = cls(funcion=ejemplo["latex"], x_min=ejemplo["x_min"], x_max=ejemplo["x_max"],
                     subintervalos=ejemplo["subintervalos"], intervalo_preferido=(ejemplo["a"], ejemplo["b"]),
                     tolerancia=ejemplo["tolerancia"], criterio=ejemplo["criterio"])
        estado.ajustar_decimales()
        return estado

    def cargar_ejemplo(self, ejemplo):
        self.funcion, self.es_latex, self.formula = ejemplo["latex"], True, None
        self.x_min, self.x_max, self.subintervalos = ejemplo["x_min"], ejemplo["x_max"], ejemplo["subintervalos"]
        self.a, self.b = f'{ejemplo["a"]:g}', f'{ejemplo["b"]:g}'
        self.intervalo_preferido = (ejemplo["a"], ejemplo["b"])
        self.tolerancia, self.criterio = ejemplo["tolerancia"], ejemplo["criterio"]
        self.rango_automatico, self.aviso_rango = False, None
        self.decimales_automaticos = True
        self.ajustar_decimales()
        self.limpiar_resultados()

    def limpiar_resultados(self, tambien_grafica=True):
        if tambien_grafica:
            self.tabulacion = self.grafica_general = self.intervalo_activo = self.vista_plano = None
        self.resultado = self.grafica_escalera = self.grafica_error = None
        self.graficas_iteracion = {}
        self.iteracion_vista = 1
