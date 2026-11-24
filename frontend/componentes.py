# frontend/componentes.py
# Piezas visuales que comparten todos los modulos (tarjetas, botones, campos,
# matrices, avisos...). Cada modulo solo combina estas piezas.
import json
import re

from nicegui import ui

from .formato import escapar


# ----------------------------------------------------------------------
# Contenedores y textos
# ----------------------------------------------------------------------
def caja(clases=""):
    return ui.element("div").classes(clases)


def tarjeta(clases=""):
    return ui.element("div").classes("vidrio tarjeta entrar " + clases)


def html(contenido, clases=""):
    # Este HTML lo arma el programa; todo lo que escribe el usuario pasa por escapar()
    return ui.html(contenido, sanitize=False).classes(clases)


def texto(contenido, clases=""):
    return ui.label(contenido).classes(clases)


def subtitulo(contenido):
    return html(escapar(contenido), "subtitulo")


def encabezado(titulo, descripcion, icono, al_pedir_guia=None):
    """Titulo de una seccion. Si se pasa al_pedir_guia aparece el boton 'Guía'."""
    with caja("encabezado"):
        with caja("fila").style("align-items:center; flex-wrap:nowrap; gap:14px"):
            with caja("icono-titulo"):
                ui.icon(icono, size="22px")
            html(f"<h2>{escapar(titulo)}</h2><p>{escapar(descripcion)}</p>")
        if al_pedir_guia:
            boton("Guía paso a paso", al_pedir_guia, icono="tour", clases="guia")


# ----------------------------------------------------------------------
# Controles
# ----------------------------------------------------------------------
def boton(etiqueta, accion, icono=None, principal=False, clases=""):
    b = ui.button(etiqueta, on_click=accion, icon=icono, color=None)
    b.props("flat no-caps unelevated").classes("boton " + ("principal " if principal else "") + clases)
    return b


def campo(etiqueta, valor, al_cambiar, ancho="140px", mono=True, placeholder="", clases=""):
    with caja().style(f"width:{ancho}; max-width:100%"):
        if etiqueta:
            html(escapar(etiqueta), "etiqueta")
        entrada = ui.input(value=valor, placeholder=placeholder, on_change=lambda e: al_cambiar(e.value or ""))
        entrada.props("borderless dense spellcheck=false").classes("campo w-full " + ("mono " if mono else "") + clases)
    return entrada


def area_texto(valor, al_cambiar, filas=4):
    entrada = ui.textarea(value=valor, on_change=lambda e: al_cambiar(e.value or ""))
    entrada.props(f"borderless rows={filas} spellcheck=false").classes("campo mono w-full")
    return entrada


def selector(etiqueta, opciones, valor, al_cambiar, ancho="210px"):
    """opciones: diccionario {valor: texto visible}."""
    with caja().style(f"width:{ancho}"):
        if etiqueta:
            html(escapar(etiqueta), "etiqueta")
        s = ui.select(opciones, value=valor, on_change=lambda e: al_cambiar(e.value))
        s.props("borderless dense options-dense").classes("selector w-full")
    return s


def segmentado(opciones, obtener_valor, al_cambiar, envolver=False):
    """Control tipo pastilla de iOS. opciones: lista de (valor, texto). Con envolver las
    opciones pasan a la linea siguiente cuando no caben."""

    @ui.refreshable
    def dibujar():
        with caja("segmentado" + (" envolver" if envolver else "")):
            for valor, etiqueta in opciones:
                elemento = html(escapar(etiqueta), "opcion-seg" + (" activa" if valor == obtener_valor() else "")).mark(f"seg-{valor}")
                elemento.on("click", lambda v=valor: (al_cambiar(v), dibujar.refresh()))

    dibujar()
    return dibujar


def tarjetas_opcion(opciones, obtener_valor, al_cambiar, columnas="tres"):
    """Tarjetas seleccionables. opciones: lista de dict con valor, titulo, detalle y extra (HTML opcional)."""

    @ui.refreshable
    def dibujar():
        with caja(f"rejilla {columnas}"):
            for o in opciones() if callable(opciones) else opciones:
                activa = o["valor"] == obtener_valor()
                contenido = (f'<div class="opcion-titulo">{o["titulo"]}</div>'
                             f'<div class="opcion-detalle">{escapar(o.get("detalle", ""))}</div>'
                             + (f'<div class="opcion-extra">{o["extra"]}</div>' if o.get("extra") else ""))
                elemento = html(contenido, "opcion" + (" activa" if activa else ""))
                elemento.on("click", lambda v=o["valor"]: (al_cambiar(v), dibujar.refresh()))

    dibujar()
    return dibujar


def selector_numero(etiqueta, valor, minimo, maximo, al_cambiar):
    """Control − n + para tamanos de matrices: cambia al instante, sin boton 'Aplicar'."""
    estado = {"valor": valor}

    @ui.refreshable
    def dibujar():
        with caja("selector-numero"):
            if etiqueta:
                html(escapar(etiqueta), "etiqueta")
            with caja("selector-numero-cuerpo"):
                menos = boton("", lambda: cambiar(-1), icono="remove", clases="redondo")
                html(str(estado["valor"]), "selector-numero-valor mono")
                mas = boton("", lambda: cambiar(1), icono="add", clases="redondo")
                menos.props(f"{'disable' if estado['valor'] <= minimo else ''}")
                mas.props(f"{'disable' if estado['valor'] >= maximo else ''}")

    def cambiar(delta):
        nuevo = max(minimo, min(maximo, estado["valor"] + delta))
        if nuevo != estado["valor"]:
            estado["valor"] = nuevo
            dibujar.refresh()
            al_cambiar(nuevo)

    dibujar()
    return dibujar


class desplegable:
    """Seccion plegable (details/summary) que admite cualquier elemento de NiceGUI dentro:
        with desplegable("Procedimiento").style("margin-top:12px"):
            ...
    """

    def __init__(self, titulo, abierto=False, clases=""):
        self.detalles = ui.element("details").classes("desplegable " + clases)
        if abierto:
            self.detalles.props("open")
        with self.detalles:
            with ui.element("summary"):
                html(escapar(titulo), "desplegable-titulo")
            self.cuerpo = caja("desplegable-cuerpo")

    def style(self, css):
        self.detalles.style(css)
        return self

    def __enter__(self):
        return self.cuerpo.__enter__()

    def __exit__(self, *error):
        return self.cuerpo.__exit__(*error)


# ----------------------------------------------------------------------
# Formulas (KaTeX), numeros animados (CountUp) y graficas (ECharts).
# recursos/realce/realce.js las activa en cuanto aparecen en la pagina.
# ----------------------------------------------------------------------
def tex_html(latex, bloque=False, clases=""):
    bloque_attr = ' data-bloque="1"' if bloque else ""
    return f'<span class="tex {clases}" data-tex="{escapar(latex)}"{bloque_attr}>{escapar(latex)}</span>'


def tex(latex, bloque=False, clases=""):
    return html(tex_html(latex, bloque), clases)


def valor_tex(texto, grande=False):
    """'-101/146' -> fraccion de KaTeX;  '−3' -> -3. Con grande usa dfrac (fraccion a tamano normal)."""
    limpio = str(texto).replace("−", "-").strip()
    fraccion = re.fullmatch(r"(-)?(\d+)/(\d+)", limpio)
    if fraccion:
        comando = r"\dfrac{" if grande else r"\frac{"
        return (fraccion[1] or "") + comando + fraccion[2] + "}{" + fraccion[3] + "}"
    return limpio


def matriz_tex(datos, corte=None):
    """Matriz con corchetes para KaTeX. corte: columna donde va la barra de una matriz aumentada.
    Si tiene fracciones se dibujan a tamano normal y con mas espacio entre filas."""
    con_fracciones = any("/" in str(v) for fila in datos for v in fila)
    filas = " \\\\ ".join(" & ".join(valor_tex(v, con_fracciones) for v in fila) for fila in datos)
    espacio = r"\def\arraystretch{2.1}" if con_fracciones else ""
    if corte is None:
        return "{" + espacio + r"\begin{bmatrix} " + filas + r" \end{bmatrix}}"
    columnas = "c" * corte + "|" + "c" * (len(datos[0]) - corte)
    return "{" + espacio + r"\left[\begin{array}{" + columnas + "} " + filas + r" \end{array}\right]}"


def vector_tex(valores):
    return matriz_tex([[v] for v in valores])


def numero_vivo(texto, decimales=None):
    """HTML de un numero que sube hasta su valor al aparecer; texto es como se ve al final."""
    limpio = str(texto).replace("−", "-")
    try:
        valor = float(limpio)
    except ValueError:
        return f'<span class="numero-nuevo">{escapar(texto)}</span>'
    if decimales is None:
        decimales = len(limpio.split(".")[1]) if "." in limpio else 0
    return f'<span data-contar="{valor!r}" data-decimales="{decimales}">{escapar(texto)}</span>'


def grafica(opciones, alto="320px"):
    """Grafica animada de ECharts (incluida en NiceGUI): lineas, escala log, tooltip y zoom."""
    base = {
        "animationDuration": 900, "animationEasing": "cubicOut",
        "textStyle": {"fontFamily": "Inter, Segoe UI, sans-serif"},
        "grid": {"left": 56, "right": 22, "top": 46, "bottom": 40},
        "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.96)", "borderColor": "rgba(0,0,0,0.08)",
                    "textStyle": {"color": "#1d1d1f", "fontSize": 12}},
        "legend": {"top": 6, "icon": "roundRect", "textStyle": {"color": "#5f6368", "fontWeight": 600}},
    }
    base.update(opciones)
    return ui.echart(base).classes("grafica-echart").style(f"height:{alto}")


# Teclado de funciones: (etiqueta, ayuda, LaTeX para el editor matematico, texto para el campo de texto).
# En el LaTeX, #0 es lo seleccionado (o una casilla vacia) y #@ lo que esta antes del cursor;
# en el texto, ▮ marca donde queda el cursor. Lo inserta recursos/teclado/teclado.js.
_F = r"\left(#0\right)"
TECLAS = [
    ("Trigonométricas", [
        ("sen", "seno", r"\operatorname{sen}" + _F, "sen(▮)"), ("cos", "coseno", r"\cos" + _F, "cos(▮)"),
        ("tan", "tangente", r"\tan" + _F, "tan(▮)"), ("sec", "secante", r"\sec" + _F, "sec(▮)"),
        ("csc", "cosecante", r"\csc" + _F, "csc(▮)"), ("cot", "cotangente", r"\cot" + _F, "cot(▮)"),
    ]),
    ("Inversas", [
        ("arcsen", "sen⁻¹", r"\operatorname{arcsen}" + _F, "arcsen(▮)"),
        ("arccos", "cos⁻¹", r"\arccos" + _F, "arccos(▮)"), ("arctan", "tan⁻¹", r"\arctan" + _F, "arctan(▮)"),
        ("arcsec", "sec⁻¹", r"\operatorname{arcsec}" + _F, "arcsec(▮)"),
        ("arccsc", "csc⁻¹", r"\operatorname{arccsc}" + _F, "arccsc(▮)"),
        ("arccot", "cot⁻¹", r"\operatorname{arccot}" + _F, "arccot(▮)"),
    ]),
    ("Hiperbólicas", [
        ("senh", "seno hiperbólico", r"\operatorname{senh}" + _F, "senh(▮)"),
        ("cosh", "coseno hiperbólico", r"\cosh" + _F, "cosh(▮)"),
        ("tanh", "tangente hiperbólica", r"\tanh" + _F, "tanh(▮)"),
        ("arcsenh", "senh⁻¹", r"\operatorname{arcsenh}" + _F, "arcsenh(▮)"),
        ("arccosh", "cosh⁻¹", r"\operatorname{arccosh}" + _F, "arccosh(▮)"),
        ("arctanh", "tanh⁻¹", r"\operatorname{arctanh}" + _F, "arctanh(▮)"),
    ]),
    ("Exponenciales, logaritmos y raíces", [
        ("eˣ", "e elevado a", r"e^{#0}", "e^(▮)"), ("ln", "logaritmo natural", r"\ln" + _F, "ln(▮)"),
        ("log", "logaritmo base 10", r"\log" + _F, "log(▮)"), ("log₂", "logaritmo base 2", r"\log_{2}" + _F, "log2(▮)"),
        ("√", "raíz cuadrada", r"\sqrt{#0}", "sqrt(▮)"), ("∛", "raíz cúbica", r"\sqrt[3]{#0}", "cbrt(▮)"),
        ("|x|", "valor absoluto", r"\left|#0\right|", "|▮|"),
    ]),
    ("Operaciones", [
        ("x", "variable", "x", "x"), ("xⁿ", "potencia", r"#@^{#?}", "^(▮)"), ("x²", "al cuadrado", r"#@^2", "^2"),
        ("a/b", "fracción", r"\frac{#@}{#?}", "/"), ("·", "multiplicar", r"\cdot ", "*"),
        ("( )", "paréntesis", r"\left(#0\right)", "(▮)"), ("π", "pi", r"\pi ", "pi"), ("e", "número e", "e", "e"),
        ("=", "igualdad (ecuación)", "=", " = "),
    ]),
]
ACCIONES_TECLADO = [("←", "izquierda", "Mover el cursor a la izquierda"), ("→", "derecha", "Mover el cursor a la derecha"),
                    ("⌫", "borrar", "Borrar el anterior"), ("Borrar todo", "limpiar", "Vaciar el campo")]


def teclado(sin_ecuacion=False, abierto=True):
    """Teclado de funciones. Escribe en el campo que este en el mismo contenedor con data-zona-teclado."""
    atributo = escapar   # tambien escapa las comillas
    grupos = []
    for titulo, teclas in TECLAS:
        botones = "".join(
            f'<button type="button" class="tecla" title="{atributo(ayuda)}" data-latex="{atributo(latex)}" '
            f'data-texto="{atributo(texto_plano)}">{escapar(etiqueta)}</button>'
            for etiqueta, ayuda, latex, texto_plano in teclas if not (sin_ecuacion and etiqueta == "="))
        grupos.append(f'<div class="teclado-grupo"><div class="teclado-titulo">{escapar(titulo)}</div>'
                      f'<div class="teclas">{botones}</div></div>')
    acciones = "".join(f'<button type="button" class="tecla accion" title="{atributo(ayuda)}" '
                       f'data-accion="{accion}">{escapar(etiqueta)}</button>'
                       for etiqueta, accion, ayuda in ACCIONES_TECLADO)
    grupos.append(f'<div class="teclado-grupo"><div class="teclado-titulo">Editar</div><div class="teclas">{acciones}</div></div>')
    return html(f'<details class="teclado"{" open" if abierto else ""}><summary>Teclado de funciones</summary>'
                f'<div class="teclado-grupos">{"".join(grupos)}</div></details>')


# ----------------------------------------------------------------------
# Mensajes y resultados
# ----------------------------------------------------------------------
ICONOS_AVISO = {"info": "info", "exito": "check_circle", "error": "error_outline", "advertencia": "warning_amber"}


def aviso(mensaje, tipo="info", es_html=False):
    with caja(f"aviso {tipo}") as contenedor:
        ui.icon(ICONOS_AVISO.get(tipo, "info"))
        html(mensaje if es_html else escapar(mensaje))
    return contenedor


def resaltado(etiqueta, valor, detalle=None, derecha=None):
    """Bloque destacado para el resultado principal de cada modulo."""
    with caja("resaltado") as contenedor:
        html(f'<div class="r-etiqueta">{escapar(etiqueta)}</div>'
             f'<div class="r-valor mono">{escapar(valor)}</div>'
             + (f'<div class="r-detalle">{detalle}</div>' if detalle else ""))
        if derecha:
            html(derecha)
    return contenedor


def dato(etiqueta, valor, fuerte=False):
    return html(f'<div class="d-etiqueta">{escapar(etiqueta)}</div><div class="d-valor mono">{escapar(valor)}</div>',
                "dato" + (" fuerte" if fuerte else ""))


def lista_pasos(lineas, preformateado=False):
    filas = "".join(f"<div>{escapar(l)}</div>" for l in lineas)
    return html(filas, "pasos-texto mono" + (" pre" if preformateado else ""))


def imagen(src, clases="grafica"):
    if src:
        return html(f'<img src="{src}" alt="gráfica" draggable="false">', clases)
    return None


def plano(datos):
    """Grafica interactiva de f(x) (recursos/plano/plano.js): zoom con la rueda, arrastrar para moverse.
    datos: expr (f en JavaScript), xmin, xmax, intervalos, asintotas, raices, clave y evento."""
    caja_plano = caja("plano")
    ui.run_javascript(f"window.Plano && window.Plano.montar({json.dumps(caja_plano.html_id)}, "
                      f"{json.dumps(datos, ensure_ascii=False)})")
    return caja_plano


def desplegable_html(titulo, contenido, abierto=False):
    return (f'<details class="desplegable"{" open" if abierto else ""}><summary>{escapar(titulo)}</summary>'
            f"<div>{contenido}</div></details>")


# ----------------------------------------------------------------------
# Matrices
# ----------------------------------------------------------------------
def matriz_html(datos, estilo=None, corte=None, barras=False, compacta=False):
    """estilo(i, j) devuelve una clase extra: fuerte, media, borde, tenue, ambar, verde, morado."""
    filas = []
    for i, fila in enumerate(datos):
        celdas = []
        for j, valor in enumerate(fila):
            if corte is not None and j == corte:
                celdas.append('<span class="divisor"></span>')
            clase = (estilo(i, j) if estilo else "") or ""
            celdas.append(f'<span class="celda mono {clase}">{escapar(valor)}</span>')
        filas.append(f'<div class="fila-m">{"".join(celdas)}</div>')
    barra = '<span class="barra"></span>' if barras else ""
    return (f'<div class="matriz{" compacta" if compacta else ""}">{barra}'
            f'<div class="filas desplazable">{"".join(filas)}</div>{barra}</div>')


def matriz(datos, **opciones):
    return html(matriz_html(datos, **opciones))


def cuadricula_entrada(valores, encabezados=None, columna_destacada=None, ancho="64px"):
    """Cuadricula de campos editables; lo escrito se guarda directamente en 'valores'."""

    def guardar(i, j, v):
        valores[i][j] = v

    with caja("desplazable").style("overflow-x:auto"):
        with ui.element("table").style("border-spacing:6px; border-collapse:separate"):
            if encabezados:
                with ui.element("tr"):
                    for j, e in enumerate(encabezados):
                        with ui.element("th"):
                            html(escapar(e), "mono").style(
                                f"font-size:11px; font-weight:800; color:{'#1d1d1f' if j == columna_destacada else '#5f6368'}")
            for i, fila in enumerate(valores):
                with ui.element("tr"):
                    for j, valor in enumerate(fila):
                        with ui.element("td"):
                            entrada = ui.input(value=valor, on_change=lambda e, i=i, j=j: guardar(i, j, e.value or ""))
                            entrada.props("borderless dense").classes(
                                "campo celda-entrada" + (" destacada" if j == columna_destacada else "")).style(f"width:{ancho}")


def redimensionar(previo, filas, columnas, relleno="0"):
    """Nueva matriz del tamano pedido conservando lo que ya estaba escrito."""
    return [[previo[i][j] if i < len(previo) and j < len(previo[i]) else relleno for j in range(columnas)]
            for i in range(filas)]


def entero(texto, minimo, maximo, defecto):
    try:
        return max(minimo, min(maximo, int(float(texto))))
    except (TypeError, ValueError):
        return defecto
