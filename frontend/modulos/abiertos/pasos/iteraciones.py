# frontend/modulos/abiertos/pasos/iteraciones.py
# Paso 4 de los metodos abiertos: la pantalla es la de biseccion (navegador, grafica, tabla);
# aqui se arma la explicacion de cada iteracion y la tabla con xₙ, f(xₙ), f'(xₙ), xₙ₊₁, error y residuo.
from ....formato import clase_signo, con_signo, escapar, numero
from ..estado import NOMBRE_ERROR

EXPLICACION_NEWTON = [
    ("Evaluar f(xₙ)", "Se sustituye la aproximación actual en la función."),
    ("Evaluar f'(xₙ)", "Se sustituye en la derivada: es la pendiente de la recta tangente en ese punto."),
    ("Fórmula de Newton-Raphson", "xₙ₊₁ = xₙ − f(xₙ)/f'(xₙ): es donde la tangente corta el eje x."),
    ("Residuo", "|f(xₙ₊₁)| mide cuánto incumple la ecuación la nueva aproximación."),
    ("Cambio entre iteraciones", "Ea = |xₙ₊₁ − xₙ|: cuánto se movió la aproximación (error absoluto)."),
    ("Decidir", "Si el error es menor que E se detiene; si no, se repite con xₙ₊₁ hasta el máximo de iteraciones."),
]

EXPLICACION_SECANTE = [
    ("Los dos puntos", "Se usan las dos últimas aproximaciones xₙ₋₁ y xₙ con sus valores de f."),
    ("Pendiente de la secante", "m = (f(xₙ) − f(xₙ₋₁)) / (xₙ − xₙ₋₁): aproxima f'(xₙ) sin derivar."),
    ("Fórmula de la secante", "xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / [f(xₙ) − f(xₙ₋₁)]: donde la secante corta el eje x."),
    ("Residuo", "|f(xₙ₊₁)| mide cuánto incumple la ecuación la nueva aproximación."),
    ("Cambio entre iteraciones", "Ea = |xₙ₊₁ − xₙ|: cuánto se movió la aproximación (error absoluto)."),
    ("Decidir y actualizar", "Si el error es menor que E se detiene; si no, xₙ₋₁ ← xₙ, xₙ ← xₙ₊₁ y se repite."),
]


def x(n):
    """x con subindice en HTML."""
    return f"x<sub>{n}</sub>"


def _signo(d):
    return lambda v: f'<span class="{clase_signo(v)}">{con_signo(v, d)}</span>'


def renglones_newton(it, r, d):
    n, s = it["n"], _signo(d)
    xn, xn1 = x(n), x(n + 1)
    if it.get("exacta"):
        return [("Evaluar la función", f"f({xn}) = f({numero(it['x'], d)}) = <b>0</b>", ""),
                ("Raíz exacta", f"{xn} = <b>{numero(it['x'], d)}</b> cumple f(x) = 0: es la raíz exacta.", "decision alto")]
    return [
        ("Evaluar la función", f"f({xn}) = f({numero(it['x'], d)}) = <b>{s(it['fx'])}</b>", ""),
        ("Evaluar la derivada", f"f'(x) = {escapar(r['derivada_texto'])}<br>"
                                f"f'({xn}) = f'({numero(it['x'], d)}) = <b>{s(it['dfx'])}</b>", ""),
        ("Fórmula de Newton-Raphson",
         f"{xn1} = {xn} − f({xn}) / f'({xn})<br>"
         f"{xn1} = {numero(it['x'], d)} − ({s(it['fx'])}) / ({s(it['dfx'])}) = <b>{numero(it['x_nuevo'], d)}</b>", ""),
    ] + _comunes(it, r, d, "se continúa con " + xn1 + ".")


def renglones_secante(it, r, d):
    n, s = it["n"], _signo(d)
    xa, xn, xn1 = x(n - 1), x(n), x(n + 1)
    puntos = (f"{xa} = {numero(it['x_anterior'], d)} &nbsp;→&nbsp; f({xa}) = {s(it['f_anterior'])}<br>"
              f"{xn} = {numero(it['x'], d)} &nbsp;→&nbsp; f({xn}) = {s(it['fx'])}")
    if it.get("exacta"):
        return [("Los dos puntos", puntos, ""),
                ("Raíz exacta", f"f({xn}) = 0: {xn} = <b>{numero(it['x'], d)}</b> es la raíz exacta.", "decision alto")]
    pendiente = (f"m = (f({xn}) − f({xa})) / ({xn} − {xa}) = ({s(it['fx'])} − ({s(it['f_anterior'])})) / "
                 f"({numero(it['x'], d)} − {numero(it['x_anterior'], d)}) = <b>{numero(it['pendiente'], d)}</b>")
    if it["dfx"] is not None:
        pendiente += (f"<br><i>Para comparar, la tangente tiene pendiente f'({xn}) = {numero(it['dfx'], d)} "
                      f"(f'(x) = {escapar(r['derivada_texto'])}).</i>")
    formula = (f"{xn1} = {xn} − f({xn})·({xn} − {xa}) / [f({xn}) − f({xa})]<br>"
               f"{xn1} = {numero(it['x'], d)} − ({s(it['fx'])})·({numero(it['x'], d)} − {numero(it['x_anterior'], d)}) / "
               f"[({s(it['fx'])}) − ({s(it['f_anterior'])})] = <b>{numero(it['x_nuevo'], d)}</b>")
    return ([("Los dos puntos", puntos, ""), ("Pendiente de la secante", pendiente, ""), ("Fórmula de la secante", formula, "")]
            + _comunes(it, r, d, f"se actualiza {xa} ← {xn}, {xn} ← {xn1} y se repite."))


def _comunes(it, r, d, continuar):
    """Residuo, cambio entre iteraciones y decision: igual en Newton-Raphson y en la secante."""
    n = it["n"]
    xn, xn1 = x(n), x(n + 1)
    pasos = [("Residuo", f"|f({xn1})| = |f({numero(it['x_nuevo'], d)})| = <b>{numero(it['residuo'], d)}</b>", "")]

    cambio = (f"Ea = |{xn1} − {xn}| = |{numero(it['x_nuevo'], d)} − {numero(it['x'], d)}| = "
              f"<b>{numero(it['error_absoluto'], d)}</b>")
    criterio = r["criterio"]
    if criterio in ("relativo", "porcentual"):
        por_cien = " · 100 %" if criterio == "porcentual" else ""
        cambio += (f"<br>{NOMBRE_ERROR[criterio]} = |({numero(it['x_nuevo'], d)} − {numero(it['x'], d)}) / "
                   f"{numero(it['x_nuevo'], d)}|{por_cien} = <b>{numero(it['error'], d)}</b>")
    pasos.append(("Cambio entre iteraciones", cambio, ""))

    tolerancia = r["tolerancia"]
    if criterio == "ambos":
        comparacion = (f"Ea = {numero(it['error_absoluto'], d)} y |f| = {numero(it['residuo'], d)}")
    else:
        comparacion = f"{NOMBRE_ERROR[criterio]} = {numero(it['error'], d)}"
    es_ultima = it["iteracion"] == r["total_iteraciones"]
    cumple = it["error"] is not None and it["error"] < tolerancia
    if it["detiene"] and cumple:
        menor = "ambos &lt;" if criterio == "ambos" else "&lt;"
        decision = (f"{comparacion} {menor} E = {tolerancia:g} → <b>se detiene (converge)</b>: la raíz aproximada es "
                    f"{xn1} = <b>{numero(it['x_nuevo'], d)}</b>.")
        clase = "decision alto"
    elif it["detiene"] and it["f_nuevo"] == 0:
        decision, clase = (f"f({xn1}) = 0 → <b>se detiene (converge)</b>: {xn1} = <b>{numero(it['x_nuevo'], d)}</b> "
                           "es la raíz."), "decision alto"
    elif it["detiene"]:
        decision, clase = f"<b>Se detiene</b>: {escapar(r['motivo'])}", "decision alto"
    elif es_ultima:
        decision = f"<b>Se detiene</b>: {escapar(r['motivo'])}"
        if r["iteraciones"] and it["iteracion"] == r["max_iteraciones"]:
            decision = (f"{comparacion} ≥ E = {tolerancia:g} y se llegó al máximo de {r['max_iteraciones']} iteraciones "
                        f"→ <b>se detiene</b>. {escapar(r['veredicto']['titulo'])}.")
        clase = "decision"
    else:
        decision, clase = f"{comparacion} ≥ E = {tolerancia:g} → {continuar}", "decision"
    pasos.append(("¿El error es menor que E?", decision, clase))
    return pasos


def tabla(r, d, actual, prefijo):
    """Tabla de iteraciones como en la presentacion (n, xₙ, f(xₙ)...) con el residuo y el error."""
    newton = r["metodo"] == "newton"
    criterio = r["criterio"]
    if newton:
        titulos = ["n", "xₙ", "f(xₙ)", "f'(xₙ)", "xₙ₊₁"]
    else:
        titulos = ["Iter.", "xₙ₋₁ (anterior)", "xₙ (actual)", "f(xₙ₋₁)", "f(xₙ)", "xₙ₊₁ (nueva)"]
    titulos += ["Ea = |xₙ₊₁ − xₙ|", "Residuo |f(xₙ₊₁)|"]
    extra = criterio in ("relativo", "porcentual")
    if extra:
        titulos.append(NOMBRE_ERROR[criterio])
    resaltadas = {"absoluto": {"Ea = |xₙ₊₁ − xₙ|"}, "residuo": {"Residuo |f(xₙ₊₁)|"},
                  "ambos": {"Ea = |xₙ₊₁ − xₙ|", "Residuo |f(xₙ₊₁)|"}}.get(criterio, {NOMBRE_ERROR[criterio]})
    cabeza = "".join(f'<th class="{"criterio" if t in resaltadas else ""}">{t}</th>' for t in titulos)
    fuerte = 'style="color:#1d1d1f; font-weight:800"'

    def valor(v, clase_si_signo=True):
        clase = clase_signo(v) if clase_si_signo else ""
        return f'<td class="{clase}">{con_signo(v, d) if clase_si_signo else numero(v, d)}</td>'

    filas = []
    for it in r["iteraciones"]:
        k = it["iteracion"]
        clases = ("actual " if k == actual else "") + ("final" if k == r["total_iteraciones"] else "")
        if newton:
            celdas = [f"<td>{it['n']}</td>", f"<td>{numero(it['x'], d)}</td>", valor(it["fx"]), valor(it["dfx"])]
        else:
            celdas = [f"<td>{k}</td>", f"<td>{numero(it['x_anterior'], d)}</td>", f"<td>{numero(it['x'], d)}</td>",
                      valor(it["f_anterior"]), valor(it["fx"])]
        celdas.append(f"<td><b>{numero(it['x_nuevo'], d)}</b></td>")
        for titulo, v in (("Ea = |xₙ₊₁ − xₙ|", it["error_absoluto"]), ("Residuo |f(xₙ₊₁)|", it["residuo"])):
            celdas.append(f'<td {fuerte if titulo in resaltadas else ""}>{numero(v, d)}</td>')
        if extra:
            celdas.append(f"<td {fuerte}>{numero(it['error'], d)}</td>")
        filas.append(f'<tr id="{prefijo}-iteracion-{k}" class="{clases}" '
                     f'onclick="emitEvent(\'{prefijo}_fila\', {k})">{"".join(celdas)}</tr>')
    return f'<table class="tabla clic"><thead><tr>{cabeza}</tr></thead><tbody>{"".join(filas)}</tbody></table>'
