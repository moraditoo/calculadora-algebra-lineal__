# frontend/modulos/ecuaciones.py
# Sistemas de ecuaciones lineales A·X = B por Gauss-Jordan, Gauss o Gauss con pivoteo, con fracciones exactas.
# Primero se ve el resultado (forma matricial, determinante, solucion y comprobacion);
# el procedimiento completo queda en una seccion plegable.
from nicegui import ui

from backend.algebra_lineal.fracciones import format_frac
from backend.algebra_lineal.parser_ecuaciones import nombre_bonito, nombre_latex, parse_ecuaciones
from backend.algebra_lineal.sistemas import METODOS, resolver_sistema
from .. import guia
from ..componentes import (area_texto, aviso, boton, caja, cuadricula_entrada, desplegable, encabezado, html, lista_pasos,
                           matriz, matriz_tex, numero_vivo, redimensionar, segmentado, selector_numero, subtitulo,
                           tarjeta, tex, valor_tex, vector_tex)
from ..formato import escapar

EJEMPLOS = [
    ("3 × 3", "2x + y - z = 8\n-3x - y + 2z = -11\n-2x + y + 2z = -3"),
    ("4 × 4", "x + 4y - z + 3w = 6\n3x - 2y + z + 3w = 22\n-3x + 4y + 6z + 3w = 41\n-x + 3y + 4z + w = 22"),
    ("Infinitas soluciones", "x + 2y - z = 3\n2x + 4y - 2z = 6\nx - y + z = 1"),
    ("Sin solución", "x + y + z = 2\n2x + 2y + 2z = 5\nx - y = 0"),
]


def construir():
    e = {
        "metodo": "gauss_jordan", "modo": "ecuaciones", "m": 3, "n": 3, "texto": EJEMPLOS[0][1],
        "matriz": [["2", "1", "-1", "8"], ["-3", "-1", "2", "-11"], ["-2", "1", "2", "-3"]],
    }
    objetivos = {}

    with tarjeta():
        encabezado("Sistemas de ecuaciones lineales", "Escriba el sistema y se resuelve con fracciones exactas.",
                   "functions", al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("metodo"), "Método", "Gauss-Jordan llega a la forma reducida; Gauss y el pivoteo "
                                                           "escalonan y sustituyen hacia atrás."),
                       (objetivos.get("entrada"), "Sistema", "Una ecuación por línea con x, y, z, w (o x1, x2…), "
                                                             "o la matriz aumentada [A | B]."),
                       (objetivos.get("resolver"), "Resolver", "Muestra A·X = B, det(A), la solución y su comprobación."),
                   ]))
        with caja("fila").style("justify-content:space-between; align-items:center") as objetivos["metodo"]:
            segmentado(list(METODOS.items()), lambda: e["metodo"], lambda v: e.update(metodo=v))
            segmentado([("ecuaciones", "Ecuaciones"), ("matriz", "Matriz [A | B]")], lambda: e["modo"],
                       lambda v: cambiar_modo(v))

        @ui.refreshable
        def entrada():
            if e["modo"] == "ecuaciones":
                area_texto(e["texto"], lambda v: e.update(texto=v), filas=max(4, e["texto"].count("\n") + 1))
                html('<div class="texto-suave nota-entrada">Una ecuación por línea. Acepta fracciones (1/2), decimales '
                     'y signos copiados de un PDF (−).</div>')
            else:
                with caja("fila").style("gap:22px"):
                    selector_numero("Ecuaciones", e["m"], 1, 8, lambda v: redimensionar_matriz(m=v))
                    selector_numero("Incógnitas", e["n"], 1, 8, lambda v: redimensionar_matriz(n=v))
                with caja("caja").style("margin-top:10px"):
                    cuadricula_entrada(e["matriz"], [f"x{j + 1}" for j in range(e["n"])] + ["B"],
                                       columna_destacada=e["n"])

        with caja().style("margin-top:14px") as objetivos["entrada"]:
            entrada()
        with caja("muestras").style("margin-top:10px"):
            html("Ejemplos:", "muestras-titulo")
            for titulo, texto in EJEMPLOS:
                html(escapar(titulo), "muestra").on("click", lambda t=texto: usar_ejemplo(t))
        with caja("fila").style("margin-top:16px"):
            objetivos["resolver"] = boton("Resolver", lambda: resolver(), icono="play_arrow", principal=True)

    def cambiar_modo(modo):
        if modo == e["modo"]:
            return
        try:
            if modo == "matriz":
                datos, m, n, _ = parse_ecuaciones(e["texto"])
                if m <= 8 and n <= 8:
                    e.update(m=m, n=n, matriz=[[format_frac(v) for v in fila] for fila in datos])
            else:
                e["texto"] = texto_desde_matriz(e["matriz"])
        except ValueError:
            pass
        e["modo"] = modo
        entrada.refresh()

    def redimensionar_matriz(m=None, n=None):
        m, n = m or e["m"], n or e["n"]
        coeficientes = redimensionar([fila[:-1] for fila in e["matriz"]], m, n)
        b = redimensionar([[fila[-1]] for fila in e["matriz"]], m, 1)
        e.update(m=m, n=n, matriz=[coeficientes[i] + b[i] for i in range(m)])
        entrada.refresh()

    def usar_ejemplo(texto):
        e.update(modo="ecuaciones", texto=texto)
        entrada.refresh()
        resolver()

    # ---------------- Resultado ----------------
    @ui.refreshable
    def resultado(datos=None, error=None):
        if error:
            aviso(error, "error")
        if not datos:
            return
        tipo = datos["clasificacion"]["tipo"]
        nombres = datos["nombres"]
        with tarjeta("escalonado"):
            # 1) Solucion
            with caja("resaltado").style("display:block"):
                html(f'<div class="r-etiqueta">{escapar(datos["nombre_metodo"])}</div>')
                if tipo == "unica":
                    chips = "".join(
                        f'<span class="chip-solucion mono"><span class="nombre-var">{escapar(nombre_bonito(v))}</span>'
                        f' = {numero_vivo(x)}</span>' for v, x in zip(nombres, datos["solucion"]))
                    html(f'<div class="solucion-vector">{chips}</div>')
                elif tipo == "infinitas":
                    html('<div class="r-valor" style="font-size:20px">Infinitas soluciones</div>')
                    lista_pasos(datos["general"]).style("margin-top:10px")
                else:
                    html('<div class="r-valor" style="font-size:20px">Sin solución</div>')
                html(f'<div class="r-detalle">{escapar(datos["clasificacion"]["texto"])}</div>')

            # 2) Forma matricial y determinante
            with caja("rejilla dos").style("margin-top:12px"):
                with caja("caja"):
                    subtitulo("Forma matricial A·X = B").style("margin-top:0")
                    incognitas = [nombre_latex(v) for v in nombres]
                    tex(matriz_tex(datos["A"]) + vector_tex(incognitas) + "=" + vector_tex(datos["B"]), bloque=True,
                        clases="formula-ancha")
                with caja("caja"):
                    subtitulo("¿Solución única?").style("margin-top:0")
                    if datos["determinante"] is not None:
                        det = datos["determinante"]
                        relacion = r" \neq 0" if det != "0" else ""
                        tex(rf"\det(A) = {valor_tex(det)}{relacion}", bloque=True)
                        explicacion = ("Como det(A) ≠ 0, A es invertible y el sistema tiene solución única."
                                       if det != "0" else
                                       "Como det(A) = 0, A no es invertible: el sistema tiene infinitas soluciones o "
                                       "ninguna.")
                    else:
                        explicacion = (f"A no es cuadrada ({datos['m']} × {datos['n']}): se decide por el rango. "
                                       f"rango(A) = {datos['clasificacion']['rango']}, incógnitas = {datos['n']}.")
                    html(f'<div class="texto-suave">{escapar(explicacion)}</div>')

            # 3) Comprobacion
            if datos["verificacion"]:
                todas = all(v["coincide"] for v in datos["verificacion"])
                subtitulo("Comprobación en las ecuaciones originales")
                filas = "".join(
                    f'<div class="fila-comprobacion"><span class="marca-c {"si" if v["coincide"] else "no"}">'
                    f'{"✓" if v["coincide"] else "✗"}</span><span class="mono">{escapar(v["texto"])}</span>'
                    f'<span class="mono esperado">= {escapar(v["esperado"])}</span></div>'
                    for v in datos["verificacion"])
                html(filas, "lista-comprobacion")
                if todas:
                    html('<div class="texto-suave" style="margin-top:6px">Todas las ecuaciones se cumplen.</div>')

            # 4) Procedimiento (plegado)
            with desplegable(f"Procedimiento paso a paso ({len(datos['pasos']) - 1} operaciones)").style("margin-top:16px"):
                if datos["detalle"]:
                    subtitulo("Despeje final").style("margin-top:4px")
                    lista_pasos(datos["detalle"])
                subtitulo("Operaciones por fila")
                with caja("rejilla dos"):
                    for descripcion, mat, fila_cambio in datos["pasos"]:
                        corte = len(mat[0]) - 1
                        with caja("caja"):
                            html(f'<div class="titulo-paso">{escapar(descripcion)}</div>')
                            matriz(mat, corte=corte, compacta=True,
                                   estilo=lambda i, j, c=corte, f=fila_cambio: "fuerte" if i == f else
                                   ("morado" if j == c else ""))

    def resolver():
        try:
            if e["modo"] == "ecuaciones":
                datos_matriz, _, _, nombres = parse_ecuaciones(e["texto"])
            else:
                datos_matriz = e["matriz"]
                nombres = [f"x{j + 1}" for j in range(len(datos_matriz[0]) - 1)]
            resultado.refresh(resolver_sistema(datos_matriz, e["metodo"], nombres))
        except ValueError as error:
            resultado.refresh(error=str(error))

    with caja("auto-animar"):
        resultado()


def texto_desde_matriz(matriz):
    """[[2, 1, 8]] -> '2x1 + x2 = 8' (para pasar de la cuadricula al modo texto)."""
    lineas = []
    for fila in matriz:
        terminos = []
        for j, valor in enumerate(fila[:-1]):
            valor = str(valor).strip() or "0"
            if valor in ("0", "-0"):
                continue
            signo = "-" if valor.startswith("-") else "+"
            magnitud = valor.lstrip("+-")
            terminos.append(f"{signo} {'' if magnitud == '1' else magnitud}x{j + 1}")
        lineas.append(f"{' '.join(terminos).lstrip('+ ') or '0'} = {fila[-1]}")
    return "\n".join(lineas)
