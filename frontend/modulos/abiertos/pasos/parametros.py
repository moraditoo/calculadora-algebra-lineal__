# frontend/modulos/abiertos/pasos/parametros.py
# Paso 3 de los metodos abiertos: valor(es) inicial(es), tolerancia E, criterio de parada y
# maximo de iteraciones. Se detiene con la primera de dos condiciones: error < E o maximo de iteraciones.
from nicegui import ui

from backend.metodos_numericos.biseccion import leer_numero
from ....componentes import aviso, boton, caja, campo, html, subtitulo, tarjetas_opcion
from ....formato import con_signo, numero
from ...biseccion.pasos import decimales
from ..estado import CRITERIOS


def construir(vista):
    e = vista.estado
    dos = vista.VALORES == 2
    html('<div class="subtitulo" style="margin-top:0">Paso 3 · Parámetros del método</div>')
    html('<div class="texto-suave">El valor inicial lo elige <b>usted</b>: escriba ' +
         ("<b>x₀</b> y <b>x₁</b>" if dos else "<b>x₀</b>") +
         ' mirando la gráfica del paso 2 (o haga clic sobre ella en ese paso). Es un método abierto: no hace falta un '
         'intervalo que encierre la raíz, pero conviene empezar cerca de ella; si x₀ está lejos el método puede '
         'divergir o llegar a otra raíz.</div>')

    def cambiar(nombre, valor):
        setattr(e, nombre, valor)
        if nombre in ("x0", "x1"):
            e.intervalo_activo = None
            revision.refresh()
            recomendados.refresh()
        if nombre in ("tolerancia", "criterio"):
            actualizar_decimales()
            vista.tarjetas_resultado.refresh()

    with caja("fila").style("margin-top:14px") as campos:
        entradas = {"x0": campo("x₀ (valor inicial)", e.x0, lambda v: cambiar("x0", v), ancho="170px")}
        if dos:
            entradas["x1"] = campo("x₁ (segundo valor)", e.x1, lambda v: cambiar("x1", v), ancho="170px")
        campo("Tolerancia E", e.tolerancia, lambda v: cambiar("tolerancia", v), ancho="140px")
        campo("Máx. iteraciones", e.max_iteraciones, lambda v: cambiar("max_iteraciones", v), ancho="140px")
    vista.pasos_guia.append((campos, "Datos del método",
                             ("x₀ y x₁ son los dos puntos con los que empieza la secante" if dos else
                              "x₀ es el punto donde se traza la primera tangente")
                             + "; E es la tolerancia y el máximo de iteraciones evita cálculos interminables."))

    aviso("El método se detiene con la primera de estas dos condiciones: <b>1)</b> el error es menor que la "
          "tolerancia E (converge) o <b>2)</b> se llega al máximo de iteraciones. Al final se indica si el método <b>converge</b> (las aproximaciones se acercan a una raíz) o <b>diverge</b> (no se acercan o se alejan).",
          "info", es_html=True).style("margin-top:12px")

    async def usar_recomendado(iv):
        valores = vista.valores_de_intervalo(iv)
        for nombre, entrada in entradas.items():
            entrada.set_value(f"{valores[nombre]:.12g}")
        await vista.elegir_intervalo(iv)  # marca el intervalo y actualiza la grafica
        if not campos.is_deleted:
            revision.refresh()
            recomendados.refresh()

    @ui.refreshable
    def recomendados():
        t = e.tabulacion
        if t is None:
            html('<div class="texto-suave" style="margin-top:10px">Buscando valores recomendados…</div>')
            return
        if not t["intervalos"]:
            aviso("La gráfica no encontró cambios de signo: escriba el valor inicial cerca de donde la curva toca el eje.",
                  "info").style("margin-top:10px")
            return
        with caja().style("margin-top:10px") as fila:
            with caja("fila").style("gap:8px; align-items:center"):
                html('<span class="etiqueta" style="margin:0">Recomendaciones (opcionales):</span>')
                for iv in t["intervalos"]:
                    valores = vista.valores_de_intervalo(iv)
                    texto = ", ".join(f"{'x₀' if n == 'x0' else 'x₁'} = {v:g}" for n, v in valores.items())
                    boton(f'I{iv["numero"]} → {texto}', lambda iv=iv: usar_recomendado(iv),
                          principal=iv["numero"] == e.intervalo_activo, clases="compacto")
            html('<div class="texto-suave" style="margin-top:6px">Salen de los intervalos del paso 2, donde f(a)·f(b) &lt; 0: '
                 + ("se usan sus dos extremos como x₀ y x₁." if dos else
                    "x₀ es el extremo donde |f| es menor (la curva está más cerca del eje x) y f'(x₀) ≠ 0.")
                 + " Son solo una sugerencia: puede escribir cualquier otro valor cercano a la raíz.</div>")
        vista.pasos_guia.append((fila, "Valores recomendados",
                                 "Salen de los intervalos donde f cambia de signo (paso 2): "
                                 + ("x₀ y x₁ son sus extremos." if dos else "x₀ es el extremo donde |f| es menor.")))

    recomendados()

    @ui.refreshable
    def revision():
        caja_revision = revisar(vista)
        if caja_revision is not None:
            caja_revision.style("margin-top:14px")
            vista.pasos_guia.append((caja_revision, "Revisión antes de iterar",
                                     "Se evalúa f en los valores iniciales y se revisa que la fórmula no divida entre cero."))

    revision()

    subtitulo("Criterio de parada (el error debe ser menor que E)")
    with caja() as criterios:
        tarjetas_opcion([{**c, "titulo": f'<span class="mono">{c["titulo"]}</span>'
                          + (' <span class="insignia verde">recomendado</span>' if c["valor"] == vista.CRITERIO_DE_CLASE else "")}
                         for c in CRITERIOS],
                        lambda: e.criterio, lambda v: cambiar("criterio", v), columnas="cinco")
    vista.pasos_guia.append((criterios, "Criterio de parada", vista.NOTA_CRITERIO))

    subtitulo("Decimales a mostrar")
    refrescar_decimales = decimales.control(vista)

    def actualizar_decimales():
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
        """Si se llego aqui sin graficar, se tabula para recomendar valores (sin borrar los que ya se escribieron)."""
        previos = {n: getattr(e, n) for n in entradas}
        if not await vista.graficar() or campos.is_deleted:
            return
        activo = e.intervalo_activo
        for nombre, entrada in entradas.items():
            if previos[nombre]:
                setattr(e, nombre, previos[nombre])
            entrada.set_value(getattr(e, nombre))
        e.intervalo_activo = activo  # set_value lo borra al avisar del cambio
        revision.refresh()
        recomendados.refresh()

    if e.tabulacion is None and e.funcion_lista() is not None:
        ui.timer(0.1, buscar_recomendados, once=True)


def revisar(vista):
    """Evalua f (y f') en los valores iniciales y avisa si la formula dividiria entre cero."""
    e = vista.estado
    f = e.funcion_lista()
    if f is None:
        return aviso("La función del paso 1 no es válida.", "error")
    nombres = ("x0", "x1") if vista.VALORES == 2 else ("x0",)
    if any(not getattr(e, n).strip() for n in nombres):
        return aviso("Elija un valor recomendado o escriba " + ("x₀ y x₁." if vista.VALORES == 2 else "x₀."), "info")
    try:
        valores = [leer_numero(getattr(e, n), n.replace("x0", "x₀").replace("x1", "x₁")) for n in nombres]
    except ValueError as error:
        return aviso(str(error), "error")
    imagenes = [f.evaluar(x) for x in valores]
    for x, fx, n in zip(valores, imagenes, ("x₀", "x₁")):
        if fx is None:
            return aviso(f"f(x) no está definida en {n} = {x:g}. Elija otro valor.", "error")
    detalle = " &nbsp;·&nbsp; ".join(f'f({x:g}) = <b class="mono">{con_signo(fx, 6)}</b>' for x, fx in zip(valores, imagenes))

    if vista.VALORES == 1:
        x0, fx0 = valores[0], imagenes[0]
        if fx0 == 0:
            return aviso(f"{detalle}<br>f(x₀) = 0: x₀ ya es la raíz exacta.", "exito", es_html=True)
        df = e.derivada_lista()
        if df is None:
            return aviso(f"{detalle}<br>La derivada del paso 1 no es válida: {e.error_derivada}", "error", es_html=True)
        dfx0 = df.evaluar(x0)
        detalle += f' &nbsp;·&nbsp; f\'({x0:g}) = <b class="mono">{con_signo(dfx0, 6) if dfx0 is not None else "no definida"}</b>'
        if dfx0 is None or dfx0 == 0:
            return aviso(f"{detalle}<br>✗ f'(x₀) = 0 (o no está definida): la tangente es horizontal y la fórmula "
                         "divide entre cero. Elija otro x₀.", "error", es_html=True)
        x1 = x0 - fx0 / dfx0
        lineas = [detalle]
        tipo = "exito"
        if abs(dfx0) < 1e-3 * max(1.0, abs(fx0)):
            lineas.append(f"⚠ |f'(x₀)| es muy pequeño: la tangente es casi horizontal y el salto puede ser enorme "
                          f"(x₁ = {numero(x1, 6)}). Conviene elegir otro x₀.")
            tipo = "advertencia"
        else:
            lineas.append("✓ f'(x₀) ≠ 0: se puede aplicar la fórmula.")
        lineas.append(f"Primera aproximación: x₁ = x₀ − f(x₀)/f'(x₀) = <b class=\"mono\">{numero(x1, 9)}</b>")
        f1 = f.evaluar(x1)
        if f1 is None:
            lineas.append("✗ f no está definida en x₁: el método se saldría del dominio. Elija otro x₀.")
            tipo = "error"
        # Recomendacion (condicion de Fourier): si f(x0)·f''(x0) > 0 la tangente no se pasa al otro lado de la raiz
        segunda = df.derivada().evaluar(x0) if hasattr(df, "derivada") else None
        if segunda is not None and segunda != 0 and tipo == "exito":
            if fx0 * segunda > 0:
                lineas.append("✓ f(x₀)·f''(x₀) &gt; 0 (condición de Fourier): buen valor inicial; si f' y f'' no cambian de "
                              "signo cerca de la raíz, las aproximaciones se acercan sin pasarse al otro lado.")
            else:
                lineas.append("f(x₀)·f''(x₀) &lt; 0: la primera tangente puede pasarse al otro lado de la raíz; "
                              "si x₀ está cerca normalmente igual converge.")
        return aviso("<br>".join(lineas), tipo, es_html=True)

    (x0, x1), (fx0, fx1) = valores, imagenes
    if x0 == x1:
        return aviso(f"{detalle}<br>✗ x₀ y x₁ deben ser distintos: la secante necesita dos puntos.", "error", es_html=True)
    if fx1 - fx0 == 0:
        return aviso(f"{detalle}<br>✗ f(x₁) − f(x₀) = 0: la secante es horizontal y la fórmula divide entre cero. "
                     "Elija otros valores.", "error", es_html=True)
    x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
    encierra = ("f(x₀)·f(x₁) &lt; 0: encierran la raíz (no es obligatorio en un método abierto)."
                if fx0 * fx1 < 0 else
                "f(x₀)·f(x₁) &gt; 0: no encierran la raíz; en un método abierto no es obligatorio, pero puede no converger.")
    return aviso(f"{detalle}<br>✓ f(x₁) − f(x₀) ≠ 0: se puede aplicar la fórmula. Primera aproximación: "
                 f"x₂ = <b class=\"mono\">{numero(x2, 9)}</b><br>{encierra}", "exito", es_html=True)
