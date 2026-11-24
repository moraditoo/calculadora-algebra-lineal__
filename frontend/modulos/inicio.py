# frontend/modulos/inicio.py
# Pantalla principal. Tiene dos partes:
#   1) Resolucion rapida: se escribe una funcion o una ecuacion (tambien sin igualar a cero)
#      (sen(x) = −2x + 1), se ve como queda f(x) = 0, su grafica y sus raices, y con un clic
#      se abre el metodo elegido con todo cargado.
#   2) Todos los modulos agrupados en tarjetas compactas (con la comparacion de Newton-Raphson
#      y la secante plegada debajo de los metodos de raices).
from nicegui import run, ui

from backend.metodos_numericos import graficas
from backend.metodos_numericos.analizador import ErrorFuncion, Funcion
from backend.metodos_numericos.newton_raphson import newton_raphson
from backend.metodos_numericos.secante import secante
from backend.metodos_numericos.vista_rapida import explorar
from ..componentes import aviso, caja, desplegable, html, plano, tarjeta
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
FORMULAS = {
    "newton": "xₙ₊₁ = xₙ − f(xₙ) / f′(xₙ)",
    "secante": "xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / [f(xₙ) − f(xₙ₋₁)]",
    "biseccion": "c = (a + b) / 2",
    "regla_falsa": "c = b − f(b)·(a − b) / [f(a) − f(b)]",
    "iterativos": "xᵢ⁽ᵏ⁺¹⁾ = [bᵢ − Σ aᵢⱼ xⱼ] / aᵢᵢ",
}


def construir(grupos, abrir, resolver):
    """grupos: el registro de modulos de aplicacion.py; abrir(id) cambia al modulo elegido;
    resolver(id, texto, x) abre un metodo de raices con la funcion o ecuacion ya cargada."""
    ResolucionRapida(resolver)
    with tarjeta("escalonado"):
        for titulo, lista in grupos:
            html(f'<div class="subtitulo grupo-inicio">{escapar(titulo)}</div>')
            with caja("rejilla herramientas"):
                for m in lista:
                    tarjeta_modulo(m, abrir)
            if titulo == "Métodos abiertos":
                comparacion()
    html('<div class="pie-inicio"><span><span class="tecla">Ctrl K</span> buscar un módulo</span>'
         '<span>·</span><span>Funciona sin conexión a internet</span></div>')


def tarjeta_modulo(m, abrir):
    insignia = '<span class="insignia verde">NUEVO</span>' if m.nuevo else ""
    formula = f'<div class="metodo-formula mono pequena">{escapar(FORMULAS[m.id])}</div>' if m.id in FORMULAS else ""
    fila = html(f'<span class="modulo-icono"><span class="material-icons">{m.icono}</span></span>'
                f'<div class="herramienta-texto"><div class="opcion-titulo">{escapar(m.nombre)} {insignia}</div>'
                f'<div class="opcion-detalle">{escapar(m.descripcion)}</div>{formula}</div>',
                "opcion herramienta")
    fila.on("click", lambda i=m.id: abrir(i))


def comparacion():
    n_newton, n_secante = _iteraciones_de_clase()
    filas = "".join(f'<tr><th>{escapar(c)}</th><td>{escapar(n)}</td><td>{escapar(s)}</td></tr>'
                    for c, n, s in COMPARACION)
    filas += (f'<tr class="destacada"><th>Ejemplo de clase<br><span class="mono">x³ − x − 2, E = 10⁻⁶</span></th>'
              f'<td><b class="mono">{n_newton}</b> iteraciones desde x₀ = 1.5</td>'
              f'<td><b class="mono">{n_secante}</b> iteraciones desde x₀ = 1, x₁ = 2</td></tr>')
    with desplegable("¿Newton-Raphson o secante?").style("margin-top:12px"):
        html('<table class="tabla-comparacion"><thead><tr><th>Criterio</th><th>Newton-Raphson</th><th>Secante</th>'
             f'</tr></thead><tbody>{filas}</tbody></table>', "contenedor-comparacion")
