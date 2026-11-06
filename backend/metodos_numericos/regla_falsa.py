# backend/metodos_numericos/regla_falsa.py
# Metodo de la Regla Falsa o Falsa Posicion (metodo cerrado, "regula falsi"):
#   Paso 1: se eligen a (xl) y b (xu) que encierren la raiz: f(a)·f(b) < 0 (Bolzano).
#   Paso 2: se une (a, f(a)) con (b, f(b)) con una recta; su corte con el eje x es
#           c = b − f(b)·(a − b) / (f(a) − f(b))      (xr = xu − f(xu)(xl − xu) / (f(xl) − f(xu)))
#   Paso 3: a) si f(a)·f(c) < 0 la raiz esta en [a, c]: se hace b = c
#           b) si f(a)·f(c) > 0 la raiz esta en [c, b]: se hace a = c
#           c) si f(a)·f(c) = 0 la raiz es c y termina.
#   Se repite hasta que el error sea MENOR que E.
# Variante modificada: si un extremo se "estanca" dos iteraciones seguidas, se divide
# a la mitad el valor de f en ese extremo (solo para la formula), asi la recta se
# inclina hacia el y el metodo deja de avanzar por un solo lado.
# La tabulacion, Bolzano, la revision de continuidad y las comprobaciones finales son
# las mismas del metodo de biseccion y se reutilizan desde alli.
from .biseccion import _fila, _signo, armar_resultado, derivada_numerica, validar_parametros, verificar_bolzano


def falsa_posicion(a, b, fa, fb):
    """Corte con el eje x de la recta que une (a, f(a)) y (b, f(b))."""
    return b - fb * (a - b) / (fa - fb)


def regla_falsa(f, a, b, tolerancia, criterio="relativo", max_iteraciones=100, modificada=False):
    tolerancia, max_iteraciones = validar_parametros(tolerancia, criterio, max_iteraciones)

    # Paso 1: Bolzano (f continua en [a, b] y f(a)·f(b) < 0)
    bolzano = verificar_bolzano(f, a, b)
    if not bolzano["valido"]:
        raise ValueError(bolzano["mensaje"])
    a, b, fa, fb = bolzano["a"], bolzano["b"], bolzano["fa"], bolzano["fb"]
    inicial = (a, b, fa, fb)

    iteraciones = []
    c_anterior = None
    convergio = False
    motivo = f"Se alcanzó el máximo de {max_iteraciones} iteraciones sin que el error fuera menor que E."
    margen = None
    # Variante modificada: factor que multiplica a f en cada extremo y cuantas veces seguidas no se movio
    peso_a = peso_b = 1.0
    quieto_a = quieto_b = 0

    if fa == 0 or fb == 0:
        convergio, motivo = True, "Uno de los extremos del intervalo ya es la raíz exacta (f = 0)."
        fila = _fila(1, a, b, a if fa == 0 else b, fa, fb, 0.0, None, criterio, 0.0, "exacto", None)
        fila.update({"fa_formula": fa, "fb_formula": fb, "nuevo_a": a, "nuevo_b": b})
        iteraciones.append(fila)
        margen = 0.0
    else:
        for k in range(1, max_iteraciones + 1):
            # Paso 2: punto de falsa posicion (con los valores de f que usa la formula)
            fa_formula, fb_formula = fa * peso_a, fb * peso_b
            c = falsa_posicion(a, b, fa_formula, fb_formula)
            if not a < c < b:
                # La recta corta el eje justo en un extremo: a y b ya no se distinguen en la computadora
                if not iteraciones:
                    raise ValueError("El intervalo [a, b] es demasiado pequeño para aplicar la regla falsa.")
                motivo = (f"La recta ya corta el eje en un extremo del intervalo (límite de precisión de la "
                          f"computadora) y el error no llegó a ser menor que E = {tolerancia:g}. Use una E más grande.")
                break
            fc = f.evaluar(c)
            if fc is None:
                raise ValueError(f"f(c) no está definida en c = {c}: la función no es continua en [a, b].")

            # Paso 3: se comparan signos (sin multiplicar, para evitar underflow con valores muy pequenos)
            raiz_a_la_izquierda = _signo(fa) * _signo(fc) < 0
            nuevo_a, nuevo_b = (a, c) if raiz_a_la_izquierda else (c, b)
            lado = "exacto" if fc == 0 else ("[a, c]" if raiz_a_la_izquierda else "[c, b]")

            error_absoluto = abs(c - c_anterior) if c_anterior is not None else None
            error_relativo = error_absoluto / abs(c) if error_absoluto is not None and c != 0 else None
            errores = {
                "absoluto": error_absoluto,
                "relativo": error_relativo,
                "porcentual": error_relativo * 100 if error_relativo is not None else None,
                "funcion": abs(fc),
                "intervalo": nuevo_b - nuevo_a,
            }
            fila = _fila(k, a, b, c, fa, fb, fc, c_anterior, criterio, errores[criterio], lado, error_relativo)
            fila.update({
                "error_absoluto": error_absoluto,
                "derivada": derivada_numerica(f, c),
                "fa_formula": fa_formula, "fb_formula": fb_formula,
                "nuevo_a": nuevo_a, "nuevo_b": nuevo_b,
            })
            iteraciones.append(fila)

            # Paso 3c: f(c) = 0 -> c es la raiz exacta
            if fc == 0:
                convergio, motivo, margen = True, f"f(c) = 0 en la iteración {k}: c es la raíz exacta.", 0.0
                break
            # Se detiene cuando el error es MENOR que E
            if errores[criterio] is not None and errores[criterio] < tolerancia:
                fila["detiene"] = True
                convergio, motivo = True, f"El error fue menor que E = {tolerancia:g} en la iteración {k}."
                break

            # Pasos 3a y 3b: se reemplaza el extremo que tiene el mismo signo que f(c)
            if raiz_a_la_izquierda:
                b, fb = c, fc
                peso_b, quieto_b = 1.0, 0
                quieto_a += 1
                if modificada and quieto_a >= 2:
                    peso_a /= 2  # a lleva 2 o mas iteraciones sin moverse: se divide f(a) a la mitad
            else:
                a, fa = c, fc
                peso_a, quieto_a = 1.0, 0
                quieto_b += 1
                if modificada and quieto_b >= 2:
                    peso_b /= 2
            c_anterior = c

    ultima = iteraciones[-1]
    if margen is None:
        # La raiz queda en el ultimo intervalo, que tiene a c como uno de sus extremos
        margen = ultima["nuevo_b"] - ultima["nuevo_a"]
    resultado = armar_resultado(f, inicial, tolerancia, criterio, max_iteraciones, iteraciones, convergio, motivo,
                                margen=margen, margen_texto="|raíz − c| ≤ longitud del último intervalo")
    resultado["modificada"] = modificada
    resultado["extremo_fijo"] = _extremo_fijo(iteraciones)
    return resultado


def _extremo_fijo(iteraciones):
    """Si un extremo no se movio en ninguna iteracion, el metodo avanzo por un solo lado (naturaleza unilateral)."""
    if len(iteraciones) < 3:
        return None
    if all(it["a"] == iteraciones[0]["a"] for it in iteraciones):
        return "a"
    if all(it["b"] == iteraciones[0]["b"] for it in iteraciones):
        return "b"
    return None
