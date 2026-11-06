# frontend/modulos/ecuaciones.py
# Sistemas de ecuaciones lineales por Gauss-Jordan, pivote o Gauss simple.
from nicegui import ui

from backend.algebra_lineal.gauss import MetodoGauss, format_frac
from backend.algebra_lineal.gauss_jordan import MetodoGaussJordan
from backend.algebra_lineal.metodo_pivote import MetodoPivote
from backend.algebra_lineal.parser_ecuaciones import parse_ecuaciones
from .. import guia
from ..componentes import (aviso, area_texto, boton, caja, campo, cuadricula_entrada, encabezado, entero, html,
                           lista_pasos, matriz, redimensionar, resaltado, segmentado, subtitulo, tarjeta, tarjetas_opcion)
from ..formato import escapar

METODOS = [
    {"valor": "gauss_jordan", "titulo": "Gauss-Jordan", "detalle": "Forma escalonada reducida (RREF): pivotes 1 y ceros en toda la columna."},
    {"valor": "pivote", "titulo": "Método del pivote", "detalle": "Pivoteo parcial por el mayor valor absoluto + sustitución regresiva."},
    {"valor": "gauss", "titulo": "Gauss simple", "detalle": "Matriz triangular superior (REF) + sustitución hacia atrás."},
]


def resolver_sistema(metodo, matriz_datos, m, n):
    """Aplica el metodo elegido. Devuelve (solver, pasos, matriz_final, solucion, detalle)."""
    if metodo == "gauss":
        solver = MetodoGauss()
        pasos, final = solver.eliminar(matriz_datos, m, n)
        extraer = solver.resolver_sustitucion_atras
    elif metodo == "pivote":
        solver = MetodoPivote()
        pasos, final = solver.resolver_por_pivote(matriz_datos, m, n)
        extraer = solver.resolver_sustitucion_atras
    else:
        solver = MetodoGaussJordan()
        pasos, final = solver.eliminar_gauss_jordan(matriz_datos, m, n)
        extraer = solver.extraer_solucion
    # Solo un sistema determinado tiene solucion unica
    if "Determinado" in solver.clasificar_sistema(final, m, n):
        solucion, detalle = extraer(final, m, n)
    else:
        solucion, detalle = None, []
    return solver, pasos, final, solucion, detalle


def construir():
    estado = {
        "metodo": "gauss_jordan", "modo": "cuadricula", "m": "3", "n": "3",
        "matriz": [["2", "1", "-1", "8"], ["-3", "-1", "2", "-11"], ["-2", "1", "2", "-3"]],
        "texto": "2x + y - z = 8\n-3x - y + 2z = -11\n-2x + y + 2z = -3",
    }
    objetivos = {}

    def nombre_metodo(valor):
        return next(x["titulo"] for x in METODOS if x["valor"] == valor)

    with tarjeta():
        encabezado("Sistemas de ecuaciones lineales", "Resuelve Ax = b con aritmética de fracciones exacta.", "functions",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("metodos"), "Método", "Elija cómo se va a resolver el sistema."),
                       (objetivos.get("modo"), "Forma de ingreso", "Matriz aumentada [A | b] o ecuaciones escritas como texto."),
                       (objetivos.get("entrada"), "Datos del sistema", "La última columna (morada) es el vector b."),
                       (objetivos.get("resolver"), "Resolver", "Muestra el diagnóstico, la solución y cada paso de reducción."),
                   ]))
        with caja() as objetivos["metodos"]:
            tarjetas_opcion(METODOS, lambda: estado["metodo"], lambda v: (estado.update(metodo=v), actualizar_boton()))

        with caja("fila separador").style("justify-content:space-between; padding-top:16px; margin-top:16px") as objetivos["modo"]:
            segmentado([("cuadricula", "Matriz aumentada"), ("texto", "Texto algebraico")],
                       lambda: estado["modo"], lambda v: (estado.update(modo=v), entrada.refresh()))

        @ui.refreshable
        def entrada():
            with caja().style("margin-top:14px") as objetivos["entrada"]:
                if estado["modo"] == "cuadricula":
                    with caja("fila").style("margin-bottom:12px"):
                        campo("Filas m", estado["m"], lambda v: estado.update(m=v), ancho="90px")
                        campo("Incógnitas n", estado["n"], lambda v: estado.update(n=v), ancho="110px")
                        boton("Generar", generar, icono="grid_on")
                    columnas = len(estado["matriz"][0]) - 1
                    with caja("caja"):
                        cuadricula_entrada(estado["matriz"], [f"x{j + 1}" for j in range(columnas)] + ["b"], columna_destacada=columnas)
                else:
                    area_texto(estado["texto"], lambda v: estado.update(texto=v), filas=4)

        def generar():
            filas, cols = entero(estado["m"], 1, 8, 3), entero(estado["n"], 1, 8, 3)
            estado.update(m=str(filas), n=str(cols), matriz=redimensionar(estado["matriz"], filas, cols + 1))
            entrada.refresh()

        entrada()

        def actualizar_boton():
            boton_resolver.set_text(f"Resolver con {nombre_metodo(estado['metodo'])}")

        with caja("fila").style("margin-top:16px"):
            boton_resolver = boton("", lambda: resolver(), icono="play_arrow", principal=True)
            objetivos["resolver"] = boton_resolver
        actualizar_boton()

    @ui.refreshable
    def resultado(datos=None, error=None):
        if error:
            aviso(error, "error")
        if not datos:
            return
        with tarjeta("escalonado"):
            resaltado("Diagnóstico del sistema", datos["clasificacion"],
                      derecha=f'<span class="chip azul">{escapar(nombre_metodo(datos["metodo"]))}</span>')
            if datos["solucion"]:
                subtitulo("Valores de las incógnitas")
                with caja("fila").style("gap:10px"):
                    for nombre, valor in datos["solucion"].items():
                        html(f"{escapar(nombre)} = <b>{escapar(valor)}</b>", "chip azul mono").style("font-size:14px; padding:8px 14px")
            with caja("rejilla dos"):
                if datos["detalle"]:
                    with caja():
                        subtitulo("Sustitución hacia atrás")
                        lista_pasos(datos["detalle"])
                if datos["verificacion"]:
                    with caja():
                        subtitulo("Comprobación en las ecuaciones originales")
                        lista_pasos(datos["verificacion"])
            subtitulo("Pasos de reducción")
            with caja("rejilla dos"):
                for descripcion, mat in datos["pasos"]:
                    corte = len(mat[0]) - 1 if mat and mat[0] else None
                    with caja("caja"):
                        html(f'<div style="font-size:12.5px; font-weight:700; margin-bottom:8px">{escapar(descripcion)}</div>')
                        matriz(mat, corte=corte, estilo=lambda i, j, c=corte: "morado" if j == c else "")

    def resolver():
        try:
            if estado["modo"] == "texto":
                datos_matriz, m, n, nombres = parse_ecuaciones(estado["texto"])
            else:
                datos_matriz = estado["matriz"]
                m, n = len(datos_matriz), len(datos_matriz[0]) - 1
                nombres = [f"x_{i + 1}" for i in range(n)]
            solver, pasos, final, solucion, detalle = resolver_sistema(estado["metodo"], datos_matriz, m, n)
            resultado.refresh({
                "metodo": estado["metodo"],
                "clasificacion": solver.clasificar_sistema(final, m, n),
                "solucion": {nombres[i]: format_frac(solucion[i]) for i in range(n)} if solucion else None,
                "detalle": detalle,
                "verificacion": solver.verificar_solucion(datos_matriz, solucion, m, n) if solucion else [],
                "pasos": pasos,
            })
        except Exception as error:
            resultado.refresh(error=str(error))

    resultado()
