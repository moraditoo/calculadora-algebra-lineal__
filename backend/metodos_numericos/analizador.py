# backend/metodos_numericos/analizador.py
# Convierte una funcion escrita tal cual en notacion matematica, por ejemplo
#   x^4 - 5x^3 + 0.5x^2 - 11x + 10      e^(-x) - x      ln x      2sen(x) + |x|
# en una funcion de Python evaluable. No usa eval() ni ninguna libreria que
# resuelva la ecuacion: solo se construye y recorre un arbol de la expresion.
import math
import re

FUNCIONES = {
    "sen": math.sin, "sin": math.sin, "cos": math.cos, "tan": math.tan, "tg": math.tan,
    "sec": lambda v: 1 / math.cos(v), "csc": lambda v: 1 / math.sin(v),
    "cot": lambda v: 1 / math.tan(v), "ctg": lambda v: 1 / math.tan(v),
    "arcsen": math.asin, "arcsin": math.asin, "asin": math.asin,
    "arccos": math.acos, "acos": math.acos,
    "arctan": math.atan, "arctg": math.atan, "atan": math.atan,
    "senh": math.sinh, "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "exp": math.exp, "ln": math.log, "log": math.log10, "log10": math.log10, "log2": math.log2,
    "sqrt": math.sqrt, "raiz": math.sqrt, "cbrt": math.cbrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}

# Nombres ordenados de mayor a menor longitud: "exp" se reconoce antes que "e"
_NOMBRES = sorted(list(FUNCIONES) + list(CONSTANTES), key=len, reverse=True)

_SUPERINDICES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_PRECEDENCIA = {"+": 1, "-": 1, "*": 2, "/": 2}


class ErrorFuncion(ValueError):
    """Error de escritura en la funcion, con la posicion donde ocurrio."""


def normalizar(texto):
    """Limpia el texto para que el analizador acepte la escritura habitual de clase."""
    if not texto or not texto.strip():
        raise ErrorFuncion("Escriba una función, por ejemplo: x^4 - 5x^3 + 0.5x^2 - 11x + 10")
    t = texto.strip().lower()
    # Se permite escribir "f(x) = ..." o "y = ..."
    t = re.sub(r"^\s*(f\s*\(\s*x\s*\)|y)\s*=", "", t)
    for viejo, nuevo in (("−", "-"), ("–", "-"), ("—", "-"), ("×", "*"), ("·", "*"), ("∙", "*"),
                         ("÷", "/"), ("**", "^"), ("√", "sqrt"), ("π", "pi"),
                         ("[", "("), ("]", ")"), ("{", "("), ("}", ")")):
        t = t.replace(viejo, nuevo)
    # Superindices: x² -> x^2,  x⁻¹ -> x^-1
    t = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", lambda m: "^" + m.group(0).translate(_SUPERINDICES), t)
    # Coma decimal entre digitos: 0,5 -> 0.5
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    if "=" in t:
        raise ErrorFuncion("Escriba solo la expresión de f(x); la ecuación se iguala a cero automáticamente.")
    return t


def tokenizar(t):
    tokens = []
    i = 0
    while i < len(t):
        c = t[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == "." and i + 1 < len(t) and t[i + 1].isdigit()):
            j = i
            while j < len(t) and (t[j].isdigit() or t[j] == "."):
                j += 1
            lexema = t[i:j]
            if lexema.count(".") > 1:
                raise ErrorFuncion(f"Número mal escrito '{lexema}' en la posición {i + 1}.")
            tokens.append(("num", float(lexema), lexema))
            i = j
        elif c in "+-*/^()|":
            tokens.append(("op", c))
            i += 1
        elif c.isalpha():
            nombre = next((n for n in _NOMBRES if t.startswith(n, i)), None)
            if nombre:
                tipo = "func" if nombre in FUNCIONES else "const"
                tokens.append((tipo, nombre))
                i += len(nombre)
            elif c == "x":
                tokens.append(("var",))
                i += 1
            else:
                raise ErrorFuncion(f"Símbolo desconocido '{c}' en la posición {i + 1}. La variable debe ser x.")
        else:
            raise ErrorFuncion(f"Carácter no permitido '{c}' en la posición {i + 1}.")
    if not tokens:
        raise ErrorFuncion("La función está vacía.")
    return tokens


class _Analizador:
    """
    Descenso recursivo con esta gramatica (de menor a mayor prioridad):
      expresion -> termino (('+' | '-') termino)*
      termino   -> unario (('*' | '/' | multiplicacion implicita) unario)*
      unario    -> ('+' | '-') unario | potencia
      potencia  -> primario ('^' unario)?          (asociativa a la derecha)
      primario  -> numero | x | constante | funcion argumento | '(' expresion ')' | '|' expresion '|'
    El arbol resultante se guarda en tuplas: ("num", v, texto), ("x",), ("const", nombre),
    ("neg", a), ("bin", op, a, b, implicita), ("func", nombre, a), ("abs", a).
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.dentro_abs = 0

    def ver(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def es_op(self, simbolo):
        tok = self.ver()
        return tok is not None and tok[0] == "op" and tok[1] == simbolo

    def consumir(self):
        tok = self.ver()
        self.pos += 1
        return tok

    def analizar(self):
        arbol = self.expresion()
        if self.ver() is not None:
            raise ErrorFuncion(f"Sobra '{self._texto(self.ver())}' al final de la función.")
        return arbol

    def expresion(self):
        nodo = self.termino()
        while self.es_op("+") or self.es_op("-"):
            op = self.consumir()[1]
            nodo = ("bin", op, nodo, self.termino(), False)
        return nodo

    def _inicia_primario(self):
        # Permite la multiplicacion implicita: 5x, 2(x+1), x sen(x), (x-1)(x+2)
        tok = self.ver()
        if tok is None:
            return False
        if tok[0] in ("num", "var", "const", "func"):
            return True
        return tok[0] == "op" and tok[1] == "("

    def termino(self):
        nodo = self.unario()
        while True:
            if self.es_op("*") or self.es_op("/"):
                op = self.consumir()[1]
                nodo = ("bin", op, nodo, self.unario(), False)
            elif self._inicia_primario():
                nodo = ("bin", "*", nodo, self.potencia(), True)
            else:
                return nodo

    def unario(self):
        if self.es_op("-"):
            self.consumir()
            return ("neg", self.unario())
        if self.es_op("+"):
            self.consumir()
            return self.unario()
        return self.potencia()

    def potencia(self):
        base = self.primario()
        if self.es_op("^"):
            self.consumir()
            return ("bin", "^", base, self.unario(), False)
        return base

    def primario(self):
        tok = self.consumir()
        if tok is None:
            raise ErrorFuncion("La función termina de forma incompleta (falta un operando).")
        tipo = tok[0]
        if tipo == "num":
            return ("num", tok[1], tok[2])
        if tipo == "var":
            return ("x",)
        if tipo == "const":
            return ("const", tok[1])
        if tipo == "func":
            # Con parentesis: ln(x), y sen(x)^2 = (sen x)^2.  Sin parentesis: ln x, sen x^2 = sen(x^2),
            # sen 2x = sen(2x).  Potencia de la funcion: sen^2 x = sen²x = (sen x)^2
            exponente = None
            if self.es_op("^"):
                self.consumir()
                exponente = self.unario() if self.es_op("(") or self.es_op("-") else self.primario()
            if self.ver() is None:
                raise ErrorFuncion(f"Falta el argumento de {tok[1]}.")
            if self.es_op("("):
                argumento = self.primario()
            else:
                argumento = self.potencia()
                # "sen 2x", "cos πx": el argumento sigue mientras haya numeros, x o constantes pegados
                while self.ver() is not None and self.ver()[0] in ("num", "var", "const"):
                    argumento = ("bin", "*", argumento, self.potencia(), True)
            nodo = ("func", tok[1], argumento)
            return ("bin", "^", nodo, exponente, False) if exponente is not None else nodo
        if tok == ("op", "("):
            nodo = self.expresion()
            if not self.es_op(")"):
                raise ErrorFuncion("Falta cerrar un paréntesis ')'.")
            self.consumir()
            return nodo
        if tok == ("op", "|") and not self.dentro_abs:
            self.dentro_abs += 1
            nodo = self.expresion()
            self.dentro_abs -= 1
            if not self.es_op("|"):
                raise ErrorFuncion("Falta cerrar el valor absoluto '|'.")
            self.consumir()
            return ("abs", nodo)
        raise ErrorFuncion(f"No se esperaba '{self._texto(tok)}' en esa posición.")

    @staticmethod
    def _texto(tok):
        return tok[2] if tok[0] == "num" else (tok[1] if len(tok) > 1 else "x")


def _potencia(base, exponente):
    if base == 0 and exponente < 0:
        raise ZeroDivisionError("0 elevado a un exponente negativo")
    if exponente == int(exponente) and abs(exponente) <= 1000:
        return base ** int(exponente)
    # math.pow lanza ValueError con base negativa y exponente fraccionario (resultado complejo)
    return math.pow(base, exponente)


def _compilar(nodo):
    """Transforma el arbol en una cadena de funciones de Python (cierres)."""
    tipo = nodo[0]
    if tipo == "num":
        valor = nodo[1]
        return lambda x: valor
    if tipo == "x":
        return lambda x: x
    if tipo == "const":
        valor = CONSTANTES[nodo[1]]
        return lambda x: valor
    if tipo == "neg":
        a = _compilar(nodo[1])
        return lambda x: -a(x)
    if tipo == "abs":
        a = _compilar(nodo[1])
        return lambda x: abs(a(x))
    if tipo == "func":
        fn = FUNCIONES[nodo[1]]
        a = _compilar(nodo[2])
        return lambda x: fn(a(x))
    op, a, b = nodo[1], _compilar(nodo[2]), _compilar(nodo[3])
    if op == "+":
        return lambda x: a(x) + b(x)
    if op == "-":
        return lambda x: a(x) - b(x)
    if op == "*":
        return lambda x: a(x) * b(x)
    if op == "/":
        return lambda x: a(x) / b(x)
    return lambda x: _potencia(a(x), b(x))


# ----------------------------------------------------------------------
# Version en JavaScript del mismo arbol: la usa la grafica interactiva del
# navegador para dibujar f(x) en cualquier zoom sin pedirle puntos al servidor.
# Solo contiene numeros, x y funciones de la lista: nada de lo escrito pasa tal cual.
# Las funciones fuera de su dominio dan NaN y la grafica no dibuja ese tramo
# (igual que evaluar() devuelve None).
# ----------------------------------------------------------------------
_JS_FUNC = {
    "sen": "Math.sin", "sin": "Math.sin", "cos": "Math.cos", "tan": "Math.tan", "tg": "Math.tan",
    "sec": "F.sec", "csc": "F.csc", "cot": "F.cot", "ctg": "F.cot",
    "arcsen": "Math.asin", "arcsin": "Math.asin", "asin": "Math.asin",
    "arccos": "Math.acos", "acos": "Math.acos",
    "arctan": "Math.atan", "arctg": "Math.atan", "atan": "Math.atan",
    "senh": "Math.sinh", "sinh": "Math.sinh", "cosh": "Math.cosh", "tanh": "Math.tanh",
    "exp": "Math.exp", "ln": "Math.log", "log": "Math.log10", "log10": "Math.log10", "log2": "Math.log2",
    "sqrt": "Math.sqrt", "raiz": "Math.sqrt", "cbrt": "Math.cbrt", "abs": "Math.abs",
}
_JS_CONST = {"pi": "Math.PI", "e": "Math.E"}


def _js(nodo):
    tipo = nodo[0]
    if tipo == "num":
        valor = float(nodo[1])
        return f"({valor!r})" if math.isfinite(valor) else "Infinity"
    if tipo == "x":
        return "x"
    if tipo == "const":
        return _JS_CONST[nodo[1]]
    if tipo == "neg":
        return f"(-{_js(nodo[1])})"
    if tipo == "abs":
        return f"Math.abs({_js(nodo[1])})"
    if tipo == "func":
        return f"{_JS_FUNC[nodo[1]]}({_js(nodo[2])})"
    op, a, b = nodo[1], _js(nodo[2]), _js(nodo[3])
    if op == "^":
        return f"F.pot({a}, {b})"
    return f"({a} {op} {b})"


# ----------------------------------------------------------------------
# Representacion bonita (mathtext de matplotlib) para mostrar la funcion
# tal como se escribe en el cuaderno.
# ----------------------------------------------------------------------
_MATHTEXT_FUNC = {
    "sen": r"\mathrm{sen}", "sin": r"\sin", "cos": r"\cos", "tan": r"\tan", "tg": r"\mathrm{tg}",
    "sec": r"\sec", "csc": r"\csc", "cot": r"\cot", "ctg": r"\mathrm{ctg}",
    "arcsen": r"\mathrm{arcsen}", "arcsin": r"\arcsin", "asin": r"\arcsin",
    "arccos": r"\arccos", "acos": r"\arccos", "arctan": r"\arctan", "arctg": r"\arctan", "atan": r"\arctan",
    "senh": r"\mathrm{senh}", "sinh": r"\sinh", "cosh": r"\cosh", "tanh": r"\tanh",
    "exp": r"\exp", "ln": r"\ln", "log": r"\log", "log10": r"\log_{10}", "log2": r"\log_{2}",
}


def _mt(nodo):
    """Devuelve (texto_mathtext, prioridad) del nodo."""
    tipo = nodo[0]
    if tipo == "num":
        return nodo[2], 5
    if tipo == "x":
        return "x", 5
    if tipo == "const":
        return (r"\pi " if nodo[1] == "pi" else "e"), 5  # el espacio evita "\pix" al multiplicar por x
    if tipo == "abs":
        return r"\left|" + _mt(nodo[1])[0] + r"\right|", 5
    if tipo == "func":
        interno = _mt(nodo[2])[0]
        if nodo[1] in ("sqrt", "raiz"):
            return r"\sqrt{" + interno + "}", 5
        if nodo[1] == "cbrt":
            return r"\sqrt[3]{" + interno + "}", 5
        if nodo[1] == "abs":
            return r"\left|" + interno + r"\right|", 5
        return _MATHTEXT_FUNC[nodo[1]] + r"\left(" + interno + r"\right)", 5
    if tipo == "neg":
        texto, prio = _mt(nodo[1])
        return "-" + (texto if prio >= 3 else r"\left(" + texto + r"\right)"), 3

    op = nodo[1]
    (ti, pi_), (td, pd) = _mt(nodo[2]), _mt(nodo[3])
    envolver = lambda t: r"\left(" + t + r"\right)"
    if op == "^":
        base = ti if pi_ >= 5 and nodo[2][0] != "func" else envolver(ti)
        return base + "^{" + td + "}", 4
    if op == "/":
        return r"\frac{" + ti + "}{" + td + "}", 5
    if op == "*":
        izq = ti if pi_ >= 2 else envolver(ti)
        der = td if pd >= 3 and nodo[3][0] != "neg" else envolver(td)
        # Multiplicacion implicita: se respeta "5x^3" tal cual se escribio
        return izq + (r"\,\cdot\," if not nodo[4] or nodo[3][0] == "num" else "") + der, 2
    der = td if (pd > 1 and nodo[3][0] != "neg") else envolver(td)
    simbolo = " + " if op == "+" else " - "
    return ti + simbolo + der, 1


# ----------------------------------------------------------------------
# Lectura de LaTeX: el editor matematico de la interfaz entrega la funcion
# en LaTeX (x^{10}, \frac{1}{x}, e^{-x}, \ln\left(x\right)) y aqui se pasa
# a la notacion de texto que entiende el analizador.
# ----------------------------------------------------------------------
_LATEX_DIRECTOS = {
    "cdot": "*", "times": "*", "ast": "*", "div": "/", "pi": "pi", "exponentialE": "e",
    "vert": "|", "lvert": "|", "rvert": "|", "mid": "|", "lbrack": "(", "rbrack": ")",
    "lbrace": "(", "rbrace": ")", "lparen": "(", "rparen": ")",
}
_LATEX_ESPACIOS = {",", ";", ":", "!", " ", "quad", "qquad", "displaystyle", "textstyle", "limits"}
_LATEX_TEXTO = {"operatorname", "mathrm", "text", "mathit", "textrm", "mathbf"}


def latex_a_texto(latex):
    s = latex.strip()
    pos = 0

    def comando():
        nonlocal pos
        inicio = pos
        if pos < len(s) and not s[pos].isalpha():
            pos += 1
            return s[inicio:pos]
        while pos < len(s) and s[pos].isalpha():
            pos += 1
        return s[inicio:pos]

    def grupo():
        """Lee {…} o un solo simbolo y devuelve su traduccion."""
        nonlocal pos
        while pos < len(s) and s[pos] == " ":
            pos += 1
        if pos >= len(s):
            raise ErrorFuncion("Falta un valor después de un exponente o una fracción.")
        if s[pos] == "{":
            pos += 1
            texto = secuencia("}")
            pos += 1
            return texto
        if s[pos] == "\\":
            pos += 1
            return traducir(comando())
        pos += 1
        return s[pos - 1]

    def traducir(nombre):
        nonlocal pos
        if nombre == "frac" or nombre == "dfrac" or nombre == "tfrac":
            numerador, denominador = grupo(), grupo()
            return f"(({numerador})/({denominador}))"
        if nombre == "sqrt":
            indice = None
            if pos < len(s) and s[pos] == "[":
                fin = s.index("]", pos)
                indice, pos = s[pos + 1:fin], fin + 1
            radicando = grupo()
            if indice in (None, "", "2"):
                return f"sqrt({radicando})"
            if indice == "3":
                return f"cbrt({radicando})"
            return f"(({radicando})^(1/({indice})))"
        if nombre in ("left", "right", "mleft", "mright", "bigl", "bigr", "Bigl", "Bigr", "big", "Big"):
            # El delimitador es el siguiente simbolo: ( ) [ ] | . o un comando como \vert
            delimitador = grupo()
            return "" if delimitador == "." else {"[": "(", "]": ")"}.get(delimitador, delimitador)
        if nombre in _LATEX_DIRECTOS:
            return _LATEX_DIRECTOS[nombre]
        if nombre in _LATEX_ESPACIOS:
            return " "
        if nombre in _LATEX_TEXTO:
            return grupo()
        if nombre == "placeholder":
            grupo()
            return ""
        if nombre in FUNCIONES or nombre in ("ln", "log", "exp"):
            return nombre
        raise ErrorFuncion(f"No se reconoce el símbolo '{nombre}' en la función.")

    def secuencia(cierre=None):
        nonlocal pos
        partes = []
        while pos < len(s):
            c = s[pos]
            if cierre and c == cierre:
                break
            if c == "\\":
                pos += 1
                partes.append(traducir(comando()))
            elif c == "^":
                pos += 1
                partes.append(f"^({grupo()})")
            elif c == "_":
                pos += 1
                base = grupo()
                # Solo se permite el subindice de log: \log_{10}, \log_2
                if partes and partes[-1] == "log" and base in ("2", "10"):
                    partes[-1] = "log" + base
                else:
                    raise ErrorFuncion("Los subíndices no se usan en f(x) (solo log₂ o log₁₀).")
            elif c == "{":
                pos += 1
                partes.append("(" + secuencia("}") + ")")
                pos += 1
            else:
                partes.append(c)
                pos += 1
        return "".join(partes)

    texto = secuencia()
    # 0{,}5 -> 0,5 (coma decimal escrita en el editor)
    return texto.replace("(,)", ",")


class Funcion:
    """Funcion lista para evaluar, con su texto original y su version bonita."""

    def __init__(self, texto, latex=False):
        self.original = texto.strip()
        if latex:
            texto = latex_a_texto(texto)
        self.texto = texto
        self.normalizada = normalizar(texto)
        self.arbol = _Analizador(tokenizar(self.normalizada)).analizar()
        self._f = _compilar(self.arbol)
        self.mathtext = "$f(x) = " + _mt(self.arbol)[0] + "$"
        self.javascript = _js(self.arbol)  # expresion en x para la grafica interactiva

    def __call__(self, x):
        return self._f(x)

    def evaluar(self, x):
        """Evalua f(x); si no esta definida (ln de negativo, division por cero...) devuelve None."""
        try:
            y = self._f(float(x))
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        if isinstance(y, complex) or math.isnan(y) or math.isinf(y):
            return None
        return float(y)
