# backend/metodos_numericos/biseccion.py
# Metodo de Biseccion (metodo cerrado):
#   1) Se define f, el intervalo inicial [a, b] y la precision requerida E.
#   2) Se calcula el punto central del intervalo: c = (a + b) / 2
#   3) Si f(c) = 0, c es la raiz y termina.
#   4) Si la raiz esta en [a, c], se sustituye b por c.
#   5) Si la raiz esta en [c, b], se sustituye a por c.
#   6) Se repiten los pasos 2 a 5 hasta que el error sea MENOR que E.
# El intervalo inicial sale de la tabulacion (grafica) de f(x): se buscan los
# subintervalos donde f cambia de signo, porque si f(a)·f(b) < 0 hay al menos
# una raiz en (a, b) (teorema de Bolzano).
import math

# El error absoluto va primero: es el criterio que se usa por defecto
CRITERIOS = {
    "absoluto": "Ea = |c nuevo − c anterior|",
    "relativo": "Er = |(c nuevo − c anterior) / c nuevo|",
    "porcentual": "Er % = |(c nuevo − c anterior) / c nuevo| · 100 %",
    "funcion": "|f(c)|",
    "intervalo": "Longitud del intervalo (b − a)",
}

MAX_SUBINTERVALOS = 2000
MAX_ITERACIONES = 1000


def _signo(valor):
    return (valor > 0) - (valor < 0)


def leer_numero(dato, nombre):
    """Convierte el texto escrito por el usuario en numero (acepta coma decimal)."""
    try:
        valor = float(str(dato).replace(",", ".").strip())
    except (TypeError, ValueError):
        raise ValueError(f"'{nombre}' debe ser un número (se escribió '{dato}').")
    if math.isnan(valor) or math.isinf(valor):
        raise ValueError(f"'{nombre}' debe ser un número finito.")
    return valor


def derivada_numerica(f, x):
    """Aproxima f'(x) con diferencia central; solo se usa para la alerta de f'(x) = 0."""
    h = 1e-5 * max(1.0, abs(x))
    izquierda, derecha = f.evaluar(x - h), f.evaluar(x + h)
    if izquierda is None or derecha is None:
        return None
    return (derecha - izquierda) / (2 * h)


# ----------------------------------------------------------------------
# Paso previo: tabulacion de f(x) para obtener los intervalos de la grafica
# ----------------------------------------------------------------------
def _redondear(x):
    """Quita el ruido de la suma en punto flotante: 0.30000000000000004 -> 0.3."""
    return round(x, 12)


def _destino_biseccion(f, a, b, fa, fb):
    """Bisecciona [a, b] hasta la precision de la maquina. Devuelve (x, f(x)) del punto
    al que llega; f(x) es None si en el camino f no estaba definida."""
    for _ in range(200):
        c = (a + b) / 2
        if c <= a or c >= b:
            break
        fc = f.evaluar(c)
        if fc is None or fc == 0:
            return c, fc
        if _signo(fa) * _signo(fc) < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return (a, fa) if abs(fa) <= abs(fb) else (b, fb)


def discontinuidad(f, a, b, fa, fb):
    """
    Un cambio de signo no siempre es una raiz: en tan(x) o 1/x el signo cambia al
    cruzar una asintota. Bolzano exige continuidad, asi que se revisa a donde llega
    la biseccion: en una raiz |f| se hace casi cero; en una asintota |f| crece.
    Devuelve la x aproximada de la discontinuidad, o None si es una raiz de verdad.
    """
    x, fx = _destino_biseccion(f, a, b, fa, fb)
    if fx is None or abs(fx) > 1e-6 * max(abs(fa), abs(fb)):
        return x
    return None


def revisar_continuidad(f, a, b, muestras=2000):
    """
    Prueba si f es continua en [a, b] (condicion de Bolzano):
      1) f debe estar definida en todo el intervalo (se evalua en muchos puntos);
      2) donde f cambia mas bruscamente se acerca el par de puntos a la mitad una y otra vez:
         si f es continua la diferencia |f(x2) - f(x1)| se hace casi cero; si hay un salto
         o una asintota, no baja (o crece).
    Devuelve {"continua", "x", "motivo"}.
    """
    xs, ys = _evaluar_rejilla(f, a, b, muestras)
    for x, y in zip(xs, ys):
        if y is None:
            return {"continua": False, "x": x, "motivo": f"f(x) no está definida en x ≈ {x:.6g}"}
    escala = max(max(abs(y) for y in ys), 1e-300)
    saltos = sorted(range(muestras), key=lambda i: abs(ys[i + 1] - ys[i]), reverse=True)[:4]
    for i in saltos:
        x1, x2, y1, y2 = xs[i], xs[i + 1], ys[i], ys[i + 1]
        for _ in range(200):
            m = (x1 + x2) / 2
            if m <= x1 or m >= x2:
                break
            ym = f.evaluar(m)
            if ym is None:
                return {"continua": False, "x": m, "motivo": f"f(x) no está definida en x ≈ {m:.6g}"}
            # Se sigue la mitad donde el cambio es mayor
            if abs(ym - y1) >= abs(y2 - ym):
                x2, y2 = m, ym
            else:
                x1, y1 = m, ym
        if abs(y2 - y1) > 1e-6 * escala:
            x = (x1 + x2) / 2
            x = 0.0 if abs(x) < 1e-9 * max(1.0, abs(b - a)) else x
            return {"continua": False, "x": x, "motivo": f"f(x) tiene un salto o una asíntota en x ≈ {x:.6g}"}
    return {"continua": True, "x": None, "motivo": "f(x) es continua en [a, b]"}


def _evaluar_rejilla(f, x_min, x_max, n):
    h = (x_max - x_min) / n
    xs = [x_max if i == n else _redondear(x_min + i * h) for i in range(n + 1)]
    return xs, [f.evaluar(x) for x in xs]


def _contar_cruces(ys):
    """Cambios de signo entre puntos definidos seguidos (un cero entre signos opuestos cuenta uno)."""
    cruces, anterior = 0, 0
    for y in ys:
        if y is None:
            anterior = 0          # un hueco (f no definida) corta la cuenta
        elif y != 0:
            s = _signo(y)
            if anterior and s != anterior:
                cruces += 1
            anterior = s
    return cruces


def tabular(f, x_min, x_max, subintervalos):
    x_min, x_max = leer_numero(x_min, "x mínimo"), leer_numero(x_max, "x máximo")
    n = int(leer_numero(subintervalos, "subintervalos"))
    if x_min >= x_max:
        raise ValueError("El rango de la gráfica debe cumplir x mínimo < x máximo.")
    if not 1 <= n <= MAX_SUBINTERVALOS:
        raise ValueError(f"Los subintervalos deben estar entre 1 y {MAX_SUBINTERVALOS}.")

    h = (x_max - x_min) / n
    xs, ys = _evaluar_rejilla(f, x_min, x_max, n)
    tabla = [{"i": i, "x": x, "y": y} for i, (x, y) in enumerate(zip(xs, ys))]

    intervalos, discontinuidades, raices_que_tocan = [], [], []
    for izq, der in zip(tabla, tabla[1:]):
        if izq["y"] is None or der["y"] is None:
            continue
        # Cambio de signo entre dos puntos seguidos: ahi hay al menos una raiz... si f es continua
        if _signo(izq["y"]) * _signo(der["y"]) < 0:
            x_salto = discontinuidad(f, izq["x"], der["x"], izq["y"], der["y"])
            if x_salto is not None:
                discontinuidades.append({"a": izq["x"], "b": der["x"], "x": x_salto})
            else:
                intervalos.append({"a": izq["x"], "b": der["x"], "fa": izq["y"], "fb": der["y"], "exacta": None})

    # f(x) = 0 justo en un punto de la tabla: no hay cambio de signo entre puntos seguidos,
    # asi que se toma el intervalo formado por sus vecinos (la biseccion lo encuentra en c).
    for i, p in enumerate(tabla):
        if p["y"] != 0:
            continue
        izq = tabla[i - 1] if i > 0 else None
        der = tabla[i + 1] if i < n else None
        signo_izq = _signo(izq["y"]) if izq and izq["y"] is not None else 0
        signo_der = _signo(der["y"]) if der and der["y"] is not None else 0
        if signo_izq and signo_der and signo_izq == signo_der:
            raices_que_tocan.append(p["x"])  # la curva toca el eje sin cruzarlo (raiz doble)
            continue
        if signo_izq and signo_der:
            a, b, fa, fb = izq["x"], der["x"], izq["y"], der["y"]
        elif signo_der:
            a, b, fa, fb = p["x"], der["x"], p["y"], der["y"]
        elif signo_izq:
            a, b, fa, fb = izq["x"], p["x"], izq["y"], p["y"]
        else:
            continue
        intervalos.append({"a": a, "b": b, "fa": fa, "fb": fb, "exacta": p["x"]})

    intervalos.sort(key=lambda iv: iv["a"])
    for numero, iv in enumerate(intervalos, start=1):
        iv["numero"] = numero

    return {
        "x_min": x_min, "x_max": x_max, "paso": h, "subintervalos": n, "tabla": tabla,
        "intervalos": intervalos, "discontinuidades": discontinuidades,
        "raices_exactas": [p["x"] for p in tabla if p["y"] == 0],
        "raices_que_tocan": raices_que_tocan,
        "puntos_indefinidos": sum(1 for p in tabla if p["y"] is None),
        "subintervalos_sugeridos": _subintervalos_sugeridos(f, x_min, x_max, n, _contar_cruces(ys)),
    }


def _subintervalos_sugeridos(f, x_min, x_max, n, cruces):
    """Si la curva cruza el eje mas veces de las que ve la tabulacion (dos raices dentro
    del mismo subintervalo se anulan), propone cuantos subintervalos usar."""
    _, ys_fino = _evaluar_rejilla(f, x_min, x_max, 4000)
    cruces_reales = _contar_cruces(ys_fino)
    if cruces_reales <= cruces:
        return None
    m = n
    while m < MAX_SUBINTERVALOS:
        m = min(m * 2, MAX_SUBINTERVALOS)
        if _contar_cruces(_evaluar_rejilla(f, x_min, x_max, m)[1]) >= cruces_reales:
            return m
    return MAX_SUBINTERVALOS


# Pasos "redondos" para la tabulacion automatica. Primero los mas comunes en clase;
# los segundos sirven para que la rejilla no caiga justo sobre una raiz entera.
_PASOS_REDONDOS = [100, 50, 20, 10, 5, 2, 1, 0.5, 0.25, 0.2, 0.1, 0.05, 0.025, 0.02, 0.01, 0.005, 0.002, 0.001]
_PASOS_ALTERNOS = [75, 30, 15, 7.5, 3, 1.5, 0.75, 0.6, 0.4, 0.3, 0.15, 0.075, 0.04, 0.03, 0.015, 0.004, 0.003]


def buscar_rango(f):
    """
    Busca automaticamente un rango [x min, x max] y un numero de subintervalos donde se
    vean las raices reales de f mas cercanas al origen. Devuelve None si no encuentra
    ningun cambio de signo entre -1000 y 1000.
    """
    raices = {}  # x -> True si la curva cruza el eje ahi (False si solo lo toca)
    # Primero de cerca (detalle) y luego de lejos; si no hay nada se amplia hasta 1000
    for radios in ((10, 100), (1000,)):
        for radio in radios:
            xs, ys = _evaluar_rejilla(f, -radio, radio, 4000)
            for i in range(len(xs)):
                y, siguiente = ys[i], (ys[i + 1] if i + 1 < len(xs) else None)
                if y == 0:
                    anterior = ys[i - 1] if i > 0 else None
                    cruza = not (anterior and siguiente and _signo(anterior) == _signo(siguiente))
                    raices[xs[i]] = cruza
                elif y is not None and siguiente and _signo(y) * _signo(siguiente) < 0 \
                        and discontinuidad(f, xs[i], xs[i + 1], y, siguiente) is None:
                    raices[_destino_biseccion(f, xs[i], xs[i + 1], y, siguiente)[0]] = True
        if raices:
            break
    if not raices:
        return None

    # Se quitan repetidas (la misma raiz vista de cerca y de lejos)
    unicas = []
    for x in sorted(raices):
        if unicas and abs(x - unicas[-1][0]) < 1e-6 * max(1.0, abs(x)):
            continue
        unicas.append((x, raices[x]))

    # Con muchas raices (sen x, tan x...) se muestran solo las mas cercanas al origen
    distancias = sorted(abs(x) for x, _ in unicas)
    limite = distancias[min(4, len(distancias) - 1)] + 1e-9
    elegidas = [x for x, _ in unicas if abs(x) <= limite]
    a_cubrir = [x for x, cruza in unicas if cruza and abs(x) <= limite]
    bajo, alto = min(elegidas), max(elegidas)
    margen = max(1.0, 0.2 * (alto - bajo))
    ancho = (alto - bajo) + 2 * margen

    def probar(h):
        x_min = _redondear(math.floor((bajo - margen) / h) * h)
        x_max = _redondear(math.ceil((alto + margen) / h) * h)
        n = round((x_max - x_min) / h)
        if not 1 <= n <= MAX_SUBINTERVALOS:
            return None
        t = tabular(f, x_min, x_max, n)
        # Cada raiz que cruza debe quedar sola en su propio intervalo
        dentro = [sum(1 for r in a_cubrir if iv["a"] <= r <= iv["b"]) for iv in t["intervalos"]]
        cubre = (all(k <= 1 for k in dentro)
                 and all(any(iv["a"] <= r <= iv["b"] for iv in t["intervalos"]) for r in a_cubrir))
        return {"x_min": x_min, "x_max": x_max, "subintervalos": n, "cubre": cubre,
                # Raices que caen en la rejilla o justo en el primer punto medio: se resuelven sin iterar
                "exactas": sum(1 for iv in t["intervalos"]
                               if iv["exacta"] is not None or f.evaluar((iv["a"] + iv["b"]) / 2) == 0)}

    # Primero tablas cortas (8 a 60 filas); si las raices estan muy juntas se permiten mas filas
    elegido = None
    for minimo, maximo in ((8, 60), (61, 400)):
        candidatos = [h for lista in (_PASOS_REDONDOS, _PASOS_ALTERNOS) for h in lista if minimo <= ancho / h <= maximo]
        pruebas = [p for p in (probar(h) for h in candidatos) if p]
        # Lo ideal: encierra cada raiz y la menor cantidad cae justo en la rejilla (asi la biseccion itera)
        validas = [p for p in pruebas if p["cubre"]]
        if validas:
            elegido = min(validas, key=lambda p: p["exactas"])  # min() respeta el orden ante empates
            break
    if elegido is None:
        elegido = probar(next(h for h in _PASOS_REDONDOS if ancho / h >= 8))
    return {"x_min": elegido["x_min"], "x_max": elegido["x_max"], "subintervalos": elegido["subintervalos"],
            "raices": len(elegidas)}


def verificar_bolzano(f, a, b):
    """Revisa si el intervalo [a, b] sirve para biseccion antes de iterar."""
    a, b = leer_numero(a, "a"), leer_numero(b, "b")
    if a >= b:
        return {"valido": False, "a": a, "b": b, "fa": None, "fb": None, "mensaje": "El intervalo debe cumplir a < b."}
    fa, fb = f.evaluar(a), f.evaluar(b)
    if fa is None or fb is None:
        punto = a if fa is None else b
        return {"valido": False, "a": a, "b": b, "fa": fa, "fb": fb,
                "mensaje": f"✗ f(x) no está definida en x = {punto:g}, así que no es continua en [a, b]. "
                           "Elija otro intervalo."}
    # Condicion 1 de Bolzano: f continua en [a, b]
    continuidad = revisar_continuidad(f, a, b)
    base = {"a": a, "b": b, "fa": fa, "fb": fb, "continua": continuidad["continua"],
            "continuidad": ("✓ f(x) es continua en [a, b]." if continuidad["continua"] else
                            f"✗ f(x) NO es continua en [a, b]: {continuidad['motivo']}.")}
    if fa == 0 or fb == 0:
        return {**base, "valido": True, "mensaje": "Un extremo ya es raíz exacta (f = 0)."}
    if not continuidad["continua"]:
        return {**base, "valido": False,
                "mensaje": "Bolzano exige que f sea continua en [a, b]; no se garantiza una raíz. Elija otro intervalo."}
    # Condicion 2 de Bolzano: signos opuestos en los extremos
    if _signo(fa) * _signo(fb) > 0:
        return {**base, "valido": False,
                "mensaje": "f(a)·f(b) > 0: tienen el mismo signo, no se garantiza una raíz en el intervalo."}
    return {**base, "valido": True, "mensaje": "f(a)·f(b) < 0: hay al menos una raíz en el intervalo."}


# ----------------------------------------------------------------------
# Metodo de biseccion
# ----------------------------------------------------------------------
def validar_parametros(tolerancia, criterio, max_iteraciones):
    """Lee y revisa E, el criterio de parada y el maximo de iteraciones (comun a los metodos cerrados)."""
    tolerancia = leer_numero(tolerancia, "tolerancia E")
    max_iteraciones = int(leer_numero(max_iteraciones, "máximo de iteraciones"))
    if criterio not in CRITERIOS:
        raise ValueError(f"Criterio de parada '{criterio}' no reconocido.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia E debe ser mayor que cero.")
    if not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe estar entre 1 y {MAX_ITERACIONES}.")
    return tolerancia, max_iteraciones


def biseccion(f, a, b, tolerancia, criterio="absoluto", max_iteraciones=100):
    tolerancia, max_iteraciones = validar_parametros(tolerancia, criterio, max_iteraciones)

    bolzano = verificar_bolzano(f, a, b)
    if not bolzano["valido"]:
        raise ValueError(bolzano["mensaje"])
    a, b, fa, fb = bolzano["a"], bolzano["b"], bolzano["fa"], bolzano["fb"]
    a0, b0, fa0, fb0 = a, b, fa, fb

    iteraciones = []
    c_anterior = None
    convergio = False
    motivo = f"Se alcanzó el máximo de {max_iteraciones} iteraciones sin que el error fuera menor que E."

    if fa == 0 or fb == 0:
        convergio, motivo = True, "Uno de los extremos del intervalo ya es la raíz exacta (f = 0)."
        iteraciones.append(_fila(1, a, b, a if fa == 0 else b, fa, fb, 0.0, None, criterio, 0.0, "exacto", None))
    else:
        for k in range(1, max_iteraciones + 1):
            # Paso 2: punto medio
            c = (a + b) / 2
            if c <= a or c >= b:
                # a y b ya son numeros consecutivos de la computadora: no se puede partir mas
                if not iteraciones:
                    raise ValueError("El intervalo [a, b] es demasiado pequeño para dividirlo.")
                motivo = (f"El intervalo ya no se puede dividir más (límite de precisión de la computadora) "
                          f"y el error no llegó a ser menor que E = {tolerancia:g}. Use una E más grande.")
                break
            fc = f.evaluar(c)
            if fc is None:
                raise ValueError(f"f(c) no está definida en c = {c}: la función no es continua en [a, b].")

            # Pasos 4 y 5: se comparan signos (no se multiplica para evitar underflow)
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
            fila["error_absoluto"] = error_absoluto
            fila["derivada"] = derivada_numerica(f, c)
            iteraciones.append(fila)

            # Paso 3: f(c) = 0 -> c es la raiz exacta
            if fc == 0:
                convergio, motivo = True, f"f(c) = 0 en la iteración {k}: c es la raíz exacta."
                break
            # Paso 6: se detiene cuando el error es MENOR que E
            if errores[criterio] is not None and errores[criterio] < tolerancia:
                fila["detiene"] = True
                convergio, motivo = True, f"El error fue menor que E = {tolerancia:g} en la iteración {k}."
                break

            if raiz_a_la_izquierda:
                b, fb = c, fc
            else:
                a, fa = c, fc
            c_anterior = c

    ultima = iteraciones[-1]
    return armar_resultado(f, (a0, b0, fa0, fb0), tolerancia, criterio, max_iteraciones, iteraciones,
                           convergio, motivo, margen=(ultima["b"] - ultima["a"]) / 2,
                           margen_texto="|raíz − c| ≤ (b − a) / 2")


def armar_resultado(f, inicial, tolerancia, criterio, max_iteraciones, iteraciones, convergio, motivo,
                    margen, margen_texto):
    """Resultado comun de los metodos cerrados: las tres conclusiones y las comprobaciones."""
    a0, b0, fa0, fb0 = inicial
    ultima = iteraciones[-1]
    resultado = {
        "a_inicial": a0, "b_inicial": b0, "fa_inicial": fa0, "fb_inicial": fb0,
        "tolerancia": tolerancia, "criterio": criterio, "criterio_texto": CRITERIOS[criterio],
        "max_iteraciones": max_iteraciones,
        "iteraciones": iteraciones,
        "convergio": convergio,
        "motivo": motivo,
        # Las tres conclusiones del metodo
        "total_iteraciones": len(iteraciones),
        "raiz": ultima["c"],
        "error_final": ultima["error"],
        "f_raiz": ultima["fc"],
        "margen": margen,
        "margen_texto": margen_texto,
        "error_relativo": ultima["error_relativo"],
        "error_absoluto": ultima["error_absoluto"],
        "cifras_significativas": _cifras_significativas(ultima["error_relativo"]),
    }
    # Pendiente promedio del intervalo: sirve de escala para decidir si f'(x) es "casi cero"
    escala_pendiente = max(abs(fa0), abs(fb0)) / (b0 - a0)
    resultado["comprobaciones"] = _comprobaciones(f, resultado, escala_pendiente)
    return resultado


def _fila(k, a, b, c, fa, fb, fc, c_anterior, criterio, error, lado, error_relativo):
    return {
        "iteracion": k, "a": a, "b": b, "c": c, "fa": fa, "fb": fb, "fc": fc,
        "c_anterior": c_anterior, "criterio": criterio, "error": error,
        "error_relativo": error_relativo, "error_absoluto": None,
        "subintervalo": lado, "detiene": False, "derivada": None,
    }


def _cifras_significativas(error_relativo):
    """Criterio de Scarborough: hay n cifras correctas si Ea% < 0.5·10^(2-n)."""
    if not error_relativo:
        return None
    return max(0, math.ceil(2 - math.log10(error_relativo * 100 / 0.5)) - 1)


def _comprobaciones(f, r, escala_pendiente):
    """Las cuatro reglas que debe cumplir el programa segun el algoritmo."""
    raiz, f_raiz = r["raiz"], r["f_raiz"]
    referencia = max(abs(r["fa_inicial"]), abs(r["fb_inicial"]))
    cerca_de_cero = abs(f_raiz) <= 1e-3 * referencia
    derivada = derivada_numerica(f, raiz)
    pendiente_nula = derivada is not None and abs(derivada) < 1e-3 * escala_pendiente
    iteraciones_planas = [it["iteracion"] for it in r["iteraciones"]
                          if it["derivada"] is not None and abs(it["derivada"]) < 1e-3 * escala_pendiente]

    return [
        {
            "titulo": "Rutina de graficación",
            "correcto": True,
            "detalle": "La gráfica de f(x) se usó para ubicar el intervalo con cambio de signo.",
        },
        {
            "titulo": "Sustituir la raíz en la función original",
            "correcto": cerca_de_cero,
            "detalle": (f"f({raiz:.10g}) = {f_raiz:.6e}, el resultado se acerca a cero." if cerca_de_cero else
                        f"f({raiz:.10g}) = {f_raiz:.6e} no se acerca a cero: puede haber una discontinuidad "
                        "(asíntota) o una convergencia lenta; revise la gráfica."),
        },
        {
            "titulo": "Límite máximo de iteraciones",
            "correcto": r["convergio"],
            "detalle": (f"Se usaron {r['total_iteraciones']} de {r['max_iteraciones']} iteraciones permitidas." if r["convergio"] else
                        r["motivo"]),
        },
        {
            "titulo": "Alerta de f'(x) = 0",
            "correcto": derivada is not None and not pendiente_nula and not iteraciones_planas,
            "detalle": _detalle_derivada(derivada, pendiente_nula, iteraciones_planas),
        },
    ]


def _detalle_derivada(derivada, pendiente_nula, iteraciones_planas):
    if derivada is None:
        return "No se pudo estimar f'(x) en la raíz."
    if not pendiente_nula and not iteraciones_planas:
        return f"f'(raíz) ≈ {derivada:.6g}: la pendiente no se anula durante el cálculo."
    donde = f" en las iteraciones {', '.join(map(str, iteraciones_planas[:8]))}" if iteraciones_planas else " en la raíz"
    return (f"f'(x) ≈ 0{donde}: la curva es casi horizontal; puede ser una raíz múltiple "
            "y el error puede ser engañoso.")
