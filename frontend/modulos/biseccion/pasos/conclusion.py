# frontend/modulos/biseccion/pasos/conclusion.py
# Paso 5: conclusion del metodo y comprobaciones que pide el algoritmo.
from ....componentes import boton, caja, html, imagen, subtitulo
from ....formato import con_signo, escapar, numero
from ..estado import NOMBRE_ERROR
from . import decimales


def construir(vista):
    e = vista.estado
    r = e.resultado
    d = e.decimales
    nombre_error = NOMBRE_ERROR[r["criterio"]]
    with caja("fila").style("justify-content:space-between; align-items:center"):
        with caja():
            html('<div class="subtitulo" style="margin-top:0">Paso 5 · Conclusión</div>')
            html(f'<div class="texto-suave">{escapar(vista.TITULO)} en [{r["a_inicial"]:g}, {r["b_inicial"]:g}] '
                 f'con E = {r["tolerancia"]:g} y criterio {escapar(nombre_error)} &lt; E.</div>')
        decimales.control(vista, vista.panel.refresh)

    # Las tres conclusiones del metodo
    with caja("rejilla tres").style("margin-top:16px") as tres:
        for titulo, valor, pie in (
            ("Se realizaron", str(r["total_iteraciones"]), "iteraciones"),
            ("La solución", numero(r["raiz"], d), "raíz aproximada"),
            ("Error", numero(r["error_final"], d), f"{nombre_error} en la última iteración"),
        ):
            html(f'<div class="c-titulo">{titulo}</div><div class="c-valor mono numero-nuevo">{escapar(valor)}</div>'
                 f'<div class="c-pie">{escapar(pie)}</div>', "conclusion")
    vista.pasos_guia.append((tres, "Las tres conclusiones",
                             "Cuántas iteraciones se hicieron, cuál es la raíz aproximada y con qué error terminó."))

    estado_texto = "CONVERGE" if r["convergio"] else "NO CONVERGE"
    frase = html(
        f'El método <b>{estado_texto}</b> a {r["total_iteraciones"]} iteraciones. '
        f'LA RAÍZ ES: <b class="mono">{con_signo(r["raiz"], d)}</b><br>'
        f'Margen de error: x = <span class="mono">{numero(r["raiz"], d)} ± {numero(r["margen"], d)}</span> '
        f'&nbsp;({escapar(r["margen_texto"])})'
        + (f'<br>Cifras significativas correctas: <b>{r["cifras_significativas"]}</b>' if r["cifras_significativas"] is not None else ""),
        "frase-final")
    frase.style("margin-top:14px")
    vista.pasos_guia.append((frase, "Resultado con su margen",
                             f"La raíz verdadera está a lo sumo a ese margen de la aproximación: {r['margen_texto']}."))
    vista.aviso_conclusion(r)

    subtitulo("Comprobaciones del algoritmo")
    with caja("rejilla dos") as comprobaciones:
        for numero_regla, c in enumerate(r["comprobaciones"], start=1):
            with caja("comprobacion"):
                html("✓" if c["correcto"] else "!", "marca-c " + ("si" if c["correcto"] else "no"))
                html(f'<div style="font-weight:800; font-size:13.5px">{numero_regla}. {escapar(c["titulo"])}</div>'
                     f'<div class="texto-suave">{escapar(c["detalle"])}</div>')
    vista.pasos_guia.append((comprobaciones, "Comprobaciones",
                             "Las cuatro reglas del algoritmo: gráfica, sustituir la raíz en f, límite de iteraciones y alerta de f'(x) = 0."))

    with caja("rejilla dos").style("margin-top:6px"):
        with caja():
            subtitulo("Gráfica con la raíz encontrada")
            imagen(e.grafica_general or e.grafica_escalera)
        with caja():
            subtitulo("El error en cada iteración")
            imagen(e.grafica_error)
    subtitulo("Cómo se reduce el intervalo [a, b]")
    imagen(e.grafica_escalera)

    with caja("fila").style("justify-content:space-between; margin-top:18px"):
        boton("Anterior", lambda: vista.ir_a(4), icono="arrow_back")
        boton("Probar otra función", lambda: vista.ir_a(1), icono="restart_alt", principal=True)
