# backend/metodos_numericos/vista_rapida.py
# Vista rapida de la pantalla principal: al escribir una funcion o una ecuacion se busca
# un rango donde se vean sus raices, se ubican los cambios de signo y cada raiz se
# afina por biseccion para mostrar su valor aproximado antes de elegir un metodo.
from .biseccion import buscar_rango, tabular

# Cuantas raices se muestran como maximo (sen x, tan x... tienen infinitas)
MAX_RAICES = 6
RANGO_POR_DEFECTO = (-10.0, 10.0, 40)


def _afinar(f, a, b, fa):
    """Biseccion corta (60 pasos) dentro de un intervalo con cambio de signo."""
    for _ in range(60):
        c = (a + b) / 2
        fc = f.evaluar(c)
        if fc is None:
            return None
        if fc == 0:
            return c
        if (fa < 0) == (fc < 0):
            a, fa = c, fc
        else:
            b = c
    return (a + b) / 2


def explorar(f):
    """Rango sugerido, raices aproximadas y asintotas de f, para la grafica del inicio."""
    rango = buscar_rango(f)
    if rango:
        x_min, x_max, n = rango["x_min"], rango["x_max"], rango["subintervalos"]
    else:
        x_min, x_max, n = RANGO_POR_DEFECTO
    tabulacion = tabular(f, x_min, x_max, n)
    raices = []
    for iv in tabulacion["intervalos"]:
        if iv["exacta"] is not None:
            x = iv["exacta"]
        else:
            x = _afinar(f, iv["a"], iv["b"], iv["fa"])
        if x is not None and all(abs(x - r["x"]) > 1e-9 * max(1.0, abs(x)) for r in raices):
            raices.append({"x": x, "a": iv["a"], "b": iv["b"]})
    for x in tabulacion["raices_que_tocan"]:
        if all(abs(x - r["x"]) > 1e-9 * max(1.0, abs(x)) for r in raices):
            raices.append({"x": x, "a": x, "b": x, "toca": True})
    raices.sort(key=lambda r: abs(r["x"]))
    raices = sorted(raices[:MAX_RAICES], key=lambda r: r["x"])
    return {
        "x_min": x_min, "x_max": x_max,
        "raices": raices,
        "asintotas": [d["x"] for d in tabulacion["discontinuidades"]],
        "sin_raices": not raices,
    }
