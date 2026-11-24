# backend/algebra_lineal/sistemas.py
# Sistemas de ecuaciones lineales A·X = B con fracciones exactas.
# Los tres metodos comparten el mismo recorrido por columnas; solo cambian dos decisiones:
#   gauss         -> intercambia filas solo si el pivote es cero; elimina hacia abajo y sustituye hacia atras
#   pivote        -> pivoteo parcial: sube la fila con mayor |valor| de la columna; luego igual que Gauss
#   gauss_jordan  -> hace 1 cada pivote y anula toda la columna (forma escalonada reducida)
from fractions import Fraction

from .fracciones import a_fracciones, a_textos, determinante_exacto, format_frac

METODOS = {
    "gauss_jordan": "Gauss-Jordan",
    "gauss": "Eliminación de Gauss",
    "pivote": "Gauss con pivoteo parcial",
}


def nombres_por_defecto(n):
    return [f"x{i + 1}" for i in range(n)]


def eliminar(matriz, n, metodo="gauss_jordan"):
    """Reduce la matriz aumentada [A | b] (m × (n+1)). Devuelve (pasos, matriz_final).
    Cada paso es (descripcion, matriz en texto, fila que cambio o None)."""
    if metodo not in METODOS:
        raise ValueError(f"Método desconocido: {metodo}")
    a = a_fracciones(matriz)
    m = len(a)
    if m == 0 or any(len(fila) != n + 1 for fila in a):
        raise ValueError("La matriz aumentada debe tener n + 1 columnas en todas sus filas.")
    pasos = [("Matriz aumentada inicial [A | B]", a_textos(a), None)]
    fila_pivote = 0
    for col in range(n):
        if fila_pivote >= m:
            break
        candidatas = [i for i in range(fila_pivote, m) if a[i][col] != 0]
        if not candidatas:
            continue
        elegida = max(candidatas, key=lambda i: abs(a[i][col])) if metodo == "pivote" else candidatas[0]
        if elegida != fila_pivote:
            a[fila_pivote], a[elegida] = a[elegida], a[fila_pivote]
            motivo = "mayor |pivote|" if metodo == "pivote" else "pivote nulo"
            pasos.append((f"F{fila_pivote + 1} ↔ F{elegida + 1}  ({motivo})", a_textos(a), fila_pivote))

        pivote = a[fila_pivote][col]
        if metodo == "gauss_jordan" and pivote != 1:
            a[fila_pivote] = [v / pivote for v in a[fila_pivote]]
            pasos.append((f"F{fila_pivote + 1} → F{fila_pivote + 1} ÷ ({format_frac(pivote)})", a_textos(a), fila_pivote))
            pivote = Fraction(1)

        filas = range(m) if metodo == "gauss_jordan" else range(fila_pivote + 1, m)
        for i in filas:
            if i == fila_pivote or a[i][col] == 0:
                continue
            factor = a[i][col] / pivote
            a[i] = [v - factor * p for v, p in zip(a[i], a[fila_pivote])]
            pasos.append((f"F{i + 1} → F{i + 1} − ({format_frac(factor)})·F{fila_pivote + 1}", a_textos(a), i))
        fila_pivote += 1
    return pasos, a


def _pivotes(a, n):
    """Lista de (fila, columna) de cada pivote de una matriz escalonada."""
    lista = []
    for i, fila in enumerate(a):
        col = next((j for j in range(n) if fila[j] != 0), None)
        if col is not None:
            lista.append((i, col))
    return lista


def clasificar(a, n, nombres):
    """Tipo de solucion de una matriz ya escalonada."""
    if any(all(v == 0 for v in fila[:n]) and fila[n] != 0 for fila in a):
        return {"tipo": "ninguna", "rango": len(_pivotes(a, n)), "libres": [],
                "texto": "Sistema inconsistente: no tiene solución (aparece una fila 0 = c con c ≠ 0)."}
    columnas = {c for _, c in _pivotes(a, n)}
    libres = [nombres[j] for j in range(n) if j not in columnas]
    if libres:
        return {"tipo": "infinitas", "rango": len(columnas), "libres": libres,
                "texto": f"Sistema compatible indeterminado: infinitas soluciones ({len(libres)} variable(s) libre(s): "
                         f"{', '.join(libres)})."}
    return {"tipo": "unica", "rango": n, "libres": [],
            "texto": "Sistema compatible determinado: tiene solución única."}


def sustitucion_atras(a, n, nombres):
    """Solucion unica de una matriz escalonada, con el detalle de cada despeje."""
    solucion = [Fraction(0)] * n
    detalle = []
    for i, col in reversed(_pivotes(a, n)):
        suma = Fraction(0)
        terminos = []
        for j in range(col + 1, n):
            if a[i][j] != 0:
                suma += a[i][j] * solucion[j]
                terminos.append(f"({format_frac(a[i][j])})({format_frac(solucion[j])})")
        solucion[col] = (a[i][n] - suma) / a[i][col]
        resta = f" − [{' + '.join(terminos)}]" if terminos else ""
        detalle.append(f"{nombres[col]} = ({format_frac(a[i][n])}{resta}) / {format_frac(a[i][col])} = "
                       f"{format_frac(solucion[col])}")
    return solucion, detalle


def solucion_general(a, n, nombres):
    """Con infinitas soluciones: cada variable pivote en funcion de las libres (desde la forma reducida)."""
    _, r = eliminar(a_textos(a), n, "gauss_jordan")
    pivotes = _pivotes(r, n)
    columnas = {c for _, c in pivotes}
    lineas = []
    for i, col in pivotes:
        partes = [format_frac(r[i][n])] if r[i][n] != 0 else []
        for j in range(n):
            if j not in columnas and r[i][j] != 0:
                coef = -r[i][j]
                signo = "−" if coef < 0 else "+"
                valor = format_frac(abs(coef))
                if "/" in valor:
                    valor = f"({valor})"    # (2/3)z, no 2/3z
                partes.append(f"{signo} {'' if valor == '1' else valor}{nombres[j]}")
        texto = " ".join(partes).lstrip("+ ") or "0"
        if texto.startswith("− "):
            texto = "−" + texto[2:]
        lineas.append(f"{nombres[col]} = {texto}")
    lineas += [f"{nombres[j]} libre" for j in range(n) if j not in columnas]
    return lineas


def verificar(matriz, solucion, nombres):
    """Sustituye la solucion en cada ecuacion original: (texto, coincide)."""
    resultados = []
    for i, fila in enumerate(a_fracciones(matriz)):
        n = len(fila) - 1
        suma = sum(fila[j] * solucion[j] for j in range(n))
        sustitucion = " + ".join(f"({format_frac(fila[j])})({format_frac(solucion[j])})" for j in range(n) if fila[j] != 0)
        resultados.append({"texto": f"Ec. {i + 1}: {sustitucion or '0'} = {format_frac(suma)}",
                           "esperado": format_frac(fila[n]), "coincide": suma == fila[n]})
    return resultados


def resolver_sistema(matriz, metodo="gauss_jordan", nombres=None):
    """Resuelve [A | B] con el metodo elegido y arma todo lo que muestra la interfaz."""
    m = len(matriz)
    if m == 0:
        raise ValueError("El sistema no tiene ecuaciones.")
    n = len(matriz[0]) - 1
    if n < 1:
        raise ValueError("El sistema necesita al menos una incógnita.")
    nombres = nombres or nombres_por_defecto(n)
    original = a_fracciones(matriz)
    pasos, final = eliminar(original, n, metodo)
    tipo = clasificar(final, n, nombres)

    resultado = {
        "metodo": metodo, "nombre_metodo": METODOS[metodo], "m": m, "n": n, "nombres": nombres,
        "A": [fila[:n] for fila in a_textos(original)], "B": [format_frac(fila[n]) for fila in original],
        "pasos": pasos, "final": a_textos(final), "clasificacion": tipo,
        "determinante": None, "solucion": None, "detalle": [], "verificacion": [], "general": [],
    }
    if m == n:
        resultado["determinante"] = format_frac(determinante_exacto([fila[:n] for fila in original]))
    if tipo["tipo"] == "unica":
        if metodo == "gauss_jordan":
            solucion = [Fraction(0)] * n
            for i, col in _pivotes(final, n):
                solucion[col] = final[i][n]
            detalle = [f"{nombres[col]} = {format_frac(final[i][n])}  (fila {i + 1} de la forma reducida)"
                       for i, col in _pivotes(final, n)]
        else:
            solucion, detalle = sustitucion_atras(final, n, nombres)
        resultado.update(solucion=[format_frac(v) for v in solucion], detalle=detalle,
                         verificacion=verificar(original, solucion, nombres))
    elif tipo["tipo"] == "infinitas":
        resultado["general"] = solucion_general(final, n, nombres)
    return resultado
