# frontend/modulos/abiertos/pasos/derivada.py
# Paso 1 (debajo de f(x)): la derivada f'(x). Se calcula sola con las reglas de derivacion;
# en Newton-Raphson tambien se puede escribir a mano y se compara con la calculada.
from nicegui import ui

from ....componentes import aviso, caja, campo, html, segmentado, subtitulo, teclado
from ....formato import escapar

# Puntos donde se compara la derivada escrita con la calculada
PUNTOS_PRUEBA = (0.4, 0.9, 1.3, 1.7, -0.3, -0.7, -1.5, 2.6, 3.4, -2.5, 6.5, -9, 11, 45, -40)


def seccion(vista):
    e = vista.estado
    temporizador = {"actual": None}

    def comparar(escrita):
        """Comprueba la derivada escrita contra la calculada en varios puntos."""
        automatica = e.derivada_automatica()
        if automatica is None:
            return
        for observacion in escrita.avisos:
            aviso(observacion, "advertencia").style("margin-top:10px")
        comparados = 0
        f = e.funcion_lista()
        for x in PUNTOS_PRUEBA:
            if f is None or f.evaluar(x) is None:
                continue   # fuera del dominio de f no importa lo que de la derivada
            a, b = escrita.evaluar(x), automatica.evaluar(x)
            if (a is None) != (b is None):
                definida, no_definida = ("escrita", "calculada") if b is None else ("calculada", "escrita")
                aviso(f"La derivada escrita no coincide con la calculada f'(x) = {automatica.legible}: en x = {x:g} "
                      f"la {definida} da un número y la {no_definida} no está definida. Revísela antes de iterar.",
                      "advertencia").style("margin-top:10px")
                return
            if a is None:
                continue
            comparados += 1
            if abs(a - b) > 1e-6 * max(1.0, abs(b)):
                aviso(f"La derivada escrita no coincide con la calculada f'(x) = {automatica.legible}: en x = {x:g} "
                      f"la escrita da {a:.6g} y la calculada {b:.6g}. Revísela antes de iterar.",
                      "advertencia").style("margin-top:10px")
                return
        if comparados == 0:
            aviso(f"No se pudo comparar con la derivada calculada f'(x) = {automatica.legible}: ninguna de las dos "
                  "da un número en los puntos de prueba. Revísela antes de iterar.", "advertencia").style("margin-top:10px")
            return
        aviso(f"✓ Coincide con la derivada calculada por el programa: f'(x) = {automatica.legible}",
              "exito").style("margin-top:10px")

    async def redibujar():
        vista.refrescar()   # una sola vez cuando deja de escribir, no en cada tecla
        await vista.actualizar_derivada()

    def programar():
        if temporizador["actual"]:
            temporizador["actual"].cancel()
        temporizador["actual"] = ui.timer(0.35, redibujar, once=True)

    def al_escribir(valor):
        if valor == e.derivada_escrita:
            return
        e.derivada_escrita = valor
        e.limpiar_resultados(tambien_grafica=False)
        programar()

    def cambiar_modo(modo):
        escrita = modo == "escrita"
        if escrita == e.usar_derivada_escrita:
            return
        e.usar_derivada_escrita = escrita
        if escrita and not e.derivada_escrita:
            automatica = e.derivada_automatica()
            e.derivada_escrita = automatica.legible if automatica else ""
        e.formula_derivada = None
        e.limpiar_resultados(tambien_grafica=False)
        vista.refrescar()
        entrada.refresh()
        cuadro.refresh()
        programar()

    with caja().style("margin-top:6px") as contenedor:
        with caja("fila").style("justify-content:space-between; align-items:center; margin:18px 0 8px"):
            subtitulo("Derivada f'(x)").style("margin:0")
            if vista.USA_DERIVADA:
                segmentado([("auto", "Calcularla automáticamente"), ("escrita", "Escribirla")],
                           lambda: "escrita" if e.usar_derivada_escrita else "auto", lambda modo: cambiar_modo(modo))
        if vista.USA_DERIVADA:
            html('<div class="texto-suave">Newton-Raphson necesita f\'(x) para trazar la tangente. El programa la deriva '
                 'solo con las reglas de derivación (potencia, producto, cociente y cadena) para polinomios, raíces, '
                 'exponenciales, logaritmos, trigonométricas, hiperbólicas, sus inversas y |x|. '
                 'También puede escribirla y se comprueba que coincida.</div>')
        else:
            html('<div class="texto-suave">La secante <b>no necesita</b> f\'(x): aproxima la pendiente con dos puntos de la curva. '
                 'Igual se muestra la derivada para comparar, en cada iteración, la pendiente de la secante con la de la tangente.</div>')

        @ui.refreshable
        def entrada():
            if not (vista.USA_DERIVADA and e.usar_derivada_escrita):
                return
            automatica = e.derivada_automatica()
            with caja().props("data-zona-teclado").style("width:100%"):
                campo_derivada = campo("f'(x) =", e.derivada_escrita, al_escribir, ancho="100%",
                                       placeholder=automatica.legible if automatica else "3x^2 - 1")
                campo_derivada.mark("texto-derivada")
                teclado(sin_ecuacion=True)
            vista.pasos_guia.append((campo_derivada, "Derivada escrita",
                                     "Escriba f'(x) como texto: 3x^2 - 1, -sen(x) - 1, 1/x + 1. Se usará en la fórmula de Newton-Raphson."))

        entrada()

        @ui.refreshable
        def cuadro():
            d = vista.derivada_usada()
            with caja("caja fila").style("min-height:64px; align-items:center; padding:10px 16px; margin-top:10px") as marco:
                if d is None and e.funcion_lista() is None and not e.usar_derivada_escrita:
                    aviso("La derivada se calcula en cuanto f(x) esté bien escrita.", "info").style("width:100%")
                elif d is None:
                    aviso(e.error_derivada or "Escriba la derivada f'(x).", "error").style("width:100%")
                elif e.formula_derivada:
                    html(f'<img src="{e.formula_derivada}" alt="f\'(x)">', "formula-img")
                else:
                    ui.spinner(size="26px", color="grey-7")
                if d is not None and vista.USA_DERIVADA and e.usar_derivada_escrita:
                    html('<span class="estado-escritura bien">✓ Bien escrita</span>').style("margin-left:auto")
            vista.pasos_guia.append((marco, "Derivada f'(x)",
                                     "Así queda la derivada que se usa en cada iteración (la tangente tiene pendiente f'(xₙ))."))
            if d is not None:
                html(f'<div class="texto-suave mono" style="margin-top:6px">f\'(x) = {escapar(d.legible)}</div>')
            if vista.USA_DERIVADA and e.usar_derivada_escrita and d is not None:
                comparar(d)

        cuadro()

    vista.refrescar_derivada = lambda: None if contenedor.is_deleted else cuadro.refresh()
    if e.formula_derivada is None and vista.derivada_usada() is not None and e.formula is not None:
        ui.timer(0.05, redibujar, once=True)
