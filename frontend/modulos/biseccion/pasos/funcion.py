# frontend/modulos/biseccion/pasos/funcion.py
# Paso 1: escribir f(x) como en el cuaderno, con el editor matematico.
import json
import re

from nicegui import ui

from ....componentes import aviso, boton, caja, campo, desplegable, html, segmentado, subtitulo, teclado
from ....formato import escapar


def construir(vista):
    e = vista.estado
    html('<div class="subtitulo" style="margin-top:0">Paso 1 · Escriba la función f(x) o la ecuación</div>')
    html('<div class="texto-suave">Tal como en el cuaderno. Una ecuación con <b>=</b> (sen(x) = −2x + 1) '
         'se pasa sola a la forma f(x) = 0.</div>')

    temporizador = {"actual": None}

    async def actualizar_vista_previa():
        vista.refrescar()   # barra de pasos y tarjetas: una sola vez cuando deja de escribir
        await vista.actualizar_formula()
        if not contenedor.is_deleted:  # el usuario pudo cambiar de paso mientras tanto
            vista_previa.refresh()

    def al_escribir(valor):
        if valor == e.funcion:
            return
        # Funcion nueva: se olvida el intervalo anterior y al graficar se busca un rango adecuado
        e.nueva_funcion(valor, e.es_latex)
        # Se espera a que deje de escribir un momento antes de redibujar (redibujar en cada tecla
        # satura el navegador cuando se escribe rapido)
        if temporizador["actual"]:
            temporizador["actual"].cancel()
        temporizador["actual"] = ui.timer(0.35, actualizar_vista_previa, once=True)

    def cambiar_modo(modo):
        f = e.funcion_lista()
        # Al cambiar de modo se conserva la funcion: se pasa a texto la version ya interpretada
        if modo == "texto_simple" and e.es_latex:
            e.funcion, e.es_latex = (f.texto if f else ""), False
        elif modo == "editor" and not e.es_latex:
            e.funcion, e.es_latex = (texto_a_latex(f.texto) if f else ""), True
        editor.refresh()

    with caja().style("margin-top:14px") as contenedor:
        with caja("fila").style("justify-content:space-between; align-items:center; margin-bottom:10px"):
            html('<div class="etiqueta" style="margin:0">f(x) o ecuación</div>')
            segmentado([("editor", "Editor matemático"), ("texto_simple", "Texto")],
                       lambda: "editor" if e.es_latex else "texto_simple", cambiar_modo)

        @ui.refreshable
        def editor():
            if e.es_latex:
                campo_matematico = ui.element("math-field").classes("w-full").mark("editor-funcion")
                campo_matematico.on("input", lambda ev: al_escribir(ev.args or ""), js_handler="(ev) => emit(ev.target.value)")
                # El valor inicial se coloca cuando el navegador termina de crear el editor
                ui.timer(0.15, lambda: ui.run_javascript(
                    "customElements.whenDefined('math-field').then(() => {"
                    f"  const mf = document.getElementById('{campo_matematico.html_id}');"
                    f"  if (mf) {{ mf.value = {json.dumps(e.funcion)}; mf.smartSuperscript = true; }}"
                    "});"), once=True)
                vista.pasos_guia.append((campo_matematico, "Editor matemático",
                                         "Escriba la función como en el cuaderno. Para un exponente use ^ (x^4); "
                                         "para exponentes de varias cifras use ^ y luego paréntesis o la flecha →."))
            else:
                entrada = campo(None, e.funcion, al_escribir, ancho="100%",
                                placeholder="x^4 - 5x^3 + 0.5x^2 - 11x + 10   ó   sen(x) = -2x + 1")
                entrada.mark("texto-funcion")
                vista.pasos_guia.append((entrada, "Escribir como texto",
                                         "Use ^ para exponentes: x^4 - 5x^3 + 0.5x^2 - 11x + 10. Acepta 5x (sin *), e^(-x), ln(x), "
                                         "sen(x), |x| y ecuaciones con '=' como sen(x) = -2x + 1."))

        # El teclado escribe en el campo que esta en su misma zona (editor matematico o texto)
        with caja().props("data-zona-teclado") as zona:
            editor()
            teclado(abierto=False)
        vista.pasos_guia.append((zona, "Teclado de funciones",
                                 "Cada tecla escribe donde está el cursor: sen, cos, tan, sus inversas, ln, log, √, |x|, "
                                 "fracciones y potencias. Funciona en el editor matemático y en el modo texto."))

        subtitulo("Así la entiende el programa")

        @ui.refreshable
        def vista_previa():
            f = e.funcion_lista()
            with caja("caja fila").style("min-height:64px; align-items:center; padding:10px 16px; gap:14px") as cuadro:
                if f is not None and f.ecuacion:
                    # Ecuacion sin igualar a cero: solo se muestra la f(x) que resulta de pasar todo a un lado
                    html('<span class="funcion-metodo">Función que usa el método</span>')
                if f is None:
                    aviso(e.error_funcion or "", "error").style("width:100%")
                elif e.formula:
                    html(f'<img src="{e.formula}" alt="f(x)">', "formula-img")
                else:
                    ui.spinner(size="26px", color="grey-7")
                if f is not None:
                    html('<span class="estado-escritura bien">✓ Bien escrita</span>').style("margin-left:auto")
            # Observaciones que no impiden usarla (tan⁻¹ x leida como arctan x, dominio vacio...)
            for observacion in (f.avisos if f is not None else []):
                aviso(observacion, "advertencia").style("margin-top:8px")
            vista.pasos_guia.append((cuadro, "Interpretación",
                                     "Aquí se ve la función exactamente como la va a usar el método. Si escribió una "
                                     "ecuación con '=', es la que queda al pasar todos los términos al lado izquierdo."))

        vista_previa()
        vista.despues_de_formula()

        with desplegable("¿Qué se puede escribir?").style("margin-top:14px"):
            html('<div class="texto-suave">sen, cos, tan, sec, csc, cot y sus inversas (arcsen o sen⁻¹…), senh, cosh, '
                 'tanh y sus inversas, ln (natural), log (base 10), log2, e^x, sqrt, cbrt, |x| y pi. Se puede escribir '
                 '5x en lugar de 5·x y una ecuación completa con «=». Los ángulos van en radianes.</div>')

    ejemplos_resueltos(vista)

    def siguiente():
        if e.funcion_lista() is None:
            ui.notify(e.error_funcion or "La función no es válida.", type="negative", position="top")
            return
        vista.ir_a(2)

    with caja("fila").style("justify-content:flex-end; margin-top:18px"):
        b = boton("Siguiente: graficar", siguiente, icono="arrow_forward", principal=True)
    vista.pasos_guia.append((b, "Siguiente paso", "Con la función lista se grafica para encontrar los intervalos con cambio de signo."))

    if e.formula is None and e.funcion_lista() is not None:
        ui.timer(0.05, actualizar_vista_previa, once=True)


def ejemplos_resueltos(vista):
    """Ejemplos ya preparados en tarjetas compactas: un clic los resuelve; el icono de la
    grafica solo los carga para elegir el intervalo."""
    subtitulo("Ejemplos resueltos")
    with caja("rejilla ejemplos-compactos") as rejilla:
        for ejemplo in vista.EJEMPLOS:
            with caja("ejemplo-compacto") as tarjeta_ejemplo:
                html(f'<div class="ejemplo-titulo">{escapar(ejemplo["titulo"])}</div>'
                     f'<div class="ejemplo-funcion mono">{escapar(texto_ejemplo(ejemplo))}</div>'
                     f'<div class="ejemplo-resumen mono">{vista.resumen_ejemplo(ejemplo)}</div>').props(
                    f'title="{escapar(ejemplo["detalle"])}"')
                graficar = html('<span class="material-icons">show_chart</span>', "ejemplo-graficar").props(
                    'title="Solo graficar"')
                graficar.on("click.stop", lambda ej=ejemplo: vista.cargar_ejemplo(ej))
            tarjeta_ejemplo.on("click", lambda ej=ejemplo: vista.cargar_ejemplo(ej, resolver=True))
    vista.pasos_guia.append((rejilla, "Ejemplos resueltos",
                             "Un clic resuelve el ejemplo y va a las iteraciones; el icono de la gráfica solo lo carga."))


def texto_ejemplo(ejemplo):
    """Una ecuacion se muestra tal cual (x³ = 2x + 5); una expresion, como f(x) = ..."""
    return ejemplo["texto"] if "=" in ejemplo["texto"] else f'f(x) = {ejemplo["texto"]}'


def texto_a_latex(texto):
    """x^10 -> x^{10}, x^(n+1) -> x^{n+1}, * -> \\cdot (para pasar del modo texto al editor)."""
    texto = re.sub(r"\^\(([^()]*)\)", r"^{\1}", texto)
    texto = re.sub(r"\^(-?[0-9.]+)", r"^{\1}", texto)
    return texto.replace("*", "\\cdot ")
