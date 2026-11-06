# frontend/formato.py
# Formato de numeros con la cantidad de decimales elegida.
import html


def numero(valor, decimales):
    if valor is None:
        return "—"
    if valor == 0:
        valor = 0.0  # evita mostrar "-0.00000" (cero negativo)
    # Un valor distinto de cero que se veria como 0.000... se muestra en notacion cientifica
    if valor != 0 and abs(valor) < 0.5 * 10 ** -decimales:
        return f"{valor:.4e}"
    return f"{valor:.{decimales}f}"


def con_signo(valor, decimales):
    texto = numero(valor, decimales)
    return "+" + texto if valor is not None and valor > 0 else texto


def clase_signo(valor):
    if valor is None or valor == 0:
        return ""
    return "positivo" if valor > 0 else "negativo"


def signo(valor):
    if valor is None:
        return "?"
    return "+" if valor > 0 else ("−" if valor < 0 else "0")


def escapar(texto):
    return html.escape(str(texto))
