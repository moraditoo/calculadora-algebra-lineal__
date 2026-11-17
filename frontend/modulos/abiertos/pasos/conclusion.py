# frontend/modulos/abiertos/pasos/conclusion.py
# Paso 5 de los metodos abiertos: reportar raiz aproximada, residuo e iteraciones (paso 6 del
# algoritmo), la derivada f'(x) con su valor en la raiz, y las comprobaciones.
from ....componentes import aviso, boton, caja, html, imagen, subtitulo
from ....formato import con_signo, escapar, numero
from ...biseccion.pasos import decimales
from ..estado import NOMBRE_ERROR

ESTADOS = {
    "exacta": "f(x) = 0 con la precisión de la computadora",
    "tolerancia": "el error fue menor que la tolerancia E",
    "maximo": "se llegó al máximo de iteraciones",
    "derivada_nula": "la fórmula dividió entre cero",
    "diverge": "las aproximaciones se alejaron (diverge)",
    "dominio": "una aproximación salió del dominio de f",
}


def construir(vista):
    e = vista.estado
    r = e.resultado
    d = e.decimales
    nombre_error = NOMBRE_ERROR[r["criterio"]]
    iniciales = f"x₀ = {r['x0']:g}" + (f", x₁ = {r['x1']:g}" if "x1" in r else "")
    with caja("fila").style("justify-content:space-between; align-items:center"):
        with caja():
            html('<div class="subtitulo" style="margin-top:0">Paso 5 · Conclusión</div>')
            html(f'<div class="texto-suave">{escapar(vista.TITULO)} con {iniciales}, tolerancia E = {r["tolerancia"]:g} '
                 f'y criterio {escapar(nombre_error)} &lt; E (o un máximo de {r["max_iteraciones"]} iteraciones).</div>')
        decimales.control(vista, vista.panel.refresh)

    # Lo que pide reportar el algoritmo: raiz aproximada, residuo e iteraciones
    with caja("rejilla cuatro").style("margin-top:16px") as cuatro:
        for titulo, valor, pie in (
            ("Se realizaron", str(r["total_iteraciones"]), "iteraciones"),
            ("Raíz aproximada", numero(r["raiz"], d), "x ≈ raíz de f(x) = 0" if r["veredicto"]["tipo"] == "converge"
             else "última aproximación"),
            ("Residuo", numero(r["residuo"], d), "|f(raíz)|"),
            ("Error", numero(r["error_final"], d), f"{nombre_error} en la última iteración"),
        ):
            html(f'<div class="c-titulo">{titulo}</div><div class="c-valor mono numero-nuevo">{escapar(valor)}</div>'
                 f'<div class="c-pie">{escapar(pie)}</div>', "conclusion")
    vista.pasos_guia.append((cuatro, "Lo que se reporta",
                             "Como pide el algoritmo: la raíz aproximada, su residuo |f(x)|, las iteraciones y el error final."))

    # La derivada que se uso (o que se compara, en la secante)
    with caja("caja").style("margin-top:14px; padding:14px 18px") as caja_derivada:
        origen = ("escrita por el usuario" if r.get("derivada_escrita") else "calculada automáticamente")
        if vista.USA_DERIVADA:
            html(f'<div class="etiqueta" style="margin:0 0 6px">Derivada usada en la fórmula ({origen})</div>')
        else:
            html('<div class="etiqueta" style="margin:0 0 6px">Derivada (la secante no la usa; se muestra para comparar)</div>')
        with caja("fila").style("align-items:center; gap:18px"):
            if e.formula_derivada:
                html(f'<img src="{e.formula_derivada}" alt="f\'(x)">', "formula-img")
            else:
                html(f'<b class="mono">f\'(x) = {escapar(r["derivada_texto"] or "—")}</b>')
            datos = [f"f'(x) = <b>{escapar(r['derivada_texto'] or '—')}</b>"]
            if r["derivada_raiz"] is not None:
                datos.append(f"f'({numero(r['raiz'], d)}) = <b>{con_signo(r['derivada_raiz'], d)}</b>")
            if r.get("df_x0") is not None:
                datos.append(f"f'(x₀) = f'({r['x0']:g}) = <b>{con_signo(r['df_x0'], d)}</b>")
            html('<div class="texto-suave mono">' + "<br>".join(datos) + "</div>")
    vista.pasos_guia.append((caja_derivada, "La derivada",
                             "La expresión de f'(x) y su valor en la raíz: si f'(raíz) ≈ 0 la raíz es múltiple y el método se vuelve lento."))

    # ¿Converge o diverge? (definiciones de la presentacion)
    v = r["veredicto"]
    tipo_aviso = {"converge": "exito", "lenta": "advertencia", "diverge": "error"}[v["tipo"]]
    veredicto = aviso(f'<div style="font-size:17px; font-weight:800; margin-bottom:2px">El método {escapar(v["titulo"])}</div>'
                      f'{escapar(v["explicacion"])}', tipo_aviso, es_html=True).style("margin-top:14px")
    vista.pasos_guia.append((veredicto, "¿Converge o diverge?",
                             "Convergencia: las aproximaciones se acercan a una raíz. Divergencia: no se acercan o se alejan."))

    raiz, residuo, n = numero(r["raiz"], d), numero(r["residuo"], d), r["total_iteraciones"]
    if v["tipo"] == "converge":
        texto = (f"Después de <b>{n}</b> iteraciones la sucesión se estabiliza cerca de <b class=\"mono\">x ≈ {con_signo(r['raiz'], d)}</b>. "
                 f"Al sustituir este valor en la función original, |f({raiz})| = <span class=\"mono\">{residuo}</span> ≈ 0, "
                 "así que es una buena aproximación de la raíz de f(x) = 0.")
    elif v["tipo"] == "lenta":
        texto = (f"Las aproximaciones se acercan a <b class=\"mono\">x ≈ {con_signo(r['raiz'], d)}</b>, pero en {n} iteraciones "
                 f"el error no llegó a ser menor que E = {r['tolerancia']:g}. Residuo |f({raiz})| = <span class=\"mono\">{residuo}</span>.")
    else:
        texto = (f"<b>No se encontró la raíz.</b> La última aproximación calculada es x = <span class=\"mono\">{con_signo(r['raiz'], d)}</span> "
                 f"con residuo |f(x)| = <span class=\"mono\">{residuo}</span>. La convergencia de los métodos abiertos es local: "
                 "depende de la función y del valor inicial. Vuelva al paso 2 y elija un valor más cercano a la raíz.")
    frase = html(
        f"<b>Conclusión.</b> {texto}<br>"
        f'Error final: {escapar(nombre_error)} = <span class="mono">{numero(r["error_final"], d)}</span> '
        f'({escapar(ESTADOS[r["estado"]])})'
        + (f' &nbsp;·&nbsp; Cifras significativas correctas: <b>{r["cifras_significativas"]}</b>'
           if r["cifras_significativas"] is not None and v["tipo"] == "converge" else ""),
        "frase-final")
    frase.style("margin-top:10px")
    vista.pasos_guia.append((frase, "Conclusión", "Raíz aproximada, residuo e iteraciones, como pide el algoritmo."))

    # La clase recomienda revisar los DOS criterios aunque el metodo se detenga con uno
    filas = "".join(
        f'<tr><td style="text-align:left"><b>{escapar(c["nombre"])}</b></td><td class="mono">{escapar(c["formula"])}</td>'
        f'<td class="mono">{numero(c["valor"], d)}</td><td>{"✓ sí" if c["cumple"] else "✗ no"}</td></tr>'
        for c in r["ambos_criterios"])
    filas += (f'<tr><td style="text-align:left"><b>Máximo de iteraciones</b></td><td class="mono">n ≤ {r["max_iteraciones"]}</td>'
              f'<td class="mono">{n}</td><td>{"se llegó al máximo" if r["estado"] == "maximo" else "no se llegó"}</td></tr>')
    with caja().style("margin-top:14px") as criterios:
        html('<div class="etiqueta" style="margin:0 0 6px">Revisión de los dos criterios de parada '
             f'(tolerancia E = {r["tolerancia"]:g})</div>')
        html('<table class="tabla"><thead><tr><th style="text-align:left">Criterio</th><th>Fórmula</th><th>Valor final</th>'
             f'<th>¿Menor que E?</th></tr></thead><tbody>{filas}</tbody></table>', "contenedor-tabla")
        html(f'<div class="texto-suave" style="margin-top:6px">El método se detuvo con el criterio elegido '
             f'({escapar(r["criterio_texto"])} &lt; E) o con el máximo de iteraciones, lo que ocurriera primero. '
             "Como recomienda la clase, aquí se revisan los dos: un residuo pequeño confirma que el valor casi cumple "
             "f(x) = 0 y un cambio pequeño confirma que la sucesión ya se estabilizó.</div>")
    vista.pasos_guia.append((criterios, "Los dos criterios",
                             "|xₙ₊₁ − xₙ| < E (cambio) y |f(xₙ₊₁)| < E (residuo), además del máximo de iteraciones."))
    if r.get("comparacion"):
        otro, desde, n_otro, convergio = r["comparacion"]
        frase_otro = f"{n_otro} iteraciones" + ("" if convergio else " (sin llegar a E)")
        aviso(f"Comparación: {otro} desde {desde}, con la misma tolerancia y criterio, necesita {frase_otro}; "
              f"{vista.NOMBRE} usó {r['total_iteraciones']}. Newton suele ser más rápido cerca de la raíz, "
              "pero necesita la derivada.", "info").style("margin-top:10px")

    subtitulo("Comprobaciones del algoritmo")
    with caja("rejilla dos") as comprobaciones:
        for numero_regla, c in enumerate(r["comprobaciones"], start=1):
            with caja("comprobacion"):
                html("✓" if c["correcto"] else "!", "marca-c " + ("si" if c["correcto"] else "no"))
                html(f'<div style="font-weight:800; font-size:13.5px">{numero_regla}. {escapar(c["titulo"])}</div>'
                     f'<div class="texto-suave">{escapar(c["detalle"])}</div>')
    vista.pasos_guia.append((comprobaciones, "Comprobaciones",
                             "Residuo de la raíz, tolerancia o máximo de iteraciones, división entre cero y convergencia."))

    with caja("rejilla dos").style("margin-top:6px"):
        with caja():
            subtitulo("Gráfica con la raíz encontrada" if r["convergio"] else "Gráfica de f(x)")
            imagen(e.grafica_general or e.grafica_escalera)
        with caja():
            subtitulo("El error en cada iteración")
            imagen(e.grafica_error)
    subtitulo("Cómo se acercan las aproximaciones (" + ("tangentes" if r["metodo"] == "newton" else "secantes") + ")")
    imagen(e.grafica_escalera)

    with caja("fila").style("justify-content:space-between; margin-top:18px"):
        boton("Anterior", lambda: vista.ir_a(4), icono="arrow_back")
        boton("Probar otra función", lambda: vista.ir_a(1), icono="restart_alt", principal=True)
