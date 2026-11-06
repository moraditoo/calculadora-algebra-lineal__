# frontend/modulos/biseccion/pasos/decimales.py
# Control de "decimales a mostrar": − / numero / + y Auto (una cifra mas de las que pide E).
# Esta en los pasos 3, 4 y 5 y cambia al instante las tarjetas, la tabla y la conclusion.
from nicegui import ui

from ....componentes import boton, caja, html

MINIMO, MAXIMO = 2, 15


def control(vista, al_cambiar=None):
    """Dibuja el control y devuelve su funcion de refresco. al_cambiar: que redibujar del paso actual."""
    e = vista.estado

    def cambiar(valor=None, automatico=False):
        if automatico:
            e.decimales_automaticos = True
            e.ajustar_decimales()
        else:
            valor = max(MINIMO, min(MAXIMO, valor))
            if valor == e.decimales:
                return
            e.decimales, e.decimales_automaticos = valor, False  # lo eligio el usuario: ya no sigue a E
        dibujar.refresh()
        vista.tarjetas_resultado.refresh()
        if al_cambiar:
            al_cambiar()

    @ui.refreshable
    def dibujar():
        with caja("control-decimales"):
            html("Decimales", "etiqueta").style("margin:0")
            menos = boton("", lambda: cambiar(e.decimales - 1), icono="remove", clases="compacto redondo")
            html(str(e.decimales), "valor-decimales mono")
            mas = boton("", lambda: cambiar(e.decimales + 1), icono="add", clases="compacto redondo")
            menos.set_enabled(e.decimales > MINIMO)
            mas.set_enabled(e.decimales < MAXIMO)
            boton("Auto", lambda: cambiar(automatico=True), icono="auto_fix_high",
                  principal=e.decimales_automaticos, clases="compacto")
            html("según la precisión E" if e.decimales_automaticos else "elegidos a mano", "texto-suave")

    # El contenedor de afuera no se redibuja: asi la guia paso a paso siempre lo encuentra
    with caja() as contenedor:
        dibujar()
    vista.pasos_guia.append((contenedor, "Decimales a mostrar",
                             "Con − y + se elige cuántos decimales se ven en las tarjetas, la tabla y la conclusión. "
                             "Auto muestra una cifra más de las que pide E."))
    return dibujar
