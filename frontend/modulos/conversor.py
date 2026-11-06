# frontend/modulos/conversor.py
# Conversion entre sistemas numericos con el procedimiento completo.
from nicegui import ui

from backend.sistemas_numericos.conversor import ConversorSistemas
from .. import guia
from ..componentes import aviso, boton, caja, campo, encabezado, html, resaltado, selector, subtitulo, tarjeta
from ..formato import escapar

BASES = {
    "Binario": "Binario (base 2)",
    "Octal": "Octal (base 8)",
    "Decimal": "Decimal (base 10)",
    "Hexadecimal": "Hexadecimal (base 16)",
}


def construir():
    estado = {"numero": "123", "origen": "Octal", "destino": "Hexadecimal"}
    objetivos = {}

    with tarjeta():
        encabezado("Conversor de sistemas numéricos", "Convierte entre bases mostrando el procedimiento.", "swap_horiz",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("bases"), "Bases", "Elija la base del número y la base a la que se convierte."),
                       (objetivos.get("numero"), "Número", "Escriba el número en la base de origen y presione Convertir."),
                   ]))
        with caja("fila") as objetivos["bases"]:
            selector("Base origen", BASES, estado["origen"], lambda v: (estado.update(origen=v), convertir()))
            ui.icon("arrow_forward", size="20px").style("color:#9aa0a6; margin-bottom:10px")
            selector("Base destino", BASES, estado["destino"], lambda v: (estado.update(destino=v), convertir()))
        with caja("fila").style("margin-top:14px") as objetivos["numero"]:
            entrada = campo("Número", estado["numero"], lambda v: estado.update(numero=v), ancho="240px")
            entrada.on("keydown.enter", lambda: convertir())
            boton("Convertir", lambda: convertir(), icono="sync_alt", principal=True)

    @ui.refreshable
    def resultado(datos=None, error=None):
        if error:
            aviso(error, "error")
        if not datos:
            return
        with tarjeta("escalonado"):
            resaltado(datos["encabezado"], datos["resultado"])
            subtitulo("Solución paso a paso")
            with caja().style("display:flex; flex-direction:column; gap:8px"):
                for paso in datos["pasos"]:
                    html(escapar(paso), "bloque-paso mono")
            if datos.get("otras_bases"):
                subtitulo("Equivalencias en las demás bases")
                with caja("rejilla cuatro"):
                    for base, valor in datos["otras_bases"].items():
                        html(f'<div class="d-etiqueta">{escapar(base)}</div><div class="d-valor mono">{escapar(valor)}</div>', "dato")

    def convertir():
        try:
            resultado.refresh(ConversorSistemas.convertir(estado["numero"], estado["origen"], estado["destino"]))
        except Exception as error:
            resultado.refresh(error=str(error))

    resultado()
