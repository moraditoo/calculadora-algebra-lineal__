# frontend/modulos/romanos.py
# Aritmetica con numeros romanos y conversion arabigo <-> romano.
from nicegui import ui

from backend.sistemas_numericos.romanos import OperacionesRomanos
from .. import guia
from ..componentes import aviso, boton, caja, campo, encabezado, lista_pasos, resaltado, subtitulo, tarjeta


def construir():
    estado = {"a": "XIV", "b": "V", "entrada": "2026"}
    objetivos = {}

    with tarjeta():
        encabezado("Aritmética con números romanos",
                   "Acepta romanos o arábigos del 1 al 3999. La multiplicación se define como suma repetida.", "account_balance",
                   al_pedir_guia=lambda: guia.iniciar([
                       (objetivos.get("operandos"), "Operandos", "Escriba cada número en romano (XIV) o en arábigo (14)."),
                       (objetivos.get("botones"), "Operación", "Suma, resta o multiplicación con su procedimiento."),
                       (objetivos.get("conversor"), "Conversor", "Convierte en ambos sentidos: 2026 ↔ MMXXVI."),
                   ]))
        with caja("fila") as objetivos["operandos"]:
            campo("Operando A", estado["a"], lambda v: estado.update(a=v), ancho="170px", placeholder="XIV o 14")
            campo("Operando B", estado["b"], lambda v: estado.update(b=v), ancho="170px", placeholder="V o 5")
            with caja("fila") as objetivos["botones"]:
                boton("Sumar +", lambda: operar("suma"))
                boton("Restar −", lambda: operar("resta"))
                boton("Multiplicar ×", lambda: operar("multiplicar"), principal=True)

        @ui.refreshable
        def resultado_operacion(datos=None, error=None):
            if error:
                aviso(error, "error").style("margin-top:14px")
            if not datos:
                return
            with caja("escalonado").style("margin-top:16px"):
                resaltado("Resultado", datos["resultado_romano"], detalle=f"Equivalente decimal: {datos['resultado_arabigo']}")
                subtitulo("Procedimiento paso a paso")
                lista_pasos(datos["pasos"])

        resultado_operacion()

    with tarjeta():
        encabezado("Conversor arábigo ↔ romano",
                   "Ingrese un número arábigo (1 - 3999) o una expresión romana válida (I - MMMCMXCIX).", "sync_alt")
        with caja("fila") as objetivos["conversor"]:
            entrada = campo("Entrada", estado["entrada"], lambda v: estado.update(entrada=v), ancho="240px", placeholder="2026 o MMXXVI")
            entrada.on("keydown.enter", lambda: convertir())
            boton("Convertir", lambda: convertir(), icono="sync_alt", principal=True)

        @ui.refreshable
        def resultado_conversion(datos=None, error=None):
            if error:
                aviso(error, "error").style("margin-top:14px")
            if not datos:
                return
            with caja("escalonado").style("margin-top:16px"):
                resaltado(datos["direccion"], f"{datos['entrada']} = {datos['resultado']}")
                lista_pasos(datos["pasos"])

        resultado_conversion()

    operaciones = {"suma": OperacionesRomanos.suma, "resta": OperacionesRomanos.resta, "multiplicar": OperacionesRomanos.multiplicacion}

    def operar(op):
        try:
            resultado_operacion.refresh(operaciones[op](estado["a"], estado["b"]))
        except Exception as error:
            resultado_operacion.refresh(error=str(error))

    def convertir():
        try:
            resultado_conversion.refresh(OperacionesRomanos.conversion_bidireccional(estado["entrada"]))
        except Exception as error:
            resultado_conversion.refresh(error=str(error))
