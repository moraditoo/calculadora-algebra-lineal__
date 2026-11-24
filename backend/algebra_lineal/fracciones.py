# backend/algebra_lineal/fracciones.py
# Utilidades comunes de algebra lineal: leer numeros escritos por el usuario como
# fracciones exactas, darles formato y calcular determinantes exactos.
from fractions import Fraction

# Signos que llegan al copiar de un PDF o de Word
_REEMPLAZOS = str.maketrans({"−": "-", "–": "-", "—": "-", ",": ".", " ": None, " ": None})


def parse_frac(valor):
    """'3', '-2.5', '3/4', '−1' (signo de PDF) -> Fraction exacta."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor)
    texto = str(valor).translate(_REEMPLAZOS)
    if not texto:
        raise ValueError("Hay una celda vacía en la matriz.")
    try:
        if "/" in texto:
            numerador, denominador = texto.split("/")
            if Fraction(denominador) == 0:
                raise ValueError(f"División entre cero en '{valor}'.")
            return Fraction(numerador) / Fraction(denominador)
        return Fraction(texto)
    except ValueError as error:
        if "División" in str(error):
            raise
        raise ValueError(f"El valor '{valor}' no es un número ni una fracción válida.") from None


def format_frac(valor):
    """Fraction -> '3', '-7/2'."""
    if not isinstance(valor, Fraction):
        valor = Fraction(str(valor))
    return str(valor.numerator) if valor.denominator == 1 else f"{valor.numerator}/{valor.denominator}"


def a_fracciones(matriz):
    return [[parse_frac(v) for v in fila] for fila in matriz]


def a_textos(matriz):
    return [[format_frac(v) for v in fila] for fila in matriz]


def determinante_exacto(matriz):
    """det(A) con fracciones exactas por eliminacion (O(n³)): (−1)^intercambios · producto de pivotes."""
    a = [fila[:] for fila in a_fracciones(matriz)]
    n = len(a)
    if any(len(fila) != n for fila in a):
        raise ValueError("El determinante solo existe para matrices cuadradas.")
    det = Fraction(1)
    for col in range(n):
        pivote = next((i for i in range(col, n) if a[i][col] != 0), None)
        if pivote is None:
            return Fraction(0)
        if pivote != col:
            a[col], a[pivote] = a[pivote], a[col]
            det = -det
        det *= a[col][col]
        for i in range(col + 1, n):
            if a[i][col] != 0:
                factor = a[i][col] / a[col][col]
                for j in range(col, n):
                    a[i][j] -= factor * a[col][j]
    return det
