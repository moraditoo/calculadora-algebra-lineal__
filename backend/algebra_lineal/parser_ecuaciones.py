# backend/algebra_lineal/parser_ecuaciones.py
# Lee un sistema lineal escrito como texto, una ecuacion por linea:
#     -3x - y + 4z + 5w = -6          10x₁ − x₂ + 2x₃ = 6          2x + 1/2 y = 3 - z
# Acepta signos copiados de un PDF (−), subindices (x₁, x_1), coeficientes enteros,
# decimales o fracciones, y variables o constantes en cualquiera de los dos lados.
import re
from fractions import Fraction

from .fracciones import parse_frac

_SUBINDICES = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_A_SUBINDICE = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
# Orden habitual de las incognitas escritas con una sola letra
_ORDEN_LETRAS = "xyzwtuvsrpqabcdefghijklmno"
_TERMINO = re.compile(r"^(?P<coef>\d*\.?\d*(?:/\d*\.?\d+)?)\*?(?P<var>[a-z]\d*)?$")


def nombre_bonito(nombre):
    """'x1' -> 'x₁' para mostrar."""
    letras = nombre.rstrip("0123456789")
    return letras + nombre[len(letras):].translate(_A_SUBINDICE)


def nombre_latex(nombre):
    """'x1' -> 'x_{1}' para KaTeX."""
    letras = nombre.rstrip("0123456789")
    return letras + (f"_{{{nombre[len(letras):]}}}" if letras != nombre else "")


def _limpiar(linea):
    t = linea.translate(_SUBINDICES).lower()
    for viejo, nuevo in (("−", "-"), ("–", "-"), ("—", "-"), ("·", "*"), ("×", "*"), ("_", ""), (",", ".")):
        t = t.replace(viejo, nuevo)
    return re.sub(r"\s+", "", t)


def _terminos(lado, linea):
    """'-3x+4z-6' -> [(-3, 'x'), (4, 'z'), (-6, None)]."""
    if not lado:
        raise ValueError(f"En «{linea}» falta un lado de la igualdad.")
    if re.search(r"[+-]{2,}|[+-]$", lado):
        raise ValueError(f"En «{linea}» hay dos signos seguidos o un signo sin término después.")
    resultado = []
    for signo, cuerpo in re.findall(r"([+-]?)([^+-]+)", lado):
        encontrado = _TERMINO.match(cuerpo)
        if not encontrado or (not encontrado["coef"] and not encontrado["var"]):
            raise ValueError(f"No se entiende el término «{signo}{cuerpo}» en «{linea}». "
                             "Escriba cada término como 3x, -1/2y o 4.5 (sin productos de variables).")
        coef = parse_frac(encontrado["coef"]) if encontrado["coef"] else Fraction(1)
        resultado.append((-coef if signo == "-" else coef, encontrado["var"]))
    return resultado


def _orden(nombre, apariciones):
    """Clave para ordenar incognitas: x, y, z, w...  o  x1, x2, x3..."""
    letras, numero = re.match(r"([a-z]+)(\d*)", nombre).groups()
    if numero:
        return (1, apariciones[letras], int(numero))
    if len(letras) == 1 and letras in _ORDEN_LETRAS:
        return (0, _ORDEN_LETRAS.index(letras), 0)
    return (2, apariciones[letras], 0)


def parse_ecuaciones(texto):
    """Devuelve (matriz aumentada, m, n, nombres de las incognitas)."""
    lineas = [l.strip() for l in re.split(r"[\n;]", texto or "") if l.strip()]
    if not lineas:
        raise ValueError("Escriba al menos una ecuación, por ejemplo: 2x + y = 5")
    ecuaciones = []
    apariciones = {}
    for linea in lineas:
        limpia = _limpiar(linea)
        if limpia.count("=") != 1:
            raise ValueError(f"La ecuación «{linea}» debe tener exactamente un signo =.")
        izquierda, derecha = limpia.split("=")
        coeficientes, constante = {}, Fraction(0)
        for lado, signo_lado in ((izquierda, 1), (derecha, -1)):
            for coef, variable in _terminos(lado, linea):
                if variable is None:
                    constante -= signo_lado * coef         # las constantes van al lado derecho
                else:
                    coeficientes[variable] = coeficientes.get(variable, Fraction(0)) + signo_lado * coef
                    apariciones.setdefault(re.match(r"[a-z]+", variable).group(), len(apariciones))
        ecuaciones.append((coeficientes, constante))

    nombres = sorted({v for coefs, _ in ecuaciones for v in coefs}, key=lambda v: _orden(v, apariciones))
    if not nombres:
        raise ValueError("No se encontró ninguna incógnita (x, y, z, w o x1, x2…).")
    matriz = [[coefs.get(v, Fraction(0)) for v in nombres] + [constante] for coefs, constante in ecuaciones]
    return matriz, len(matriz), len(nombres), nombres
