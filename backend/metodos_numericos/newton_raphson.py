# backend/metodos_numericos/newton_raphson.py
# Metodo de Newton-Raphson (metodo abierto). Algoritmo de la presentacion:
#   1) Definir f(x) y f'(x)      (f'(x) se calcula sola con las reglas de derivacion, o se escribe a mano)
#   2) Elegir x0
#   3) Calcular x(n+1) = x(n) − f(x(n)) / f'(x(n))
#   4) Evaluar el residuo |f(x(n+1))| y el cambio |x(n+1) − x(n)|
#   5) Repetir hasta cumplir la tolerancia o llegar al maximo de iteraciones
#   6) Reportar raiz aproximada, residuo e iteraciones
# Idea geometrica: la tangente en (x(n), f(x(n))) corta el eje x en x(n+1).
from .abiertos import (armar_resultado, calcular_errores, detener_si_cumple, fila, fila_exacta, fuera_de_rango,
                       leer_inicial, sub, validar_parametros)


def newton_raphson(f, df, x0, tolerancia, criterio="absoluto", max_iteraciones=50):
    """f: la funcion; df: su derivada (otra Funcion). Devuelve el resultado con todas las iteraciones."""
    tolerancia, max_iteraciones = validar_parametros(tolerancia, criterio, max_iteraciones)
    x, fx = leer_inicial(x0, "x₀", f)
    iniciales = {"x0": x, "f_x0": fx, "df_x0": df.evaluar(x)}

    iteraciones = []
    convergio, estado = False, "maximo"
    motivo = (f"Se llegó al máximo de {max_iteraciones} iteraciones sin que el error fuera menor que "
              f"E = {tolerancia:g}: el método no converge desde este x₀.")

    for k in range(1, max_iteraciones + 1):
        n = k - 1
        if fx == 0:
            nueva = fila_exacta(k, n, x, criterio)
            nueva["dfx"] = df.evaluar(x)
            iteraciones.append(nueva)
            convergio, estado, motivo = True, "exacta", f"f({sub(n)}) = 0: {sub(n)} = {x:g} ya es la raíz exacta."
            break

        # Paso 3: la formula necesita f'(xₙ) distinta de cero
        dfx = df.evaluar(x)
        if dfx is None or dfx == 0:
            problema = "no está definida" if dfx is None else "= 0"
            mensaje = (f"f'({sub(n)}) {problema} en {sub(n)} = {x:.10g}: la tangente es horizontal y la fórmula "
                       "de Newton-Raphson no está definida (división entre cero).")
            if not iteraciones:
                raise ValueError(mensaje + " Elija otro x₀.")
            motivo, estado = mensaje, "derivada_nula"
            break
        x_nuevo = x - fx / dfx
        if fuera_de_rango(x_nuevo):
            mensaje = (f"{sub(k)} = {x_nuevo:.4g}: la aproximación se alejó demasiado; el método diverge "
                       "(f'(xₙ) muy pequeña o x₀ inadecuado).")
            if not iteraciones:
                raise ValueError(mensaje + " Elija otro x₀.")
            motivo, estado = mensaje, "diverge"
            break
        f_nuevo = f.evaluar(x_nuevo)
        if f_nuevo is None:
            mensaje = f"{sub(k)} = {x_nuevo:.10g} queda fuera del dominio de f (f no está definida ahí)."
            if not iteraciones:
                raise ValueError(mensaje + " Elija otro x₀.")
            motivo, estado = mensaje, "dominio"
            break

        # Paso 4: residuo y cambio entre iteraciones
        nueva = fila(k, n, x, fx, x_nuevo, f_nuevo, criterio, calcular_errores(x_nuevo, x, f_nuevo))
        nueva.update({"dfx": dfx, "cociente": fx / dfx})
        iteraciones.append(nueva)

        # Paso 5: se repite hasta cumplir la tolerancia (o el maximo de iteraciones)
        parada = detener_si_cumple(nueva, k, tolerancia)
        if parada:
            estado, motivo = parada
            convergio = True
            break
        x, fx = x_nuevo, f_nuevo

    return armar_resultado("newton", f, df, iniciales, tolerancia, criterio, max_iteraciones, iteraciones,
                           convergio, motivo, estado)
