# backend/algebra_lineal/gauss_jordan.py
from fractions import Fraction
from .gauss import format_frac, parse_frac

class MetodoGaussJordan:
    def eliminar_gauss_jordan(self, matriz_original, m, n):
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

            pivote_val = matriz[fila_piv][col]
            if pivote_val != 1:
                for j in range(col, n + 1):
                    matriz[fila_piv][j] /= pivote_val
                pasos.append((f"Normalización: Fila {fila_piv + 1} = Fila {fila_piv + 1} / ({format_frac(pivote_val)})", [[format_frac(f) for f in fila] for fila in matriz]))

            for i in range(m):
                if i != fila_piv and matriz[i][col] != 0:
                    factor = matriz[i][col]
                    for j in range(col, n + 1):
                        matriz[i][j] -= factor * matriz[fila_piv][j]
                    pasos.append((f"Eliminación: Fila {i + 1} = Fila {i + 1} - ({format_frac(factor)}) × Fila {fila_piv + 1}", [[format_frac(f) for f in fila] for fila in matriz]))

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
            return "Sistema Inconsistente (Sin Solución). Contradicción encontrada (0 = constante ≠ 0)."

        rango_a = len(columnas_pivote)
        if rango_a < n:
            variables_libres = [f"x_{j+1}" for j in range(n) if j not in columnas_pivote]
            vars_str = ", ".join(variables_libres)
            return f"Sistema Consistente Indeterminado (Infinitas Soluciones). Presenta {n - rango_a} variable(s) libre(s): {vars_str}"
        else:
            return "Sistema Consistente Determinado (Solución Única). No presenta variables libres."

    def extraer_solucion(self, matriz, m, n):
        solucion = [Fraction(0)] * n
        pasos_detalle = []
        for i in range(min(m, n)):
            for j in range(n):
                if matriz[i][j] == 1:
                    solucion[j] = matriz[i][n]
                    pasos_detalle.append(f"De la fila {i+1}, la columna {j+1} es pivote unitario: x_{j+1} = {format_frac(matriz[i][n])}")
                    break
        return solucion, pasos_detalle

    def verificar_solucion(self, matriz_original, solucion, m, n):
        resultados = []
        for i in range(m):
            suma = sum(parse_frac(matriz_original[i][j]) * solucion[j] for j in range(n))
            esperado = parse_frac(matriz_original[i][n])
            estado = "✓ OK" if suma == esperado else "✗ Error"
            resultados.append(f"Ecuación {i + 1}: {format_frac(suma)} = {format_frac(esperado)}  [{estado}]")
        return resultados