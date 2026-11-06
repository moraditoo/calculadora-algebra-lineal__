# frontend/modulos/vectores.py
# Operaciones con vectores de Rⁿ y combinacion lineal.
from matplotlib.figure import Figure
from nicegui import ui

from backend.algebra_lineal.vectores import OperacionesVectores
from backend.metodos_numericos.graficas import ACENTO, SUAVE, TINTA, a_svg
from .. import guia
from ..componentes import (aviso, boton, caja, campo, encabezado, entero, html, imagen, lista_pasos, matriz,
                           resaltado, selector, subtitulo, tarjeta)
from ..formato import escapar

VERDE = "#8e8e93"  # segundo vector en gris medio


def a_numero(texto):
    """Acepta enteros, decimales y fracciones como '3/2'."""
    try:
        partes = str(texto).split("/")
        return float(partes[0]) / (float(partes[1]) if len(partes) > 1 else 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


def grafica_r2(vectores, paralelogramo=False):
    """Vectores de R² dibujados desde el origen."""
    fig = Figure(figsize=(6.4, 4.4), dpi=100)
    ax = fig.add_subplot()
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(True, color=SUAVE, alpha=0.25)
    ax.tick_params(colors=TINTA, labelsize=9)
    limite = 1.25 * max([1.0] + [abs(v) for vec in vectores for v in (vec["x"], vec["y"])])
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    ax.set_aspect("equal")
    ax.axhline(0, color=TINTA, linewidth=1, alpha=0.6)
    ax.axvline(0, color=TINTA, linewidth=1, alpha=0.6)
    if paralelogramo and len(vectores) >= 3:
        v1, v2, r = vectores
        ax.plot([v1["x"], r["x"], v2["x"]], [v1["y"], r["y"], v2["y"]], color=SUAVE, linestyle=(0, (4, 3)), linewidth=1.2)
    for vec in vectores:
        ax.annotate("", xy=(vec["x"], vec["y"]), xytext=(0, 0),
                    arrowprops={"arrowstyle": "-|>", "color": vec["color"], "lw": 2.4, "mutation_scale": 16})
        ax.annotate(f"{vec['etiqueta']} ({vec['x']:g}, {vec['y']:g})", (vec["x"], vec["y"]), xytext=(6, 6),
                    textcoords="offset points", color=vec["color"], fontsize=9.5, fontweight="bold")
    return a_svg(fig)


def construir():
    estado = {"n": "3", "k": "2", "vectores": [["1", "-2", "-5"], ["2", "5", "6"]], "b": [["7"], ["4"], ["-3"]],
              "escalar": "5", "a": 0, "b_idx": 1}
    objetivos = {}

    with tarjeta():
        encabezado("Operaciones en Rⁿ y combinación lineal",
                   "Defina los vectores por columnas y el vector objetivo b para saber si es combinación lineal.", "north_east",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("dimensiones"), "Tamaño", "n es la dimensión de cada vector y k cuántos vectores hay."),
                       (objetivos.get("vectores"), "Vectores", "Cada columna es un vector; la columna morada es b."),
                       (objetivos.get("operaciones"), "Operaciones", "Suma, resta, producto por escalar o combinación lineal."),
                   ]))
        with caja("fila") as objetivos["dimensiones"]:
            campo("Dimensión n", estado["n"], lambda v: estado.update(n=v), ancho="110px")
            campo("Cantidad k", estado["k"], lambda v: estado.update(k=v), ancho="110px")
            boton("Reconstruir cuadrícula", lambda: reconstruir(), icono="grid_on")

        @ui.refreshable
        def cuadricula():
            with caja("caja desplazable").style("margin-top:14px; display:flex; gap:12px; overflow-x:auto") as objetivos["vectores"]:
                for indice, vector in enumerate(estado["vectores"]):
                    columna_vector(f"v{indice + 1}", vector, destacada=False)
                with caja().style("border-left:2px solid rgba(0,0,0,0.15); padding-left:12px"):
                    columna_vector("b", [fila[0] for fila in estado["b"]], destacada=True)

        def columna_vector(nombre, valores, destacada):
            def guardar(i, v):
                if destacada:
                    estado["b"][i][0] = v
                else:
                    valores[i] = v

            with caja().style("display:flex; flex-direction:column; gap:6px; align-items:center; min-width:70px"):
                html(escapar(nombre), "mono").style(f"font-weight:800; font-size:12px; color:{'#1d1d1f' if destacada else '#3a3a3c'}")
                for i, valor in enumerate(valores):
                    entrada = ui.input(value=valor, on_change=lambda e, i=i: guardar(i, e.value or ""))
                    entrada.props("borderless dense").classes("campo celda-entrada" + (" destacada" if destacada else "")).style("width:70px")

        def reconstruir():
            dimension, cantidad = entero(estado["n"], 1, 10, 3), entero(estado["k"], 1, 10, 2)
            estado["vectores"] = [[estado["vectores"][i][j] if i < len(estado["vectores"]) and j < len(estado["vectores"][i]) else "0"
                                   for j in range(dimension)] for i in range(cantidad)]
            estado["b"] = [[estado["b"][j][0] if j < len(estado["b"]) else "0"] for j in range(dimension)]
            estado.update(n=str(dimension), k=str(cantidad), a=0, b_idx=1 if cantidad > 1 else 0)
            cuadricula.refresh()
            operaciones.refresh()
            resultado.refresh()

        cuadricula()

        @ui.refreshable
        def operaciones():
            opciones = {i: f"v{i + 1}" for i in range(len(estado["vectores"]))}
            with caja("fila separador").style("padding-top:16px; margin-top:16px") as objetivos["operaciones"]:
                selector("Vector A", opciones, estado["a"], lambda v: estado.update(a=v), ancho="110px")
                selector("Vector B", opciones, estado["b_idx"], lambda v: estado.update(b_idx=v), ancho="110px")
                boton("A + B", lambda: operar("suma"))
                boton("A − B", lambda: operar("resta"))
                campo("Escalar c", estado["escalar"], lambda v: estado.update(escalar=v), ancho="100px")
                boton("c · A", lambda: operar("escalar"))
                boton("¿b es combinación lineal?", lambda: operar("combinacion"), icono="help_outline", principal=True)

        operaciones()

    @ui.refreshable
    def resultado(op=None, datos=None, error=None):
        if error:
            aviso(error, "error")
        if not datos:
            return
        with tarjeta("escalonado"):
            if op == "combinacion":
                resaltado("Combinación lineal",
                          "Sí, b es combinación lineal" if datos["es_combinacion"] else "No, b no es combinación lineal",
                          detalle=escapar(datos["detalles"]))
                subtitulo("Fundamento algebraico")
                lista_pasos(datos["pasos_teoricos"])
                if datos.get("pasos_matriz"):
                    subtitulo("Reducción de la matriz aumentada")
                    with caja("rejilla dos"):
                        for descripcion, mat in datos["pasos_matriz"]:
                            corte = len(mat[0]) - 1
                            with caja("caja"):
                                html(f'<div style="font-size:12.5px; font-weight:700; margin-bottom:8px">{escapar(descripcion)}</div>')
                                matriz(mat, corte=corte, estilo=lambda i, j, c=corte: "morado" if j == c else "")
            else:
                resaltado("Vector resultante", "[" + ", ".join(datos["resultado"]) + "]")
                subtitulo("Desglose paso a paso")
                lista_pasos(datos["pasos"])
                if len(datos["resultado"]) == 2:
                    va, vb = estado["vectores"][estado["a"]], estado["vectores"][estado["b_idx"]]
                    dibujo = [
                        {"x": a_numero(va[0]), "y": a_numero(va[1]), "etiqueta": f"v{estado['a'] + 1}", "color": TINTA},
                        {"x": a_numero(vb[0]), "y": a_numero(vb[1]), "etiqueta": f"v{estado['b_idx'] + 1}", "color": VERDE},
                        {"x": a_numero(datos["resultado"][0]), "y": a_numero(datos["resultado"][1]), "etiqueta": "R", "color": ACENTO},
                    ]
                    subtitulo("Representación geométrica en R²")
                    imagen(grafica_r2(dibujo, paralelogramo=op == "suma")).style("max-width:640px")

    def operar(op):
        vectores = estado["vectores"]
        v1, v2 = vectores[estado["a"]], vectores[estado["b_idx"]]
        try:
            if op == "suma":
                datos = OperacionesVectores.suma(v1, v2)
            elif op == "resta":
                datos = OperacionesVectores.resta(v1, v2)
            elif op == "escalar":
                datos = OperacionesVectores.producto_escalar(estado["escalar"], v1)
            else:
                datos = OperacionesVectores.combinacion_lineal(vectores, [fila[0] for fila in estado["b"]])
            resultado.refresh(op, datos)
        except Exception as error:
            resultado.refresh(error=str(error))

    resultado()
