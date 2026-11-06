# frontend/modulos/regla_falsa/pasos/iteraciones.py
# Paso 4 de la regla falsa: la pantalla es la de biseccion; aqui solo cambia como se
# obtiene c (la recta entre (a, f(a)) y (b, f(b))) en la explicacion de cada iteracion.
from ....formato import clase_signo, con_signo, numero
from ...biseccion.pasos.iteraciones import EXPLICACION_RENGLON as EXPLICACION_BISECCION
from ...biseccion.pasos.iteraciones import renglones_comunes

# Lo que se explica en la guia de cada renglon (del segundo en adelante es igual que en biseccion)
EXPLICACION_RENGLON = [
    ("Falsa posición", "Se une (a, f(a)) con (b, f(b)) con una recta; donde corta al eje x está la nueva "
                       "aproximación: c = b − f(b)·(a − b) / (f(a) − f(b))."),
] + EXPLICACION_BISECCION[1:]


def renglones(it, r, d):
    """Explicacion de una iteracion: lista de (titulo, contenido HTML, clase extra)."""
    a, b, c = it["a"], it["b"], it["c"]
    fa, fb = it["fa_formula"], it["fb_formula"]
    s = lambda v: f'<span class="{clase_signo(v)}">{con_signo(v, d)}</span>'

    formula = (f"c = b − f(b)·(a − b) / (f(a) − f(b))<br>"
               f"c = {numero(b, d)} − ({s(fb)})·({numero(a, d)} − {numero(b, d)}) / (({s(fa)}) − ({s(fb)}))"
               f" = <b>{numero(c, d)}</b>")
    # Variante modificada: el extremo estancado entra a la formula con f dividida a la mitad
    for nombre, usado, real in (("a", fa, it["fa"]), ("b", fb, it["fb"])):
        if usado != real:
            divisor = round(real / usado)
            formula += (f"<br><i>{nombre} lleva varias iteraciones sin moverse: en la fórmula se usa "
                        f"f({nombre}) / {divisor} = {s(usado)} en lugar de f({nombre}) = {s(real)}.</i>")
    return [("Recta de falsa posición", formula, "")] + renglones_comunes(it, r, d)
