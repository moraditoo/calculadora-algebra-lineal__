# frontend/modulos/matrices/cofactores.py
# Dibuja la expansion por cofactores nivel por nivel (es recursiva, como el calculo).
from ...componentes import matriz_html
from ...formato import escapar


def nodo_html(nodo, nivel=0):
    if nodo["tipo"] == "1x1":
        return f'<div class="mono" style="font-weight:800">det = {escapar(nodo["det"])}</div>'

    if nodo["tipo"] == "2x2":
        # Diagonal principal en azul y secundaria con borde rojo
        diagonal = matriz_html(nodo["matriz"], estilo=lambda i, j: "media" if i == j else "borde", barras=True, compacta=True)
        return (
            f'<div class="fila" style="align-items:center; gap:10px">{diagonal}'
            f'<span class="mono" style="font-size:12.5px; font-weight:700">= '
            f'<span style="color:#1d1d1f">({escapar(nodo["a"])})({escapar(nodo["d"])})</span> − '
            f'<span style="color:#5f6368">({escapar(nodo["b"])})({escapar(nodo["c"])})</span> = '
            f'{escapar(nodo["ad"])} − ({escapar(nodo["bc"])}) = <b>{escapar(nodo["det"])}</b></span></div>'
        )

    linea = nodo["linea"]
    en_linea = (lambda i, j: i == linea["indice"]) if linea["tipo"] == "fila" else (lambda i, j: j == linea["indice"])
    partes = [
        '<div style="display:flex; flex-direction:column; gap:10px">',
        '<div class="fila" style="align-items:center; gap:12px">',
        matriz_html(nodo["matriz"], estilo=lambda i, j: "ambar" if en_linea(i, j) else "", barras=True, compacta=True),
        f'<span style="font-size:12px; font-weight:700; color:#5f6368">Submatriz {nodo["orden"]}×{nodo["orden"]}: se expande por la '
        f'<b style="color:#1d1d1f">{escapar(linea["tipo"])} {escapar(linea["original"])}</b> (la de más ceros)</span></div>',
        f'<div style="display:flex; flex-direction:column; gap:8px; {"padding-left:12px; border-left:2px solid rgba(0,0,0,0.08)" if nivel else ""}">',
    ]
    for t in nodo["terminos"]:
        partes.append(termino_html(nodo, t, nivel))
    partes.append("</div>")
    suma = " + ".join(f'({escapar(t["termino"])})' for t in nodo["terminos"] if not t["nulo"]) or "0"
    partes.append(f'<div class="aviso exito mono" style="font-weight:800">det = {suma} = {escapar(nodo["det"])}</div></div>')
    return "".join(partes)


def termino_html(nodo, t, nivel):
    def tachado(i, j):
        if i == t["pi"] and j == t["pj"]:
            return "ambar-fuerte"
        if i == t["pi"] or j == t["pj"]:
            return "tenue"
        return ""

    f, c = escapar(t["fila"]), escapar(t["col"])
    cabecera = (f'<div class="mono" style="font-size:11.5px; font-weight:800">a[{f},{c}]·C[{f},{c}] = '
                f'(−1)<sup>{t["pi"] + 1}+{t["pj"] + 1}</sup> · a[{f},{c}] · det(M[{f},{c}])</div>')
    if t["nulo"]:
        cuerpo = f'<div style="font-size:12px; color:#5f6368; font-weight:600">a[{f},{c}] = 0 → término nulo, se omite.</div>'
        return f'<div class="caja" style="opacity:.6; padding:12px">{cabecera}{cuerpo}</div>'

    menor = ""
    if t.get("menor") and t["menor"]["orden"] >= 2:
        menor = (f'<details class="desplegable"{" open" if nivel == 0 else ""} style="margin-top:6px">'
                 f'<summary>Calcular det(M[{f},{c}])</summary><div>{nodo_html(t["menor"], nivel + 1)}</div></details>')
    return (
        f'<div class="caja" style="padding:12px; display:flex; flex-direction:column; gap:8px">{cabecera}'
        f'<div class="fila" style="align-items:center; gap:8px">'
        f'{matriz_html(nodo["matriz"], estilo=tachado, barras=True, compacta=True)}'
        f'<span style="color:#9aa0a6; font-weight:800">→</span>'
        f'<span class="mono" style="font-size:11.5px; font-weight:700; color:#5f6368">M[{f},{c}] =</span>'
        f'{matriz_html(t["menor_matriz"], barras=True, compacta=True)}</div>'
        f'{menor}'
        f'<div class="mono" style="font-size:12.5px; font-weight:800">({escapar(t["signo"])}1)·({escapar(t["elemento"])})·'
        f'({escapar(t["det_menor"])}) = <span style="color:#1d1d1f">{escapar(t["termino"])}</span></div></div>'
    )
