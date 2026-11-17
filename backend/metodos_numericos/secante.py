# backend/metodos_numericos/secante.py
# Metodo de la secante (metodo abierto). Algoritmo de la presentacion:
#   1) Definir f(x) y elegir x0, x1
#   2) Calcular f(x0) y f(x1)
#   3) Calcular x2 con la formula de la secante:
#        x(n+1) = x(n) − f(x(n))·(x(n) − x(n−1)) / [f(x(n)) − f(x(n−1))]
#   4) Actualizar: x0 <- x1 y x1 <- x2
#   5) Repetir hasta cumplir la tolerancia o el maximo de iteraciones
#   6) Reportar aproximacion, residuo e iteraciones
# No necesita f'(x): la pendiente se aproxima con la recta que pasa por dos puntos de la curva.
# (Si se entrega la derivada, solo se usa para comparar esa pendiente con f'(xₙ).)
from .abiertos import (armar_resultado, calcular_errores, detener_si_cumple, fila, fila_exacta, fuera_de_rango,
                       leer_inicial, sub, validar_parametros)


def secante(f, x0, x1, tolerancia, criterio="absoluto", max_iteraciones=50, df=None):
    tolerancia, max_iteraciones = validar_parametros(tolerancia, criterio, max_iteraciones)
    x_anterior, f_anterior = leer_inicial(x0, "x₀", f)
    x, fx = leer_inicial(x1, "x₁", f)
    if x_anterior == x:
        raise ValueError("x₀ y x₁ deben ser distintos: la secante necesita dos puntos diferentes de la curva.")
    iniciales = {"x0": x_anterior, "x1": x, "f_x0": f_anterior, "f_x1": fx}

    iteraciones = []
    convergio, estado = False, "maximo"
    motivo = (f"Se llegó al máximo de {max_iteraciones} iteraciones sin que el error fuera menor que "
              f"E = {tolerancia:g}: el método no converge con estos valores iniciales.")

    for k in range(1, max_iteraciones + 1):
        n = k  # en la iteracion k se usan x(k−1) y x(k) para obtener x(k+1)
        if fx == 0:
            nueva = fila_exacta(k, n, x, criterio)
            nueva.update({"x_anterior": x_anterior, "f_anterior": f_anterior, "denominador": None, "pendiente": None,
                          "dfx": df.evaluar(x) if df else None})
            iteraciones.append(nueva)
            convergio, estado, motivo = True, "exacta", f"f({sub(n)}) = 0: {sub(n)} = {x:g} ya es la raíz exacta."
            break

        # Paso 3: el denominador f(xₙ) − f(xₙ₋₁) debe ser distinto de cero
        denominador = fx - f_anterior
        if denominador == 0:
            mensaje = (f"f({sub(n)}) − f({sub(n - 1)}) = 0: la recta secante es horizontal y no corta el eje x "
                       "(división entre cero).")
            if not iteraciones:
                raise ValueError(mensaje + " Elija otros x₀ y x₁.")
            motivo, estado = mensaje, "derivada_nula"
            break
        x_nuevo = x - fx * (x - x_anterior) / denominador
        if fuera_de_rango(x_nuevo):
            mensaje = (f"{sub(n + 1)} = {x_nuevo:.4g}: la aproximación se alejó demasiado; el método diverge "
                       "(denominador muy pequeño o valores iniciales inadecuados).")
            if not iteraciones:
                raise ValueError(mensaje + " Elija otros x₀ y x₁.")
            motivo, estado = mensaje, "diverge"
            break
        f_nuevo = f.evaluar(x_nuevo)
        if f_nuevo is None:
            mensaje = f"{sub(n + 1)} = {x_nuevo:.10g} queda fuera del dominio de f (f no está definida ahí)."
            if not iteraciones:
                raise ValueError(mensaje + " Elija otros x₀ y x₁.")
            motivo, estado = mensaje, "dominio"
            break

        nueva = fila(k, n, x, fx, x_nuevo, f_nuevo, criterio, calcular_errores(x_nuevo, x, f_nuevo))
        nueva.update({
            "x_anterior": x_anterior, "f_anterior": f_anterior, "denominador": denominador,
            "pendiente": denominador / (x - x_anterior),   # pendiente de la recta secante (≈ f'(xₙ))
            "dfx": df.evaluar(x) if df else None,          # solo para comparar
        })
        iteraciones.append(nueva)

        parada = detener_si_cumple(nueva, k, tolerancia)
        if parada:
            estado, motivo = parada
            convergio = True
            break
        # Paso 4: se desplazan las dos aproximaciones
        x_anterior, f_anterior, x, fx = x, fx, x_nuevo, f_nuevo

    return armar_resultado("secante", f, df, iniciales, tolerancia, criterio, max_iteraciones, iteraciones,
                           convergio, motivo, estado)
