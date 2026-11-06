# frontend/modulos/biseccion/pasos/grafica.py
# Paso 2: graficar f(x) para ubicar los intervalos donde cambia de signo.
import math

from nicegui import ui

from ....componentes import aviso, boton, caja, campo, desplegable_html, html, plano, subtitulo
from ....formato import clase_signo, con_signo, escapar, numero, signo


def rango_redondo(x0, x1):
    """Redondea el rango visible de la grafica a numeros comodos para la tabulacion (-3.27 -> -3.3)."""
    paso = 10 ** math.floor(math.log10((x1 - x0) / 50))
    return f"{math.floor(x0 / paso) * paso:.10g}", f"{math.ceil(x1 / paso) * paso:.10g}"


def datos_plano(vista):
    """Lo que necesita la grafica interactiva: f en JavaScript, el rango tabulado y lo que se marca encima."""
    e, t = vista.estado, vista.estado.tabulacion
    raices = [{"x": x, "texto": f"x = {x:.6g} (exacta)"} for x in t["raices_exactas"]]
    if e.resultado:
        raices.append({"x": e.resultado["raiz"], "texto": f"raíz ≈ {e.resultado['raiz']:.8f}"})
    return {
        "expr": e.funcion_lista().javascript, "xmin": t["x_min"], "xmax": t["x_max"],
        "intervalos": [{"numero": iv["numero"], "a": iv["a"], "b": iv["b"], "fa": iv["fa"], "fb": iv["fb"],
                        "activo": iv["numero"] == e.intervalo_activo} for iv in t["intervalos"]],
        "asintotas": [d["x"] for d in t["discontinuidades"]],
        "raices": raices,
        "clave": vista.PREFIJO,                  # la vista (zoom) se recuerda por metodo
        "evento": f"{vista.PREFIJO}_vista",      # avisa al servidor que rango se esta viendo
    }


def construir(vista):
    e = vista.estado
    html('<div class="subtitulo" style="margin-top:0">Paso 2 · Gráfica e intervalos</div>')
    html('<div class="texto-suave">La gráfica sirve para <b>ubicar</b> los intervalos donde f(x) cambia de signo. '
         'Los valores exactos los calcula el método en los pasos siguientes.</div>')

    async def graficar(ajustar_rango=False):
        boton_graficar.props("loading")
        try:
            if await vista.graficar(ajustar_rango) and not boton_graficar.is_deleted:
                # El rango pudo cambiar solo (rango automatico): se muestra en los campos
                for entrada, valor in ((entrada_min, e.x_min), (entrada_max, e.x_max), (entrada_n, e.subintervalos)):
                    if entrada.value != valor:
                        entrada.set_value(valor)
                resultados.refresh()
        finally:
            if not boton_graficar.is_deleted:
                boton_graficar.props(remove="loading")

    def cambiar_rango(nombre, valor):
        if getattr(e, nombre) != valor:
            setattr(e, nombre, valor)
            e.rango_automatico = False  # el usuario eligio el rango a mano

    with caja("fila").style("margin-top:14px; align-items:flex-end") as controles:
        entrada_min = campo("x mínimo", e.x_min, lambda v: cambiar_rango("x_min", v), ancho="120px")
        entrada_max = campo("x máximo", e.x_max, lambda v: cambiar_rango("x_max", v), ancho="120px")
        entrada_n = campo("Subintervalos", e.subintervalos, lambda v: cambiar_rango("subintervalos", v), ancho="130px")
        boton_graficar = boton("Graficar", graficar, icono="show_chart", principal=True)
        boton_auto = boton("Rango automático", lambda: graficar(ajustar_rango=True), icono="auto_fix_high")
    vista.pasos_guia.append((controles, "Rango de la gráfica",
                             "Elija desde qué x hasta qué x graficar y en cuántos subintervalos se tabula la función."))
    vista.pasos_guia.append((boton_auto, "Rango automático",
                             "Busca solo un rango y un paso h donde se vean las raíces de f(x), cada una en su propio intervalo."))

    async def tabular_vista():
        """Usa como rango de la tabulacion lo que se esta viendo en la grafica (despues de mover o hacer zoom)."""
        if not e.vista_plano:
            ui.notify("Primero mueva la gráfica o haga zoom para elegir qué parte tabular.", type="info", position="top")
            return
        e.x_min, e.x_max = rango_redondo(*e.vista_plano)
        e.rango_automatico = False
        await graficar()

    with caja("fila").style("gap:8px; align-items:center; margin-top:10px") as zoom:
        html('<span class="texto-suave">Explore la gráfica como en GeoGebra: <b>rueda</b> para acercar o alejar, '
             '<b>arrastrar</b> para moverse. Si encuentra otra raíz, puede tabular esa zona:</span>')
        boton("Tabular la vista actual", tabular_vista, icono="crop_free", clases="compacto")
    vista.pasos_guia.append((zoom, "Zoom y paneo",
                             "Con la rueda del ratón (o pellizcando) la gráfica se aleja o acerca sin límite; se arrastra para moverla. "
                             "«Tabular la vista actual» busca los intervalos con cambio de signo en la zona que se está viendo."))

    @ui.refreshable
    def resultados():
        t = e.tabulacion
        if t is None:
            with caja("caja").style("display:grid; place-items:center; padding:50px; margin-top:16px"):
                ui.spinner(size="40px", color="grey-7")
            return

        with caja("escalonado").style("margin-top:16px"):
            if e.aviso_rango:
                aviso(e.aviso_rango, "info").style("margin-bottom:12px")
            grafico = plano(datos_plano(vista))
            vista.pasos_guia.append((grafico, "Gráfica de f(x)",
                                     "Las franjas (I1, I2…) son los intervalos donde la curva cruza el eje x. "
                                     "Pase el cursor para ver f(x) en cada punto."))

            subtitulo("Intervalos con cambio de signo: f(a)·f(b) < 0")
            if t["intervalos"]:
                with caja("rejilla tres") as lista:
                    for iv in t["intervalos"]:
                        tarjeta_intervalo(iv)
                vista.pasos_guia.append((lista, "Elegir el intervalo",
                                         "Haga clic en el intervalo que quiere resolver. f(a) y f(b) tienen signos distintos: "
                                         "por el teorema de Bolzano hay una raíz dentro."))
            else:
                with caja("fila").style("align-items:center; gap:12px"):
                    aviso("No hay cambios de signo en este rango. Use «Rango automático», amplíe el rango "
                          "o aumente los subintervalos.", "advertencia").style("flex:1")
                    boton("Rango automático", lambda: graficar(ajustar_rango=True), icono="auto_fix_high")

            n_sugerido = t["subintervalos_sugeridos"]
            if n_sugerido:
                with caja("fila").style("align-items:center; gap:12px; margin-top:10px"):
                    aviso(f"La curva cruza el eje más veces de las que muestra la tabla: con h = {t['paso']:g} hay raíces "
                          f"que quedan juntas en un mismo subintervalo y se anulan. Con {n_sugerido} subintervalos se ven todas.",
                          "advertencia").style("flex:1")

                    async def usar_sugerido(n=n_sugerido):
                        e.subintervalos = str(n)
                        await graficar()

                    boton(f"Usar {n_sugerido} subintervalos", usar_sugerido, icono="grid_on")

            if t["discontinuidades"]:
                saltos = "; ".join(f"[{d['a']:g}, {d['b']:g}] (x ≈ {d['x']:.4g})" for d in t["discontinuidades"])
                aviso(f"f(x) también cambia de signo en {saltos}, pero ahí hay una asíntota o un salto, no una raíz: "
                      "Bolzano exige que f sea continua, por eso esos tramos no se ofrecen como intervalo.",
                      "advertencia").style("margin-top:10px")

            exactas = [iv["exacta"] for iv in t["intervalos"] if iv["exacta"] is not None]
            if exactas:
                aviso(f"En la tabulación f(x) = 0 exactamente en x = {', '.join(f'{x:g}' for x in exactas)}: "
                      + vista.AVISO_RAIZ_EXACTA, "exito").style("margin-top:10px")
            if t["raices_que_tocan"]:
                aviso(f"En x = {', '.join(f'{x:g}' for x in t['raices_que_tocan'])} la curva toca el eje sin cruzarlo "
                      f"(raíz doble): f no cambia de signo, así que el método de {vista.NOMBRE} no puede encerrar esa raíz.",
                      "info").style("margin-top:10px")
            if t["puntos_indefinidos"]:
                aviso(f"f(x) no está definida en {t['puntos_indefinidos']} punto(s) del rango "
                      "(por ejemplo ln de un número negativo); esos tramos no se consideran.",
                      "info").style("margin-top:10px")

            html(desplegable_html(f"Tabulación de f(x): {len(t['tabla']) - 1} subintervalos con paso h = {t['paso']:g}",
                                  tabla_tabulacion(t)))

        with caja("fila").style("justify-content:space-between; margin-top:18px"):
            boton("Anterior", lambda: vista.ir_a(1), icono="arrow_back")
            activo = e.intervalo_activo
            with caja("fila").style("gap:8px"):
                if activo:
                    boton("Escribir mi propio intervalo", lambda: vista.ir_a(3), icono="edit")
                boton(f"Continuar con I{activo}" if activo else "Escribir el intervalo a mano",
                      lambda: vista.ir_a(3), icono="arrow_forward", principal=True)

    def tarjeta_intervalo(iv):
        activa = iv["numero"] == e.intervalo_activo
        if iv["exacta"] is not None:
            explicacion = f'f({iv["exacta"]:g}) = 0: raíz exacta en x = {iv["exacta"]:g}'
        else:
            explicacion = f'Signos {signo(iv["fa"])} y {signo(iv["fb"])}: hay una raíz dentro'
        tarjeta = html(
            f'<div class="opcion-titulo mono">I{iv["numero"]} = [{iv["a"]:g}, {iv["b"]:g}]</div>'
            f'<div class="opcion-detalle mono">f(a) = <b class="{clase_signo(iv["fa"])}">{con_signo(iv["fa"], 4)}</b>'
            f' &nbsp;→&nbsp; f(b) = <b class="{clase_signo(iv["fb"])}">{con_signo(iv["fb"], 4)}</b></div>'
            f'<div class="opcion-extra">{escapar(explicacion)}</div>',
            "opcion" + (" activa" if activa else ""))

        async def elegir():
            await vista.elegir_intervalo(iv)
            if not tarjeta.is_deleted:
                resultados.refresh()

        tarjeta.on("click", elegir)

    resultados()

    # Al entrar por primera vez se grafica automaticamente
    if e.tabulacion is None and e.funcion_lista() is not None:
        ui.timer(0.1, graficar, once=True)


def tabla_tabulacion(t):
    inicios = {iv["a"] for iv in t["intervalos"] if iv["exacta"] is None}
    exactas = {iv["exacta"] for iv in t["intervalos"] if iv["exacta"] is not None}
    filas = []
    for p in t["tabla"]:
        if p["x"] in inicios:
            marca = ' <span class="insignia azul">cambia de signo</span>'
        elif p["x"] in exactas:
            marca = ' <span class="insignia azul">raíz exacta</span>'
        else:
            marca = ""
        valor = "indefinida" if p["y"] is None else con_signo(p["y"], 4)
        filas.append(f'<tr class="{"cambio" if marca else ""}"><td>{p["i"]}</td><td>{numero(p["x"], 4)}</td>'
                     f'<td class="{clase_signo(p["y"])}">{escapar(valor)}</td>'
                     f'<td style="text-align:left">{signo(p["y"])}{marca}</td></tr>')
    return ('<div class="contenedor-tabla mono" style="max-height:320px">'
            '<table class="tabla"><thead><tr><th>i</th><th>x[i]</th><th>f(x[i])</th><th style="text-align:left">signo</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>')
