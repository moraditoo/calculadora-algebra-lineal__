# frontend/modulos/inicio.py
# Pantalla principal. Tiene cuatro partes:
#   1) Resolucion rapida: se escribe una funcion o una ecuacion (tambien sin igualar a cero)
#      (sen(x) = −2x + 1), se ve como queda f(x) = 0, su grafica y sus raices, y con un clic
#      se abre el metodo elegido con todo cargado.
#   2) Los metodos para raices: abiertos (Newton-Raphson y secante) destacados, y cerrados.
#   3) Comparacion de Newton-Raphson y la secante (como en la presentacion de clase).
#   4) Las demas herramientas (algebra lineal y sistemas numericos).
from nicegui import run, ui

from backend.metodos_numericos import graficas
from backend.metodos_numericos.analizador import ErrorFuncion, Funcion
from backend.metodos_numericos.newton_raphson import newton_raphson
from backend.metodos_numericos.secante import secante
from backend.metodos_numericos.vista_rapida import explorar
from ..componentes import aviso, caja, html, plano, tarjeta
from ..formato import escapar

# Ecuaciones de muestra (las del curso y algunas sin igualar a cero)
#   (lo que se escribe en el campo, como se ve en la pastilla)
MUESTRAS = [
    ("sen(x) = -2x + 1", "sen(x) = −2x + 1"),
    ("x^3 = x + 2", "x³ = x + 2"),
    ("x^3 = 2x + 5", "x³ = 2x + 5"),
    ("e^x = 3x", "eˣ = 3x"),
    ("cos(x) = x", "cos(x) = x"),
    ("ln(x) = 2 - x", "ln(x) = 2 − x"),
    ("x^4 - 5x^3 + 0.5x^2 - 11x + 10", "x⁴ − 5x³ + 0.5x² − 11x + 10"),
]

# Metodos que se pueden abrir con la funcion escrita: (id, nombre, icono, pista)
ACCIONES = [
    ("newton", "Newton-Raphson", "trending_up", "Tangente desde x₀"),
    ("secante", "Secante", "insights", "Sin derivar: x₀ y x₁"),
    ("biseccion", "Bisección", "my_location", "Mitad de [a, b]"),
    ("regla_falsa", "Regla falsa", "timeline", "Recta entre a y b"),
]


# ----------------------------------------------------------------------
# Ilustraciones de las tarjetas de Newton-Raphson y secante: se calculan con el
# problema conductor de la clase, f(x) = x³ − x − 2, para que sean exactas.
# ----------------------------------------------------------------------
_ANCHO, _ALTO = 440, 150
_X0, _X1, _Y0, _Y1 = 0.9, 2.12, -2.7, 5.6


def _f(x):
    return x ** 3 - x - 2


def _p(x, y):
    px = 14 + (x - _X0) / (_X1 - _X0) * (_ANCHO - 28)
    py = _ALTO - 12 - (y - _Y0) / (_Y1 - _Y0) * (_ALTO - 24)
    return f"{px:.1f}", f"{py:.1f}"


def _curva():
    puntos = [_p(_X0 + i * (_X1 - _X0) / 80, _f(_X0 + i * (_X1 - _X0) / 80)) for i in range(81)]
    return "M " + " L ".join(f"{x} {y}" for x, y in puntos)


def _linea(x1, y1, x2, y2, clase):
    a, b = _p(x1, y1), _p(x2, y2)
    return f'<line class="{clase}" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'


def _punto(x, y, clase, r=4):
    cx, cy = _p(x, y)
    return f'<circle class="{clase}" cx="{cx}" cy="{cy}" r="{r}"/>'


def _ilustracion(tipo):
    eje_izq, eje_der = _p(_X0, 0), _p(_X1, 0)
    partes = [f'<line class="eje" x1="{eje_izq[0]}" y1="{eje_izq[1]}" x2="{eje_der[0]}" y2="{eje_der[1]}"/>',
              f'<path class="curva" d="{_curva()}"/>']
    if tipo == "newton":
        x = 2.0
        for k in range(1, 3):
            y, pendiente = _f(x), 3 * x ** 2 - 1
            siguiente = x - y / pendiente
            partes.append(_linea(x, y, siguiente, 0, f"recta r{k}"))
            partes.append(_punto(x, y, f"punto q{k}"))
            partes.append(_linea(siguiente, 0, siguiente, _f(siguiente), f"guia r{k}"))
            partes.append(_punto(siguiente, 0, f"corte q{k}", 3.4))
            x = siguiente
    else:
        anterior, actual = 1.0, 2.0
        for k in range(1, 3):
            fa, fb = _f(anterior), _f(actual)
            siguiente = actual - fb * (actual - anterior) / (fb - fa)
            partes.append(_linea(anterior, fa, actual, fb, f"recta r{k}"))
            partes.append(_punto(anterior, fa, f"punto q{k}"))
            partes.append(_punto(actual, fb, f"punto q{k}"))
            partes.append(_punto(siguiente, 0, f"corte q{k}", 3.4))
            anterior, actual = actual, siguiente
    partes.append(_punto(1.5213797, 0, "raiz-ilustracion", 5))
    texto = "Tangentes de Newton-Raphson" if tipo == "newton" else "Secantes por dos puntos"
    return (f'<svg viewBox="0 0 {_ANCHO} {_ALTO}" role="img" aria-label="{texto} acercándose a la raíz">'
            + "".join(partes) + "</svg>")


def _iteraciones_de_clase():
    """Iteraciones del ejemplo de clase (x³ − x − 2, E = 10⁻⁶) calculadas por el propio programa."""
    f = Funcion("x^3 - x - 2")
    try:
        n = newton_raphson(f, f.derivada(), 1.5, "0.000001")["total_iteraciones"]
        s = secante(f, 1, 2, "0.000001")["total_iteraciones"]
    except ValueError:
        return "—", "—"
    return str(n), str(s)


COMPARACION = [
    ("Valores iniciales", "Uno: x₀", "Dos: x₀ y x₁"),
    ("Derivada", "Explícita: usa f′(x)", "No la necesita"),
    ("Geometría", "Recta tangente", "Recta secante"),
    ("Ventaja", "Puede converger muy rápido cerca de la raíz", "Evita derivar la función"),
    ("Riesgo", "f′(xₙ) nula o muy pequeña", "Denominador f(xₙ) − f(xₙ₋₁) nulo o pequeño"),
]


# ----------------------------------------------------------------------
# Resolucion rapida
# ----------------------------------------------------------------------
class ResolucionRapida:
    def __init__(self, resolver):
        self.resolver = resolver
        self.texto = MUESTRAS[0][0]
        self.funcion = None
        self.error = None
        self.exploracion = None
        self.formula = None
        self.raiz_elegida = 0
        self.abriendo = None
        self.version = 0
        self.temporizador = None
        self.construir()
        ui.timer(0.1, self.actualizar, once=True)

    # Acciones ---------------------------------------------------------
    def al_escribir(self, valor):
        if valor == self.texto:
            return
        self.texto = valor
        if self.temporizador:
            self.temporizador.cancel()
        with self.anclaje:
            self.temporizador = ui.timer(0.35, self.actualizar, once=True)

    async def usar_muestra(self, texto):
        self.texto = texto
        self.entrada.value = texto
        await self.actualizar()

    async def actualizar(self):
        self.version += 1
        version = self.version
        try:
            f = Funcion(self.texto)
            self.error = None
        except ErrorFuncion as error:
            self.funcion, self.error, self.exploracion, self.formula = None, str(error), None, None
            self.refrescar()
            return
        self.funcion = f
        exploracion = await run.io_bound(explorar, f)
        formula = await run.io_bound(graficas.formula, f.mathtext)
        if version != self.version:  # mientras tanto se escribio otra cosa
            return
        self.exploracion, self.formula, self.raiz_elegida = exploracion, formula, 0
        self.refrescar()

    def elegir_raiz(self, indice):
        self.raiz_elegida = indice
        self.raices.refresh()
        self.grafica.refresh()

    async def abrir(self, id_metodo):
        if self.funcion is None or self.abriendo:
            return
        raices = self.exploracion["raices"] if self.exploracion else []
        x = raices[self.raiz_elegida]["x"] if raices else None
        self.abriendo = id_metodo
        self.acciones.refresh()
        try:
            await self.resolver(id_metodo, self.texto, x)
        finally:
            self.abriendo = None
            self.acciones.refresh()

    def refrescar(self):
        self.interpretacion.refresh()
        self.raices.refresh()
        self.grafica.refresh()
        self.acciones.refresh()

    # Dibujo -----------------------------------------------------------
    def construir(self):
        with tarjeta("inicio-rapido"):
            self.anclaje = ui.element("div")
            with caja("rapido-rejilla"):
                with caja("rapido-izquierda"):
                    html('<span class="insignia">Resolución rápida</span>')
                    html("<h1>Escriba la ecuación.<br><span class=\"atenuado\">El programa hace el resto.</span></h1>")
                    html('<p class="rapido-intro">Funciones o ecuaciones, también <b>sin igualar a cero</b>: '
                         'se pasa todo a un lado, se grafica, se ubican las raíces y se abre el método '
                         'que elija con todo cargado.</p>')
                    with caja("entrada-heroe"):
                        html('<span class="material-icons">edit</span>', "entrada-icono")
                        self.entrada = ui.input(value=self.texto, placeholder="sen(x) = -2x + 1",
                                                on_change=lambda e: self.al_escribir(e.value or ""))
                        self.entrada.props("borderless spellcheck=false autocomplete=off").classes("campo-heroe mono")
                        self.entrada.on("keydown.enter", lambda: self.abrir("newton"))
                    with caja("muestras"):
                        html("Probar:", "muestras-titulo")
                        for texto, visible in MUESTRAS:
                            chip = html(escapar(visible), "muestra mono")
                            chip.on("click", lambda t=texto: self.usar_muestra(t))
                    self.interpretacion()
                with caja("rapido-derecha"):
                    self.grafica()
                    self.raices()
                    html('<div class="etiqueta" style="margin:6px 0 0">Resolver con</div>')
                    self.acciones()

    @ui.refreshable_method
    def interpretacion(self):
        with caja("interpretacion"):
            if self.error:
                aviso(self.error, "error")
                return
            f = self.funcion
            if f is None:
                html('<div class="texto-suave">Interpretando…</div>')
                return
            html(f'<div class="etiqueta">{"Función que usa el método" if f.ecuacion else "Se busca la raíz de"}</div>')
            with caja("formula-resultado"):
                if self.formula:
                    html(f'<img src="{self.formula}" alt="f(x)">', "formula-img")
                else:
                    html(f'<b class="mono">f(x) = {escapar(f.legible)}</b>')
                html('<span class="igual-cero">= 0</span>')

    @ui.refreshable_method
    def grafica(self):
        f, ex = self.funcion, self.exploracion
        if f is None or ex is None:
            html('<div class="plano-vacio"><span class="material-icons">show_chart</span>'
                 '<div>La gráfica aparece al escribir una función válida.</div></div>', "plano-vacio-caja")
            return
        raices = [{"x": r["x"], "texto": f"x ≈ {r['x']:.6g}" if i == self.raiz_elegida else f"r{i + 1}"}
                  for i, r in enumerate(ex["raices"])]
        plano({"expr": f.javascript, "xmin": ex["x_min"], "xmax": ex["x_max"], "intervalos": [],
               "asintotas": ex["asintotas"], "raices": raices, "clave": "inicio",
               "ayuda": "Rueda: zoom · arrastrar: mover"}).classes("plano-inicio")

    @ui.refreshable_method
    def raices(self):
        ex = self.exploracion
        if self.funcion is None or ex is None:
            return
        with caja("raices-rapidas"):
            if ex["sin_raices"]:
                aviso("No se encontró ningún cruce con el eje x entre −1000 y 1000: la ecuación parece no tener "
                      "soluciones reales. Puede abrir un método igual para explorar la gráfica.", "advertencia")
                return
            html(f'<span class="etiqueta" style="margin:0">Raíces aproximadas ({len(ex["raices"])})</span>')
            with caja("fila").style("gap:6px; align-items:center"):
                for indice, r in enumerate(ex["raices"]):
                    activa = indice == self.raiz_elegida
                    chip = html(f'<span class="r-nombre">r{indice + 1}</span> {r["x"]:.6g}',
                                "chip-raiz mono" + (" activa" if activa else ""))
                    chip.on("click", lambda i=indice: self.elegir_raiz(i))
            if len(ex["raices"]) > 1:
                html('<div class="texto-suave" style="font-size:11.5px">Elija la raíz que quiere calcular: '
                     'el método se abre con su intervalo (y su valor inicial) ya marcado.</div>')

    @ui.refreshable_method
    def acciones(self):
        f = self.funcion
        derivada = None
        if f is not None:
            try:
                derivada = f.derivada().legible
            except (ValueError, ZeroDivisionError, OverflowError):
                derivada = None
        with caja("acciones-rapidas"):
            for id_metodo, nombre, icono, pista in ACCIONES:
                if id_metodo == "newton" and derivada:
                    pista = f"f′(x) = {derivada}"
                clases = "accion" + (" abierto" if id_metodo in ("newton", "secante") else "")
                if f is None:
                    clases += " deshabilitada"
                if self.abriendo == id_metodo:
                    clases += " cargando"
                icono_final = "autorenew" if self.abriendo == id_metodo else "arrow_forward"
                tile = html(
                    f'<span class="accion-icono"><span class="material-icons">{icono}</span></span>'
                    f'<span class="accion-texto"><span class="accion-nombre">{escapar(nombre)}</span>'
                    f'<span class="accion-pista mono">{escapar(pista)}</span></span>'
                    f'<span class="material-icons accion-flecha">{icono_final}</span>', clases)
                tile.on("click", lambda m=id_metodo: self.abrir(m))


# ----------------------------------------------------------------------
# Pantalla completa
# ----------------------------------------------------------------------
def construir(grupos, abrir, resolver):
    """grupos: el registro de modulos de aplicacion.py; abrir(id) cambia al modulo elegido;
    resolver(id, texto, x) abre un metodo de raices con la funcion o ecuacion ya cargada."""
    modulos = {m.id: m for _, lista in grupos for m in lista}

    ResolucionRapida(resolver)
    metodos_de_raices(modulos, abrir)
    comparacion()
    otras_herramientas(grupos, abrir)
    html('<div class="pie-inicio"><span><span class="tecla">Ctrl K</span> buscar un módulo</span>'
         '<span>·</span><span>Escriba ecuaciones con <b>=</b> en cualquier método de raíces</span>'
         '<span>·</span><span>Funciona sin conexión a internet</span></div>')


def metodos_de_raices(modulos, abrir):
    with tarjeta("escalonado"):
        with caja("seccion-cabeza"):
            html('<div><div class="subtitulo" style="margin:0">Métodos para encontrar raíces</div>'
                 '<h2 class="seccion-titulo">Abiertos: rápidos, parten de valores iniciales</h2></div>')
            html('<div class="texto-suave seccion-nota">No necesitan un intervalo que encierre la raíz; convergen '
                 'rápido, pero no garantizan convergencia para cualquier valor inicial.</div>')
        with caja("rejilla dos"):
            tarjeta_abierta(modulos["newton"], abrir, "newton", "xₙ₊₁ = xₙ − f(xₙ) / f′(xₙ)",
                            ["1 valor inicial", "usa f′(x)", "tangente"])
            tarjeta_abierta(modulos["secante"], abrir, "secante", "xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / [f(xₙ) − f(xₙ₋₁)]",
                            ["2 valores iniciales", "sin derivada", "secante"])
        html('<h2 class="seccion-titulo" style="margin-top:24px">Cerrados: seguros, encierran la raíz en [a, b]</h2>')
        with caja("rejilla dos"):
            for id_modulo, formula in (("biseccion", "c = (a + b) / 2"),
                                       ("regla_falsa", "c = b − f(b)·(a − b) / [f(a) − f(b)]")):
                tarjeta_cerrada(modulos[id_modulo], abrir, formula)


def tarjeta_abierta(m, abrir, tipo, formula, etiquetas):
    insignia = '<span class="insignia verde">NUEVO</span>' if m.nuevo else ""
    chips = "".join(f'<span class="etiqueta-metodo">{escapar(t)}</span>' for t in etiquetas)
    tarjeta_html = html(
        f'<div class="metodo-ilustracion {tipo}">{_ilustracion(tipo)}</div>'
        '<div class="metodo-cuerpo">'
        f'<div class="modulo-cabeza"><span class="modulo-icono"><span class="material-icons">{m.icono}</span></span>{insignia}</div>'
        f'<div class="metodo-nombre">{escapar(m.nombre)}</div>'
        f'<div class="opcion-detalle">{escapar(m.descripcion)}</div>'
        f'<div class="metodo-formula mono">{escapar(formula)}</div>'
        f'<div class="etiquetas-metodo">{chips}</div>'
        '<div class="modulo-abrir">Abrir método <span class="material-icons">arrow_forward</span></div>'
        "</div>",
        "opcion metodo-destacado")
    tarjeta_html.on("click", lambda: abrir(m.id))


def tarjeta_cerrada(m, abrir, formula):
    tarjeta_html = html(
        f'<span class="modulo-icono"><span class="material-icons">{m.icono}</span></span>'
        f'<div class="cerrado-texto"><div class="opcion-titulo">{escapar(m.nombre)}</div>'
        f'<div class="opcion-detalle">{escapar(m.descripcion)}</div>'
        f'<div class="metodo-formula mono pequena">{escapar(formula)}</div></div>'
        '<span class="material-icons cerrado-flecha">arrow_forward</span>',
        "opcion metodo-cerrado")
    tarjeta_html.on("click", lambda: abrir(m.id))


def comparacion():
    n_newton, n_secante = _iteraciones_de_clase()
    filas = "".join(f'<tr><th>{escapar(c)}</th><td>{escapar(n)}</td><td>{escapar(s)}</td></tr>'
                    for c, n, s in COMPARACION)
    filas += (f'<tr class="destacada"><th>Ejemplo de clase<br><span class="mono">x³ − x − 2, E = 10⁻⁶</span></th>'
              f'<td><b class="mono">{n_newton}</b> iteraciones desde x₀ = 1.5</td>'
              f'<td><b class="mono">{n_secante}</b> iteraciones desde x₀ = 1, x₁ = 2</td></tr>')
    with tarjeta("escalonado"):
        with caja("seccion-cabeza"):
            html('<div><div class="subtitulo" style="margin:0">Comparación</div>'
                 '<h2 class="seccion-titulo">¿Newton-Raphson o secante?</h2></div>')
            html('<div class="texto-suave seccion-nota">Si la derivada es fácil de obtener, Newton-Raphson suele '
                 'llegar en menos iteraciones. Si derivar es difícil o costoso, la secante es la alternativa.</div>')
        html('<table class="tabla-comparacion"><thead><tr><th>Criterio</th><th>Newton-Raphson</th><th>Secante</th>'
             f'</tr></thead><tbody>{filas}</tbody></table>', "contenedor-comparacion")


def otras_herramientas(grupos, abrir):
    with tarjeta("escalonado"):
        html('<div class="subtitulo" style="margin-top:0">Más herramientas</div>')
        with caja("rejilla herramientas"):
            for titulo, lista in grupos:
                if titulo.startswith("Métodos"):
                    continue
                for m in lista:
                    fila = html(f'<span class="modulo-icono"><span class="material-icons">{m.icono}</span></span>'
                                f'<div><div class="herramienta-grupo">{escapar(titulo)}</div>'
                                f'<div class="opcion-titulo">{escapar(m.nombre)}</div>'
                                f'<div class="opcion-detalle">{escapar(m.descripcion)}</div></div>',
                                "opcion herramienta")
                    fila.on("click", lambda i=m.id: abrir(i))
