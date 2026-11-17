# frontend/modulos/abiertos/pasos/eleccion.py
# Paso 2 de los metodos abiertos (debajo de los intervalos): el usuario elige x0 (y x1) mirando
# la grafica. El programa NO lo elige solo: explica como hacerlo y da una recomendacion que el
# usuario puede aceptar con un boton.
from ....componentes import aviso, boton, caja, html, subtitulo
from ....formato import con_signo

COMO_NEWTON = [
    "Ubique en la gráfica dónde la curva <b>corta el eje x</b> (las franjas I1, I2… marcan esos cortes).",
    "<b>Haga clic sobre la gráfica</b> en un punto cercano a ese corte: ese x será x₀. Con la rueda del ratón "
    "puede acercarse para elegirlo con más precisión. También puede escribirlo en el paso 3.",
    "Evite puntos donde la curva es casi horizontal (<b>f'(x₀) ≈ 0</b>): la tangente cortaría el eje muy lejos "
    "y el método puede divergir.",
    "Si hay varias raíces, Newton-Raphson suele llegar a la más cercana a x₀: elija x₀ cerca de la que quiere encontrar.",
]

COMO_SECANTE = [
    "Ubique en la gráfica dónde la curva <b>corta el eje x</b> (las franjas I1, I2… marcan esos cortes).",
    "<b>Haga dos clics sobre la gráfica</b>: el primero elige x₀ y el segundo x₁ (después se alternan). "
    "También puede escribirlos en el paso 3.",
    "Conviene que x₀ y x₁ estén cerca de la raíz, por ejemplo uno a cada lado del corte (como en clase: x₀ = 1, x₁ = 2). "
    "En un método abierto <b>no es obligatorio</b> que encierren la raíz.",
    "f(x₀) y f(x₁) deben ser distintos: si son iguales la recta secante es horizontal y no corta el eje.",
]


def razon_newton(iv, x0, df):
    """Por que se recomienda ese x0 en el intervalo."""
    a, b, fa, fb = iv["a"], iv["b"], iv["fa"], iv["fb"]
    texto = (f"En I{iv['numero']} = [{a:g}, {b:g}]: |f({a:g})| = {abs(fa):.4g} y |f({b:g})| = {abs(fb):.4g}. "
             f"Se recomienda <b>x₀ = {x0:g}</b>, el extremo donde |f| es menor: ahí la curva está más cerca del eje x "
             "y por lo tanto de la raíz.")
    pendiente = df.evaluar(x0) if df else None
    if pendiente is not None:
        texto += f" Además f'({x0:g}) = {con_signo(pendiente, 4)} ≠ 0, así que la tangente sí corta el eje."
    return texto


def razon_secante(iv):
    return (f"En I{iv['numero']} = [{iv['a']:g}, {iv['b']:g}]: f({iv['a']:g}) = {con_signo(iv['fa'], 4)} y "
            f"f({iv['b']:g}) = {con_signo(iv['fb'], 4)} tienen signos distintos. Se recomienda usar los extremos, "
            f"<b>x₀ = {iv['a']:g} y x₁ = {iv['b']:g}</b>: la primera secante corta el eje entre ellos, muy cerca de la raíz "
            "(como en el ejemplo de clase x₀ = 1, x₁ = 2).")


def _estado_valores(vista, f):
    """Lo que vale f (y f') en los valores que eligio el usuario."""
    e = vista.estado
    valores = vista.valores_elegidos()
    dos = vista.VALORES == 2
    if not valores:
        return aviso("Todavía no eligió " + ("x₀ ni x₁" if dos else "x₀") + ". Haga clic sobre la gráfica "
                     "o use la recomendación de un intervalo.", "info")
    nombres = {"x0": "x₀", "x1": "x₁"}
    partes = []
    for nombre, x in valores.items():
        fx = f.evaluar(x)
        partes.append(f'{nombres[nombre]} = <b class="mono">{x:g}</b> → f({x:g}) = '
                      f'<b class="mono">{con_signo(fx, 6) if fx is not None else "no definida"}</b>')
    lineas = [" &nbsp;·&nbsp; ".join(partes)]
    tipo = "exito"

    t = e.tabulacion
    iv = vista._intervalo_de_valores(t["intervalos"]) if t else None
    if iv:
        lineas.append(f"Está en I{iv['numero']} = [{iv['a']:g}, {iv['b']:g}], cerca de una raíz.")
    elif t and t["intervalos"]:
        lineas.append("No está dentro de ningún intervalo con cambio de signo: puede funcionar, pero el método podría "
                      "ir a otra raíz o divergir.")
        tipo = "advertencia"

    if any(f.evaluar(x) is None for x in valores.values()):
        lineas.append("f(x) no está definida ahí: elija otro valor.")
        tipo = "error"
    elif not dos and "x0" in valores:
        df = vista.derivada_usada()
        pendiente = df.evaluar(valores["x0"]) if df else None
        if pendiente is None or pendiente == 0:
            lineas.append("f'(x₀) = 0 (o no está definida): la tangente es horizontal y la fórmula divide entre cero. "
                          "Elija otro x₀.")
            tipo = "error"
        else:
            escala = max(1.0, abs(f.evaluar(valores["x0"])))
            lineas.append(f"f'(x₀) = {con_signo(pendiente, 6)}"
                          + (" ≈ 0: la tangente es casi horizontal y el salto puede ser enorme." if abs(pendiente) < 1e-3 * escala
                             else " ≠ 0 ✓"))
            if abs(pendiente) < 1e-3 * escala:
                tipo = "advertencia"
    elif dos and len(valores) == 2:
        (x0, x1) = valores["x0"], valores["x1"]
        if x0 == x1:
            lineas.append("x₀ y x₁ deben ser distintos.")
            tipo = "error"
        elif f.evaluar(x0) == f.evaluar(x1):
            lineas.append("f(x₀) = f(x₁): la secante sería horizontal. Elija otros valores.")
            tipo = "error"
    elif dos:
        lineas.append("Falta " + ("x₁" if "x0" in valores else "x₀") + ": haga otro clic sobre la gráfica.")
        tipo = "info"
    return aviso("<br>".join(lineas), tipo, es_html=True)


def panel(vista):
    e = vista.estado
    f = e.funcion_lista()
    t = e.tabulacion
    if f is None or t is None:
        return
    dos = vista.VALORES == 2
    subtitulo("Elija usted el valor inicial " + ("x₀ y x₁" if dos else "x₀"))
    with caja("caja").style("padding:14px 18px") as marco:
        pasos = COMO_SECANTE if dos else COMO_NEWTON
        html('<div class="etiqueta" style="margin:0 0 4px">Cómo elegirlo</div>'
             '<ol class="texto-suave" style="margin:0 0 10px 18px; line-height:1.65">'
             + "".join(f"<li>{p}</li>" for p in pasos) + "</ol>")
        _estado_valores(vista, f)

        activo = next((iv for iv in t["intervalos"] if iv["numero"] == e.intervalo_activo), None)
        if activo is None and t["intervalos"]:
            html('<div class="texto-suave" style="margin-top:10px">Haga clic en una tarjeta de intervalo (I1, I2…) para ver '
                 "qué valor inicial se recomienda en ese tramo.</div>")
        elif activo is not None:
            recomendado = vista.valores_de_intervalo(activo)
            razon = razon_secante(activo) if dos else razon_newton(activo, recomendado["x0"], vista.derivada_usada())
            with caja("fila").style("align-items:center; gap:12px; margin-top:10px"):
                aviso("Recomendación: " + razon, "info", es_html=True).style("flex:1")
                texto = ", ".join(f"{'x₀' if n == 'x0' else 'x₁'} = {v:g}" for n, v in recomendado.items())

                async def usar(iv=activo):
                    await vista.aplicar_recomendacion(iv)
                    if vista._refrescar_paso2:
                        vista._refrescar_paso2()

                boton(f"Usar {texto}", usar, icono="check", clases="compacto")
    vista.pasos_guia.append((marco, "Elegir el valor inicial",
                             "El valor inicial lo elige usted con un clic sobre la gráfica, cerca de donde la curva corta "
                             "el eje x. Abajo se muestra una recomendación con su explicación."))
