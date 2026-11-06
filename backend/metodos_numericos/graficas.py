# backend/metodos_numericos/graficas.py
# Graficas propias del metodo de biseccion hechas con matplotlib, con fondo
# transparente para integrarse con el vidrio blanco de la interfaz.
# Se entregan como SVG (nitidas a cualquier tamano).
import base64
import io
import math

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.transforms import blended_transform_factory

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "svg.fonttype": "path",
    "axes.unicode_minus": True,
})

TINTA = "#3a3a3c"      # curva y textos
SUAVE = "#a1a1a6"      # ejes y rejilla
ACENTO = "#1d1d1f"     # lo importante: raiz, intervalo elegido
POSITIVO = "#2e7d5b"   # f(x) > 0
NEGATIVO = "#b3261e"   # f(x) < 0
BLANCO = "#ffffff"
MUESTRAS = 1400


def a_svg(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.12)
    return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _ejes(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("bottom", "left"):
        ax.spines[lado].set_color(SUAVE)
    ax.tick_params(colors=TINTA, labelsize=9, length=3)
    ax.grid(True, color=SUAVE, alpha=0.25, linewidth=0.8)
    ax.xaxis.label.set_color(TINTA)
    ax.yaxis.label.set_color(TINTA)
    ax.set_facecolor("none")


def _color_signo(y):
    return POSITIVO if y > 0 else NEGATIVO


def _muestrear(f, x_min, x_max, n=MUESTRAS):
    xs = [x_min + (x_max - x_min) * i / (n - 1) for i in range(n)]
    ys = [f.evaluar(x) for x in xs]
    return xs, [math.nan if y is None else y for y in ys]


def _limites_y(ys):
    """Limites robustos: si hay asintotas o valores enormes se recorta a la zona util."""
    finitos = sorted(y for y in ys if not math.isnan(y))
    if not finitos:
        return -1, 1
    bajo, alto = finitos[0], finitos[-1]
    q05 = finitos[int(0.05 * (len(finitos) - 1))]
    q95 = finitos[int(0.95 * (len(finitos) - 1))]
    if (alto - bajo) > 25 * max(q95 - q05, 1e-12):
        extra = 0.6 * max(q95 - q05, 1e-9)
        bajo, alto = q05 - extra, q95 + extra
    bajo, alto = min(bajo, 0), max(alto, 0)
    if alto - bajo < 1e-15:
        bajo, alto = bajo - 1, alto + 1
    margen = 0.1 * (alto - bajo)
    return bajo - margen, alto + margen


def _sin_saltos(ys, bajo, alto):
    """Evita dibujar una linea vertical falsa al cruzar una asintota."""
    salida = list(ys)
    for i in range(1, len(salida)):
        if not math.isnan(salida[i]) and not math.isnan(salida[i - 1]):
            if abs(salida[i] - salida[i - 1]) > 0.75 * (alto - bajo):
                salida[i] = math.nan
    return salida


def _curva(ax, f, x_min, x_max, muestras=MUESTRAS):
    xs, ys = _muestrear(f, x_min, x_max, muestras)
    bajo, alto = _limites_y(ys)
    ax.plot(xs, _sin_saltos(ys, bajo, alto), color=TINTA, linewidth=2.3, solid_capstyle="round", zorder=3)
    ax.axhline(0, color=TINTA, linewidth=1, alpha=0.6, zorder=2)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(bajo, alto)


def _etiqueta(ax, x, y, texto, desplazamiento=(14, 18)):
    ax.annotate(
        texto, (x, y), xytext=desplazamiento, textcoords="offset points",
        color=ACENTO, fontsize=9.5, fontweight="bold", zorder=9,
        bbox={"boxstyle": "round,pad=0.5,rounding_size=0.9", "fc": BLANCO, "ec": SUAVE, "lw": 0.8},
        arrowprops={"arrowstyle": "-", "color": TINTA, "lw": 1},
    )


def _punto_raiz(ax, x, y):
    ax.scatter([x], [y], s=260, color=ACENTO, alpha=0.12, linewidths=0, zorder=7)
    ax.scatter([x], [y], s=80, color=ACENTO, edgecolors=BLANCO, linewidths=1.8, zorder=8)


# ----------------------------------------------------------------------
def formula(mathtext, color=TINTA):
    """La funcion escrita con notacion matematica, como en el cuaderno."""
    with matplotlib.rc_context({"mathtext.fontset": "cm"}):
        fig = Figure(figsize=(0.2, 0.2), dpi=100)
        fig.text(0, 0, mathtext, fontsize=22, color=color)
        try:
            return a_svg(fig)
        except ValueError:
            return None


def grafica_funcion(f, tabulacion, intervalo_activo=None, raiz=None):
    """Grafica general: sirve para ver en que intervalos f(x) cambia de signo."""
    fig = Figure(figsize=(9.6, 4.6), dpi=100)
    ax = fig.add_subplot()
    _ejes(ax)
    _curva(ax, f, tabulacion["x_min"], tabulacion["x_max"])
    bajo, alto = ax.get_ylim()

    mezcla = blended_transform_factory(ax.transData, ax.transAxes)
    for iv in tabulacion["intervalos"]:
        activo = iv["numero"] == intervalo_activo
        ax.axvspan(iv["a"], iv["b"], color=TINTA, alpha=0.12 if activo else 0.05, linewidth=0, zorder=1)
        for borde in (iv["a"], iv["b"]):
            ax.axvline(borde, color=TINTA, alpha=0.6 if activo else 0.25, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.text((iv["a"] + iv["b"]) / 2, 0.965, f"I{iv['numero']}", transform=mezcla, ha="center", va="top",
                color=ACENTO if activo else SUAVE, fontsize=9, fontweight="bold",
                bbox={"boxstyle": "round,pad=0.35,rounding_size=0.7", "ec": TINTA if activo else SUAVE,
                      "fc": BLANCO, "lw": 1.4 if activo else 0.8})
        for x, y in ((iv["a"], iv["fa"]), (iv["b"], iv["fb"])):
            if bajo <= y <= alto:
                ax.scatter([x], [y], s=36, color=_color_signo(y), edgecolors=BLANCO, linewidths=1.2, zorder=5)

    # Asintotas: f cambia de signo pero no hay raiz (no se ofrecen como intervalo)
    for d in tabulacion.get("discontinuidades", []):
        ax.axvline(d["x"], color=NEGATIVO, alpha=0.55, linewidth=1.2, linestyle=(0, (2, 3)), zorder=2)
        ax.text(d["x"], 0.035, "asíntota", transform=mezcla, ha="center", va="bottom", rotation=90,
                color=NEGATIVO, fontsize=8, alpha=0.8,
                bbox={"boxstyle": "round,pad=0.25", "fc": BLANCO, "ec": "none", "alpha": 0.8})

    for x in tabulacion["raices_exactas"]:
        _punto_raiz(ax, x, 0)
        _etiqueta(ax, x, 0, f"x = {x:.6g} (exacta)")
    if raiz is not None:
        _punto_raiz(ax, raiz, 0)
        _etiqueta(ax, raiz, 0, f"raíz ≈ {raiz:.8f}")

    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    return a_svg(fig)


def grafica_iteracion(f, it, secante=False):
    """Acercamiento a una sola iteracion: intervalo [a, b], el punto c y signos.
    Con secante=True (regla falsa) se dibuja la recta que une (a, f(a)) con (b, f(b)) y su corte con el eje x."""
    a, b, c = it["a"], it["b"], it["c"]
    ancho = b - a
    fig = Figure(figsize=(7.4, 3.9), dpi=100)
    ax = fig.add_subplot()
    _ejes(ax)
    _curva(ax, f, a - 0.45 * ancho, b + 0.45 * ancho, 500)
    if secante:
        _recta_falsa_posicion(ax, it)

    ax.axvspan(a, b, color=TINTA, alpha=0.05, linewidth=0, zorder=1)
    nuevo = (a, c) if it["subintervalo"] == "[a, c]" else (c, b)
    ax.axvspan(*nuevo, facecolor=(0.23, 0.23, 0.24, 0.08), edgecolor=(0.23, 0.23, 0.24, 0.3),
               linewidth=0, zorder=1, hatch="///")
    for x, y, nombre in ((a, it["fa"], "a"), (b, it["fb"], "b")):
        ax.axvline(x, color=SUAVE, linewidth=1, linestyle=(0, (4, 3)))
        ax.scatter([x], [y], s=60, color=_color_signo(y), edgecolors=BLANCO, linewidths=1.4, zorder=6)
        ax.annotate(nombre, (x, 0), xytext=(0, -16), textcoords="offset points", ha="center",
                    color=TINTA, fontsize=10, fontweight="bold")
    ax.axvline(c, color=ACENTO, alpha=0.6, linewidth=1.2)
    _punto_raiz(ax, c, it["fc"])
    # La etiqueta va hacia arriba si f(c) < 0 y hacia abajo si f(c) > 0, lejos de la curva
    _etiqueta(ax, c, it["fc"], f"c = {c:.8f}", (-60, 30) if it["fc"] <= 0 else (-60, -40))
    ax.ticklabel_format(useOffset=False, axis="x")
    ax.locator_params(axis="x", nbins=5)
    return a_svg(fig)


def _recta_falsa_posicion(ax, it):
    """Recta de la regla falsa: une (a, f(a)) y (b, f(b)) y corta el eje x en c."""
    a, b, c = it["a"], it["b"], it["c"]
    fa, fb = it.get("fa_formula", it["fa"]), it.get("fb_formula", it["fb"])
    ax.plot([a, b], [fa, fb], color=ACENTO, linewidth=1.6, linestyle=(0, (6, 3)), alpha=0.85, zorder=4)
    # En la variante modificada la recta sale de f/2: se marca ese punto aparte
    for x, usado, real in ((a, fa, it["fa"]), (b, fb, it["fb"])):
        if usado != real:
            ax.scatter([x], [usado], s=46, facecolors=BLANCO, edgecolors=_color_signo(usado), linewidths=1.6, zorder=6)
    ax.scatter([c], [0], s=46, marker="D", color=ACENTO, edgecolors=BLANCO, linewidths=1.2, zorder=7)
    ax.vlines(c, min(0, it["fc"]), max(0, it["fc"]), color=ACENTO, linewidth=1, linestyle=(0, (2, 2)), zorder=4)


def grafica_iteraciones(f, resultado):
    """Escalera de intervalos: cada fila es [a_i, b_i] de la iteracion i."""
    iteraciones = resultado["iteraciones"]
    a0, b0 = resultado["a_inicial"], resultado["b_inicial"]
    total = len(iteraciones)
    fig = Figure(figsize=(9.6, max(3.2, 0.26 * total + 1.6)), dpi=100)
    ax = fig.add_subplot()
    _ejes(ax)
    ax.grid(False, axis="y")

    for it in iteraciones:
        k = it["iteracion"]
        final = k == total
        ax.hlines(k, it["a"], it["b"], color=ACENTO if final else TINTA, linewidth=4 if final else 2.2,
                  alpha=1 if final else 0.3 + 0.5 * k / max(total, 1))
        ax.scatter([it["a"], it["b"]], [k, k], marker="|", s=70, color=TINTA, linewidths=1.3, zorder=4)
        ax.scatter([it["c"]], [k], s=60 if final else 24, color=ACENTO if final else _color_signo(it["fc"]),
                   edgecolors=BLANCO, linewidths=1.2, zorder=5)
    ax.axvline(resultado["raiz"], color=ACENTO, alpha=0.5, linewidth=1, linestyle=(0, (4, 3)))
    ancho = b0 - a0
    ax.set_xlim(a0 - 0.05 * ancho, b0 + 0.05 * ancho)
    ax.set_ylim(total + 0.8, 0.2)
    paso = max(1, math.ceil(total / 14))
    ax.set_yticks(list(range(1, total + 1, paso)))
    ax.set_ylabel("iteración")
    ax.set_xlabel("x")
    return a_svg(fig)


def grafica_error(resultado):
    """Como baja el error en cada iteracion (escala logaritmica) frente a la tolerancia E."""
    iteraciones = resultado["iteraciones"]
    fig = Figure(figsize=(9.6, 3.6), dpi=100)
    ax = fig.add_subplot()
    _ejes(ax)

    puntos = [(it["iteracion"], it["error"]) for it in iteraciones if it["error"] not in (None, 0)]
    if puntos:
        xs, ys = zip(*puntos)
        ax.plot(xs, ys, color=TINTA, linewidth=2.2, marker="o", markersize=5, markerfacecolor=BLANCO)
        ax.set_yscale("log")
        _punto_raiz(ax, xs[-1], ys[-1])
    ax.axhline(resultado["tolerancia"], color=TINTA, linewidth=1.4, linestyle=(0, (8, 4)))
    ax.annotate(f"E = {resultado['tolerancia']:g}", (1, resultado["tolerancia"]), xytext=(4, 6),
                textcoords="offset points", color=TINTA, fontsize=9, fontweight="bold",
                xycoords=("axes fraction", "data"), ha="right")
    ax.set_xlabel("iteración")
    ax.set_ylabel("error")
    ax.xaxis.get_major_locator().set_params(integer=True)
    return a_svg(fig)

