# backend/metodos_numericos/abiertos.py
# Lo comun a los metodos abiertos (Newton-Raphson y secante):
#   - parten de uno o dos valores iniciales y generan x1, x2, x3... con una regla iterativa;
#   - no necesitan un intervalo que encierre la raiz (no se usa Bolzano);
#   - pueden converger muy rapido, pero no garantizan convergencia para cualquier valor inicial.
# Criterios de parada (presentacion de clase):
#   |x(n+1) − x(n)| < E   cambio entre aproximaciones (error absoluto, el que se usa por defecto)
#   |f(x(n+1))|     < E   residuo
# El metodo se detiene cuando se cumple la tolerancia O cuando se llega al maximo de iteraciones.
import math

from .biseccion import MAX_ITERACIONES, _cifras_significativas, leer_numero

# El error absoluto va primero: es el criterio que se usa por defecto
CRITERIOS = {
    "absoluto": "Ea = |xₙ₊₁ − xₙ|",
    "relativo": "Er = |(xₙ₊₁ − xₙ) / xₙ₊₁|",
    "porcentual": "Er % = |(xₙ₊₁ − xₙ) / xₙ₊₁| · 100 %",
    "residuo": "Residuo |f(xₙ₊₁)|",
    "ambos": "|xₙ₊₁ − xₙ| < E y |f(xₙ₊₁)| < E",
}

# Si una aproximacion pasa de este valor se considera que el metodo diverge
LIMITE_DIVERGENCIA = 1e12

_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def sub(n):
    """x con subindice: sub(2) -> 'x₂'."""
    return "x" + str(n).translate(_SUBINDICES)


# Por debajo de esto la computadora (doble precision, unas 16 cifras) ya no distingue los numeros
TOLERANCIA_MINIMA = 1e-15


def validar_parametros(tolerancia, criterio, max_iteraciones):
    tolerancia = leer_numero(tolerancia, "tolerancia E")
    maximo = leer_numero(max_iteraciones, "máximo de iteraciones")
    if maximo != int(maximo):
        raise ValueError("El máximo de iteraciones debe ser un número entero.")
    max_iteraciones = int(maximo)
    if criterio not in CRITERIOS:
        raise ValueError(f"Criterio de parada '{criterio}' no reconocido.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia E debe ser mayor que cero.")
    if tolerancia < TOLERANCIA_MINIMA:
        raise ValueError(f"La tolerancia E debe ser al menos {TOLERANCIA_MINIMA:g}: la computadora trabaja con unas "
                         "16 cifras y no puede medir errores más pequeños.")
    if not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe estar entre 1 y {MAX_ITERACIONES}.")
    return tolerancia, max_iteraciones


def leer_inicial(dato, nombre, f):
    """Lee un valor inicial y evalua f en el; f debe estar definida ahi."""
    if str(dato).strip() == "":
        raise ValueError(f"Escriba el valor inicial {nombre}.")
    x = leer_numero(dato, nombre)
    fx = f.evaluar(x)
    if fx is None:
        raise ValueError(f"f(x) no está definida en {nombre} = {x:g}. Elija otro valor inicial.")
    return x, fx


def calcular_errores(x_nuevo, x, f_nuevo):
    absoluto = abs(x_nuevo - x)
    relativo = absoluto / abs(x_nuevo) if x_nuevo != 0 else None
    residuo = abs(f_nuevo)
    return {
        "absoluto": absoluto,
        "relativo": relativo,
        "porcentual": relativo * 100 if relativo is not None else None,
        "residuo": residuo,
        "ambos": max(absoluto, residuo),  # los dos son menores que E si el mayor lo es
    }


def fila(k, n, x, fx, x_nuevo, f_nuevo, criterio, errores):
    """Una fila de la tabla: de xₙ se obtiene xₙ₊₁."""
    return {
        "iteracion": k, "n": n, "x": x, "fx": fx, "x_nuevo": x_nuevo, "f_nuevo": f_nuevo,
        "criterio": criterio, "error": errores[criterio],
        "error_absoluto": errores["absoluto"], "error_relativo": errores["relativo"],
        "residuo": errores["residuo"], "detiene": False, "dfx": None,
    }


def fila_exacta(k, n, x, criterio):
    """xₙ ya cumple f(xₙ) = 0: no hace falta aplicar la formula."""
    errores = {"absoluto": 0.0, "relativo": 0.0, "porcentual": 0.0, "residuo": 0.0, "ambos": 0.0}
    nueva = fila(k, n, x, 0.0, x, 0.0, criterio, errores)
    nueva["detiene"] = True
    nueva["exacta"] = True
    return nueva


def armar_resultado(metodo, f, df, iniciales, tolerancia, criterio, max_iteraciones, iteraciones,
                    convergio, motivo, estado):
    """Resultado comun: raiz aproximada, residuo, iteraciones, derivada y comprobaciones."""
    ultima = iteraciones[-1]
    raiz, f_raiz = ultima["x_nuevo"], ultima["f_nuevo"]
    resultado = {
        "metodo": metodo,
        **iniciales,
        "tolerancia": tolerancia, "criterio": criterio, "criterio_texto": CRITERIOS[criterio],
        "max_iteraciones": max_iteraciones,
        "iteraciones": iteraciones,
        "convergio": convergio,
        "motivo": motivo,
        "estado": estado,  # exacta, tolerancia, maximo, derivada_nula, diverge o dominio
        # Lo que pide reportar el algoritmo: raiz aproximada, residuo e iteraciones
        "total_iteraciones": len(iteraciones),
        "raiz": raiz,
        "f_raiz": f_raiz,
        "residuo": abs(f_raiz),
        "error_final": ultima["error"],
        "error_absoluto": ultima["error_absoluto"],
        "error_relativo": ultima["error_relativo"],
        "cifras_significativas": _cifras_significativas(ultima["error_relativo"]),
        # La derivada: su expresion y su valor en la raiz
        "derivada_texto": df.legible if df else None,
        "derivada_mathtext": df.mathtext if df else None,
        "derivada_raiz": df.evaluar(raiz) if df else None,
    }
    # La presentacion pide revisar los dos criterios (cambio y residuo) aunque se pare con uno
    resultado["ambos_criterios"] = [
        {"nombre": "Cambio entre aproximaciones", "formula": "|xₙ₊₁ − xₙ|", "valor": ultima["error_absoluto"],
         "cumple": ultima["error_absoluto"] < tolerancia},
        {"nombre": "Residuo", "formula": "|f(xₙ₊₁)|", "valor": abs(f_raiz), "cumple": abs(f_raiz) < tolerancia},
    ]
    resultado["veredicto"] = _veredicto(resultado)
    resultado["comprobaciones"] = _comprobaciones(resultado, f)
    return resultado


def _es_raiz_multiple(r):
    derivada_raiz = r["derivada_raiz"]
    if derivada_raiz is None:
        return False
    pendientes = [abs(it["dfx"]) for it in r["iteraciones"] if it.get("dfx")]
    referencia = max([1.0] + pendientes[:1])
    return abs(derivada_raiz) < 1e-3 * referencia


def _veredicto(r):
    """CONVERGE o DIVERGE, como en la presentacion:
       Convergencia: las aproximaciones se acercan a una raiz.
       Divergencia:  las aproximaciones no se acercan o se alejan."""
    iteraciones = r["iteraciones"]
    cambios = [it["error_absoluto"] for it in iteraciones]
    n = r["total_iteraciones"]

    if r["convergio"]:
        if _es_raiz_multiple(r):
            return {"tipo": "converge", "titulo": "CONVERGE (lentamente)",
                    "explicacion": (f"Las aproximaciones se acercan a la raíz y se cumplió la tolerancia en {n} iteraciones, "
                                    f"pero f'(raíz) ≈ {r['derivada_raiz']:.2g} ≈ 0: es una raíz múltiple y por eso "
                                    "la convergencia es más lenta.")}
        if r["estado"] == "exacta":
            texto = (f"Se llegó a un valor donde f(x) = 0 (con la precisión de la computadora) en la iteración {n}: "
                     "las aproximaciones llegaron a la raíz.")
        elif len(cambios) > 1:
            texto = (f"Las aproximaciones se acercan a la raíz: el cambio |xₙ₊₁ − xₙ| bajó de {cambios[0]:.3g} "
                     f"a {cambios[-1]:.3g} y fue menor que E = {r['tolerancia']:g} en la iteración {n}.")
        else:
            texto = f"El cambio fue menor que E = {r['tolerancia']:g} en la primera iteración."
        return {"tipo": "converge", "titulo": "CONVERGE", "explicacion": texto}

    if r["estado"] == "diverge":
        return {"tipo": "diverge", "titulo": "DIVERGE",
                "explicacion": "Las aproximaciones se alejan de la raíz. " + r["motivo"]}
    if r["estado"] in ("derivada_nula", "dominio"):
        return {"tipo": "diverge", "titulo": "DIVERGE (el método falla)",
                "explicacion": r["motivo"] + " Las aproximaciones no se pueden seguir acercando a la raíz."}

    # Se llego al maximo de iteraciones: se mira como se movieron las aproximaciones
    xs = [iteraciones[0]["x"]] + [it["x_nuevo"] for it in iteraciones]
    if len(xs) >= 5 and abs(xs[-1] - xs[-3]) <= 1e-9 * max(1.0, abs(xs[-1])) and abs(xs[-1] - xs[-2]) > r["tolerancia"]:
        return {"tipo": "diverge", "titulo": "DIVERGE (ciclo)",
                "explicacion": (f"Las aproximaciones no se acercan: saltan entre {xs[-2]:.6g} y {xs[-1]:.6g} sin parar "
                                f"(ciclo). Se llegó al máximo de {r['max_iteraciones']} iteraciones.")}
    inicial = max(1.0, abs(xs[0]))
    if abs(xs[-1]) > 100 * inicial and abs(xs[-1]) > abs(xs[len(xs) // 2]):
        return {"tipo": "diverge", "titulo": "DIVERGE",
                "explicacion": (f"Las aproximaciones se alejan: x pasó de {xs[0]:.6g} a {xs[-1]:.6g} en "
                                f"{r['max_iteraciones']} iteraciones.")}
    cola = cambios[-4:]
    bajando = len(cola) >= 3 and all(b < a for a, b in zip(cola, cola[1:])) and cambios[-1] < 0.1 * cambios[0]
    if bajando:
        return {"tipo": "lenta", "titulo": "CONVERGE, PERO NO ALCANZÓ E",
                "explicacion": (f"Las aproximaciones sí se acercan (el cambio bajó de {cambios[0]:.3g} a {cambios[-1]:.3g}), "
                                f"pero {r['max_iteraciones']} iteraciones no alcanzaron para que fuera menor que "
                                f"E = {r['tolerancia']:g}. Aumente el máximo de iteraciones o use un valor inicial más cercano.")}
    return {"tipo": "diverge", "titulo": "DIVERGE",
            "explicacion": (f"Las aproximaciones no se acercan a una raíz: después de {r['max_iteraciones']} iteraciones "
                            f"el cambio sigue en {cambios[-1]:.3g} (oscilan sin estabilizarse). Revise la gráfica: "
                            "puede que no haya raíz cerca del valor inicial.")}


def _comprobaciones(r, f):
    """Las reglas que debe cumplir el programa segun el algoritmo de los metodos abiertos."""
    raiz, f_raiz = r["raiz"], r["f_raiz"]
    iteraciones = r["iteraciones"]
    referencia = max(1.0, abs(iteraciones[0]["fx"]))
    cerca_de_cero = abs(f_raiz) < r["tolerancia"] or abs(f_raiz) <= 1e-6 * referencia
    es_newton = r["metodo"] == "newton"

    # Pasos con division casi entre cero: el salto |xₙ₊₁ − xₙ| es desproporcionado
    saltos = [it["iteracion"] for it in iteraciones
              if not it.get("exacta") and it["error_absoluto"] > 100 * max(1.0, abs(it["x"]))]
    if es_newton:
        titulo_division = "Alerta de f'(xₙ) = 0"
        pequenas = [it["iteracion"] for it in iteraciones
                    if it["dfx"] is not None and not it.get("exacta") and abs(it["dfx"]) < 1e-8]
        nombre = "f'(xₙ)"
    else:
        titulo_division = "Denominador f(xₙ) − f(xₙ₋₁) ≠ 0"
        pequenas = [it["iteracion"] for it in iteraciones
                    if not it.get("exacta") and abs(it.get("denominador", 1.0)) < 1e-12 * max(1.0, abs(it["fx"]))]
        nombre = "f(xₙ) − f(xₙ₋₁)"
    problemas = sorted(set(saltos + pequenas))
    if r["estado"] == "derivada_nula":
        division_ok, detalle_division = False, r["motivo"]
    elif problemas:
        division_ok = False
        detalle_division = (f"En las iteraciones {', '.join(map(str, problemas[:8]))} {nombre} es casi cero "
                            "y el paso fue excesivo: revise el valor inicial.")
    else:
        division_ok = True
        detalle_division = f"{nombre} nunca fue cero ni demasiado pequeño durante el cálculo."

    # Convergencia: el veredicto (converge o diverge) con su explicacion
    veredicto = r["veredicto"]
    convergencia_ok = veredicto["tipo"] == "converge"
    detalle_convergencia = f"{veredicto['titulo']}: {veredicto['explicacion']}"

    return [
        {
            "titulo": "Sustituir la raíz en la función original",
            "correcto": cerca_de_cero,
            "detalle": (f"Residuo: |f({raiz:.10g})| = {abs(f_raiz):.6e}, el resultado se acerca a cero." if cerca_de_cero else
                        f"Residuo: |f({raiz:.10g})| = {abs(f_raiz):.6e} no se acerca a cero; revise la gráfica "
                        "y el valor inicial."),
        },
        {
            "titulo": "Tolerancia o máximo de iteraciones",
            "correcto": r["convergio"],
            "detalle": (f"Se cumplió la tolerancia usando {r['total_iteraciones']} de {r['max_iteraciones']} "
                        "iteraciones permitidas." if r["convergio"] else r["motivo"]),
        },
        {"titulo": titulo_division, "correcto": division_ok, "detalle": detalle_division},
        {"titulo": "Convergencia", "correcto": convergencia_ok, "detalle": detalle_convergencia},
    ]


def detener_si_cumple(nueva, k, tolerancia):
    """Revisa si el error de la fila es menor que E. Devuelve el motivo o None."""
    if nueva["error"] is not None and nueva["error"] < tolerancia:
        nueva["detiene"] = True
        return "tolerancia", f"El error fue menor que E = {tolerancia:g} en la iteración {k}."
    if nueva["f_nuevo"] == 0:
        nueva["detiene"] = True
        return "exacta", (f"f({sub(nueva['n'] + 1)}) = 0 en la iteración {k} (con la precisión de la computadora): "
                          "es la raíz.")
    if nueva["x_nuevo"] == nueva["x"]:
        # La formula ya no mueve la aproximacion: se llego al limite de precision de la computadora
        nueva["detiene"] = True
        return "tolerancia", (f"En la iteración {k} la aproximación ya no cambia (límite de precisión de la computadora): "
                              "no se puede mejorar más.")
    return None


def fuera_de_rango(x_nuevo):
    return not math.isfinite(x_nuevo) or abs(x_nuevo) > LIMITE_DIVERGENCIA
