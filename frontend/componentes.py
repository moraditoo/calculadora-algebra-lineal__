# frontend/componentes.py
# Piezas visuales que comparten todos los modulos (tarjetas, botones, campos,
# matrices, avisos...). Cada modulo solo combina estas piezas.
import json

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


def segmentado(opciones, obtener_valor, al_cambiar):
    """Control tipo pastilla de iOS. opciones: lista de (valor, texto)."""

    @ui.refreshable
    def dibujar():
        with caja("segmentado"):
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
