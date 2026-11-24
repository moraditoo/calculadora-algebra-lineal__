# backend/algebra_lineal/iterativos.py
# Metodos iterativos para A·x = b: Jacobi y Gauss-Seidel (presentacion de clase).
#   1) Se despeja cada incognita de su ecuacion:  xᵢ = [bᵢ − Σⱼ≠ᵢ aᵢⱼ xⱼ] / aᵢᵢ
#   2) Se parte de x⁽⁰⁾ (por defecto el vector cero)
#   3) Jacobi usa SOLO los valores de x⁽ᵏ⁾; Gauss-Seidel usa de inmediato los xⱼ⁽ᵏ⁺¹⁾ ya calculados (j < i)
#   4) Se detiene cuando ‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ < ε (o el residuo ‖b − A·x‖∞ < ε) o al llegar al maximo de iteraciones
# Condicion suficiente de convergencia: dominancia diagonal estricta por filas |aᵢᵢ| > Σⱼ≠ᵢ |aᵢⱼ|.
# La condicion necesaria y suficiente es que el radio espectral de la matriz de iteracion sea < 1.
import math
from itertools import permutations

import numpy as np

from .fracciones import parse_frac
from .parser_ecuaciones import nombre_bonito, nombre_latex

METODOS = {"jacobi": "Jacobi", "gauss_seidel": "Gauss-Seidel"}
CRITERIOS = {
    "cambio": "Cambio entre iteraciones < ε",
    "residuo": "Residuo ‖b − Ax‖∞ < ε",
    "ambos": "Cambio y residuo < ε",
}
LIMITE_DIVERGENCIA = 1e12
MAX_ITERACIONES = 2000


# ----------------------------------------------------------------------
# Formato
# ----------------------------------------------------------------------
def num(valor, decimales=6):
    """Numero con los decimales pedidos y signo − tipografico."""
    if valor == 0:
        valor = 0.0
    texto = f"{valor:.{decimales}f}" if abs(valor) < 1e9 else f"{valor:.4e}"
    return texto.replace("-", "−")


def coeficiente(valor):
    """10 -> '10', 0.5 -> '0.5', 1/3 -> '0.333333'."""
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.6g}"


# ----------------------------------------------------------------------
# Lectura y analisis del sistema
# ----------------------------------------------------------------------
def leer_sistema(A_texto, b_texto):
    try:
        A = np.array([[float(parse_frac(v)) for v in fila] for fila in A_texto], dtype=float)
        b = np.array([float(parse_frac(v)) for v in b_texto], dtype=float)
    except ValueError as error:
        raise ValueError(str(error)) from None
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"Los métodos iterativos necesitan un sistema cuadrado (n ecuaciones y n incógnitas); "
                         f"se recibieron {A.shape[0]} ecuaciones y {A.shape[1] if A.ndim == 2 else 0} incógnitas.")
    if b.shape[0] != A.shape[0]:
        raise ValueError("El vector b debe tener un valor por cada ecuación.")
    return A, b


def leer_inicial(texto, n):
    """'0, 0, 0, 0' (o vacio = vector cero) -> array."""
    if texto is None or not str(texto).strip():
        return np.zeros(n)
    partes = [p for p in str(texto).replace(";", ",").replace("(", "").replace(")", "").split(",") if p.strip()]
    if len(partes) == 1 and n > 1:
        partes = partes * n          # un solo valor: se usa para todas las incognitas
    if len(partes) != n:
        raise ValueError(f"x⁽⁰⁾ debe tener {n} valores separados por comas (o dejarlo vacío para usar el vector cero).")
    try:
        return np.array([float(parse_frac(p)) for p in partes])
    except ValueError:
        raise ValueError("x⁽⁰⁾ solo admite números, por ejemplo: 0, 0, 0, 0") from None


def leer_tolerancia(texto):
    try:
        tolerancia = float(str(texto).replace("−", "-").replace("^", "e").replace("10e", "1e"))
    except ValueError:
        raise ValueError("La tolerancia debe ser un número positivo, por ejemplo 0.000001 o 1e-6.") from None
    if not 0 < tolerancia < 1:
        raise ValueError("La tolerancia debe estar entre 0 y 1 (por ejemplo 0.000001).")
    return tolerancia


def dominancia(A):
    """Tabla de dominancia diagonal por filas (como en la presentacion)."""
    filas = []
    for i, fila in enumerate(A):
        otros = [abs(v) for j, v in enumerate(fila) if j != i]
        suma = sum(otros)
        filas.append({
            "fila": i + 1, "diagonal": coeficiente(abs(fila[i])),
            "suma_texto": " + ".join(coeficiente(v) for v in otros) + f" = {coeficiente(suma)}",
            "suma": suma, "cumple": abs(fila[i]) > suma, "debil": abs(fila[i]) >= suma,
        })
    return {"filas": filas, "estricta": all(f["cumple"] for f in filas)}


def buscar_orden(A):
    """Orden de filas que deja la matriz estrictamente dominante. Si no existe, el orden sin ceros en
    la diagonal con menor radio espectral (el que mejor converge). Devuelve (orden, es_estricta)
    u (None, False) si ningun orden deja la diagonal sin ceros."""
    n = len(A)
    # Una fila solo puede ser dominante en la columna de su mayor |valor|
    destino = {}
    for i, fila in enumerate(A):
        j = int(np.argmax(np.abs(fila)))
        if abs(fila[j]) > np.sum(np.abs(fila)) - abs(fila[j]):
            destino.setdefault(j, i)
    if len(destino) == n:
        return [destino[j] for j in range(n)], True
    if n <= 7:
        mejor, puntaje = None, (math.inf, math.inf)
        for orden in permutations(range(n)):
            P = A[list(orden)]
            if np.any(np.diag(P) == 0):
                continue
            radios = (radio_espectral(P, "gauss_seidel"), radio_espectral(P, "jacobi"))
            if None not in radios and radios < puntaje:
                mejor, puntaje = list(orden), radios
        return mejor, False
    # Matrices grandes: voraz por columna (la fila libre con mayor |valor|)
    libres, orden = set(range(n)), []
    for j in range(n):
        i = max(libres, key=lambda r: abs(A[r][j]))
        if A[i][j] == 0:
            return None, False
        orden.append(i)
        libres.remove(i)
    return orden, False


def radio_espectral(A, metodo):
    """ρ(T) de la matriz de iteracion: el metodo converge para todo x⁽⁰⁾ si y solo si ρ(T) < 1."""
    D = np.diag(np.diag(A))
    L = np.tril(A, -1)
    U = np.triu(A, 1)
    try:
        T = -np.linalg.solve(D, L + U) if metodo == "jacobi" else -np.linalg.solve(D + L, U)
        return float(max(abs(np.linalg.eigvals(T))))
    except np.linalg.LinAlgError:
        return None


def despejes(A, b, nombres):
    """Formula de cada incognita despejada de su ecuacion, en texto y en LaTeX.
    10x₁ − x₂ + 2x₃ = 6   ->   x₁ = (6 + x₂ − 2x₃) / 10"""
    lista = []
    for i, fila in enumerate(A):
        texto, latex = [coeficiente(b[i])], [coeficiente(b[i])]
        for j, a in enumerate(fila):
            if j == i or a == 0:
                continue
            c = -a
            signo = "+" if c > 0 else "−"
            magnitud = "" if abs(c) == 1 else coeficiente(abs(c))
            texto.append(f"{signo} {magnitud}{nombre_bonito(nombres[j])}")
            latex.append(f"{'+' if c > 0 else '-'} {magnitud}{nombre_latex(nombres[j])}")
        lista.append({
            "texto": f"{nombre_bonito(nombres[i])} = ({' '.join(texto)}) / {coeficiente(A[i][i])}".replace("-", "−"),
            "latex": rf"{nombre_latex(nombres[i])} = \dfrac{{{' '.join(latex)}}}{{{coeficiente(A[i][i])}}}",
        })
    return lista


def _sustitucion(A, b, i, valores, decimales):
    """'(6 + 2.272727 − 2(−1.100000)) / 10' con los valores que usa la formula de xᵢ."""
    partes = [coeficiente(b[i])]
    for j, a in enumerate(A[i]):
        if j == i or a == 0:
            continue
        c = -a
        if abs(c) == 1:
            # ± 1·v se escribe como en clase: + 0.6, − 1.1 (el signo de v se combina con el de c)
            signo = "+" if c * valores[j] >= 0 else "−"
            partes.append(f"{signo} {num(abs(valores[j]), decimales)}")
        else:
            partes.append(f"{'+' if c > 0 else '−'} {coeficiente(abs(c))}({num(valores[j], decimales)})")
    return f"({' '.join(partes)}) / {coeficiente(A[i][i])}".replace("-", "−")


# ----------------------------------------------------------------------
# Iteraciones
# ----------------------------------------------------------------------
def iterar(A, b, x0, metodo, tolerancia, max_iteraciones, criterio="cambio", exacta=None, decimales=6):
    """Aplica Jacobi o Gauss-Seidel. Cada iteracion guarda el vector, la sustitucion de cada
    componente, el cambio ‖Δx‖∞, el residuo ‖b − Ax‖∞ y el error contra la solucion exacta."""
    if metodo not in METODOS:
        raise ValueError(f"Método desconocido: {metodo}")
    n = len(b)
    if np.any(np.diag(A) == 0):
        fila = int(np.where(np.diag(A) == 0)[0][0]) + 1
        raise ValueError(f"El coeficiente diagonal a{fila}{fila} es 0: no se puede despejar la incógnita {fila}. "
                         "Reordene las ecuaciones (opción «Reordenar filas»).")
    x = np.array(x0, dtype=float)
    iteraciones = [{
        "k": 0, "x": x.tolist(), "cambio": None, "residuo": float(np.max(np.abs(b - A @ x))),
        "error": float(np.max(np.abs(x - exacta))) if exacta is not None else None, "sustituciones": [],
    }]
    estado, motivo = "maximo", f"Se alcanzó el máximo de {max_iteraciones} iteraciones sin cumplir la tolerancia."
    for k in range(1, max_iteraciones + 1):
        anterior = x.copy()
        nuevo = x.copy()
        sustituciones = []
        for i in range(n):
            # Jacobi lee siempre el vector anterior; Gauss-Seidel el que se va actualizando
            fuente = anterior if metodo == "jacobi" else nuevo
            sustituciones.append(_sustitucion(A, b, i, fuente, decimales))
            nuevo[i] = (b[i] - (A[i] @ fuente - A[i][i] * fuente[i])) / A[i][i]
        x = nuevo
        if not np.all(np.isfinite(x)) or np.max(np.abs(x)) > LIMITE_DIVERGENCIA:
            estado, motivo = "diverge", (f"En la iteración {k} los valores crecieron sin control (|x| > 10¹²): "
                                         "el método diverge para este sistema.")
            break
        cambio = float(np.max(np.abs(x - anterior)))
        residuo = float(np.max(np.abs(b - A @ x)))
        iteraciones.append({
            "k": k, "x": x.tolist(), "cambio": cambio, "residuo": residuo,
            "error": float(np.max(np.abs(x - exacta))) if exacta is not None else None,
            "sustituciones": sustituciones,
        })
        cumple = {"cambio": cambio < tolerancia, "residuo": residuo < tolerancia,
                  "ambos": cambio < tolerancia and residuo < tolerancia}[criterio]
        if cumple:
            estado = "converge"
            motivo = (f"En la iteración {k} se cumple el criterio de parada: "
                      f"{CRITERIOS[criterio].lower().replace('ε', f'ε = {tolerancia:g}')}.")
            break
    ultima = iteraciones[-1]
    return {
        "metodo": metodo, "nombre": METODOS[metodo], "estado": estado, "convergio": estado == "converge",
        "motivo": motivo, "iteraciones": iteraciones, "total": ultima["k"], "solucion": ultima["x"],
        "cambio": ultima["cambio"], "residuo": ultima["residuo"], "error": ultima["error"],
        "verificacion": [{"ecuacion": i + 1, "ax": float(A[i] @ np.array(ultima["x"])), "b": float(b[i])}
                         for i in range(n)],
    }


def resolver(A_texto, b_texto, nombres=None, x0=None, metodos=("jacobi", "gauss_seidel"), tolerancia="0.000001",
             max_iteraciones=50, criterio="cambio", reordenar=True, decimales=6):
    """Analiza el sistema (dominancia, reordenamiento, radio espectral) y aplica los metodos pedidos."""
    A, b = leer_sistema(A_texto, b_texto)
    n = len(b)
    nombres = nombres or [f"x{i + 1}" for i in range(n)]
    tolerancia = leer_tolerancia(tolerancia)
    try:
        max_iteraciones = max(1, min(MAX_ITERACIONES, int(float(max_iteraciones))))
    except (TypeError, ValueError):
        raise ValueError("El máximo de iteraciones debe ser un número entero.") from None
    if criterio not in CRITERIOS:
        raise ValueError("Criterio de parada desconocido.")
    inicial = leer_inicial(x0, n)

    dominancia_original = dominancia(A)
    orden = list(range(n))
    reordenado = False
    if reordenar and not dominancia_original["estricta"]:
        nuevo, estricta = buscar_orden(A)
        if nuevo is not None and nuevo != orden:
            # Sin dominancia estricta solo se reordena si el nuevo orden converge mejor (menor ρ)
            actual = radio_espectral(A, "gauss_seidel") if np.all(np.diag(A) != 0) else None
            propuesto = radio_espectral(A[nuevo], "gauss_seidel")
            if estricta or actual is None or (propuesto is not None and propuesto < actual - 1e-12):
                orden, reordenado = nuevo, True
                A, b = A[orden], b[orden]

    try:
        exacta = np.linalg.solve(A, b) if abs(np.linalg.det(A)) > 1e-12 else None
    except np.linalg.LinAlgError:
        exacta = None

    resultados = {}
    for metodo in metodos:
        resultados[metodo] = iterar(A, b, inicial, metodo, tolerancia, max_iteraciones, criterio, exacta, decimales)
        res = resultados[metodo]
        res["radio"] = radio = radio_espectral(A, metodo) if np.all(np.diag(A) != 0) else None
        # ρ < 1 pero se acabaron las iteraciones: cuantas harian falta (el error se reduce ≈ ρ por iteracion)
        res["estimadas"] = None
        if res["estado"] == "maximo" and radio is not None and 0 < radio < 1 and res["cambio"]:
            res["estimadas"] = res["total"] + max(1, math.ceil(math.log(tolerancia / res["cambio"]) / math.log(radio)))

    return {
        "n": n, "nombres": nombres, "nombres_bonitos": [nombre_bonito(v) for v in nombres],
        "A": A.tolist(), "b": b.tolist(), "orden": orden, "reordenado": reordenado,
        "dominancia_original": dominancia_original, "dominancia": dominancia(A),
        "despejes": despejes(A, b, nombres) if np.all(np.diag(A) != 0) else [],
        "exacta": exacta.tolist() if exacta is not None else None, "inicial": inicial.tolist(),
        "tolerancia": tolerancia, "criterio": criterio, "texto_criterio": CRITERIOS[criterio],
        "max_iteraciones": max_iteraciones, "decimales": decimales, "resultados": resultados,
    }
