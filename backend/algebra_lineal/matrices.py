# backend/algebra_lineal/matrices.py
from fractions import Fraction
from .gauss import format_frac, parse_frac

class OperacionesMatrices:
    @staticmethod
    def validar_matriz(mat, nombre="Matriz"):
        if not mat or not isinstance(mat, list):
            raise ValueError(f"{nombre} no tiene un formato valido.")
        filas = len(mat)
        if filas == 0:
            raise ValueError(f"{nombre} no puede estar vacia.")
        cols = len(mat[0])
        for i, f in enumerate(mat):
            if len(f) != cols:
                raise ValueError(f"{nombre} tiene dimensiones irregulares en la fila {i + 1}.")
        return filas, cols

    @classmethod
    def sumar(cls, A, B):
        fa, ca = cls.validar_matriz(A, "Matriz A")
        fb, cb = cls.validar_matriz(B, "Matriz B")
        if fa != fb or ca != cb:
            raise ValueError(f"Dimensiones incompatibles para suma: {fa}x{ca} vs {fb}x{cb}.")

        pasos = [
            f"Operacion: Suma de matrices de orden {fa}x{ca}.",
            "Regla: C[i, j] = A[i, j] + B[i, j] celda a celda."
        ]
        res = []
        for i in range(fa):
            fila = []
            for j in range(ca):
                va = parse_frac(A[i][j])
                vb = parse_frac(B[i][j])
                s = va + vb
                fila.append(format_frac(s))
                pasos.append(f"• C[{i+1},{j+1}] = ({format_frac(va)}) + ({format_frac(vb)}) = {format_frac(s)}")
            res.append(fila)
        return {"resultado": res, "pasos": pasos, "filas": fa, "cols": ca}

    @classmethod
    def restar(cls, A, B):
        fa, ca = cls.validar_matriz(A, "Matriz A")
        fb, cb = cls.validar_matriz(B, "Matriz B")
        if fa != fb or ca != cb:
            raise ValueError(f"Dimensiones incompatibles para resta: {fa}x{ca} vs {fb}x{cb}.")

        pasos = [
            f"Operacion: Resta de matrices de orden {fa}x{ca}.",
            "Regla: C[i, j] = A[i, j] - B[i, j] celda a celda."
        ]
        res = []
        for i in range(fa):
            fila = []
            for j in range(ca):
                va = parse_frac(A[i][j])
                vb = parse_frac(B[i][j])
                r = va - vb
                fila.append(format_frac(r))
                pasos.append(f"• C[{i+1},{j+1}] = ({format_frac(va)}) - ({format_frac(vb)}) = {format_frac(r)}")
            res.append(fila)
        return {"resultado": res, "pasos": pasos, "filas": fa, "cols": ca}

    @classmethod
    def escalar(cls, c, A):
        fa, ca = cls.validar_matriz(A, "Matriz A")
        c_frac = parse_frac(c)
        pasos = [
            f"Operacion: Multiplicacion por escalar c = {format_frac(c_frac)} en orden {fa}x{ca}.",
            "Regla: C[i, j] = c * A[i, j]."
        ]
        res = []
        for i in range(fa):
            fila = []
            for j in range(ca):
                va = parse_frac(A[i][j])
                prod = c_frac * va
                fila.append(format_frac(prod))
                pasos.append(f"• C[{i+1},{j+1}] = ({format_frac(c_frac)}) * ({format_frac(va)}) = {format_frac(prod)}")
            res.append(fila)
        return {"resultado": res, "pasos": pasos, "filas": fa, "cols": ca}

    @classmethod
    def multiplicar(cls, A, B):
        fa, ca = cls.validar_matriz(A, "Matriz A")
        fb, cb = cls.validar_matriz(B, "Matriz B")
        if ca != fb:
            raise ValueError(f"Incompatibilidad de dimensiones: Columnas de A ({ca}) deben coincidir con Filas de B ({fb}).")

        pasos = [
            f"Multiplicacion de matrices ({fa}x{ca}) * ({fb}x{cb}) -> ({fa}x{cb}):",
            "Regla fila por columna: C[i, j] = Suma(A[i, k] * B[k, j])"
        ]
        res = []
        for i in range(fa):
            fila = []
            for j in range(cb):
                detalles_k = []
                suma = Fraction(0)
                for k in range(ca):
                    va = parse_frac(A[i][k])
                    vb = parse_frac(B[k][j])
                    prod = va * vb
                    suma += prod
                    detalles_k.append(f"({format_frac(va)}*{format_frac(vb)})")
                fila.append(format_frac(suma))
                pasos.append(f"• C[{i+1},{j+1}] = {' + '.join(detalles_k)} = {format_frac(suma)}")
            res.append(fila)
        return {"resultado": res, "pasos": pasos, "filas": fa, "cols": cb}

    @classmethod
    def transponer(cls, A):
        fa, ca = cls.validar_matriz(A, "Matriz A")
        pasos = [
            f"Transposicion de orden ({fa}x{ca}) -> ({ca}x{fa}):",
            "Regla: A^T[j, i] = A[i, j]"
        ]
        res = []
        for j in range(ca):
            fila = []
            for i in range(fa):
                v = parse_frac(A[i][j])
                fila.append(format_frac(v))
                pasos.append(f"• A^T[{j+1},{i+1}] = A[{i+1},{j+1}] = {format_frac(v)}")
            res.append(fila)
        return {"resultado": res, "pasos": pasos, "filas": ca, "cols": fa}

    @classmethod
    def calcular_inversa_gauss_jordan(cls, A_raw):
        fa, ca = cls.validar_matriz(A_raw, "Matriz A")
        
        # Salida anticipada 1: Matriz estrictamente cuadrada
        if fa != ca:
            return {
                "invertible": False,
                "n": fa,
                "motivo": "TEOREMA: La matriz debe ser estrictamente cuadrada (n x n) para tener inversa.",
                "detalle": f"La matriz ingresada tiene orden {fa}x{ca}.",
                "pasos": [f"Salida anticipada: Matriz no cuadrada ({fa}x{ca})."]
            }

        n = fa
        A = [[parse_frac(val) for val in fila] for fila in A_raw]

        # Salida anticipada 2: Filas o Columnas de ceros
        for i in range(n):
            if all(A[i][j] == 0 for j in range(n)):
                return {
                    "invertible": False,
                    "n": n,
                    "motivo": "TEOREMA DE LA MATRIZ INVERTIBLE: Fila nula detectada.",
                    "detalle": f"La fila {i+1} contiene solo ceros. det(A) = 0.",
                    "pasos": [f"Salida anticipada: Fila {i+1} nula. Matriz singular."]
                }
        for j in range(n):
            if all(A[i][j] == 0 for i in range(n)):
                return {
                    "invertible": False,
                    "n": n,
                    "motivo": "TEOREMA DE LA MATRIZ INVERTIBLE: Columna nula detectada.",
                    "detalle": f"La columna {j+1} contiene solo ceros.",
                    "pasos": [f"Salida anticipada: Columna {j+1} nula. Matriz singular."]
                }

        # Salida anticipada 3: Dependencia lineal entre filas
        for i in range(n):
            for k in range(i + 1, n):
                ratio = None
                proporcional = True
                for j in range(n):
                    if A[i][j] == 0 and A[k][j] == 0:
                        continue
                    if A[i][j] == 0 or A[k][j] == 0:
                        proporcional = False
                        break
                    r_act = A[k][j] / A[i][j]
                    if ratio is None:
                        ratio = r_act
                    elif ratio != r_act:
                        proporcional = False
                        break
                if proporcional and ratio is not None:
                    return {
                        "invertible": False,
                        "n": n,
                        "motivo": "TEOREMA: Dependencia lineal (Filas proporcionales).",
                        "detalle": f"La Fila {k+1} es multiplo de la Fila {i+1} (factor {format_frac(ratio)}).",
                        "pasos": [f"Salida anticipada: Filas dependientes {i+1} y {k+1}. det(A) = 0."]
                    }

        # Salida anticipada 4: Determinante en matrices 2x2
        if n == 2:
            a, b = A[0][0], A[0][1]
            c, d = A[1][0], A[1][1]
            det = a * d - b * c
            if det == 0:
                return {
                    "invertible": False,
                    "n": 2,
                    "motivo": "TEOREMA 2x2: det(A) = ad - bc = 0.",
                    "detalle": f"({format_frac(a)})({format_frac(d)}) - ({format_frac(b)})({format_frac(c)}) = 0.",
                    "pasos": ["Salida anticipada: Determinante nulo."]
                }

        # Construccion de [A | I_n]
        aumentada = []
        for i in range(n):
            identidad = [Fraction(1) if i == j else Fraction(0) for j in range(n)]
            aumentada.append([parse_frac(A_raw[i][j]) for j in range(n)] + identidad)

        pasos_matrices = [("Paso 1: Construccion de la Matriz Aumentada inicial [A | I]:", 
                           [[format_frac(c) for c in fila] for fila in aumentada])]
        detalles_explicativos = [
            f"Se construye la matriz aumentada [A | I_{n}] de orden {n}x{2*n}.",
            "Se aplican operaciones elementales por fila para transformar [A | I] en [I | A^-1]."
        ]

        # Eliminacion Gauss-Jordan
        for col in range(n):
            max_fila = col
            for i in range(col + 1, n):
                if abs(aumentada[i][col]) > abs(aumentada[max_fila][col]):
                    max_fila = i

            if aumentada[max_fila][col] == 0:
                return {
                    "invertible": False,
                    "n": n,
                    "motivo": "TEOREMA DE LA MATRIZ INVERTIBLE: Columna sin pivote no nulo.",
                    "detalle": f"En la columna {col+1} todos los pivotes son cero. Rango menor a {n}.",
                    "pasos": [f"Salida anticipada: Ausencia de pivote en columna {col+1}."]
                }

            if max_fila != col:
                aumentada[col], aumentada[max_fila] = aumentada[max_fila], aumentada[col]
                desc = f"Intercambio: Fila {col+1} <-> Fila {max_fila+1} (Pivoteo Parcial)"
                pasos_matrices.append((desc, [[format_frac(c) for c in fila] for fila in aumentada]))
                detalles_explicativos.append(f"• Intercambio Fila {col+1} con Fila {max_fila+1} por maximo pivote.")

            pivote = aumentada[col][col]
            if pivote != 1:
                for j in range(2 * n):
                    aumentada[col][j] /= pivote
                desc = f"Normalizacion: Fila {col+1} / ({format_frac(pivote)}) para hacer pivote = 1"
                pasos_matrices.append((desc, [[format_frac(c) for c in fila] for fila in aumentada]))
                detalles_explicativos.append(f"• Fila {col+1} normalizada dividiendo entre {format_frac(pivote)}.")

            for i in range(n):
                if i != col and aumentada[i][col] != 0:
                    factor = aumentada[i][col]
                    for j in range(2 * n):
                        aumentada[i][j] -= factor * aumentada[col][j]
                    desc = f"Eliminacion: Fila {i+1} - ({format_frac(factor)}) * Fila {col+1}"
                    pasos_matrices.append((desc, [[format_frac(c) for c in fila] for fila in aumentada]))
                    detalles_explicativos.append(f"• Anulando posicion ({i+1},{col+1}) mediante Fila {i+1} - ({format_frac(factor)})*Fila {col+1}.")

        # Extraer A^-1 de la mitad derecha
        A_inv = [[aumentada[i][n + j] for j in range(n)] for i in range(n)]
        A_inv_str = [[format_frac(c) for c in fila] for fila in A_inv]

        # Verificacion formal termino a termino A * A^-1 = I_n
        verif_I = []
        detalles_verificacion = []
        for i in range(n):
            fila_v = []
            for j in range(n):
                sumandos = []
                suma = Fraction(0)
                for k in range(n):
                    va = A[i][k]
                    vb = A_inv[k][j]
                    prod = va * vb
                    suma += prod
                    sumandos.append(f"({format_frac(va)})*({format_frac(vb)})")
                fila_v.append(format_frac(suma))
                esperado = "1 [Diagonal]" if i == j else "0 [Fuera de diagonal]"
                detalles_verificacion.append(
                    f"Posicion ({i+1},{j+1}) [Fila {i+1} de A . Col {j+1} de A^-1]: "
                    f"{' + '.join(sumandos)} = {format_frac(suma)} [{esperado}]"
                )
            verif_I.append(fila_v)

        return {
            "invertible": True,
            "n": n,
            "motivo": f"Matriz equivalente por filas a I_{n}. Se obtuvo la inversa por Gauss-Jordan.",
            "inversa": A_inv_str,
            "verificacion_identidad": verif_I,
            "detalles_explicativos": detalles_explicativos,
            "detalles_verificacion": detalles_verificacion,
            "pasos_matrices": pasos_matrices
        }

    @classmethod
    def inversa_de_inversa(cls, A_raw):
        paso1 = cls.calcular_inversa_gauss_jordan(A_raw)
        if not paso1["invertible"]:
            return paso1

        A_inv = paso1["inversa"]
        paso2 = cls.calcular_inversa_gauss_jordan(A_inv)

        A_orig_eval = [[format_frac(parse_frac(c)) for c in fila] for fila in A_raw]
        A_inv_inv = paso2["inversa"]

        return {
            "invertible": True,
            "n": paso1["n"],
            "teorema": "Teorema: Si A es invertible, entonces (A^-1)^-1 = A.",
            "A_original": A_orig_eval,
            "A_inversa": A_inv,
            "A_inversa_de_inversa": A_inv_inv,
            "coincide": A_orig_eval == A_inv_inv,
            "pasos": [
                "1. Se aplico Gauss-Jordan sobre A obteniendo A^-1.",
                "2. Se aplico Gauss-Jordan sobre A^-1 obteniendo (A^-1)^-1.",
                "3. Se comprobo que (A^-1)^-1 coincide elemento por elemento con la matriz original A."
            ]
        }

    @classmethod
    def resolver_por_inversa(cls, A_raw, b_col):
        fa, ca = cls.validar_matriz(A_raw, "Matriz A")
        fb, cb = cls.validar_matriz(b_col, "Vector b")

        if cb != 1:
            raise ValueError("El termino b debe ser un vector columna de 1 columna.")
        if fb != fa:
            raise ValueError(f"Incompatibilidad: b tiene {fb} filas y A tiene {fa} filas.")

        inv_res = cls.calcular_inversa_gauss_jordan(A_raw)
        if not inv_res["invertible"]:
            return {
                "resuelto": False,
                "n": fa,
                "motivo": "No se puede resolver x = A^-1 * b porque A es singular.",
                "detalle": inv_res["detalle"]
            }

        A_inv = inv_res["inversa"]
        mult_res = cls.multiplicar(A_inv, b_col)
        x_sol = [fila[0] for fila in mult_res["resultado"]]

        return {
            "resuelto": True,
            "n": fa,
            "teorema": "Teorema: Si A es invertible, Ax = b tiene la solucion unica x = A^-1 * b.",
            "A_inversa": A_inv,
            "x_solucion": x_sol,
            "pasos_multiplicacion": mult_res["pasos"]
        }

    # ------------------------------------------------------------------
    # DETERMINANTE: Cofactores (Laplace) y Descomposicion LU (PA = LU)
    # ------------------------------------------------------------------
    # Las submatrices no se copian: se representan con tuplas de indices
    # (filas, cols) sobre la matriz original M. Esto permite usarlas como
    # clave del diccionario 'memo'.
    #
    # --- Utilidades para la expansion por cofactores ---
    @staticmethod
    def _elegir_linea(M, filas, cols):
        """Elige la fila o columna con mas ceros (minimiza los terminos a expandir)."""
        # mejor = (tipo, posicion relativa, cantidad de ceros); ante empate gana la primera
        mejor = ("fila", 0, -1)
        for pi, i in enumerate(filas):
            ceros = sum(1 for j in cols if M[i][j] == 0)
            if ceros > mejor[2]:
                mejor = ("fila", pi, ceros)
        for pj, j in enumerate(cols):
            ceros = sum(1 for i in filas if M[i][j] == 0)
            if ceros > mejor[2]:
                mejor = ("columna", pj, ceros)
        return mejor[0], mejor[1]

    @staticmethod
    def _entradas_linea(filas, cols, tipo, idx):
        """Posiciones (pos_fila, pos_col), relativas a la submatriz, de la linea elegida."""
        if tipo == "fila":
            return [(idx, pj) for pj in range(len(cols))]
        return [(pi, idx) for pi in range(len(filas))]

    @staticmethod
    def _menor(filas, cols, pi, pj):
        """Indices del menor M[pi,pj]: quita la fila pi y la columna pj."""
        return filas[:pi] + filas[pi + 1:], cols[:pj] + cols[pj + 1:]

    @classmethod
    def _det_cofactor(cls, M, filas, cols, memo):
        """
        Retorna (det, ops) de la submatriz M[filas][cols] por expansion de cofactores.
        'ops' cuenta las operaciones aritmeticas (multiplicaciones + sumas/restas) que
        realiza la expansion recursiva tal como se hace a mano; la memoizacion solo
        evita recalcular menores repetidos, no altera el conteo.
        """
        # Si este menor ya se calculo, se reutiliza
        clave = (filas, cols)
        if clave in memo:
            return memo[clave]

        k = len(filas)
        # Casos base: 1x1 (el propio valor) y 2x2 (ad - bc = 2 mult + 1 resta = 3 ops)
        if k == 1:
            res = (M[filas[0]][cols[0]], 0)
        elif k == 2:
            a, b = M[filas[0]][cols[0]], M[filas[0]][cols[1]]
            c, d = M[filas[1]][cols[0]], M[filas[1]][cols[1]]
            res = (a * d - b * c, 3)
        else:
            # Caso recursivo: se expande por la linea con mas ceros
            tipo, idx = cls._elegir_linea(M, filas, cols)
            det = Fraction(0)
            ops = 0
            terminos = 0
            for pi, pj in cls._entradas_linea(filas, cols, tipo, idx):
                a = M[filas[pi]][cols[pj]]
                if a == 0:
                    continue  # termino nulo: no se calcula su menor
                sub_f, sub_c = cls._menor(filas, cols, pi, pj)
                sub_det, sub_ops = cls._det_cofactor(M, sub_f, sub_c, memo)
                # Signo del cofactor (-1)^(i+j); ops: menor + 1 multiplicacion
                signo = 1 if (pi + pj) % 2 == 0 else -1
                det += signo * a * sub_det
                ops += sub_ops + 1
                terminos += 1
            ops += max(terminos - 1, 0)  # sumas entre los terminos
            res = (det, ops)

        memo[clave] = res
        return res

    @classmethod
    def _pasos_cofactor(cls, M, filas, cols, memo, nivel, max_nivel, pasos):
        """
        Genera el texto paso a paso de la expansion (lo agrega a 'pasos').
        No recalcula nada: lee los determinantes ya guardados en 'memo'.
        'nivel' define la sangria; solo se baja de nivel mientras nivel < max_nivel.
        """
        k = len(filas)
        sangria = "    " * nivel
        if k == 1:
            pasos.append(f"{sangria}det = {format_frac(M[filas[0]][cols[0]])}")
            return
        if k == 2:
            a, b = M[filas[0]][cols[0]], M[filas[0]][cols[1]]
            c, d = M[filas[1]][cols[0]], M[filas[1]][cols[1]]
            pasos.append(
                f"{sangria}det = ({format_frac(a)})({format_frac(d)}) - ({format_frac(b)})({format_frac(c)}) "
                f"= {format_frac(a * d - b * c)}"
            )
            return

        # Se indica la linea elegida con su numero en la matriz original
        tipo, idx = cls._elegir_linea(M, filas, cols)
        num_original = (filas if tipo == "fila" else cols)[idx] + 1
        pasos.append(f"{sangria}Submatriz {k}x{k}: se expande por la {tipo} {num_original} (la de mas ceros).")
        for pi, pj in cls._entradas_linea(filas, cols, tipo, idx):
            i, j = filas[pi], cols[pj]
            a = M[i][j]
            if a == 0:
                pasos.append(f"{sangria}• a[{i+1},{j+1}] = 0 -> termino nulo, se omite.")
                continue
            sub_f, sub_c = cls._menor(filas, cols, pi, pj)
            sub_det = memo[(sub_f, sub_c)][0]
            s = "+" if (pi + pj) % 2 == 0 else "-"
            termino = sub_det * a * (1 if s == "+" else -1)
            pasos.append(
                f"{sangria}• C[{i+1},{j+1}]: ({s}1)·({format_frac(a)})·det(M[{i+1},{j+1}]) "
                f"= ({s}1)·({format_frac(a)})·({format_frac(sub_det)}) = {format_frac(termino)}"
            )
            if nivel < max_nivel:  # desglose del menor, un nivel mas adentro
                cls._pasos_cofactor(M, sub_f, sub_c, memo, nivel + 1, max_nivel, pasos)
        det = memo[(filas, cols)][0]
        pasos.append(f"{sangria}=> Suma de terminos: det = {format_frac(det)}")

    @classmethod
    def _arbol_cofactor(cls, M, filas, cols, memo, nivel, max_nivel):
        """
        Estructura recursiva para dibujar la expansion como matrices:
        cada nodo trae su submatriz, la linea de expansion y, por termino, el menor
        (expandido a su vez mientras nivel < max_nivel).
        """
        k = len(filas)
        # Datos comunes a todo nodo (indices en base 1 para mostrarlos)
        nodo = {
            "orden": k,
            "matriz": [[format_frac(M[i][j]) for j in cols] for i in filas],
            "filas": [i + 1 for i in filas],
            "cols": [j + 1 for j in cols],
            "det": format_frac(memo[(filas, cols)][0]),
        }
        if k == 1:
            nodo["tipo"] = "1x1"
            return nodo
        if k == 2:
            a, b = M[filas[0]][cols[0]], M[filas[0]][cols[1]]
            c, d = M[filas[1]][cols[0]], M[filas[1]][cols[1]]
            nodo.update({
                "tipo": "2x2",
                "ad": format_frac(a * d), "bc": format_frac(b * c),
                "a": format_frac(a), "b": format_frac(b), "c": format_frac(c), "d": format_frac(d),
            })
            return nodo

        # Nodo de expansion: un termino por cada elemento de la linea elegida
        tipo, idx = cls._elegir_linea(M, filas, cols)
        nodo["tipo"] = "expansion"
        nodo["linea"] = {
            "tipo": tipo,
            "indice": idx,  # relativo a la submatriz (indices desde 0)
            "original": (filas if tipo == "fila" else cols)[idx] + 1,
        }
        terminos = []
        for pi, pj in cls._entradas_linea(filas, cols, tipo, idx):
            a = M[filas[pi]][cols[pj]]
            signo = 1 if (pi + pj) % 2 == 0 else -1
            t = {
                "pi": pi, "pj": pj,
                "fila": filas[pi] + 1, "col": cols[pj] + 1,
                "elemento": format_frac(a),
                "signo": "+" if signo > 0 else "-",
            }
            if a == 0:  # sin menor: el termino vale 0
                t.update({"nulo": True, "termino": "0", "det_menor": None, "menor": None})
            else:
                sub_f, sub_c = cls._menor(filas, cols, pi, pj)
                sub_det = memo[(sub_f, sub_c)][0]
                t.update({
                    "nulo": False,
                    "det_menor": format_frac(sub_det),
                    "termino": format_frac(signo * a * sub_det),
                    "menor_matriz": [[format_frac(M[i][j]) for j in sub_c] for i in sub_f],
                    # Hijo recursivo solo mientras no se pase de max_nivel
                    "menor": (cls._arbol_cofactor(M, sub_f, sub_c, memo, nivel + 1, max_nivel)
                              if nivel < max_nivel else None),
                })
            terminos.append(t)
        nodo["terminos"] = terminos
        return nodo

    @staticmethod
    def _descomposicion_lu(M):
        """
        Factorizacion PA = LU (Doolittle, con intercambio de filas cuando el pivote es 0).
        det(A) = (-1)^intercambios * Producto(U[i,i]).
        """
        # U empieza como copia de A; L como identidad; perm registra la permutacion P
        n = len(M)
        U = [fila[:] for fila in M]
        L = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        perm = list(range(n))
        intercambios = 0
        ops = 0
        pasos = []
        pasos_matrices = [("Matriz inicial U = A:", [[format_frac(c) for c in f] for f in U])]

        for k in range(n):
            # Busca el primer pivote no nulo desde la fila k hacia abajo
            p = next((i for i in range(k, n) if U[i][k] != 0), None)
            if p is None:
                # Columna sin pivote -> U tendra un 0 en la diagonal -> det = 0
                pasos.append(f"• Columna {k+1}: no existe pivote no nulo en o debajo de la diagonal -> U[{k+1},{k+1}] = 0.")
                pasos.append("• Con un cero en la diagonal de U, det(A) = 0 (matriz singular).")
                return {
                    "singular": True, "det": Fraction(0), "ops": ops, "intercambios": intercambios,
                    "L": L, "U": U, "perm": perm, "pasos": pasos, "pasos_matrices": pasos_matrices,
                }
            if p != k:
                # Intercambio de filas en U, en la parte ya calculada de L y en perm
                U[k], U[p] = U[p], U[k]
                for j in range(k):
                    L[k][j], L[p][j] = L[p][j], L[k][j]
                perm[k], perm[p] = perm[p], perm[k]
                intercambios += 1
                pasos.append(f"• Pivote U[{k+1},{k+1}] = 0: intercambio Fila {k+1} <-> Fila {p+1} (cambia el signo del det).")
                pasos_matrices.append((f"Intercambio F{k+1} <-> F{p+1}", [[format_frac(c) for c in f] for f in U]))

            # Eliminacion debajo del pivote: el multiplicador m se guarda en L
            pivote = U[k][k]
            for i in range(k + 1, n):
                if U[i][k] == 0:
                    continue  # ya es cero, no hace falta operar
                m = U[i][k] / pivote  # 1 division
                ops += 1
                L[i][k] = m
                U[i][k] = Fraction(0)
                for j in range(k + 1, n):
                    U[i][j] -= m * U[k][j]
                    ops += 2  # 1 multiplicacion + 1 resta
                pasos.append(
                    f"• l[{i+1},{k+1}] = {format_frac(m * pivote)} / {format_frac(pivote)} = {format_frac(m)}  ->  "
                    f"F{i+1} = F{i+1} - ({format_frac(m)})·F{k+1}"
                )
                pasos_matrices.append(
                    (f"F{i+1} - ({format_frac(m)})·F{k+1}", [[format_frac(c) for c in f] for f in U])
                )

        # det = producto de la diagonal de U (n-1 multiplicaciones), con signo
        # cambiado si hubo un numero impar de intercambios
        det = Fraction(1)
        for i in range(n):
            det *= U[i][i]
        ops += n - 1
        if intercambios % 2 == 1:
            det = -det
        return {
            "singular": False, "det": det, "ops": ops, "intercambios": intercambios,
            "L": L, "U": U, "perm": perm, "pasos": pasos, "pasos_matrices": pasos_matrices,
        }

    @staticmethod
    def _comprobar_lu(M, L, U, perm):
        """
        Comprobacion principal: L x U = P x A.
        (P x A)[i] es la fila perm[i] de A, asi que no hace falta multiplicar por P.
        Devuelve ambos productos, si coinciden y el detalle entrada por entrada.
        """
        n = len(M)
        LU = [[sum((L[i][k] * U[k][j] for k in range(n)), Fraction(0)) for j in range(n)] for i in range(n)]
        PA = [M[perm[i]][:] for i in range(n)]

        detalles = []
        for i in range(n):
            for j in range(n):
                # Solo intervienen k <= min(i, j): L es triangular inferior y U superior
                sumandos = [f"({format_frac(L[i][k])})({format_frac(U[k][j])})" for k in range(min(i, j) + 1)]
                marca = "✓" if LU[i][j] == PA[i][j] else "✗"
                detalles.append(
                    f"(LU)[{i+1},{j+1}] = {' + '.join(sumandos)} = {format_frac(LU[i][j])}   "
                    f"(PA)[{i+1},{j+1}] = A[{perm[i]+1},{j+1}] = {format_frac(PA[i][j])}  {marca}"
                )

        return {
            "LU": [[format_frac(c) for c in f] for f in LU],
            "PA": [[format_frac(c) for c in f] for f in PA],
            "coincide": LU == PA,
            "detalles": detalles,
        }

    # --- Conteo teorico de operaciones (peor caso: matriz sin ceros) ---
    @staticmethod
    def _ops_cofactor_densa(n):
        """Operaciones de la expansion por cofactores en una matriz sin ceros."""
        if n <= 1:
            return 0
        if n == 2:
            return 3
        # n terminos x (menor + 1 mult) + (n-1) sumas -> crece como n!
        return n * (OperacionesMatrices._ops_cofactor_densa(n - 1) + 1) + (n - 1)

    @staticmethod
    def _ops_lu_densa(n):
        """Operaciones de LU en una matriz sin ceros: ~ (2/3)n^3."""
        # Por columna k: (n-k-1) filas, cada una 1 division + 2 ops por elemento;
        # mas las n-1 multiplicaciones de la diagonal
        return sum((n - k - 1) * (1 + 2 * (n - k - 1)) for k in range(n)) + max(n - 1, 0)

    # --- Validacion y metodos publicos ---
    @classmethod
    def _matriz_cuadrada(cls, A_raw):
        """Valida que A sea n x n y la devuelve convertida a Fraction."""
        fa, ca = cls.validar_matriz(A_raw, "Matriz A")
        if fa != ca:
            raise ValueError(f"El determinante solo esta definido para matrices cuadradas. Dimension actual: {fa}x{ca}.")
        return fa, [[parse_frac(v) for v in fila] for fila in A_raw]

    @classmethod
    def comparar_metodos_determinante(cls, A_raw):
        """
        Cuenta las operaciones reales de cada metodo sobre ESTA matriz
        (los ceros abaratan ambos) y recomienda el mas barato.
        Tambien devuelve el costo teorico para una matriz densa del mismo orden.
        """
        n, M = cls._matriz_cuadrada(A_raw)
        indices = tuple(range(n))
        _, ops_cof = cls._det_cofactor(M, indices, indices, {})
        ops_lu = cls._descomposicion_lu(M)["ops"]

        if ops_cof < ops_lu:
            recomendado = "cofactor"
            mensaje = (f"Para esta matriz, Cofactores requiere {ops_cof} operaciones frente a {ops_lu} de LU: "
                       f"es la opcion mas rapida.")
        elif ops_lu < ops_cof:
            recomendado = "lu"
            mensaje = f"Para esta matriz, LU requiere {ops_lu} operaciones frente a {ops_cof} de Cofactores"
            mensaje += f" (~{ops_cof / ops_lu:.1f} veces menos trabajo)." if ops_lu else " (detecta la singularidad sin calcular)."
        else:
            recomendado = "empate"
            mensaje = f"Ambos metodos requieren {ops_lu} operaciones para esta matriz: costo equivalente."

        return {
            "n": n,
            "recomendado": recomendado,
            "mensaje": mensaje,
            "cofactor": {"ops": ops_cof, "ops_densa": cls._ops_cofactor_densa(n), "complejidad": "O(n!)"},
            "lu": {"ops": ops_lu, "ops_densa": cls._ops_lu_densa(n), "complejidad": "O(n³)"},
        }

    @classmethod
    def determinante(cls, A_raw, metodo="lu"):
        """
        Punto de entrada. metodo = "cofactor" o "lu".
        Devuelve el determinante, el conteo de operaciones, los pasos en texto,
        datos para dibujar (arbol / matrices L, U, P) y la comparacion de metodos.
        """
        n, M = cls._matriz_cuadrada(A_raw)
        comparacion = cls.comparar_metodos_determinante(A_raw)
        indices = tuple(range(n))

        # ---------------- Metodo de cofactores ----------------
        if metodo == "cofactor":
            # 1) Calculo completo; 'memo' queda lleno con todos los menores
            memo = {}
            det, ops = cls._det_cofactor(M, indices, indices, memo)
            pasos = [
                f"Metodo: Expansion por cofactores (Laplace) sobre una matriz {n}x{n}.",
                "Regla: det(A) = Suma a[i,j]·C[i,j], con C[i,j] = (-1)^(i+j)·det(M[i,j]).",
                "En cada nivel se expande por la fila o columna con mas ceros.",
            ]
            # 2) Resumen del primer nivel (linea elegida y sus terminos), solo si n >= 3
            terminos = []
            linea = None
            if n >= 3:
                tipo, idx = cls._elegir_linea(M, indices, indices)
                linea = {"tipo": tipo, "indice": idx + 1}
                for pi, pj in cls._entradas_linea(indices, indices, tipo, idx):
                    a = M[pi][pj]
                    sub_f, sub_c = cls._menor(indices, indices, pi, pj)
                    signo = 1 if (pi + pj) % 2 == 0 else -1
                    sub_det = memo[(sub_f, sub_c)][0] if a != 0 else None
                    terminos.append({
                        "fila": pi + 1,
                        "col": pj + 1,
                        "elemento": format_frac(a),
                        "signo": "+" if signo > 0 else "-",
                        "menor": [[format_frac(M[i][j]) for j in sub_c] for i in sub_f],
                        "det_menor": format_frac(sub_det) if sub_det is not None else None,
                        "termino": format_frac(signo * a * sub_det) if sub_det is not None else "0",
                    })
            # El desglose anidado completo solo se muestra mientras sea legible
            max_nivel = n if n <= 4 else (1 if n == 5 else 0)
            # 3) Texto y arbol visual, limitados por max_nivel
            #    (n<=4: completo, n=5: un nivel, n>=6: solo el primero)
            cls._pasos_cofactor(M, indices, indices, memo, 0, max_nivel, pasos)
            arbol = cls._arbol_cofactor(M, indices, indices, memo, 0, max_nivel)
            if n > 4:
                pasos.append(f"(Desglose de menores de orden inferior omitido por longitud: {ops} operaciones en total.)")

            return {
                "metodo": "cofactor",
                "n": n,
                "determinante": format_frac(det),
                "operaciones": ops,
                "linea_expansion": linea,
                "terminos": terminos,
                "arbol": arbol,
                "pasos": pasos,
                "comparacion": comparacion,
            }

        # ---------------- Metodo LU ----------------
        if metodo == "lu":
            lu = cls._descomposicion_lu(M)
            pasos = [
                f"Metodo: Descomposicion PA = LU (Doolittle) sobre una matriz {n}x{n}.",
                "L es triangular inferior con 1 en la diagonal; U es triangular superior.",
                "Regla: det(A) = (-1)^s · Producto(U[i,i]), donde s = numero de intercambios de filas.",
            ] + lu["pasos"]

            # Paso final: producto de la diagonal de U con su signo
            diag = [format_frac(lu["U"][i][i]) for i in range(n)]
            if not lu["singular"]:
                signo = "-" if lu["intercambios"] % 2 else "+"
                producto = "·".join(f"({d})" for d in diag)
                pasos.append(
                    f"• det(A) = ({signo}1)·{producto} = {format_frac(lu['det'])}   [s = {lu['intercambios']}]"
                )

            # Matriz de permutacion P construida a partir de 'perm'
            P = [["1" if lu["perm"][i] == j else "0" for j in range(n)] for i in range(n)]
            comprobacion = cls._comprobar_lu(M, lu["L"], lu["U"], lu["perm"])
            return {
                "metodo": "lu",
                "n": n,
                "determinante": format_frac(lu["det"]),
                "operaciones": lu["ops"],
                "singular": lu["singular"],
                "intercambios": lu["intercambios"],
                "diagonal_U": diag,
                "L": [[format_frac(c) for c in f] for f in lu["L"]],
                "U": [[format_frac(c) for c in f] for f in lu["U"]],
                "P": P,
                "pasos": pasos,
                "pasos_matrices": lu["pasos_matrices"],
                "comprobacion": comprobacion,
                "comparacion": comparacion,
            }

        raise ValueError(f"Metodo de determinante '{metodo}' no reconocido. Use 'cofactor' o 'lu'.")