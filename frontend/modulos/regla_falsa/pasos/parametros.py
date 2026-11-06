# frontend/modulos/regla_falsa/pasos/parametros.py
# Paso 3 de la regla falsa: los mismos parametros de biseccion mas la variante del metodo.
from ....componentes import caja, subtitulo, tarjetas_opcion

VARIANTES = [
    {"valor": False, "titulo": "Clásica",
     "detalle": "c = b − f(b)·(a − b) / (f(a) − f(b)) con los valores reales de f en los extremos.",
     "extra": "Puede avanzar por un solo lado si un extremo se queda fijo."},
    {"valor": True, "titulo": "Modificada",
     "detalle": "Si un extremo se estanca dos iteraciones seguidas, se divide a la mitad su valor de f en la fórmula.",
     "extra": "Evita la convergencia lenta unilateral."},
]


def variante(vista):
    """Elegir entre la falsa posicion clasica y la modificada (se dibuja dentro del paso 3)."""
    e = vista.estado

    def cambiar(valor):
        e.modificada = valor

    subtitulo("Variante del método")
    with caja() as opciones:
        tarjetas_opcion(VARIANTES, lambda: e.modificada, cambiar, columnas="dos")
    vista.pasos_guia.append((opciones, "Variante del método",
                             "La regla falsa clásica puede quedarse con un extremo fijo y avanzar muy lento. "
                             "La modificada detecta ese estancamiento y divide a la mitad f en ese extremo."))
