# backend/algebra_lineal/vectores.py
from fractions import Fraction
from .gauss import format_frac, parse_frac
from .gauss_jordan import MetodoGaussJordan

class OperacionesVectores:
    @staticmethod
    def validar_vector(v, nombre="Vector"):
        if not v or not isinstance(v, list):
            raise ValueError(f"{nombre} no tiene un formato válido.")
        if len(v) == 0:
            raise ValueError(f"{nombre} no puede estar vacío.")
        return [parse_frac(x) for x in v]

    @classmethod
    def suma(cls, v1, v2):
        u1 = cls.validar_vector(v1, "Vector 1")
        u2 = cls.validar_vector(v2, "Vector 2")
        if len(u1) != len(u2):
            raise ValueError(f"Dimensión incompatible: Vector 1 tiene dimensión {len(u1)} y Vector 2 tiene dimensión {len(u2)}.")

        n = len(u1)
        pasos = [
            f"Operación: Suma componente a componente en R^{n}.",
            f"u + v = [ (u_1 + v_1), (u_2 + v_2), ..., (u_{n} + v_{n}) ]"
        ]
        
        detalles = []
        resultado = []
        for i in range(n):
            s = u1[i] + u2[i]
            detalles.append(f"Componente {i + 1}: ({format_frac(u1[i])}) + ({format_frac(u2[i])}) = {format_frac(s)}")
            resultado.append(format_frac(s))

        pasos.extend(detalles)
        return {
            "resultado": resultado,
            "pasos": pasos
        }

    @classmethod
    def resta(cls, v1, v2):
        u1 = cls.validar_vector(v1, "Vector 1")
        u2 = cls.validar_vector(v2, "Vector 2")
        if len(u1) != len(u2):
            raise ValueError(f"Dimensión incompatible: Vector 1 tiene dimensión {len(u1)} y Vector 2 tiene dimensión {len(u2)}.")

        n = len(u1)
        pasos = [
            f"Operación: Resta componente a componente en R^{n}.",
            f"u - v = [ (u_1 - v_1), (u_2 - v_2), ..., (u_{n} - v_{n}) ]"
        ]

        detalles = []
        resultado = []
        for i in range(n):
            r = u1[i] - u2[i]
            detalles.append(f"Componente {i + 1}: ({format_frac(u1[i])}) - ({format_frac(u2[i])}) = {format_frac(r)}")
            resultado.append(format_frac(r))

        pasos.extend(detalles)
        return {
            "resultado": resultado,
            "pasos": pasos
        }

    @classmethod
    def producto_escalar(cls, c, v):
        u = cls.validar_vector(v, "Vector")
        c_frac = parse_frac(c)
        n = len(u)
        
        pasos = [
            f"Operación: Múltiplo escalar c * u en R^{n} con c = {format_frac(c_frac)}.",
            f"c * u = [ c * u_1, c * u_2, ..., c * u_{n} ]"
        ]

        detalles = []
        resultado = []
        for i in range(n):
            prod = c_frac * u[i]
            detalles.append(f"Componente {i + 1}: ({format_frac(c_frac)}) * ({format_frac(u[i])}) = {format_frac(prod)}")
            resultado.append(format_frac(prod))

        pasos.extend(detalles)
        return {
            "resultado": resultado,
            "pasos": pasos
        }

    @classmethod
    def combinacion_lineal(cls, vectores_k, b):
        if not vectores_k or len(vectores_k) == 0:
            raise ValueError("Debe ingresar al menos un vector generador.")

        b_val = cls.validar_vector(b, "Vector objetivo b")
        n = len(b_val)
        k = len(vectores_k)

        for idx, v in enumerate(vectores_k):
            u = cls.validar_vector(v, f"Vector v{idx + 1}")
            if len(u) != n:
                raise ValueError(
                    f"Dimensión incompatible: El vector v{idx + 1} tiene dimensión {len(u)}, "
                    f"pero el vector b tiene dimensión {n}."
                )

        pasos_teoricos = [
            f"1. Ecuación Vectorial planteada: x_1*v_1 + x_2*v_2 + ... + x_{k}*v_{k} = b",
            f"2. Construcción de la matriz aumentada del sistema [v_1  v_2 ... v_{k} | b]:"
        ]

        matriz = []
        for i in range(n):
            fila = [vectores_k[j][i] for j in range(k)] + [b[i]]
            matriz.append(fila)

        solver = MetodoGaussJordan()
        pasos_eliminacion, matriz_final = solver.eliminar_gauss_jordan(matriz, n, k)
        clasificacion = solver.clasificar_sistema(matriz_final, n, k)

        es_cl = "Inconsistente" not in clasificacion
        solucion_pesos = None

        if es_cl and "Determinado" in clasificacion:
            sol, _ = solver.extraer_solucion(matriz_final, n, k)
            solucion_pesos = [format_frac(x) for x in sol]
            detalles = f"El vector b SÍ es combinación lineal única con pesos: " + ", ".join(f"c_{i+1} = {solucion_pesos[i]}" for i in range(k))
        elif es_cl:
            detalles = "El vector b SÍ es combinación lineal (existen infinitas combinaciones de pesos)."
        else:
            detalles = "El vector b NO es combinación lineal del conjunto de vectores (el sistema lineal no tiene solución)."

        return {
            "es_combinacion": es_cl,
            "clasificacion": clasificacion,
            "detalles": detalles,
            "solucion_pesos": solucion_pesos,
            "pasos_teoricos": pasos_teoricos,
            "pasos_matriz": pasos_eliminacion
        }