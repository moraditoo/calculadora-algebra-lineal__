# backend/algebra_lineal/metodo_pivote.py
from fractions import Fraction
from .gauss import format_frac, parse_frac

class MetodoPivote:
    def resolver_por_pivote(self, matriz_original, m, n):
        # Validar dimensiones minimas
        if not matriz_original or m < 1 or n < 1:
            raise ValueError("Dimensiones no validas para el metodo del pivote.")
        # Convertir a matriz racional exacta
        matriz = [[parse_frac(val) for val in fila] for fila in matriz_original]
        pasos = [("Matriz inicial para eliminacion con Pivoteo Parcial:", [[format_frac(f) for f in fila] for fila in matriz])]
        fila_piv = 0
        for col in range(n):
            if fila_piv >= m:
                break
            # Seleccion del mayor valor absoluto en la columna activa
            max_idx = fila_piv
            for i in range(fila_piv + 1, m):
                if abs(matriz[i][col]) > abs(matriz[max_idx][col]):
                    max_idx = i
            # Salto si la columna entera es nula
            if matriz[max_idx][col] == 0:
                continue
            # Intercambio de fila para garantizar maximo pivote
            if max_idx != fila_piv:
                matriz[fila_piv], matriz[max_idx] = matriz[max_idx], matriz[fila_piv]
                pasos.append((
                    f"Pivoteo Parcial: Fila {fila_piv + 1} ↔ Fila {max_idx + 1} (Pivote maximo: {format_frac(matriz[fila_piv][col])})",
                    [[format_frac(f) for f in fila] for fila in matriz]
                ))
            # Eliminacion hacia abajo
            for i in range(fila_piv + 1, m):
                if matriz[i][col] != 0:
                    factor = matriz[i][col] / matriz[fila_piv][col]
                    for j in range(col, n + 1):
                        matriz[i][j] -= factor * matriz[fila_piv][j]
                    pasos.append((
                        f"Anulacion Fila {i + 1}: Fila {i + 1} - ({format_frac(factor)}) × Fila {fila_piv + 1}",
                        [[format_frac(f) for f in fila] for fila in matriz]
                    ))
            fila_piv += 1
        return pasos, matriz

    def clasificar_sistema(self, matriz, m, n):
        inconsistente = False
        pivotes = []
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
            if not todos_cero and piv_col not in pivotes:
                pivotes.append(piv_col)
        if inconsistente:
            return "Sistema Inconsistente (Sin Solucion)."
        rango = len(pivotes)
        if rango < n:
            return f"Sistema Consistente Indeterminado ({n - rango} variable(s) libre(s))."
        return "Sistema Consistente Determinado (Solucion Unica)."

    def resolver_sustitucion_atras(self, matriz, m, n):
        solucion = [Fraction(0)] * n
        filas_pivote = []
        pasos_detalle = []
        # Encontrar posiciones de pivotes
        for i in range(m):
            for j in range(n):
                if matriz[i][j] != 0:
                    filas_pivote.append((i, j))
                    break
        # Sustitucion regresiva
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
            resultados.append(f"Ecuacion {i + 1}: {format_frac(suma)} = {format_frac(esperado)} [{estado}]")
        return resultados