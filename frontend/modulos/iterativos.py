# frontend/modulos/iterativos.py
# Metodos iterativos para A·x = b: Jacobi y Gauss-Seidel (con la comparacion de ambos).
# Arriba se escribe el sistema y los parametros; abajo, el resultado con cuatro vistas:
# tabla de iteraciones, paso a paso (como en las diapositivas), graficas y convergencia.
from fractions import Fraction

from nicegui import run, ui

from backend.algebra_lineal import iterativos as metodo
from backend.algebra_lineal.fracciones import format_frac
from backend.algebra_lineal.parser_ecuaciones import parse_ecuaciones
from .. import guia
from ..componentes import (area_texto, aviso, boton, caja, campo, cuadricula_entrada, desplegable, encabezado, grafica,
                           html, matriz_tex, numero_vivo, redimensionar, segmentado, selector, selector_numero, subtitulo,
                           tarjeta, tex, vector_tex)
from ..formato import escapar
from .ecuaciones import texto_desde_matriz

# Paleta categorica validada (orden fijo): una por incognita; Jacobi = 1, Gauss-Seidel = 2
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
COLOR_METODO = {"jacobi": COLORES[0], "gauss_seidel": COLORES[1]}

EJEMPLOS = [
    ("Ejemplo de clase", "10x1 - x2 + 2x3 = 6\n-x1 + 11x2 - x3 + 3x4 = 25\n2x1 - x2 + 10x3 - x4 = -11\n3x2 - x3 + 8x4 = 15"),
    ("Actividad en parejas", "8x1 - x2 + x3 = 8\n-x1 + 10x2 - 2x3 + x4 = 7\nx1 - 2x2 + 9x3 - x4 = -4\nx2 - x3 + 7x4 = 5"),
    ("Hay que reordenar", "x + 10y + z = 12\n10x + y + z = 12\nx + y + 10z = 12"),
    ("No converge", "x + 2y = 5\n3x + y = 5"),
]
METODOS = [("ambos", "Comparar ambos"), ("jacobi", "Jacobi"), ("gauss_seidel", "Gauss-Seidel")]
VISTAS = [("tabla", "Iteraciones"), ("pasos", "Paso a paso"), ("graficas", "Gráficas"), ("analisis", "Despeje y convergencia")]


def corto(valor):
    """Errores y residuos: notacion cientifica cuando son muy pequenos."""
    if valor is None:
        return "—"
    if valor == 0:
        return "0"
    texto = f"{valor:.2e}" if abs(valor) < 1e-3 or abs(valor) >= 1e6 else f"{valor:.6f}"
    return texto.replace("-", "−")


def construir():
    return VistaIterativos()


class VistaIterativos:
    def __init__(self):
        self.e = {
            "modo": "ecuaciones", "texto": EJEMPLOS[0][1], "n": 4,
            "matriz": [["10", "-1", "2", "0", "6"], ["-1", "11", "-1", "3", "25"],
                       ["2", "-1", "10", "-1", "-11"], ["0", "3", "-1", "8", "15"]],
            "metodo": "ambos", "x0": "", "tolerancia": "0.000001", "max": "100", "criterio": "cambio",
            "decimales": 6, "reordenar": True,
        }
        self.r = None            # resultado del backend
        self.error = None
        self.vista = "tabla"
        self.metodo_vista = "gauss_seidel"
        self.k = 1               # iteracion que se ve en "Paso a paso"
        self.objetivos = {}

        with tarjeta():
            encabezado("Jacobi y Gauss-Seidel",
                       "Métodos iterativos para A·x = b: parten de x⁽⁰⁾ y se acercan a la solución en cada iteración.",
                       "autorenew", al_pedir_guia=self.guia)
            self.formulario()
        with caja("auto-animar"):
            self.resultado()

    # ------------------------------------------------------------------
    # Entrada
    # ------------------------------------------------------------------
    def guia(self):
        o = self.objetivos
        guia.iniciar([
            (o.get("metodo"), "Método", "Jacobi usa solo los valores de la iteración anterior; Gauss-Seidel usa de "
                                        "inmediato los recién calculados. «Comparar ambos» los ejecuta juntos."),
            (o.get("entrada"), "Sistema", "Una ecuación por línea (x, y, z, w o x1, x2…), o la matriz aumentada [A | b]."),
            (o.get("parametros"), "Parámetros", "x⁽⁰⁾ vacío = vector cero. Se detiene cuando el cambio es menor que ε "
                                                "o al llegar al máximo de iteraciones."),
            (o.get("resolver"), "Resolver", "Muestra la solución, la tabla de iteraciones, el paso a paso y las gráficas."),
        ])

    def formulario(self):
        e = self.e
        with caja("fila").style("justify-content:space-between; align-items:center") as self.objetivos["metodo"]:
            segmentado(METODOS, lambda: e["metodo"], lambda v: e.update(metodo=v))
            segmentado([("ecuaciones", "Ecuaciones"), ("matriz", "Matriz [A | b]")], lambda: e["modo"], self.cambiar_modo)

        with caja().style("margin-top:14px") as self.objetivos["entrada"]:
            self.entrada()
        with caja("muestras").style("margin-top:10px"):
            html("Ejemplos:", "muestras-titulo")
            for titulo, texto in EJEMPLOS:
                html(escapar(titulo), "muestra").on("click", lambda t=texto: self.usar_ejemplo(t))

        with caja("fila").style("margin-top:16px") as self.objetivos["parametros"]:
            campo("x⁽⁰⁾ inicial", e["x0"], lambda v: e.update(x0=v), ancho="170px", placeholder="0, 0, 0, 0")
            campo("Tolerancia ε", e["tolerancia"], lambda v: e.update(tolerancia=v), ancho="130px")
            campo("Máx. iteraciones", e["max"], lambda v: e.update(max=v), ancho="130px")
            selector("Detener cuando", {k: v for k, v in metodo.CRITERIOS.items()}, e["criterio"],
                     lambda v: e.update(criterio=v), ancho="230px")
        with desplegable("Más opciones").style("margin-top:12px"):
            with caja("fila").style("align-items:center; gap:22px"):
                selector_numero("Decimales", e["decimales"], 2, 10, lambda v: e.update(decimales=v))
                ui.switch("Reordenar las ecuaciones si no hay dominancia diagonal", value=e["reordenar"],
                          on_change=lambda ev: e.update(reordenar=ev.value)).classes("interruptor")

        with caja("fila").style("margin-top:16px"):
            self.objetivos["resolver"] = boton("Resolver", self.resolver, icono="play_arrow", principal=True)

    @ui.refreshable_method
    def entrada(self):
        e = self.e
        if e["modo"] == "ecuaciones":
            area_texto(e["texto"], lambda v: e.update(texto=v), filas=max(4, e["texto"].count("\n") + 1))
            html('<div class="texto-suave nota-entrada">Una ecuación por línea. Acepta x₁ o x1, fracciones (1/2) '
                 'y signos copiados de un PDF (−).</div>')
        else:
            selector_numero("Incógnitas n", e["n"], 2, 8, self.cambiar_n)
            nombres = [f"x{j + 1}" for j in range(e["n"])] + ["b"]
            with caja("caja").style("margin-top:10px"):
                cuadricula_entrada(e["matriz"], nombres, columna_destacada=e["n"])

    def cambiar_modo(self, modo):
        e = self.e
        if modo == e["modo"]:
            return
        # Se conserva el sistema al pasar de un modo al otro
        try:
            if modo == "matriz":
                matriz, _, n, _ = parse_ecuaciones(e["texto"])
                if len(matriz) == n and 2 <= n <= 8:
                    e.update(n=n, matriz=[[format_frac(v) for v in fila] for fila in matriz])
            else:
                e["texto"] = texto_desde_matriz(e["matriz"])
        except ValueError:
            pass
        e["modo"] = modo
        self.entrada.refresh()

    def cambiar_n(self, n):
        e = self.e
        filas = [fila[:-1] for fila in e["matriz"]]
        b = [[fila[-1]] for fila in e["matriz"]]
        filas = redimensionar(filas, n, n)
        b = redimensionar(b, n, 1)
        e.update(n=n, matriz=[filas[i] + b[i] for i in range(n)])
        self.entrada.refresh()

    async def usar_ejemplo(self, texto):
        self.e.update(modo="ecuaciones", texto=texto)
        self.entrada.refresh()
        await self.resolver()

    # ------------------------------------------------------------------
    # Calculo
    # ------------------------------------------------------------------
    def leer_sistema(self):
        e = self.e
        if e["modo"] == "ecuaciones":
            matriz, m, n, nombres = parse_ecuaciones(e["texto"])
            if m != n:
                raise ValueError(f"El sistema tiene {m} ecuaciones y {n} incógnitas: los métodos iterativos "
                                 "necesitan la misma cantidad.")
            A = [[format_frac(v) for v in fila[:-1]] for fila in matriz]
            b = [format_frac(fila[-1]) for fila in matriz]
            return A, b, nombres
        A = [fila[:-1] for fila in e["matriz"]]
        b = [fila[-1] for fila in e["matriz"]]
        return A, b, [f"x{j + 1}" for j in range(len(b))]

    async def resolver(self):
        e = self.e
        try:
            A, b, nombres = self.leer_sistema()
            metodos = ("jacobi", "gauss_seidel") if e["metodo"] == "ambos" else (e["metodo"],)
            self.r = await run.io_bound(metodo.resolver, A, b, nombres, e["x0"], metodos, e["tolerancia"], e["max"],
                                        e["criterio"], e["reordenar"], e["decimales"])
            self.error = None
        except ValueError as error:
            self.r, self.error = None, str(error)
        if self.r:
            disponibles = list(self.r["resultados"])
            if self.metodo_vista not in disponibles:
                self.metodo_vista = disponibles[-1]
            self.k = 1
        self.resultado.refresh()
        if self.r:
            ui.run_javascript("document.querySelector('.resultado-iterativo')?.scrollIntoView({behavior: 'smooth', block: 'start'})")

    # ------------------------------------------------------------------
    # Resultado
    # ------------------------------------------------------------------
    @ui.refreshable_method
    def resultado(self):
        if self.error:
            aviso(self.error, "error")
            return
        r = self.r
        if not r:
            return
        with tarjeta("escalonado resultado-iterativo"):
            with caja("rejilla dos" if len(r["resultados"]) == 2 else ""):
                for res in r["resultados"].values():
                    self.tarjeta_metodo(res)
            self.comparacion()
            self.diagnostico()
            self.selector_vistas()
            with caja("panel-vista auto-animar").style("margin-top:14px"):
                self.panel_vista()

    @ui.refreshable_method
    def selector_vistas(self):
        """Pestanas del resultado: al cambiar solo se redibujan ellas y su panel."""
        r = self.r
        with caja("fila").style("margin-top:18px; justify-content:space-between; align-items:center"):
            segmentado(VISTAS, lambda: self.vista, self.cambiar_vista, envolver=True)
            if len(r["resultados"]) == 2 and self.vista in ("tabla", "pasos"):
                segmentado([(m, metodo.METODOS[m]) for m in r["resultados"]], lambda: self.metodo_vista,
                           self.cambiar_metodo_vista)

    def cambiar_vista(self, vista):
        if vista == self.vista:
            return
        self.vista = vista
        self.selector_vistas.refresh()
        self.panel_vista.refresh()

    def cambiar_metodo_vista(self, valor):
        self.metodo_vista = valor
        self.k = min(self.k, self.r["resultados"][valor]["total"]) or 1
        self.panel_vista.refresh()

    def tarjeta_metodo(self, res):
        r, d = self.r, self.e["decimales"]
        estado = {
            "converge": (f"Converge en {res['total']} iteraciones", "exito", "check_circle"),
            "maximo": (f"Sin converger en {res['total']} iteraciones", "advertencia", "hourglass_bottom"),
            "diverge": ("Diverge", "error", "trending_up"),
        }[res["estado"]]
        with caja("resaltado resultado-metodo") as contenedor:
            contenedor.style(f"--color-metodo:{COLOR_METODO[res['metodo']]}")
            html(f'<div class="r-etiqueta"><span class="punto-metodo"></span>{escapar(res["nombre"])}</div>'
                 f'<span class="estado-metodo {estado[1]}"><span class="material-icons">{estado[2]}</span>'
                 f'{escapar(estado[0])}</span>')
            if res["estado"] == "diverge":
                html(f'<div class="texto-suave">{escapar(res["motivo"])}</div>')
            else:
                chips = "".join(
                    f'<span class="chip-solucion mono"><span class="nombre-var">{escapar(v)}</span> = '
                    f'{numero_vivo(metodo.num(x, d), d)}</span>'
                    for v, x in zip(r["nombres_bonitos"], res["solucion"]))
                html(f'<div class="solucion-vector">{chips}</div>')
                html(f'<div class="r-detalle mono">‖Δx‖∞ = {corto(res["cambio"])} · residuo ‖b − Ax‖∞ = '
                     f'{corto(res["residuo"])}</div>')
            if res.get("estimadas"):
                html(f'<div class="r-detalle">ρ = {res["radio"]:.3f} &lt; 1: sí converge, pero lento. Harían falta '
                     f'unas <b>{res["estimadas"]}</b> iteraciones; aumente el máximo.</div>')

    def comparacion(self):
        resultados = self.r["resultados"]
        if len(resultados) != 2:
            return
        j, g = resultados["jacobi"], resultados["gauss_seidel"]
        if j["convergio"] and g["convergio"]:
            diferencia = j["total"] - g["total"]
            if diferencia > 0:
                texto = (f"<b>Gauss-Seidel</b> llegó en {g['total']} iteraciones, <b>{diferencia} menos</b> que Jacobi "
                         f"({j['total']}): aprovecha de inmediato los valores recién calculados.")
            elif diferencia < 0:
                texto = (f"Aquí <b>Jacobi</b> necesitó {-diferencia} iteraciones menos ({j['total']} contra {g['total']}): "
                         "Gauss-Seidel no siempre es más rápido.")
            else:
                texto = f"Ambos métodos necesitaron {j['total']} iteraciones."
        elif g["convergio"]:
            texto = "Solo <b>Gauss-Seidel</b> converge con este sistema; Jacobi no."
        elif j["convergio"]:
            texto = "Solo <b>Jacobi</b> converge con este sistema; Gauss-Seidel no."
        else:
            texto = ("Ninguno de los dos converge con este sistema. Use un método directo (Gauss-Jordan en "
                     "«Sistemas lineales») o revise el orden de las ecuaciones.")
        aviso(texto, "info", es_html=True).style("margin-top:12px")

    def diagnostico(self):
        r = self.r
        chips = []
        if r["dominancia"]["estricta"]:
            chips.append(('check', "Diagonal estrictamente dominante: converge con cualquier x⁽⁰⁾", "si"))
        else:
            chips.append(('info', "No es diagonalmente dominante (la convergencia no está garantizada)", "no"))
        for res in r["resultados"].values():
            if res["radio"] is not None:
                signo = "<" if res["radio"] < 1 else "≥"
                chips.append(("functions", f"ρ(T) {res['nombre']} = {res['radio']:.4f} {signo} 1",
                              "si" if res["radio"] < 1 else "no"))
        html('<div class="diagnostico">' + "".join(
            f'<span class="chip-diagnostico {clase}"><span class="material-icons">{icono}</span>{escapar(texto)}</span>'
            for icono, texto, clase in chips) + "</div>")
        if r["reordenado"]:
            orden = ", ".join(f"E{i + 1}" for i in r["orden"])
            aviso(f"Se reordenaron las ecuaciones ({orden}) para que la diagonal sea "
                  f"{'dominante' if r['dominancia']['estricta'] else 'lo más fuerte posible'}: así cada incógnita se "
                  "despeja de la ecuación donde más pesa.", "info").style("margin-top:10px")

    @ui.refreshable_method
    def panel_vista(self):
        {"tabla": self.vista_tabla, "pasos": self.vista_pasos, "graficas": self.vista_graficas,
         "analisis": self.vista_analisis}[self.vista]()

    # Vista 1: tabla de iteraciones -------------------------------------
    def vista_tabla(self):
        r, d = self.r, self.e["decimales"]
        res = r["resultados"][self.metodo_vista]
        cabeza = "".join(f"<th>{escapar(v)}</th>" for v in ["k"] + r["nombres_bonitos"]) + \
            '<th class="criterio">Cambio ‖Δx‖∞</th><th>Residuo ‖b − Ax‖∞</th>'
        filas = []
        ultima = res["iteraciones"][-1]["k"]
        for it in res["iteraciones"]:
            clase = ' class="actual final"' if it["k"] == ultima and res["convergio"] else ""
            celdas = "".join(f"<td>{metodo.num(x, d)}</td>" for x in it["x"])
            filas.append(f'<tr{clase}><td>{it["k"]}</td>{celdas}<td>{corto(it["cambio"])}</td>'
                         f'<td>{corto(it["residuo"])}</td></tr>')
        html(f'<table class="tabla mono sin-mayusculas"><thead><tr>{cabeza}</tr></thead><tbody>{"".join(filas)}</tbody></table>',
             "contenedor-tabla")
        html(f'<div class="texto-suave" style="margin-top:8px">{escapar(res["motivo"])}</div>')

    # Vista 2: paso a paso (como las diapositivas) ------------------------
    def vista_pasos(self):
        r, d = self.r, self.e["decimales"]
        res = r["resultados"][self.metodo_vista]
        total = res["total"]
        if total == 0:
            aviso("No hay iteraciones que mostrar.", "info")
            return
        k = max(1, min(self.k, total))
        anterior, actual = res["iteraciones"][k - 1], res["iteraciones"][k]
        x_ant = ", ".join(metodo.num(v, d) for v in anterior["x"])
        with caja("navegador"):
            boton("", lambda: self.ir_a_iteracion(k - 1), icono="chevron_left", clases="redondo").props(
                "disable" if k <= 1 else "")
            html(f'Iteración <b>{k}</b> de {total}', "contador")
            boton("", lambda: self.ir_a_iteracion(k + 1), icono="chevron_right", clases="redondo").props(
                "disable" if k >= total else "")
            if total > 2:
                # Se cambia de iteracion al soltar (redibujar mientras se arrastra cortaria el gesto)
                deslizador = ui.slider(min=1, max=total, value=k).props("dense label").classes("deslizador-iteracion")
                deslizador.on("change", lambda ev: self.ir_a_iteracion(ev.args))
        if self.metodo_vista == "jacobi":
            explicacion = f"Se usan únicamente los valores de x⁽{k - 1}⁾ = ({x_ant}) en las {r['n']} fórmulas."
        else:
            explicacion = (f"Se parte de x⁽{k - 1}⁾ = ({x_ant}) y cada valor nuevo se usa de inmediato en las "
                           "fórmulas siguientes.")
        html(f'<div class="texto-suave" style="margin:12px 0 8px">{escapar(explicacion)}</div>')
        filas = "".join(
            f'<tr><td>{escapar(v)}⁽{k}⁾</td><td class="izquierda">{escapar(s)}</td><td><b>{metodo.num(x, d)}</b></td></tr>'
            for v, s, x in zip(r["nombres_bonitos"], actual["sustituciones"], actual["x"]))
        html('<table class="tabla mono tabla-pasos sin-mayusculas"><thead><tr><th>Componente</th><th class="izquierda">Cálculo</th>'
             f'<th>Resultado</th></tr></thead><tbody>{filas}</tbody></table>', "contenedor-tabla")
        vector = ", ".join(metodo.num(v, d) for v in actual["x"])
        html(f'<div class="vector-iteracion mono">x⁽{k}⁾ = ({escapar(vector)})</div>'
             f'<div class="texto-suave mono" style="margin-top:6px">‖x⁽{k}⁾ − x⁽{k - 1}⁾‖∞ = {corto(actual["cambio"])}'
             f' · residuo = {corto(actual["residuo"])}</div>')

    def ir_a_iteracion(self, k):
        self.k = int(k)
        self.panel_vista.refresh()

    # Vista 3: graficas (ECharts) ---------------------------------------
    def vista_graficas(self):
        r = self.r
        nombres = r["nombres_bonitos"]
        with caja("rejilla dos graficas-iterativas"):
            for res in r["resultados"].values():
                series = []
                for i, nombre in enumerate(nombres):
                    serie = {
                        "name": nombre, "type": "line", "data": [round(it["x"][i], 10) for it in res["iteraciones"]],
                        "symbolSize": 8, "lineStyle": {"width": 2}, "color": COLORES[i % len(COLORES)],
                        "endLabel": {"show": len(nombres) <= 4, "formatter": "{a}", "color": "#5f6368", "fontWeight": 700},
                        "emphasis": {"focus": "series"},
                    }
                    if r["exacta"] is not None:
                        serie["markLine"] = {"silent": True, "symbol": "none", "label": {"show": False},
                                             "lineStyle": {"type": "dashed", "width": 1, "color": "#9aa0a6"},
                                             "data": [{"yAxis": round(r["exacta"][i], 10)}]}
                    series.append(serie)
                with caja("caja"):
                    html(f'<div class="titulo-grafica">Evolución de las incógnitas · {escapar(res["nombre"])}</div>')
                    grafica({
                        "xAxis": {"type": "category", "name": "Iteración", "nameLocation": "middle", "nameGap": 26,
                                  "data": [it["k"] for it in res["iteraciones"]], **_eje()},
                        "yAxis": {"type": "value", "name": "Valor", "scale": True, **_eje(), "splitLine": _rejilla()},
                        "grid": {"left": 56, "right": 48, "top": 46, "bottom": 44},
                        "dataZoom": [{"type": "inside"}],
                        "series": series,
                    })
        # Comparacion del error (escala logaritmica), como la diapositiva 25
        con_exacta = r["exacta"] is not None
        campo_error = "error" if con_exacta else "cambio"
        series = []
        for clave, res in r["resultados"].items():
            datos = [[it["k"], max(it[campo_error], 1e-16)] for it in res["iteraciones"] if it[campo_error] is not None]
            series.append({"name": res["nombre"], "type": "line", "data": datos, "symbolSize": 8,
                           "symbol": "circle" if clave == "jacobi" else "rect", "lineStyle": {"width": 2},
                           "color": COLOR_METODO[clave], "endLabel": {"show": True, "formatter": "{a}",
                                                                      "color": "#5f6368", "fontWeight": 700}})
        titulo = "Error respecto a la solución exacta" if con_exacta else "Cambio entre iteraciones"
        with caja("caja").style("margin-top:12px"):
            html(f'<div class="titulo-grafica">{escapar(titulo)} · escala logarítmica</div>')
            grafica({
                "xAxis": {"type": "value", "name": "Iteración", "nameLocation": "middle", "nameGap": 26,
                          "minInterval": 1, **_eje(), "splitLine": {"show": False}},
                "yAxis": {"type": "log", "name": "Error", **_eje(), "splitLine": _rejilla(),
                          "axisLabel": {"color": "#5f6368", ":formatter": "v => v.toExponential(0)"}},
                "grid": {"left": 64, "right": 96, "top": 46, "bottom": 44},
                "series": series,
            }, alto="300px")

    # Vista 4: despeje y convergencia -----------------------------------
    def vista_analisis(self):
        r = self.r
        with caja("rejilla dos"):
            with caja("caja"):
                subtitulo("Despeje de cada incógnita").style("margin-top:0")
                if r["despejes"]:
                    for despeje in r["despejes"]:
                        tex(despeje["latex"], bloque=True, clases="despeje")
                else:
                    aviso("Hay un cero en la diagonal: no se puede despejar cada incógnita de su ecuación.", "error")
                html('<div class="texto-suave" style="margin-top:8px">Fórmula general</div>')
                tex(_FORMULA_GS if self.metodo_vista == "gauss_seidel" else _FORMULA_J, bloque=True, clases="despeje")
            with caja("caja"):
                subtitulo("Dominancia diagonal por filas").style("margin-top:0")
                filas = "".join(
                    f'<tr><td>{f["fila"]}</td><td>{escapar(f["diagonal"])}</td><td>{escapar(f["suma_texto"])}</td>'
                    f'<td class="{"positivo" if f["cumple"] else "negativo"}">{"Sí" if f["cumple"] else "No"}</td></tr>'
                    for f in r["dominancia"]["filas"])
                html('<table class="tabla mono sin-mayusculas"><thead><tr><th>Fila</th><th>|aᵢᵢ|</th><th>Suma fuera de la diagonal</th>'
                     f'<th>¿Cumple?</th></tr></thead><tbody>{filas}</tbody></table>', "contenedor-tabla")
                conclusion = ("El sistema es estrictamente diagonalmente dominante por filas: Jacobi y Gauss-Seidel "
                              "convergen con cualquier x⁽⁰⁾." if r["dominancia"]["estricta"] else
                              "No hay dominancia diagonal estricta. No es una condición necesaria: lo que decide es "
                              "el radio espectral ρ(T) de la matriz de iteración (converge si ρ < 1).")
                html(f'<div class="texto-suave" style="margin-top:10px">{escapar(conclusion)}</div>')
        with desplegable("Sistema usado (A·x = b)").style("margin-top:12px"):
            a_texto = [[format_frac(_fraccion(v)) for v in fila] for fila in r["A"]]
            incognitas = [metodo.nombre_latex(v) for v in r["nombres"]]
            tex(matriz_tex(a_texto) + vector_tex(incognitas) + "=" + vector_tex([format_frac(_fraccion(v)) for v in r["b"]]),
                bloque=True)


_FORMULA_J = r"x_i^{(k+1)} = \frac{b_i - \sum_{j \ne i} a_{ij}\, x_j^{(k)}}{a_{ii}}"
_FORMULA_GS = r"x_i^{(k+1)} = \frac{b_i - \sum_{j<i} a_{ij}\, x_j^{(k+1)} - \sum_{j>i} a_{ij}\, x_j^{(k)}}{a_{ii}}"


def _fraccion(valor):
    return Fraction(valor).limit_denominator(10000)


def _eje():
    return {"axisLine": {"lineStyle": {"color": "#c4c7cc"}}, "axisTick": {"show": False},
            "axisLabel": {"color": "#5f6368"}, "nameTextStyle": {"color": "#5f6368", "fontWeight": 600}}


def _rejilla():
    return {"lineStyle": {"color": "rgba(0,0,0,0.06)"}}
