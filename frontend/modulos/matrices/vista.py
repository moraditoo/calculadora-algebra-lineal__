# frontend/modulos/matrices/vista.py
# Operaciones con matrices: A⁻¹ y det(A), determinante (LU o cofactores), transpuesta, c·A,
# (A⁻¹)⁻¹, x = A⁻¹b, A + B, A − B y A × B.
# La matriz se escribe en la cuadricula o se pega como texto (por ejemplo copiada de un PDF).
import re

from nicegui import ui

from backend.algebra_lineal.matrices import OperacionesMatrices
from ... import guia
from ...componentes import (area_texto, aviso, boton, caja, campo, cuadricula_entrada, desplegable, encabezado, html,
                            lista_pasos, matriz, matriz_tex, numero_vivo, redimensionar, segmentado, selector_numero,
                            subtitulo, tarjeta, tex, valor_tex, vector_tex)
from ...formato import escapar
from .cofactores import nodo_html

# (valor, texto del selector, que necesita: "A" cuadrada, "AB" otra matriz, "Ab" vector b, "rect" A de cualquier tamano)
OPERACIONES = [
    ("inversa", "A⁻¹ y det(A)", "A"),
    ("determinante", "det(A)", "A"),
    ("transponer", "Aᵀ", "rect"),
    ("escalar", "c · A", "rect"),
    ("inversa_de_inversa", "(A⁻¹)⁻¹", "A"),
    ("resolver_por_inversa", "x = A⁻¹b", "Ab"),
    ("suma", "A + B", "AB"),
    ("resta", "A − B", "AB"),
    ("multiplicar", "A × B", "AB"),
]
NECESITA = {v: n for v, _, n in OPERACIONES}
NUMERO = re.compile(r"[-−]?\d+(?:[.,]\d+)?(?:/\d+)?")


def leer_texto_matriz(texto):
    """'[ -4 5 -4 5 ]' por linea (o separado por comas) -> lista de filas de textos."""
    filas = [NUMERO.findall(linea) for linea in (texto or "").splitlines()]
    filas = [[v.replace("−", "-").replace(",", ".") for v in fila] for fila in filas if fila]
    if not filas:
        raise ValueError("Pegue la matriz con una fila por línea, por ejemplo: [ -4 5 -4 5 ]")
    if len({len(f) for f in filas}) != 1:
        raise ValueError("Todas las filas deben tener la misma cantidad de números.")
    if len(filas) > 8 or len(filas[0]) > 8:
        raise ValueError("El tamaño máximo es 8 × 8.")
    return filas


def construir():
    e = {"op": "inversa", "metodo_det": "lu", "fa": 4, "ca": 4, "cb": 1, "escalar": "2", "modo": "cuadricula",
         "A": [["-4", "5", "-4", "5"], ["-3", "3", "-1", "3"], ["-3", "5", "1", "-1"], ["1", "-4", "-1", "-3"]],
         "B": [["1"], ["0"], ["0"], ["0"]], "texto": ""}
    objetivos = {}

    def cuadrada():
        return NECESITA[e["op"]] in ("A", "Ab")

    def sincronizar():
        """A se vuelve cuadrada si la operacion lo exige; B toma el tamano compatible con A."""
        if cuadrada() and e["fa"] != e["ca"]:
            e["ca"] = e["fa"]
            e["A"] = redimensionar(e["A"], e["fa"], e["ca"])
        necesita = NECESITA[e["op"]]
        if necesita == "Ab":
            filas_b, cols_b = e["fa"], 1
        elif e["op"] in ("suma", "resta"):
            filas_b, cols_b = e["fa"], e["ca"]
        else:
            filas_b, cols_b = e["ca"], e["cb"]
        e["B"] = redimensionar(e["B"], filas_b, cols_b)

    with tarjeta():
        encabezado("Matrices", "Elija la operación, escriba o pegue la matriz y calcule.", "grid_on",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("op"), "Operación", "«A⁻¹ y det(A)» calcula el determinante, la inversa y "
                                                          "comprueba que A·A⁻¹ = I."),
                       (objetivos.get("entrada"), "Matriz", "Cambie el tamaño con − y +, o elija «Pegar texto» para "
                                                            "copiar la matriz tal como viene en el ejercicio."),
                       (objetivos.get("calcular"), "Calcular", "El resultado aparece arriba; el procedimiento, plegado."),
                   ]))
        with caja() as objetivos["op"]:
            segmentado([(v, t) for v, t, _ in OPERACIONES], lambda: e["op"], lambda v: cambiar_operacion(v), envolver=True)

        @ui.refreshable
        def entrada():
            necesita = NECESITA[e["op"]]
            with caja("fila").style("align-items:flex-end; gap:22px; justify-content:space-between"):
                with caja("fila").style("gap:22px"):
                    if e["modo"] == "cuadricula":
                        if cuadrada():
                            selector_numero("Orden n", e["fa"], 1, 8, lambda v: cambiar_tamano(v, v))
                        else:
                            selector_numero("Filas de A", e["fa"], 1, 8, lambda v: cambiar_tamano(v, e["ca"]))
                            selector_numero("Columnas de A", e["ca"], 1, 8, lambda v: cambiar_tamano(e["fa"], v))
                        if e["op"] == "multiplicar":
                            selector_numero("Columnas de B", e["cb"], 1, 8, lambda v: cambiar_columnas_b(v))
                    if e["op"] == "escalar":
                        campo("Escalar c", e["escalar"], lambda v: e.update(escalar=v), ancho="110px")
                    if e["op"] == "determinante":
                        with caja():
                            html("Método", "etiqueta")
                            segmentado([("lu", "LU"), ("cofactor", "Cofactores")], lambda: e["metodo_det"],
                                       lambda v: e.update(metodo_det=v))
                segmentado([("cuadricula", "Cuadrícula"), ("texto", "Pegar texto")], lambda: e["modo"], lambda v: cambiar_modo(v))

            with caja("fila entrada-matrices").style("margin-top:12px; gap:22px; align-items:flex-start"):
                with caja("caja"):
                    subtitulo(f"Matriz A ({e['fa']} × {e['ca']})" if e["modo"] == "cuadricula" else "Matriz A").style(
                        "margin-top:0")
                    if e["modo"] == "cuadricula":
                        cuadricula_entrada(e["A"])
                    else:
                        area_texto(e["texto"] or texto_de(e["A"]), lambda v: e.update(texto=v), filas=5).style(
                            "min-width:280px")
                        html('<div class="texto-suave nota-entrada">Una fila por línea; sirven [ -4 5 -4 5 ], '
                             '«-4, 5, -4, 5» o fracciones como 3/4.</div>')
                if necesita in ("AB", "Ab"):
                    with caja("caja"):
                        titulo = "Vector b" if necesita == "Ab" else "Matriz B"
                        subtitulo(f"{titulo} ({len(e['B'])} × {len(e['B'][0])})").style("margin-top:0")
                        cuadricula_entrada(e["B"], columna_destacada=0 if necesita == "Ab" else None)

        with caja().style("margin-top:14px") as objetivos["entrada"]:
            entrada()
        with caja("fila").style("margin-top:16px"):
            objetivos["calcular"] = boton("Calcular", lambda: ejecutar(), icono="play_arrow", principal=True)

    def cambiar_operacion(valor):
        e["op"] = valor
        sincronizar()
        entrada.refresh()

    def cambiar_tamano(filas, columnas):
        e.update(fa=filas, ca=columnas, A=redimensionar(e["A"], filas, columnas), texto="")
        sincronizar()
        entrada.refresh()

    def cambiar_columnas_b(columnas):
        e["cb"] = columnas
        sincronizar()
        entrada.refresh()

    def cambiar_modo(modo):
        if modo == e["modo"]:
            return
        if modo == "cuadricula" and e["texto"]:
            try:
                usar_texto()
            except ValueError as error:
                ui.notify(str(error), type="warning", position="top")
        e["modo"] = modo
        e["texto"] = ""
        entrada.refresh()

    def usar_texto():
        """Pasa lo pegado a la matriz A (y ajusta el tamano)."""
        filas = leer_texto_matriz(e["texto"])
        e.update(A=filas, fa=len(filas), ca=len(filas[0]))
        sincronizar()

    # ---------------- Resultados ----------------
    @ui.refreshable
    def resultado(op=None, d=None, error=None):
        if error:
            aviso(error, "error")
        if not d:
            return
        with tarjeta("escalonado"):
            {"inversa": resultado_inversa, "inversa_de_inversa": resultado_inversa_de_inversa,
             "resolver_por_inversa": resultado_resolver, "determinante": resultado_determinante}.get(
                op, resultado_matriz)(d)

    def resultado_matriz(d):
        with caja("resaltado").style("display:block"):
            html('<div class="r-etiqueta">Resultado</div>')
            tex(matriz_tex(d["resultado"]), bloque=True, clases="formula-ancha")
        if d.get("pasos"):
            with desplegable("Cálculo elemento por elemento").style("margin-top:12px"):
                lista_pasos(d["pasos"])

    def bloque_determinante(det, detalle=""):
        with caja("resaltado"):
            html(f'<div><div class="r-etiqueta">Determinante</div>'
                 f'<div class="r-valor mono">det(A) = {numero_vivo(det)}</div>'
                 f'{f"<div class=r-detalle>{escapar(detalle)}</div>" if detalle else ""}</div>')
            estado = "invertible" if det != "0" else "singular"
            html(f'<span class="estado-metodo {"exito" if det != "0" else "error"}"><span class="material-icons">'
                 f'{"check_circle" if det != "0" else "block"}</span>A es {estado}</span>')

    def resultado_inversa(d):
        if d.get("determinante") is not None:
            bloque_determinante(d["determinante"], d["motivo"])
        if not d["invertible"]:
            aviso(f"{d['motivo']} {d['detalle']}", "error").style("margin-top:12px")
            return
        n = d["n"]
        with caja("rejilla dos").style("margin-top:12px"):
            with caja("caja"):
                subtitulo(f"Matriz inversa A⁻¹ ({n} × {n})").style("margin-top:0")
                tex(r"A^{-1} = " + matriz_tex(d["inversa"]), bloque=True, clases="formula-ancha")
            with caja("caja"):
                subtitulo(f"Comprobación A · A⁻¹ = I{_sub(n)}").style("margin-top:0")
                tex(r"A\,A^{-1} = " + matriz_tex(d["verificacion_identidad"]), bloque=True, clases="formula-ancha")
                if d["es_identidad"]:
                    html('<span class="chip-diagnostico si"><span class="material-icons">check</span>'
                         'El producto es la identidad: la inversa es correcta.</span>')
        with desplegable(f"Procedimiento: [A | I] → [I | A⁻¹] ({len(d['pasos_matrices']) - 1} operaciones)").style(
                "margin-top:12px"):
            with caja("rejilla dos"):
                for descripcion, mat in d["pasos_matrices"]:
                    with caja("caja"):
                        html(f'<div class="titulo-paso">{escapar(descripcion)}</div>')
                        matriz(mat, corte=n, compacta=True, estilo=lambda i, j: "verde" if j >= n else "")
        with desplegable("Comprobación entrada por entrada").style("margin-top:8px"):
            lista_pasos(d["detalles_verificacion"])

    def resultado_inversa_de_inversa(d):
        if not d["invertible"]:
            aviso(d["motivo"], "error")
            return
        aviso(d["teorema"], "exito")
        with caja("rejilla dos").style("margin-top:12px"):
            with caja("caja"):
                subtitulo("Primera inversa A⁻¹").style("margin-top:0")
                tex(matriz_tex(d["A_inversa"]), bloque=True, clases="formula-ancha")
            with caja("resaltado").style("display:block"):
                html('<div class="r-etiqueta">(A⁻¹)⁻¹</div>')
                tex(matriz_tex(d["A_inversa_de_inversa"]), bloque=True, clases="formula-ancha")
                if d["coincide"]:
                    html('<span class="chip-diagnostico si"><span class="material-icons">check</span>'
                         'Coincide con A</span>')

    def resultado_resolver(d):
        if not d["resuelto"]:
            aviso(f"{d['motivo']} {d['detalle']}", "error")
            return
        with caja("resaltado").style("display:block"):
            html('<div class="r-etiqueta">Solución x = A⁻¹·b</div>')
            chips = "".join(f'<span class="chip-solucion mono"><span class="nombre-var">x{_sub(i + 1)}</span> = '
                            f'{numero_vivo(v)}</span>' for i, v in enumerate(d["x_solucion"]))
            html(f'<div class="solucion-vector">{chips}</div><div class="r-detalle">{escapar(d["teorema"])}</div>')
        with caja("caja").style("margin-top:12px"):
            tex("x = " + matriz_tex(d["A_inversa"]) + vector_tex([fila[0] for fila in e["B"]]) + " = " +
                vector_tex(d["x_solucion"]), bloque=True, clases="formula-ancha")
        with desplegable("Producto A⁻¹ · b paso a paso").style("margin-top:12px"):
            lista_pasos(d["pasos_multiplicacion"])

    def resultado_determinante(d):
        metodo = "descomposición LU" if d["metodo"] == "lu" else "cofactores"
        bloque_determinante(d["determinante"], f"Por {metodo} · {d['operaciones']:,} operaciones aritméticas")
        if d["metodo"] == "lu":
            with caja("rejilla tres").style("margin-top:12px"):
                for titulo, datos in (("P", d["P"]), ("L", d["L"]), ("U", d["U"])):
                    with caja("caja"):
                        subtitulo(titulo).style("margin-top:0")
                        tex(matriz_tex(datos), bloque=True, clases="formula-ancha")
            diagonal = r" \cdot ".join(f"({valor_tex(v)})" for v in d["diagonal_U"])
            signo = "-" if d["intercambios"] % 2 else ""
            tex(rf"\det(A) = {signo}{diagonal} = {valor_tex(d['determinante'])}", bloque=True,
                clases="formula-ancha formula-final")
            with desplegable("Eliminación hacia U paso a paso").style("margin-top:12px"):
                with caja("rejilla dos"):
                    for descripcion, mat in d["pasos_matrices"]:
                        with caja("caja"):
                            html(f'<div class="titulo-paso">{escapar(descripcion)}</div>')
                            matriz(mat, compacta=True)
        elif d.get("arbol"):
            with desplegable("Expansión por cofactores", abierto=d["n"] <= 3).style("margin-top:12px"):
                html(nodo_html(d["arbol"]), "desplazable").style("overflow-x:auto")
                if d["n"] > 4:
                    html('<div class="texto-suave">Para orden mayor que 4 solo se despliegan los primeros niveles.</div>')
        with desplegable("Desarrollo en texto").style("margin-top:8px"):
            lista_pasos(d["pasos"], preformateado=True)

    def ejecutar():
        op = e["op"]
        try:
            if e["modo"] == "texto" and e["texto"]:
                usar_texto()
            A = e["A"]
            if cuadrada() and len(A) != len(A[0]):
                raise ValueError(f"Esta operación necesita una matriz cuadrada; A es {len(A)} × {len(A[0])}.")
            B = e["B"]
            llamadas = {
                "suma": lambda: OperacionesMatrices.sumar(A, B),
                "resta": lambda: OperacionesMatrices.restar(A, B),
                "escalar": lambda: OperacionesMatrices.escalar(e["escalar"], A),
                "multiplicar": lambda: OperacionesMatrices.multiplicar(A, B),
                "transponer": lambda: OperacionesMatrices.transponer(A),
                "inversa": lambda: OperacionesMatrices.calcular_inversa_gauss_jordan(A),
                "inversa_de_inversa": lambda: OperacionesMatrices.inversa_de_inversa(A),
                "resolver_por_inversa": lambda: OperacionesMatrices.resolver_por_inversa(A, B),
                "determinante": lambda: OperacionesMatrices.determinante(A, e["metodo_det"]),
            }
            resultado.refresh(op, llamadas[op]())
        except ValueError as error:
            resultado.refresh(error=str(error))

    with caja("auto-animar"):
        resultado()


def texto_de(matriz_valores):
    return "\n".join("[ " + "  ".join(str(v) for v in fila) + " ]" for fila in matriz_valores)


def _sub(n):
    return str(n).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
