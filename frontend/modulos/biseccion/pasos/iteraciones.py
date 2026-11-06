# frontend/modulos/biseccion/pasos/iteraciones.py
# Paso 4: recorrer las iteraciones una por una, explicando cada calculo.
from nicegui import ui

from .... import guia
from ....componentes import boton, caja, html, imagen, subtitulo
from ....formato import clase_signo, con_signo, escapar, numero
from ..estado import NOMBRE_ERROR
from . import decimales

# Lo que se explica en la guia de cada renglon de una iteracion
EXPLICACION_RENGLON = [
    ("Punto medio", "Se parte el intervalo [a, b] a la mitad: c = (a + b) / 2."),
    ("Evaluar f(c)", "Se sustituye c en la función para saber de qué lado del eje queda."),
    ("Comparar signos", "Si f(a)·f(c) < 0 la raíz está en [a, c] y b toma el valor de c; si es > 0 está en [c, b] y a toma el valor de c."),
    ("Calcular el error", "Se mide cuánto cambió la aproximación respecto a la iteración anterior."),
    ("Decidir", "Si el error es menor que E el método se detiene y c es la raíz; si no, se repite con el nuevo intervalo."),
]


def construir(vista):
    e = vista.estado
    r = e.resultado
    total = r["total_iteraciones"]
    html('<div class="subtitulo" style="margin-top:0">Paso 4 · Iteraciones paso a paso</div>')
    html(f'<div class="texto-suave">{vista.INTRO_ITERACIONES}</div>')

    # Barra para moverse entre iteraciones (se actualiza, no se vuelve a dibujar)
    with caja("navegador").style("margin:16px 0") as navegador_caja:
        boton("", lambda: vista.ver_iteracion(e.iteracion_vista - 1), icono="chevron_left").mark("iteracion-anterior")
        contador = html("", "contador")
        boton("", lambda: vista.ver_iteracion(e.iteracion_vista + 1), icono="chevron_right").mark("iteracion-siguiente")
        boton_reproducir = boton("Reproducir", vista.alternar_reproduccion, icono="play_arrow", principal=True).mark("reproducir")
        boton("Explicar esta iteración", lambda: explicar(), icono="tour", clases="guia")
        deslizador = ui.slider(min=1, max=max(total, 2), step=1, value=e.iteracion_vista,
                               on_change=lambda ev: vista.ver_iteracion(ev.value) if ev.value != e.iteracion_vista else None)
        deslizador.props("color=grey-8").classes("grow").style("min-width:150px")
        deslizador.set_visibility(total > 1)
    vista.pasos_guia.append((navegador_caja, "Recorrer las iteraciones",
                             "Avance o retroceda una iteración, o use Reproducir para verlas solas una tras otra."))

    def navegador():
        contador.set_content(f"Iteración <b>{e.iteracion_vista}</b> de {total}")
        reproduciendo = vista.reproductor.active
        boton_reproducir.set_text("Pausar" if reproduciendo else "Reproducir")
        boton_reproducir.props(f"icon={'pause' if reproduciendo else 'play_arrow'}")
        if deslizador.value != e.iteracion_vista:
            deslizador.set_value(e.iteracion_vista)

    renglones_actuales = []

    @ui.refreshable
    def detalle():
        renglones_actuales.clear()
        it = r["iteraciones"][e.iteracion_vista - 1]
        with caja("rejilla dos").style("align-items:start"):
            with caja("explicacion"):
                for indice, (titulo, contenido, clase) in enumerate(vista.renglones(it, r, e.decimales), start=1):
                    with caja("renglon " + clase).style(f"animation-delay:{0.05 * indice:.2f}s") as renglon:
                        html(str(indice), "circulo")
                        html(f'<div class="que">{escapar(titulo)}</div><div class="como mono">{contenido}</div>')
                    renglones_actuales.append(renglon)
            imagen(e.graficas_iteracion.get(e.iteracion_vista))

    def explicar():
        """Resalta uno por uno los calculos de la iteracion que se esta viendo."""
        vista.reproductor.deactivate()
        navegador()
        guia.iniciar([(elemento, f"{indice}. {titulo}", texto)
                      for indice, (elemento, (titulo, texto)) in enumerate(zip(renglones_actuales, vista.EXPLICACION_RENGLON), start=1)])

    navegador()
    detalle()

    def con_otros_decimales():
        """Redibuja la explicacion y la tabla con la nueva cantidad de decimales."""
        detalle.refresh()
        tabla.set_content(tabla_iteraciones(r, e.decimales, e.iteracion_vista, vista.PREFIJO))

    with caja("fila").style("justify-content:space-between; align-items:center; margin-top:18px"):
        subtitulo("Tabla de iteraciones").style("margin:0")
        decimales.control(vista, con_otros_decimales)
    tabla = html(tabla_iteraciones(r, e.decimales, e.iteracion_vista, vista.PREFIJO), "contenedor-tabla mono").style("margin-top:10px")
    vista.pasos_guia.append((tabla, "Tabla de iteraciones",
                             "Resumen de todas las iteraciones. La columna en azul es el error del criterio; "
                             "haga clic en una fila para ver su explicación."))

    with caja("fila").style("justify-content:space-between; margin-top:18px"):
        boton("Anterior", lambda: vista.ir_a(3), icono="arrow_back")
        boton("Ver conclusión", lambda: vista.ir_a(5), icono="arrow_forward", principal=True)

    vista.refrescos_iteracion = (navegador, detalle.refresh)


def al_cambiar_iteracion(vista):
    """Actualiza la explicacion y marca la fila de la tabla sin volver a dibujar todo el panel."""
    if vista.estado.paso != 4:
        return
    for refrescar in vista.refrescos_iteracion:
        refrescar()
    k = vista.estado.iteracion_vista
    ui.run_javascript(
        "document.querySelectorAll('.tabla tr.actual').forEach(f => f.classList.remove('actual'));"
        f"const fila = document.getElementById('{vista.PREFIJO}-iteracion-{k}');"
        "if (fila) { fila.classList.add('actual'); fila.scrollIntoView({block: 'nearest', behavior: 'smooth'}); }"
    )


def renglones(it, r, d):
    """Explicacion de una iteracion: lista de (titulo, contenido HTML, clase extra)."""
    a, b, c = it["a"], it["b"], it["c"]
    punto = ("Punto medio", f"c = (a + b) / 2 = ({numero(a, d)} + {numero(b, d)}) / 2 = <b>{numero(c, d)}</b>", "")
    return [punto] + renglones_comunes(it, r, d)


def renglones_comunes(it, r, d):
    """Evaluar f(c), comparar signos, calcular el error y decidir: igual en biseccion y en regla falsa."""
    a, b, c, fa, fc = it["a"], it["b"], it["c"], it["fa"], it["fc"]
    s = lambda v: f'<span class="{clase_signo(v)}">{con_signo(v, d)}</span>'
    izquierda = it["subintervalo"] == "[a, c]"
    nuevo_a, nuevo_b = (a, c) if izquierda else (c, b)
    pasos = [("Evaluar la función", f"f(c) = f({numero(c, d)}) = <b>{s(fc)}</b>", "")]
    if fc == 0:
        pasos.append(("Comparar signos", "f(c) = 0: c es la raíz exacta.", ""))
    else:
        comparacion = "&lt; 0" if izquierda else "&gt; 0"
        reemplazo = "se sustituye <b>b</b> por c" if izquierda else "se sustituye <b>a</b> por c"
        pasos.append(("Comparar signos",
                      f"f(a)·f(c) = ({s(fa)})·({s(fc)}) {comparacion} → la raíz está en {it['subintervalo']}, {reemplazo}.<br>"
                      f"Nuevo intervalo: [{numero(nuevo_a, d)}, {numero(nuevo_b, d)}]", ""))

    error, tolerancia, criterio = it["error"], r["tolerancia"], r["criterio"]
    nombre = NOMBRE_ERROR[criterio]
    anterior = it["c_anterior"]
    if criterio in ("absoluto", "relativo", "porcentual") and anterior is None:
        pasos.append(("Calcular el error", "En la primera iteración todavía no hay un c anterior, así que el error no se calcula.", ""))
    elif criterio == "absoluto":
        pasos.append(("Calcular el error",
                      f"Ea = |c nuevo − c anterior| = |{numero(c, d)} − {numero(anterior, d)}| = <b>{numero(error, d)}</b>", ""))
    elif criterio in ("relativo", "porcentual"):
        por_cien = " · 100 %" if criterio == "porcentual" else ""
        pasos.append(("Calcular el error",
                      f"{nombre} = |({numero(c, d)} − {numero(anterior, d)}) / {numero(c, d)}|{por_cien} = <b>{numero(error, d)}</b>", ""))
    elif criterio == "funcion":
        pasos.append(("Calcular el error", f"|f(c)| = <b>{numero(error, d)}</b>", ""))
    else:
        pasos.append(("Calcular el error", f"b − a = {numero(nuevo_b, d)} − {numero(nuevo_a, d)} = <b>{numero(error, d)}</b>", ""))

    es_ultima = it["iteracion"] == r["total_iteraciones"]
    if fc == 0:
        decision, clase = f"Se detiene: la raíz es c = <b>{numero(c, d)}</b>.", "decision alto"
    elif it["detiene"]:
        decision = f"{nombre} = {numero(error, d)} &lt; E = {tolerancia:g} → <b>se detiene</b>: la raíz aproximada es c = <b>{numero(c, d)}</b>."
        clase = "decision alto"
    elif es_ultima:
        decision, clase = escapar(r["motivo"]), "decision"
    elif error is None:
        decision, clase = "Se continúa con la siguiente iteración.", "decision"
    else:
        decision, clase = f"{nombre} = {numero(error, d)} ≥ E = {tolerancia:g} → se continúa con el nuevo intervalo.", "decision"
    pasos.append(("¿El error es menor que E?", decision, clase))
    return pasos


def tabla_iteraciones(r, d, actual, prefijo="biseccion"):
    nombre_error = NOMBRE_ERROR[r["criterio"]]
    titulos = ["Iteración", "a", "b", "c", "f(a)", "f(b)", "f(c)", nombre_error]
    cabeza = "".join(f'<th class="{"criterio" if t == nombre_error else ""}">{t}</th>' for t in titulos)
    filas = []
    for it in r["iteraciones"]:
        k = it["iteracion"]
        clases = ("actual " if k == actual else "") + ("final" if k == r["total_iteraciones"] else "")
        celdas = [
            f"<td>{k}</td>",
            f"<td>{numero(it['a'], d)}</td>",
            f"<td>{numero(it['b'], d)}</td>",
            f"<td><b>{numero(it['c'], d)}</b></td>",
            f'<td class="{clase_signo(it["fa"])}">{con_signo(it["fa"], d)}</td>',
            f'<td class="{clase_signo(it["fb"])}">{con_signo(it["fb"], d)}</td>',
            f'<td class="{clase_signo(it["fc"])}">{con_signo(it["fc"], d)}</td>',
            f'<td style="color:#1d1d1f; font-weight:800">{numero(it["error"], d)}</td>',
        ]
        filas.append(f'<tr id="{prefijo}-iteracion-{k}" class="{clases}" '
                     f'onclick="emitEvent(\'{prefijo}_fila\', {k})">{"".join(celdas)}</tr>')
    return f'<table class="tabla clic"><thead><tr>{cabeza}</tr></thead><tbody>{"".join(filas)}</tbody></table>'
