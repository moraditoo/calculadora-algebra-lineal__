# frontend/modulos/biseccion/pasos/funcion.py
# Paso 1: escribir f(x) como en el cuaderno, con el editor matematico.
import json
import re

from nicegui import ui

from ....componentes import aviso, boton, caja, campo, html, segmentado, subtitulo
from ....formato import escapar
from ..estado import NOMBRE_ERROR


def construir(vista):
    e = vista.estado
    html('<div class="subtitulo" style="margin-top:0">Paso 1 · Escriba la función f(x)</div>')
    html('<div class="texto-suave">Escríbala tal como en el cuaderno: los exponentes se ven arriba (x⁴), '
         'las fracciones se arman con <b>/</b> y la raíz con <b>sqrt</b>. Se buscará la raíz de f(x) = 0.</div>')

    temporizador = {"actual": None}

    async def actualizar_vista_previa():
        await vista.actualizar_formula()
        if not contenedor.is_deleted:  # el usuario pudo cambiar de paso mientras tanto
            vista_previa.refresh()

    def al_escribir(valor):
        if valor == e.funcion:
            return
        # Funcion nueva: se olvida el intervalo anterior y al graficar se busca un rango adecuado
        e.nueva_funcion(valor, e.es_latex)
        vista.refrescar()
        # Se espera a que deje de escribir un momento antes de redibujar la vista previa
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
            html('<div class="etiqueta" style="margin:0">f(x) =</div>')
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
                entrada = campo(None, e.funcion, al_escribir, ancho="100%", placeholder="x^4 - 5x^3 + 0.5x^2 - 11x + 10")
                entrada.mark("texto-funcion")
                vista.pasos_guia.append((entrada, "Escribir como texto",
                                         "Use ^ para exponentes: x^4 - 5x^3 + 0.5x^2 - 11x + 10. Acepta 5x (sin *), e^(-x), ln(x), sen(x), |x|."))

        editor()

        subtitulo("Así la entiende el programa")

        @ui.refreshable
        def vista_previa():
            f = e.funcion_lista()
            with caja("caja fila").style("min-height:64px; align-items:center; padding:10px 16px") as cuadro:
                if f is None:
                    aviso(e.error_funcion or "", "error").style("width:100%")
                elif e.formula:
                    html(f'<img src="{e.formula}" alt="f(x)">', "formula-img")
                else:
                    ui.spinner(size="26px", color="grey-7")
            vista.pasos_guia.append((cuadro, "Interpretación",
                                     "Aquí se ve la función exactamente como la va a usar el método. Revise que coincida con la que escribió."))

        vista_previa()

        aviso("Funciones disponibles: sen, cos, tan, ln (natural), log (base 10), e^x, sqrt, |x| y pi. "
              "Se puede escribir 5x en lugar de 5·x.", "info").style("margin-top:14px")

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
    """Tarjetas con ejemplos ya preparados: se cargan en la gráfica o se resuelven de una vez."""
    subtitulo("Ejemplos resueltos")
    html('<div class="texto-suave">Cargue un ejemplo para ver todo el método: la gráfica con su intervalo, '
         'las iteraciones hasta que el error es menor que E y la conclusión.</div>')
    with caja("rejilla tres").style("margin-top:12px") as rejilla:
        for ejemplo in vista.EJEMPLOS:
            with caja("opcion ejemplo"):
                html(f'<div class="opcion-titulo">{escapar(ejemplo["titulo"])}</div>'
                     f'<div class="ejemplo-funcion mono">f(x) = {escapar(ejemplo["texto"])}</div>'
                     f'<div class="opcion-detalle">{escapar(ejemplo["detalle"])}</div>'
                     f'<div class="opcion-extra mono">[{ejemplo["a"]:g}, {ejemplo["b"]:g}] · '
                     f'{escapar(NOMBRE_ERROR[ejemplo["criterio"]])} &lt; {escapar(ejemplo["tolerancia"])}</div>')
                with caja("fila").style("gap:6px"):
                    boton("Graficar", lambda ej=ejemplo: vista.cargar_ejemplo(ej), icono="show_chart", clases="compacto")
                    boton("Resolver", lambda ej=ejemplo: vista.cargar_ejemplo(ej, resolver=True),
                          icono="play_arrow", principal=True, clases="compacto")
    vista.pasos_guia.append((rejilla, "Ejemplos resueltos",
                             "Graficar carga el ejemplo y muestra sus intervalos; Resolver lo ejecuta y va directo a las iteraciones."))


def texto_a_latex(texto):
    """x^10 -> x^{10}, x^(n+1) -> x^{n+1}, * -> \\cdot (para pasar del modo texto al editor)."""
    texto = re.sub(r"\^\(([^()]*)\)", r"^{\1}", texto)
    texto = re.sub(r"\^(-?[0-9.]+)", r"^{\1}", texto)
    return texto.replace("*", "\\cdot ")
