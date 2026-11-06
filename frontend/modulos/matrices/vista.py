# frontend/modulos/matrices/vista.py
# Operaciones con matrices: inversa, determinante, Ax = b, suma, producto...
from nicegui import ui

from backend.algebra_lineal.matrices import OperacionesMatrices
from ... import guia
from ...componentes import (aviso, boton, caja, campo, cuadricula_entrada, desplegable_html, encabezado, entero, html,
                            lista_pasos, matriz, matriz_html, redimensionar, resaltado, subtitulo, tarjeta, tarjetas_opcion)
from ...formato import escapar
from .cofactores import nodo_html

OPERACIONES = [
    {"valor": "inversa", "titulo": "Inversa A⁻¹ [A | I]", "detalle": "Solo matriz A"},
    {"valor": "inversa_de_inversa", "titulo": "(A⁻¹)⁻¹ = A", "detalle": "Solo matriz A"},
    {"valor": "transponer", "titulo": "Transpuesta Aᵀ", "detalle": "Solo matriz A"},
    {"valor": "determinante", "titulo": "Determinante det(A)", "detalle": "Cofactores o LU"},
    {"valor": "escalar", "titulo": "Escalar c · A", "detalle": "Matriz A y una constante"},
    {"valor": "resolver_por_inversa", "titulo": "Resolver x = A⁻¹b", "detalle": "Requiere vector b"},
    {"valor": "suma", "titulo": "Suma A + B", "detalle": "Requiere matriz B"},
    {"valor": "resta", "titulo": "Resta A − B", "detalle": "Requiere matriz B"},
    {"valor": "multiplicar", "titulo": "Producto A × B", "detalle": "Requiere matriz B"},
]
TITULO = {o["valor"]: o["titulo"] for o in OPERACIONES}


def estimar_tiempo(n):
    if n <= 4:
        return "< 20 ms (inmediato)"
    return {5: "~50 - 100 ms", 6: "~200 - 400 ms", 7: "~800 - 1500 ms"}.get(n, "~3 - 6 segundos (precisión racional)")


def construir():
    e = {"op": "inversa", "metodo_det": "lu", "fa": 3, "ca": 3, "fb": 3, "cb": 1, "escalar": "2",
         "A": [["0", "1", "2"], ["1", "0", "3"], ["4", "-3", "8"]], "B": [["3"], ["7"], ["0"]], "comparacion": None}
    objetivos = {}

    def requiere_vector_b():
        return e["op"] == "resolver_por_inversa"

    def requiere_matriz_b():
        return e["op"] in ("suma", "resta", "multiplicar")

    def sincronizar_b():
        """La matriz B o el vector b toman el tamano que exige la operacion."""
        if requiere_vector_b():
            e.update(fb=e["fa"], cb=1)
        elif e["op"] in ("suma", "resta"):
            e.update(fb=e["fa"], cb=e["ca"])
        elif e["op"] == "multiplicar":
            e.update(fb=e["ca"], cb=max(e["cb"], 1))
        e["B"] = redimensionar(e["B"], e["fb"], e["cb"])

    def advertencia():
        fa, ca, fb, cb, op = e["fa"], e["ca"], e["fb"], e["cb"], e["op"]
        if op in ("inversa", "inversa_de_inversa") and fa != ca:
            return f"Teorema: la matriz debe ser cuadrada (n × n) para ser invertible. Dimensión actual: {fa}×{ca}."
        if op == "determinante" and fa != ca:
            return f"El determinante solo está definido para matrices cuadradas. Dimensión actual: {fa}×{ca}."
        if op == "resolver_por_inversa":
            if fa != ca:
                return f"Teorema: para aplicar x = A⁻¹b la matriz A debe ser cuadrada. Dimensión actual: {fa}×{ca}."
            if fb != fa or cb != 1:
                return f"El vector b debe ser columna ({fa} × 1)."
        if op in ("suma", "resta") and (fa != fb or ca != cb):
            return f"Las matrices deben tener dimensiones idénticas: ({fa}×{ca}) contra ({fb}×{cb})."
        if op == "multiplicar" and ca != fb:
            return f"Incompatibles: las columnas de A ({ca}) deben coincidir con las filas de B ({fb})."
        return None

    # ---------------- Dialogo para matrices grandes ----------------
    with ui.dialog() as dialogo, caja("vidrio tarjeta").style("max-width:430px"):
        texto_dialogo = html("")
        with caja("fila").style("justify-content:flex-end; margin-top:14px"):
            boton("Cancelar", dialogo.close)
            boton("Confirmar y generar", lambda: dialogo.submit(True), principal=True)

    async def pedir_dimension(filas, columnas, aplicar):
        if filas >= 5 or columnas >= 5:
            texto_dialogo.set_content(
                f'<h3 style="margin:0 0 8px; font-size:16px; font-weight:800; color:#1d1d1f">⚠ Matriz {filas} × {columnas}</h3>'
                '<p class="texto-suave">El cálculo con fracciones exactas tiene complejidad <b>O(n³)</b>.</p>'
                f'<div class="aviso advertencia mono">Tiempo estimado: {estimar_tiempo(max(filas, columnas))}</div>'
                '<p class="texto-suave">¿Desea confirmar el tamaño y generar la cuadrícula?</p>')
            if not await dialogo:
                return
        aplicar()

    # ---------------- Entrada ----------------
    with tarjeta():
        encabezado("Matrices y operaciones algebraicas",
                   "Seleccione la operación; la matriz B o el vector b se ajustan solos al tamaño que exige.", "grid_on",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("operaciones"), "Operación", "Elija qué calcular."),
                       (objetivos.get("dimensiones"), "Tamaño", "Filas y columnas de A (y de B cuando hace falta)."),
                       (objetivos.get("entrada"), "Valores", "Acepta enteros, decimales y fracciones como 3/4."),
                       (objetivos.get("ejecutar"), "Ejecutar", "Muestra el resultado con todo el procedimiento."),
                   ]))
        with caja() as objetivos["operaciones"]:
            tarjetas_opcion(OPERACIONES, lambda: e["op"], lambda v: cambiar_operacion(v), columnas="cinco")

        @ui.refreshable
        def controles():
            aviso_texto = advertencia()
            if aviso_texto:
                aviso(aviso_texto, "advertencia").style("margin-top:14px")

            with caja("fila").style("margin-top:14px; gap:22px") as objetivos["dimensiones"]:
                with caja("fila").style("gap:8px"):
                    campo_fa = campo("Filas A", str(e["fa"]), lambda v: None, ancho="90px")
                    campo_ca = campo("Columnas A", str(e["ca"]), lambda v: None, ancho="100px")
                    boton("Aplicar", lambda: cambiar_a(campo_fa.value, campo_ca.value), icono="check")
                if requiere_matriz_b():
                    with caja("fila").style("gap:8px"):
                        campo_fb = campo("Filas B", str(e["fb"]), lambda v: None, ancho="90px")
                        campo_cb = campo("Columnas B", str(e["cb"]), lambda v: None, ancho="100px")
                        boton("Aplicar", lambda: cambiar_b(campo_fb.value, campo_cb.value), icono="check")
                if requiere_vector_b():
                    html(f'Vector b: {e["fa"]} × 1 (sincronizado con las filas de A)', "chip").style("margin-bottom:4px")
                if e["op"] == "escalar":
                    campo("Escalar c", e["escalar"], lambda v: e.update(escalar=v), ancho="100px")

            with caja("caja fila").style("margin-top:14px; gap:26px; align-items:flex-start") as objetivos["entrada"]:
                with caja():
                    subtitulo(f"Matriz A ({e['fa']} × {e['ca']})")
                    cuadricula_entrada(e["A"])
                if requiere_matriz_b():
                    with caja().style("border-left:1px solid rgba(0,0,0,0.08); padding-left:22px"):
                        subtitulo(f"Matriz B ({e['fb']} × {e['cb']})")
                        cuadricula_entrada(e["B"])
                if requiere_vector_b():
                    with caja().style("border-left:2px solid rgba(0,0,0,0.15); padding-left:22px"):
                        subtitulo(f"Vector b ({e['fa']} × 1)")
                        cuadricula_entrada(e["B"], columna_destacada=0)

            if e["op"] == "determinante" and e["fa"] == e["ca"]:
                subtitulo("Método para calcular det(A)")
                actualizar_comparacion()
                metodos_determinante()

        @ui.refreshable
        def metodos_determinante():
            c = e["comparacion"]

            def extra(metodo):
                if not c:
                    return ""
                rapido = ' <span class="insignia verde">⚡ más rápido</span>' if c["recomendado"] == metodo else ""
                return f'{c[metodo]["ops"]:,} operaciones · {escapar(c[metodo]["complejidad"])}{rapido}'

            tarjetas_opcion([
                {"valor": "cofactor", "titulo": "Expansión por cofactores", "detalle": "Laplace: Σ a[i,j]·(−1)^(i+j)·det(M[i,j])", "extra": extra("cofactor")},
                {"valor": "lu", "titulo": "Descomposición LU", "detalle": "PA = LU  →  det(A) = (−1)^s · Π U[i,i]", "extra": extra("lu")},
            ], lambda: e["metodo_det"], lambda v: e.update(metodo_det=v), columnas="dos")
            if c:
                mejor = "Ambos métodos cuestan lo mismo." if c["recomendado"] == "empate" else \
                    f"Más rápido para esta matriz: {'Descomposición LU' if c['recomendado'] == 'lu' else 'Cofactores'}."
                aviso(f"<b>{mejor}</b> {escapar(c['mensaje'])}<br><span style='font-size:11.5px'>Referencia para una matriz "
                      f"{c['n']}×{c['n']} sin ceros: cofactores ≈ {c['cofactor']['ops_densa']:,} ops · LU ≈ {c['lu']['ops_densa']:,} ops.</span>",
                      "info", es_html=True).style("margin-top:10px")

        def actualizar_comparacion():
            try:
                e["comparacion"] = OperacionesMatrices.comparar_metodos_determinante(e["A"])
            except Exception:
                e["comparacion"] = None

        controles()

        with caja("fila").style("margin-top:16px") as objetivos["ejecutar"]:
            boton_ejecutar = boton("", lambda: ejecutar(), icono="play_arrow", principal=True)
            boton_comparar = boton("Actualizar comparación", lambda: (actualizar_comparacion(), metodos_determinante.refresh()),
                                   icono="bolt")
            boton_comparar.set_visibility(e["op"] == "determinante")

    def cambiar_operacion(valor):
        e["op"] = valor
        sincronizar_b()
        boton_ejecutar.set_text(f"Ejecutar: {TITULO[valor]}")
        boton_comparar.set_visibility(valor == "determinante")
        controles.refresh()
        resultado.refresh()

    async def cambiar_a(filas, columnas):
        f, c = entero(filas, 1, 10, e["fa"]), entero(columnas, 1, 10, e["ca"])

        def aplicar():
            e.update(fa=f, ca=c, A=redimensionar(e["A"], f, c))
            sincronizar_b()
            controles.refresh()
            resultado.refresh()
        await pedir_dimension(f, c, aplicar)

    async def cambiar_b(filas, columnas):
        f, c = entero(filas, 1, 10, e["fb"]), entero(columnas, 1, 10, e["cb"])

        def aplicar():
            e.update(fb=f, cb=c, B=redimensionar(e["B"], f, c))
            controles.refresh()
            resultado.refresh()
        await pedir_dimension(f, c, aplicar)

    boton_ejecutar.set_text(f"Ejecutar: {TITULO[e['op']]}")

    # ---------------- Resultados ----------------
    @ui.refreshable
    def resultado(op=None, d=None, error=None):
        if error:
            aviso(error, "error")
        if not d:
            return
        with tarjeta("escalonado"):
            if op == "inversa":
                resultado_inversa(d)
            elif op == "inversa_de_inversa":
                resultado_inversa_de_inversa(d)
            elif op == "resolver_por_inversa":
                resultado_resolver(d)
            elif op == "determinante":
                resultado_determinante(d)
            if d.get("resultado"):
                with caja("resaltado").style("display:block"):
                    html('<div class="r-etiqueta" style="margin-bottom:10px">Matriz resultante</div>')
                    matriz(d["resultado"], estilo=lambda i, j: "media")
                if d.get("pasos"):
                    subtitulo("Desglose elemento por elemento")
                    lista_pasos(d["pasos"])

    def resultado_inversa(d):
        if not d["invertible"]:
            aviso(f"<b>{escapar(d['motivo'])}</b><br>{escapar(d['detalle'])}", "error", es_html=True)
            return
        n = d.get("n") or len(d["inversa"])
        aviso(d["motivo"], "exito")
        with caja("rejilla dos"):
            with caja("resaltado").style("display:block"):
                html(f'<div class="r-etiqueta" style="margin-bottom:10px">Matriz inversa A⁻¹ ({n} × {n})</div>')
                matriz(d["inversa"], estilo=lambda i, j: "media")
            with caja("caja"):
                subtitulo(f"Comprobación A · A⁻¹ = I{n}")
                matriz(d["verificacion_identidad"], estilo=lambda i, j: "fuerte" if i == j else "tenue")
        html(desplegable_html(f"Demostración del producto A · A⁻¹ = I{n} entrada por entrada",
                              "".join(f'<div class="mono" style="font-size:12px">{escapar(l)}</div>' for l in d["detalles_verificacion"])))
        subtitulo("Transformación de [A | I] hacia [I | A⁻¹]")
        with caja("rejilla dos"):
            for descripcion, mat in d["pasos_matrices"]:
                corte = (len(mat[0]) if mat and mat[0] else n * 2) // 2
                with caja("caja"):
                    html(f'<div style="font-size:12.5px; font-weight:700; margin-bottom:8px">{escapar(descripcion)}</div>')
                    matriz(mat, corte=corte, compacta=True, estilo=lambda i, j, c=corte: "verde" if j >= c else "")

    def resultado_inversa_de_inversa(d):
        if not d["invertible"]:
            aviso(d["motivo"], "error")
            return
        aviso(d["teorema"], "exito")
        with caja("rejilla dos"):
            with caja("caja"):
                subtitulo("Primera inversa A⁻¹")
                matriz(d["A_inversa"])
            with caja("resaltado").style("display:block"):
                html('<div class="r-etiqueta" style="margin-bottom:10px">Inversa de la inversa (A⁻¹)⁻¹</div>')
                matriz(d["A_inversa_de_inversa"], estilo=lambda i, j: "media")

    def resultado_resolver(d):
        if not d["resuelto"]:
            aviso(f"{d['motivo']} — {d['detalle']}", "error")
            return
        aviso(d["teorema"], "exito")
        resaltado("Vector solución x = A⁻¹b", "x = [" + ", ".join(d["x_solucion"]) + "]")
        subtitulo("Cálculo del producto A⁻¹ · b")
        lista_pasos(d["pasos_multiplicacion"])

    def resultado_determinante(d):
        comparacion = d["comparacion"]
        otro = ""
        if comparacion["recomendado"] not in ("empate", d["metodo"]):
            otro = f'<br><span style="color:#1d1d1f">(el otro método habría usado {comparacion[comparacion["recomendado"]]["ops"]:,})</span>'
        resaltado(f"det(A) por {'descomposición LU' if d['metodo'] == 'lu' else 'cofactores'}", f"det(A) = {d['determinante']}",
                  derecha=f'<div style="text-align:right; font-size:12.5px; font-weight:700; color:#5f6368">'
                          f'{d["operaciones"]:,} operaciones aritméticas{otro}</div>')
        if d["determinante"] == "0":
            aviso("det(A) = 0 → la matriz es singular (no invertible).", "advertencia")

        if d["metodo"] == "cofactor" and d.get("arbol"):
            subtitulo("Expansión por cofactores paso a paso")
            html('<div class="leyenda"><span><i style="background:rgba(0,0,0,0.1);border:1px solid rgba(0,0,0,0.15)"></i>línea de expansión</span>'
                 '<span><i style="background:#fff;border:2px solid #3a3a3c"></i>elemento a[i,j]</span>'
                 '<span><i style="background:rgba(0,0,0,0.03);border:1px solid rgba(0,0,0,0.12)"></i>fila y columna eliminadas</span></div>')
            html(nodo_html(d["arbol"]), "caja desplazable").style("overflow-x:auto; margin-top:10px")
            if d["n"] > 4:
                html(f'<div class="texto-suave">Para orden {d["n"]} solo se despliegan los primeros niveles; '
                     'los menores restantes se muestran con su determinante.</div>')

        if d["metodo"] == "lu":
            with caja("rejilla tres"):
                for titulo, datos, estilo in (
                    ("P (permutación)", d["P"], None),
                    ("L (triangular inferior)", d["L"], lambda i, j: "media" if j <= i else "tenue"),
                    ("U (triangular superior)", d["U"], lambda i, j: "fuerte" if i == j else ("verde" if j > i else "tenue")),
                ):
                    with caja("caja"):
                        subtitulo(titulo)
                        matriz(datos, estilo=estilo)
            if d.get("comprobacion"):
                comp = d["comprobacion"]
                subtitulo("Comprobación: L × U = P × A")
                aviso("L × U coincide entrada por entrada con P × A: la factorización es correcta." if comp["coincide"]
                      else "L × U no coincide con P × A: la factorización no es válida.", "exito" if comp["coincide"] else "error")
                with caja("rejilla dos").style("margin-top:10px"):
                    for titulo, datos in (("L × U", comp["LU"]), ("P × A", comp["PA"])):
                        with caja("caja"):
                            subtitulo(titulo)
                            matriz(datos)
                html(desplegable_html("Ver comprobación entrada por entrada",
                                      "".join(f'<div class="mono" style="font-size:12px; white-space:pre">{escapar(l)}</div>'
                                              for l in comp["detalles"]))).style("margin-top:10px")
            subtitulo("Eliminación hacia U")
            with caja("rejilla dos"):
                for descripcion, mat in d["pasos_matrices"]:
                    with caja("caja"):
                        html(f'<div style="font-size:12.5px; font-weight:700; margin-bottom:8px">{escapar(descripcion)}</div>')
                        matriz(mat, compacta=True)

        titulo_pasos = "Ver desarrollo en texto" if d["metodo"] == "cofactor" else "Desarrollo paso a paso"
        html(desplegable_html(titulo_pasos, "".join(f'<div class="mono" style="font-size:12px; white-space:pre">{escapar(l)}</div>'
                                                    for l in d["pasos"]), abierto=d["metodo"] != "cofactor")).style("margin-top:12px")

    def ejecutar():
        op = e["op"]
        try:
            B = e["B"] if requiere_vector_b() or requiere_matriz_b() else None
            llamadas = {
                "suma": lambda: OperacionesMatrices.sumar(e["A"], B),
                "resta": lambda: OperacionesMatrices.restar(e["A"], B),
                "escalar": lambda: OperacionesMatrices.escalar(e["escalar"], e["A"]),
                "multiplicar": lambda: OperacionesMatrices.multiplicar(e["A"], B),
                "transponer": lambda: OperacionesMatrices.transponer(e["A"]),
                "inversa": lambda: OperacionesMatrices.calcular_inversa_gauss_jordan(e["A"]),
                "inversa_de_inversa": lambda: OperacionesMatrices.inversa_de_inversa(e["A"]),
                "resolver_por_inversa": lambda: OperacionesMatrices.resolver_por_inversa(e["A"], B),
                "determinante": lambda: OperacionesMatrices.determinante(e["A"], e["metodo_det"]),
            }
            resultado.refresh(op, llamadas[op]())
        except Exception as error:
            resultado.refresh(error=str(error))

    resultado()
