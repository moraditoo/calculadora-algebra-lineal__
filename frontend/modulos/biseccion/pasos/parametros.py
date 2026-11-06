# frontend/modulos/biseccion/pasos/parametros.py
# Paso 3: intervalo [a, b], precision E, criterio de parada y limite de iteraciones.
from nicegui import ui

from backend.metodos_numericos import biseccion as metodo
from ....componentes import aviso, boton, caja, campo, html, subtitulo, tarjetas_opcion
from ....formato import con_signo, escapar
from ..estado import CRITERIOS
from . import decimales


def construir(vista):
    e = vista.estado
    html('<div class="subtitulo" style="margin-top:0">Paso 3 · Parámetros del método</div>')
    html('<div class="texto-suave">Escriba su propio intervalo [a, b] o elija uno de los <b>recomendados</b> por la gráfica. '
         'Antes de iterar se prueba que f sea continua y que f(a)·f(b) &lt; 0 (Bolzano). '
         'El método se detiene cuando el error es <b>menor que la precisión E</b>.</div>')

    def cambiar(nombre, valor):
        setattr(e, nombre, valor)
        if nombre in ("a", "b"):
            e.intervalo_activo = None
            bolzano.refresh()
            recomendados.refresh()
        if nombre in ("tolerancia", "criterio"):
            actualizar_decimales()
            vista.tarjetas_resultado.refresh()

    with caja("fila").style("margin-top:14px") as campos:
        entrada_a = campo("a (límite inferior)", e.a, lambda v: cambiar("a", v), ancho="170px")
        entrada_b = campo("b (límite superior)", e.b, lambda v: cambiar("b", v), ancho="170px")
        campo("Precisión E", e.tolerancia, lambda v: cambiar("tolerancia", v), ancho="140px")
        campo("Máx. iteraciones", e.max_iteraciones, lambda v: cambiar("max_iteraciones", v), ancho="140px")
    vista.pasos_guia.append((campos, "Datos del método",
                             "a y b encierran la raíz; E es la precisión: el método termina cuando el error es menor que E. "
                             "El máximo de iteraciones evita cálculos interminables."))

    async def usar_recomendado(iv):
        entrada_a.set_value(f"{iv['a']:.12g}")
        entrada_b.set_value(f"{iv['b']:.12g}")
        await vista.elegir_intervalo(iv)  # marca el intervalo y actualiza la grafica
        if not entrada_a.is_deleted:
            bolzano.refresh()
            recomendados.refresh()

    @ui.refreshable
    def recomendados():
        t = e.tabulacion
        if t is None:
            html('<div class="texto-suave" style="margin-top:10px">Buscando intervalos recomendados…</div>')
            return
        if not t["intervalos"]:
            aviso("La gráfica no encontró intervalos con cambio de signo: escriba a y b, "
                  "o use «Rango automático» en el paso 2.", "info").style("margin-top:10px")
            return
        with caja("fila").style("gap:8px; align-items:center; margin-top:10px") as fila:
            html('<span class="etiqueta" style="margin:0">Recomendados por la gráfica:</span>')
            for iv in t["intervalos"]:
                activo = iv["numero"] == e.intervalo_activo
                boton(f'I{iv["numero"]} = [{iv["a"]:g}, {iv["b"]:g}]', lambda iv=iv: usar_recomendado(iv),
                      principal=activo, clases="compacto")
        vista.pasos_guia.append((fila, "Intervalos recomendados",
                                 "Salen de la gráfica (paso 2): haga clic para usar uno, o escriba su propio a y b arriba."))

    recomendados()

    @ui.refreshable
    def bolzano():
        f = e.funcion_lista()
        if f is None:
            aviso("La función del paso 1 no es válida.", "error")
            return
        if not e.a or not e.b:
            aviso("Elija un intervalo en la gráfica (paso 2) o escriba a y b.", "info")
            return
        try:
            v = metodo.verificar_bolzano(f, e.a, e.b)
        except ValueError as error:
            aviso(str(error), "error")
            return
        detalle = ""
        if v["fa"] is not None and v["fb"] is not None:
            detalle = (f'f({v["a"]:g}) = <b class="mono">{con_signo(v["fa"], 6)}</b> &nbsp;·&nbsp; '
                       f'f({v["b"]:g}) = <b class="mono">{con_signo(v["fb"], 6)}</b><br>')
        if v.get("continuidad"):
            detalle += f'{escapar(v["continuidad"])}<br>'
        caja_bolzano = aviso(f"{detalle}{escapar(v['mensaje'])}", "exito" if v["valido"] else "error", es_html=True)
        caja_bolzano.style("margin-top:14px")
        vista.pasos_guia.append((caja_bolzano, "Teorema de Bolzano",
                                 "Si f(a) y f(b) tienen signos opuestos, hay al menos una raíz entre a y b."))

    bolzano()

    subtitulo("Criterio de parada (el error debe ser menor que E)")
    with caja() as criterios:
        tarjetas_opcion([{**c, "titulo": f'<span class="mono">{c["titulo"]}</span>'
                          + (' <span class="insignia verde">como en clase</span>' if c["valor"] == vista.CRITERIO_DE_CLASE else "")}
                         for c in CRITERIOS],
                        lambda: e.criterio, lambda v: cambiar("criterio", v), columnas="cinco")
    vista.pasos_guia.append((criterios, "Criterio de parada", vista.NOTA_CRITERIO))

    vista.opciones_metodo()

    subtitulo("Decimales a mostrar")
    refrescar_decimales = decimales.control(vista)

    def actualizar_decimales():
        """Si estan en Auto, los decimales siguen a la precision E."""
        e.ajustar_decimales()
        refrescar_decimales.refresh()

    async def ejecutar():
        boton_ejecutar.props("loading")
        try:
            await vista.resolver()  # si todo sale bien pasa solo al paso 4
        finally:
            if not boton_ejecutar.is_deleted:
                boton_ejecutar.props(remove="loading")

    with caja("fila").style("justify-content:space-between; margin-top:20px"):
        boton("Anterior", lambda: vista.ir_a(2), icono="arrow_back")
        boton_ejecutar = boton(f"Ejecutar {vista.NOMBRE}", ejecutar, icono="play_arrow", principal=True)
    vista.pasos_guia.append((boton_ejecutar, "Ejecutar", "Aplica el método y muestra cada iteración paso a paso."))

    async def buscar_recomendados():
        """Si se llego aqui sin graficar (funcion nueva), se tabula para recomendar intervalos,
        respetando el intervalo que el usuario ya haya escrito."""
        a_previo, b_previo = e.a, e.b
        if not await vista.graficar() or entrada_a.is_deleted:
            return
        if a_previo and b_previo:
            e.a, e.b = a_previo, b_previo
            e.intervalo_activo = next((iv["numero"] for iv in e.tabulacion["intervalos"]
                                       if f"{iv['a']:.12g}" == a_previo and f"{iv['b']:.12g}" == b_previo), None)
        activo = e.intervalo_activo
        entrada_a.set_value(e.a)
        entrada_b.set_value(e.b)
        e.intervalo_activo = activo  # set_value lo borra al avisar del cambio
        bolzano.refresh()
        recomendados.refresh()

    if e.tabulacion is None and e.funcion_lista() is not None:
        ui.timer(0.1, buscar_recomendados, once=True)
