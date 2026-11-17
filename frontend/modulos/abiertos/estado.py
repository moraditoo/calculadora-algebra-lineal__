# frontend/modulos/abiertos/estado.py
# Estado de los metodos abiertos: el mismo de biseccion (funcion, grafica, E, decimales...)
# mas los valores iniciales x0 (y x1 en la secante) y la derivada f'(x).
from dataclasses import dataclass

from backend.metodos_numericos.analizador import ErrorFuncion, Funcion
from ..biseccion.estado import Estado

# El error absoluto va primero: es el que se usa por defecto
CRITERIOS = [
    {"valor": "absoluto", "titulo": "Ea < E", "detalle": "Error absoluto: |xₙ₊₁ − xₙ| (cambio entre aproximaciones)"},
    {"valor": "relativo", "titulo": "Er < E", "detalle": "Error relativo: |(xₙ₊₁ − xₙ) / xₙ₊₁|"},
    {"valor": "porcentual", "titulo": "Er % < E", "detalle": "Error relativo porcentual (· 100 %)"},
    {"valor": "residuo", "titulo": "|f(xₙ₊₁)| < E", "detalle": "Residuo: cuánto incumple la ecuación"},
    {"valor": "ambos", "titulo": "Ea y |f| < E", "detalle": "Cambio y residuo a la vez (los dos criterios)"},
]

NOMBRE_ERROR = {"absoluto": "Ea", "relativo": "Er", "porcentual": "Er %", "residuo": "|f(x)|", "ambos": "máx(Ea, |f|)"}


def _texto_numero(valor):
    return "" if valor is None or valor == "" else f"{valor:g}"


@dataclass
class EstadoAbierto(Estado):
    # Paso 3: valores iniciales (la secante usa dos)
    x0: str = ""
    x1: str = ""
    siguiente: str = "x0"     # secante: que valor elige el proximo clic sobre la grafica
    max_iteraciones: str = "50"
    # f'(x): se calcula sola; si el profesor la da, se puede escribir
    usar_derivada_escrita: bool = False
    derivada_escrita: str = ""
    formula_derivada: str | None = None
    error_derivada: str | None = None
    _cache_derivada: tuple = (None, None, None)

    def derivada_automatica(self):
        f = self.funcion_lista()
        return f.derivada() if f else None

    def derivada_lista(self):
        """La derivada que se usa: la escrita (si se eligio) o la calculada; None si esta mal escrita."""
        if not self.usar_derivada_escrita:
            self.error_derivada = None
            return self.derivada_automatica()
        texto, objeto, error = self._cache_derivada
        if texto != self.derivada_escrita:
            try:
                objeto, error = Funcion(self.derivada_escrita, nombre=r"f^{\prime}(x)"), None
            except ErrorFuncion as e:
                objeto, error = None, str(e)
            self._cache_derivada = (self.derivada_escrita, objeto, error)
        self.error_derivada = error
        return objeto

    def nueva_funcion(self, texto, es_latex):
        super().nueva_funcion(texto, es_latex)
        self.x0 = self.x1 = ""          # los elige el usuario mirando la grafica (no se llenan solos)
        self.siguiente = "x0"
        self.formula_derivada = None

    @classmethod
    def desde_ejemplo(cls, ejemplo):
        estado = cls(funcion=ejemplo["latex"], tolerancia=ejemplo["tolerancia"], criterio=ejemplo["criterio"],
                     intervalo_preferido=None, rango_automatico=True,
                     x0=_texto_numero(ejemplo["x0"]), x1=_texto_numero(ejemplo.get("x1")),
                     max_iteraciones=ejemplo.get("max_iteraciones", "50"))
        estado.ajustar_decimales()
        return estado

    def cargar_ejemplo(self, ejemplo):
        self.funcion, self.es_latex, self.formula, self.formula_derivada = ejemplo["latex"], True, None, None
        self.x0, self.x1 = _texto_numero(ejemplo["x0"]), _texto_numero(ejemplo.get("x1"))
        self.siguiente = "x0"
        self.tolerancia, self.criterio = ejemplo["tolerancia"], ejemplo["criterio"]
        self.max_iteraciones = ejemplo.get("max_iteraciones", "50")
        self.usar_derivada_escrita = False
        # El rango de la grafica se busca solo para que se vean las raices
        self.intervalo_preferido, self.rango_automatico, self.aviso_rango = None, True, None
        self.decimales_automaticos = True
        self.ajustar_decimales()
        self.limpiar_resultados()
