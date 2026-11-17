# frontend/modulos/abiertos/pasos/algoritmo.py
# Algoritmo de Newton-Raphson y de la secante (como en la presentacion de clase), lo que
# cumple el programa, cuando pueden fallar y la comparacion entre los dos metodos.
from ....componentes import caja, html
from ...biseccion.pasos.algoritmo import dibujar

PASOS_NEWTON = [
    ("Definir f(x) y f'(x)", "Se escribe f(x); el programa calcula <b>f'(x)</b> con las reglas de derivación "
                             "(o se escribe la que da el profesor)."),
    ("Elegir x₀", "Un valor inicial cerca de la raíz (la gráfica ayuda a ubicarlo)."),
    ("Calcular xₙ₊₁", "<b>xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)</b>: la tangente en (xₙ, f(xₙ)) corta el eje x en xₙ₊₁. "
                      "La derivada no debe ser cero ni demasiado pequeña."),
    ("Evaluar residuo y cambio", "Residuo <b>|f(xₙ₊₁)|</b> y cambio entre iteraciones <b>|xₙ₊₁ − xₙ|</b>."),
    ("Repetir", "Hasta cumplir la <b>tolerancia</b> (error &lt; E) o llegar al <b>máximo de iteraciones</b>."),
    ("Reportar", "Raíz aproximada, residuo e iteraciones."),
]

PASOS_SECANTE = [
    ("Definir f(x) y elegir x₀, x₁", "Dos valores iniciales distintos; no hace falta que encierren la raíz."),
    ("Calcular f(x₀) y f(x₁)", "Son los dos puntos de la curva por donde pasa la recta secante."),
    ("Calcular x₂", "<b>xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / [f(xₙ) − f(xₙ₋₁)]</b>: donde la secante corta el eje x. "
                    "El denominador debe ser distinto de cero."),
    ("Actualizar", "<b>x₀ ← x₁</b> y <b>x₁ ← x₂</b>: se desplazan las dos aproximaciones."),
    ("Repetir", "Hasta cumplir la <b>tolerancia</b> (error &lt; E) o llegar al <b>máximo de iteraciones</b>."),
    ("Reportar", "Aproximación, residuo e iteraciones."),
]

REGLAS = [
    ("Rutina de graficación", "El paso 2 grafica f(x) y marca dónde cambia de signo para elegir buenos valores iniciales."),
    ("Derivada automática", "f'(x) se obtiene del árbol de la función con las reglas de derivación y se muestra en "
     "los pasos 1, 4 y 5; si se escribe a mano se compara con la calculada."),
    ("Dos condiciones de parada", "Se detiene cuando el error es menor que E (por defecto el absoluto |xₙ₊₁ − xₙ|) "
     "o al llegar al máximo de iteraciones."),
    ("Sustituir la raíz en la función", "La conclusión reporta el residuo |f(raíz)| para confirmar que se acerca a cero."),
    ("Alertas", "Avisa si la fórmula divide entre cero (f'(xₙ) = 0 o f(xₙ) = f(xₙ₋₁)), si las aproximaciones se alejan "
     "(diverge), si salen del dominio de f o si la raíz parece múltiple."),
]

FALLAS_NEWTON = [
    ("f'(xₙ) = 0", "La fórmula no está definida: la tangente es horizontal."),
    ("|f'(xₙ)| muy pequeño", "Puede producir un salto excesivo."),
    ("x₀ inadecuado", "Puede llevar a divergencia, a un ciclo o a otra raíz."),
    ("Raíces múltiples", "Disminuye la rapidez de convergencia (f'(raíz) = 0)."),
]

FALLAS_SECANTE = [
    ("f(xₙ) − f(xₙ₋₁) = 0", "La fórmula no está definida: la secante es horizontal."),
    ("Denominador muy pequeño", "Puede generar un paso inestable."),
    ("Elección de x₀ y x₁", "Influye en el comportamiento; no conserva un intervalo que encierre la raíz."),
    ("Verificar siempre", "El residuo, los cambios entre iteraciones y el máximo de iteraciones."),
]

COMPARACION = [
    ("Valores iniciales", "Uno", "Dos"),
    ("Derivada", "Explícita", "No explícita"),
    ("Geometría", "Tangente", "Secante"),
    ("Ventaja", "Puede converger muy rápido cerca de la raíz", "Evita derivar la función"),
    ("Riesgo", "Derivada nula o pequeña", "Denominador nulo o pequeño"),
]


def _sub(texto):
    """xₙ₊₁ -> x<sub>n+1</sub>: los subindices Unicode se ven muy pequenos en la fuente de la interfaz."""
    for viejo, nuevo in (("ₙ₊₁", "n+1"), ("ₙ₋₁", "n−1"), ("ₙ", "n"), ("₀", "0"), ("₁", "1"), ("₂", "2")):
        texto = texto.replace(viejo, f"<sub>{nuevo}</sub>")
    return texto


def _html(lista):
    return [tuple(_sub(parte) for parte in fila) for fila in lista]


def construir(vista):
    newton = vista.USA_DERIVADA
    if newton:
        introduccion = ("Newton-Raphson es un método abierto: parte de un valor inicial x₀ y reemplaza localmente la curva "
                        "por su recta tangente. Puede converger muy rápido, pero la convergencia es local: depende de la "
                        "función y de x₀.")
    else:
        introduccion = ("La secante es un método abierto: es una alternativa a Newton-Raphson cuando no se desea calcular "
                        "la derivada. Usa dos aproximaciones para construir una recta secante y no necesita que encierren la raíz.")
    dibujar(vista, introduccion, "Pasos de " + ("Newton-Raphson" if newton else "la secante"),
            _html(PASOS_NEWTON if newton else PASOS_SECANTE), _html(REGLAS), extra=lambda: _extra(vista, newton))


def _extra(vista, newton):
    html('<div class="subtitulo">¿Cuándo puede fallar?</div>')
    with caja("rejilla dos") as fallas:
        for indice, (titulo, contenido) in enumerate(_html(FALLAS_NEWTON if newton else FALLAS_SECANTE), start=1):
            with caja("renglon").style(f"animation-delay:{0.07 * indice + 0.5:.2f}s"):
                html("!", "circulo")
                html(f'<div class="que">{titulo}</div><div class="como">{contenido}</div>')
    vista.pasos_guia.append((fallas, "Cuándo puede fallar", "Las situaciones en las que el método no converge o no se puede aplicar."))

    html('<div class="subtitulo">Comparación de los métodos</div>')
    filas = "".join(f"<tr><td><b>{c}</b></td><td>{n}</td><td>{s}</td></tr>" for c, n, s in COMPARACION)
    tabla = html('<table class="tabla"><thead><tr><th>Criterio</th><th>Newton-Raphson</th><th>Secante</th></tr></thead>'
                 f"<tbody>{filas}</tbody></table>", "contenedor-tabla")
    vista.pasos_guia.append((tabla, "Comparación", "Diferencias entre Newton-Raphson y la secante."))
