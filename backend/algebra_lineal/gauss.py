# backend/algebra_lineal/gauss.py
from fractions import Fraction

def format_frac(f):
    if not isinstance(f, Fraction):
        f = Fraction(str(f))
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

def parse_frac(val):
    if isinstance(val, Fraction):
        return val
    s = str(val).strip().replace(',', '.')
    if not s:
        raise ValueError("Se detectó una celda vacía en la matriz.")
    try:
        if '/' in s:
            partes = s.split('/')
            if len(partes) != 2:
                raise ValueError
            num = int(partes[0].strip())
            den = int(partes[1].strip())
            if den == 0:
                raise ZeroDivisionError("División por cero en fracción.")
            return Fraction(num, den)
        return Fraction(s)
    except ZeroDivisionError as zde:
        raise ValueError(str(zde))
    except Exception:
        raise ValueError(f"El valor '{val}' no es un número o fracción válida.")

class MetodoGauss:
    def eliminar(self, matriz_original, m, n):
        if not matriz_original or m < 1 or n < 1:
            raise ValueError("Dimensiones inválidas para el sistema de ecuaciones.")

        matriz = [[parse_frac(val) for val in fila] for fila in matriz_original]
        pasos = [("Matriz aumentada inicial:", [[format_frac(f) for f in fila] for fila in matriz])]

        fila_piv = 0
        for col in range(n):
            if fila_piv >= m:
                break

            max_idx = fila_piv
            for i in range(fila_piv + 1, m):
                if abs(matriz[i][col]) > abs(matriz[max_idx][col]):
                    max_idx = i

            if matriz[max_idx][col] == 0:
                continue

            if max_idx != fila_piv:
                matriz[fila_piv], matriz[max_idx] = matriz[max_idx], matriz[fila_piv]
                pasos.append((f"Intercambio: Fila {fila_piv + 1} ↔ Fila {max_idx + 1}", [[format_frac(f) for f in fila] for fila in matriz]))

            for i in range(fila_piv + 1, m):
                if matriz[i][col] != 0:
                    factor = matriz[i][col] / matriz[fila_piv][col]
                    for j in range(col, n + 1):
                        matriz[i][j] -= factor * matriz[fila_piv][j]
                    pasos.append((f"Operación: Fila {i + 1} = Fila {i + 1} - ({format_frac(factor)}) × Fila {fila_piv + 1}", [[format_frac(f) for f in fila] for fila in matriz]))

            fila_piv += 1

        return pasos, matriz

    def clasificar_sistema(self, matriz, m, n):
        inconsistente = False
        columnas_pivote = []

        for i in range(m):
            todos_cero = True
            piv_col = -1
            for j in range(n):
                if matriz[i][j] != 0:
                    todos_cero = False
                    piv_col = j
                    break

            if todos_cero and matriz[i][n] != 0:
                inconsistente = True
                break

            if not todos_cero and piv_col not in columnas_pivote:
                columnas_pivote.append(piv_col)

        if inconsistente:
            return "Sistema Inconsistente (Sin Solución). Existe una contradicción matemática (0 = b con b ≠ 0)."

        rango_a = len(columnas_pivote)
        if rango_a < n:
            libres = [f"x_{j+1}" for j in range(n) if j not in columnas_pivote]
            return f"Sistema Consistente Indeterminado (Infinitas Soluciones). Presenta {n - rango_a} variable(s) libre(s): {', '.join(libres)}."
        return "Sistema Consistente Determinado (Solución Única). No presenta variables libres."

    def resolver_sustitucion_atras(self, matriz, m, n):
        solucion = [Fraction(0)] * n
        filas_pivote = []
        pasos_detalle = []

        for i in range(m):
            for j in range(n):
                if matriz[i][j] != 0:
                    filas_pivote.append((i, j))
                    break

        for i, col in reversed(filas_pivote):
            suma = Fraction(0)
            detalles_suma = []
            for j in range(col + 1, n):
                if matriz[i][j] != 0:
                    suma += matriz[i][j] * solucion[j]
                    detalles_suma.append(f"({format_frac(matriz[i][j])})({format_frac(solucion[j])})")

            solucion[col] = (matriz[i][n] - suma) / matriz[i][col]
            resta_str = f" - [{' + '.join(detalles_suma)}]" if detalles_suma else ""
            pasos_detalle.append(f"x_{col+1} = ({format_frac(matriz[i][n])}{resta_str}) / {format_frac(matriz[i][col])} = {format_frac(solucion[col])}")

        return solucion, pasos_detalle

    def verificar_solucion(self, matriz_original, solucion, m, n):
        resultados = []
        for i in range(m):
            suma = sum(parse_frac(matriz_original[i][j]) * solucion[j] for j in range(n))
            esperado = parse_frac(matriz_original[i][n])
            estado = "✓ OK" if suma == esperado else "✗ Error"
            resultados.append(f"Ecuación {i + 1}: {format_frac(suma)} = {format_frac(esperado)}  [{estado}]")
        return resultados