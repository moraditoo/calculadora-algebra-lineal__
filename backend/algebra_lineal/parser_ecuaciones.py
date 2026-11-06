# backend/algebra_lineal/parser_ecuaciones.py
import re
from fractions import Fraction
from .gauss import parse_frac

def parse_ecuaciones(texto_ecuaciones):
    lineas = [l.strip() for l in texto_ecuaciones.strip().split('\n') if l.strip()]
    if not lineas:
        raise ValueError("No se ingresaron ecuaciones.")

    # Reconocer nombres de variables (ej. x, y, z o x1, x2)
    vars_encontradas = set()
    patron_var = re.compile(r'([a-zA-Z]+[0-9]*)')

    for linea in lineas:
        partes = linea.split('=')
        if len(partes) != 2:
            raise ValueError(f"La ecuación '{linea}' debe contener exactamente un signo '='.")
        izq = partes[0]
        coincidencias = patron_var.findall(izq)
        for c in coincidencias:
            vars_encontradas.add(c)

    lista_vars = sorted(list(vars_encontradas), key=lambda x: (len(x), x))
    if not lista_vars:
        raise ValueError("No se detectaron variables válidas en las ecuaciones.")

    matriz = []
    for linea in lineas:
        izq, der = linea.split('=')
        b_val = parse_frac(der.strip())

        # Descomponer términos por signos + o -
        tokens = re.findall(r'[\+\-]?[^\+\-]+', izq.replace(" ", ""))
        coefs = {v: Fraction(0) for v in lista_vars}

        for token in tokens:
            m = re.match(r'^([\+\-]?[0-9\./]*)([a-zA-Z]+[0-9]*)$', token)
            if m:
                coef_str, v_nom = m.groups()
                if v_nom in coefs:
                    if coef_str in ("", "+"):
                        val = Fraction(1)
                    elif coef_str == "-":
                        val = Fraction(-1)
                    else:
                        val = parse_frac(coef_str)
                    coefs[v_nom] += val
            else:
                # Constante en el lado izquierdo
                try:
                    c_val = parse_frac(token)
                    b_val -= c_val
                except:
                    pass

        fila = [coefs[v] for v in lista_vars] + [b_val]
        matriz.append(fila)

    return matriz, len(lineas), len(lista_vars), lista_vars