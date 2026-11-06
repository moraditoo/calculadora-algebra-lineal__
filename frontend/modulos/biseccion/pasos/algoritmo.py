# frontend/modulos/biseccion/pasos/algoritmo.py
# Explicacion del algoritmo del metodo y de las reglas que cumple el programa.
from ....componentes import boton, caja, html

PASOS_METODO = [
    ("Definir", "Se definen <b>f</b>, el intervalo inicial <b>[a, b]</b> y la precisión requerida <b>E</b>. "
                "Si f es continua en [a, b] y f(a)·f(b) &lt; 0, el intervalo contiene al menos una raíz real."),
    ("Punto central", "Se calcula el punto central del intervalo: <b>c = (a + b) / 2</b>."),
    ("¿Raíz exacta?", "Si <b>f(c) = 0</b>, c es la raíz y termina."),
    ("Mitad izquierda", "Si la raíz está en <b>[a, c]</b> (f(a)·f(c) &lt; 0), se sustituye <b>b</b> por <b>c</b>."),
    ("Mitad derecha", "Si la raíz está en <b>[c, b]</b> (f(a)·f(c) &gt; 0), se sustituye <b>a</b> por <b>c</b>."),
    ("Repetir", "Se repiten los pasos 2 a 5 hasta que el error sea <b>menor que E</b>. "
                "En la hoja de clase el error de cada iteración es <b>|f(c)|</b>. "
                "Otros criterios: error absoluto Ea = |c nuevo − c anterior| y error relativo porcentual "
                "|(c nuevo − c anterior) / c nuevo| · 100 %."),
]

REGLAS_PROGRAMA = [
    ("Rutina de graficación", "El paso 2 grafica f(x) y marca los intervalos donde cambia de signo."),
    ("Sustituir la raíz final en la función", "La conclusión evalúa f(raíz) para confirmar que se acerca a cero; "
     "así se detectan convergencias lentas u oscilatorias que dan un error pequeño lejos de la raíz."),
    ("Límite máximo de iteraciones", "En el paso 3 se fija el máximo; si se alcanza sin cumplir el criterio, el programa lo avisa."),
    ("Alerta de f'(x) = 0", "Durante el cálculo se estima la pendiente en cada punto medio; si es casi cero "
     "(curva horizontal, posible raíz múltiple) se muestra una alerta en la conclusión."),
]


def construir(vista):
    dibujar(vista, "Bisección es un método cerrado: la raíz siempre queda dentro de un intervalo que se reduce "
                   "a la mitad en cada iteración, por eso siempre converge.",
            "Pasos de la bisección", PASOS_METODO, REGLAS_PROGRAMA)


def dibujar(vista, introduccion, titulo_pasos, pasos_metodo, reglas_programa, extra=None):
    """Dos columnas: los pasos del metodo y como el programa cumple las reglas del algoritmo.
    extra: funcion opcional que dibuja algo mas debajo (por ejemplo, una variante del metodo)."""
    html('<div class="subtitulo" style="margin-top:0">Algoritmo del método</div>')
    html(f'<div class="texto-suave">{introduccion}</div>')

    with caja("rejilla dos").style("align-items:start; margin-top:16px"):
        with caja() as metodo:
            html(f'<div class="subtitulo" style="margin-top:0">{titulo_pasos}</div>')
            with caja("explicacion"):
                for indice, (titulo, contenido) in enumerate(pasos_metodo, start=1):
                    ultimo = indice == len(pasos_metodo)
                    with caja("renglon" + (" decision" if ultimo else "")).style(f"animation-delay:{0.05 * indice:.2f}s"):
                        html(str(indice), "circulo")
                        html(f'<div class="que">{titulo}</div><div class="como">{contenido}</div>')
        with caja() as reglas:
            html('<div class="subtitulo" style="margin-top:0">Lo que cumple el programa</div>')
            with caja("explicacion"):
                for indice, (titulo, contenido) in enumerate(reglas_programa, start=1):
                    with caja("renglon").style(f"animation-delay:{0.07 * indice + 0.2:.2f}s"):
                        html(str(indice), "circulo")
                        html(f'<div class="que">{titulo}</div><div class="como">{contenido}</div>')
    vista.pasos_guia += [(metodo, "Algoritmo", f"Los {len(pasos_metodo)} pasos del método de {vista.NOMBRE}."),
                         (reglas, "Requisitos del programa", "Cómo este programa cumple cada recomendación del algoritmo.")]
    if extra:
        extra()

    with caja("fila").style("justify-content:flex-end; margin-top:18px"):
        boton("Ir al paso 1", lambda: vista.ir_a(1), icono="arrow_forward", principal=True)
