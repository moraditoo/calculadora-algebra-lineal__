# frontend/modulos/regla_falsa/pasos/algoritmo.py
# Explicacion del algoritmo de la regla falsa y de las reglas que cumple el programa.
from ....componentes import caja, html
from ...biseccion.pasos.algoritmo import dibujar

PASOS_METODO = [
    ("Elegir el intervalo", "Se eligen <b>a</b> (x<sub>l</sub>) y <b>b</b> (x<sub>u</sub>) que encierren la raíz, "
                            "de forma que la función cambie de signo: <b>f(a)·f(b) &lt; 0</b>. "
                            "f debe ser continua en [a, b] (teorema de Bolzano)."),
    ("Unir con una recta", "Se une (a, f(a)) con (b, f(b)) con una línea recta. Por triángulos semejantes: "
                           "f(a) / (c − a) = f(b) / (c − b)."),
    ("Falsa posición", "La recta corta el eje x en <b>c = b − f(b)·(a − b) / (f(a) − f(b))</b> "
                       "(x<sub>r</sub> = x<sub>u</sub> − f(x<sub>u</sub>)(x<sub>l</sub> − x<sub>u</sub>) / "
                       "(f(x<sub>l</sub>) − f(x<sub>u</sub>)))."),
    ("Subintervalo izquierdo", "Si <b>f(a)·f(c) &lt; 0</b> la raíz está en <b>[a, c]</b>: se hace <b>b = c</b>."),
    ("Subintervalo derecho", "Si <b>f(a)·f(c) &gt; 0</b> la raíz está en <b>[c, b]</b>: se hace <b>a = c</b>."),
    ("¿Raíz exacta?", "Si <b>f(a)·f(c) = 0</b>, la raíz es c y termina el cálculo."),
    ("Repetir", "Se vuelve al paso 3 hasta que el error sea <b>menor que E</b>. En el ejemplo de clase el error es "
                "relativo: <b>|(c nuevo − c anterior) / c nuevo|</b>. Otros criterios: error absoluto, "
                "porcentual, |f(c)| o la longitud del intervalo."),
]

REGLAS_PROGRAMA = [
    ("Rutina de graficación", "El paso 2 grafica f(x), marca los intervalos con cambio de signo y avisa de las "
     "asíntotas o saltos (una función discontinua no cumple Bolzano en ese tramo)."),
    ("Sustituir la raíz final en la función", "La conclusión evalúa f(raíz) para confirmar que se acerca a cero; "
     "así se detectan convergencias lentas u oscilatorias que dan un error pequeño lejos de la raíz."),
    ("Límite máximo de iteraciones", "En el paso 3 se fija el máximo; si se alcanza sin cumplir el criterio, el programa lo avisa."),
    ("Alerta de f'(x) = 0", "Durante el cálculo se estima la pendiente en cada punto c; si es casi cero "
     "(curva horizontal, posible raíz múltiple) se muestra una alerta en la conclusión."),
]

DIFERENCIAS = [
    ("Bisección vs. regla falsa", "Bisección toma siempre el punto medio y no usa los valores de f; la regla falsa "
     "usa f(a) y f(b) para estimar dónde corta la curva, por eso suele necesitar menos iteraciones."),
    ("Falsa posición modificada", "Si la curva es muy convexa un extremo puede quedarse fijo y el método avanza por un "
     "solo lado (por ejemplo x¹⁰ − 1). La variante modificada detecta que un extremo se «estanca» y divide a la mitad "
     "el valor de f en ese punto, así la recta se inclina hacia él."),
]


def construir(vista):
    dibujar(vista, "La regla falsa (falsa posición o <i>regula falsi</i>) es un método cerrado: la raíz siempre queda "
                   "dentro de [a, b], pero en lugar de partir el intervalo a la mitad, se reemplaza la curva por una "
                   "recta y se usa su corte con el eje x. También se le conoce como interpolación lineal.",
            "Pasos de la regla falsa", PASOS_METODO, REGLAS_PROGRAMA, extra=lambda: _diferencias(vista))


def _diferencias(vista):
    html('<div class="subtitulo">Para tener en cuenta</div>')
    with caja("rejilla dos") as rejilla:
        for indice, (titulo, contenido) in enumerate(DIFERENCIAS, start=1):
            with caja("renglon").style(f"animation-delay:{0.07 * indice + 0.5:.2f}s"):
                html("i", "circulo")
                html(f'<div class="que">{titulo}</div><div class="como">{contenido}</div>')
    vista.pasos_guia.append((rejilla, "Diferencias", "Qué cambia respecto a bisección y cuándo conviene la variante modificada."))
