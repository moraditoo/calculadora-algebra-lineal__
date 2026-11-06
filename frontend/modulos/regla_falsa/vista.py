# frontend/modulos/regla_falsa/vista.py
# Vista del metodo de regla falsa. Los pasos 1 a 5 son los mismos de biseccion (funcion,
# grafica, parametros, iteraciones y conclusion); aqui solo se cambia lo que es propio
# del metodo: el calculo, la explicacion de cada iteracion, la grafica con la recta,
# la variante modificada y el algoritmo.
from backend.metodos_numericos import biseccion as metodo_biseccion
from backend.metodos_numericos import graficas
from backend.metodos_numericos import regla_falsa as metodo
from ...componentes import aviso
from ..biseccion.vista import VistaBiseccion
from .ejemplos import EJEMPLOS
from .estado import EstadoReglaFalsa
from .pasos import algoritmo, iteraciones, parametros


def construir():
    VistaReglaFalsa()


class VistaReglaFalsa(VistaBiseccion):
    NOMBRE = "regla falsa"
    TITULO = "Método de Regla Falsa"
    DESCRIPCION = ("Método cerrado (falsa posición): se grafica la función, se toma un intervalo donde cambia de signo "
                   "y se une (a, f(a)) con (b, f(b)) con una recta; su corte con el eje x es la nueva aproximación. "
                   "Se repite hasta que el error sea menor que E.")
    ICONO = "timeline"
    PREFIJO = "regla_falsa"
    EJEMPLOS = EJEMPLOS
    ESTADO = EstadoReglaFalsa
    CRITERIO_DE_CLASE = "relativo"
    NOTA_CRITERIO = ("En el ejemplo de clase el error de cada iteración es el relativo Er = |(c nuevo − c anterior) / c nuevo|. "
                     "También puede usar el absoluto, el porcentual, |f(c)| o la longitud del intervalo. "
                     "En cada iteración se compara con E y se itera hasta que el error sea menor que E.")
    AVISO_RAIZ_EXACTA = ("esa raíz ya es exacta. La regla falsa la alcanza desde el intervalo que la rodea "
                         "(o al instante si la raíz es uno de los extremos).")
    INTRO_ITERACIONES = ("Cada iteración une (a, f(a)) con (b, f(b)) con una recta; donde corta el eje x está c. "
                         "Luego se queda con el subintervalo donde f cambia de signo. "
                         "Use las flechas, el control deslizante, la tabla o <b>Reproducir</b>.")
    EXPLICACION_RENGLON = iteraciones.EXPLICACION_RENGLON
    PASOS_DIBUJO = {**VistaBiseccion.PASOS_DIBUJO, 6: algoritmo.construir}

    def calcular(self, f):
        e = self.estado
        resultado = metodo.regla_falsa(f, e.a, e.b, e.tolerancia, e.criterio, e.max_iteraciones, e.modificada)
        # Para comparar: cuantas iteraciones necesita biseccion con los mismos datos
        try:
            comparacion = metodo_biseccion.biseccion(f, e.a, e.b, e.tolerancia, e.criterio, e.max_iteraciones)
            resultado["iteraciones_biseccion"] = (comparacion["total_iteraciones"], comparacion["convergio"])
        except ValueError:
            resultado["iteraciones_biseccion"] = None
        return resultado

    def renglones(self, it, r, d):
        return iteraciones.renglones(it, r, d)

    def grafica_de_iteracion(self, f, it):
        return graficas.grafica_iteracion(f, it, secante=True)

    def opciones_metodo(self):
        parametros.variante(self)

    def aviso_conclusion(self, r):
        n = r["total_iteraciones"]
        if r["extremo_fijo"] and not r["modificada"]:
            aviso(f"El extremo {r['extremo_fijo']} no se movió en ninguna iteración: la regla falsa avanzó por un solo lado "
                  f"(naturaleza unilateral) y por eso necesitó {n} iteraciones. Pruebe la variante «modificada» en el paso 3.",
                  "advertencia").style("margin-top:10px")
        elif r["modificada"]:
            aviso("Se usó la falsa posición modificada: cuando un extremo se estancaba dos iteraciones seguidas, "
                  "su valor de f se dividió a la mitad en la fórmula para que la recta se acercara a la raíz por ambos lados.",
                  "info").style("margin-top:10px")
        if r.get("iteraciones_biseccion"):
            n_biseccion, convergio = r["iteraciones_biseccion"]
            frase = f"{n_biseccion} iteraciones" + ("" if convergio else " (sin llegar a E)")
            aviso(f"Comparación: con bisección, en el mismo intervalo y con el mismo criterio, se necesitan {frase}; "
                  f"la regla falsa usó {n}.", "info").style("margin-top:10px")
