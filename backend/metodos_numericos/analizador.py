# backend/metodos_numericos/analizador.py
# Convierte una funcion escrita tal cual en notacion matematica, por ejemplo
#   x^4 - 5x^3 + 0.5x^2 - 11x + 10      e^(-x) - x      ln x      2sen(x) + |x|
# en una funcion de Python evaluable. No usa eval() ni ninguna libreria que
# resuelva la ecuacion: solo se construye y recorre un arbol de la expresion.
import difflib
import math
import re

FUNCIONES = {
    "sen": math.sin, "sin": math.sin, "cos": math.cos, "tan": math.tan, "tg": math.tan,
    "sec": lambda v: 1 / math.cos(v), "csc": lambda v: 1 / math.sin(v),
    "cot": lambda v: 1 / math.tan(v), "ctg": lambda v: 1 / math.tan(v),
    "arcsen": math.asin, "arcsin": math.asin, "asin": math.asin,
    "arccos": math.acos, "acos": math.acos,
    "arctan": math.atan, "arctg": math.atan, "atan": math.atan,
    "arcsec": lambda v: math.acos(1 / v), "asec": lambda v: math.acos(1 / v),
    "arccsc": lambda v: math.asin(1 / v), "acsc": lambda v: math.asin(1 / v),
    "arccot": lambda v: math.pi / 2 - math.atan(v), "acot": lambda v: math.pi / 2 - math.atan(v),
    "arcctg": lambda v: math.pi / 2 - math.atan(v),
    "senh": math.sinh, "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh, "tgh": math.tanh,
    "sech": lambda v: 1 / math.cosh(v), "csch": lambda v: 1 / math.sinh(v), "coth": lambda v: 1 / math.tanh(v),
    "arcsenh": math.asinh, "arcsinh": math.asinh, "asinh": math.asinh, "argsenh": math.asinh,
    "arccosh": math.acosh, "acosh": math.acosh, "argcosh": math.acosh,
    "arctanh": math.atanh, "atanh": math.atanh, "argtanh": math.atanh,
    "arcsech": lambda v: math.acosh(1 / v), "asech": lambda v: math.acosh(1 / v),
    "arccsch": lambda v: math.asinh(1 / v), "acsch": lambda v: math.asinh(1 / v),
    "arccoth": lambda v: math.atanh(1 / v), "acoth": lambda v: math.atanh(1 / v),
    "exp": math.exp, "ln": math.log, "log": math.log10, "log10": math.log10, "log2": math.log2,
    "sqrt": math.sqrt, "raiz": math.sqrt, "cbrt": math.cbrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}

# Nombres ordenados de mayor a menor longitud: "exp" se reconoce antes que "e"
_NOMBRES = sorted(list(FUNCIONES) + list(CONSTANTES), key=len, reverse=True)

_SUPERINDICES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_PRECEDENCIA = {"+": 1, "-": 1, "*": 2, "/": 2}

# Notacion de funcion inversa del cuaderno: sen⁻¹ x = arcsen x, tan⁻¹ x = arctan x.
# (No es 1/tan x: para eso se escribe cot x o (tan x)⁻¹.)
_INVERSAS = {
    "sen": "arcsen", "sin": "arcsin", "cos": "arccos", "tan": "arctan", "tg": "arctg",
    "sec": "arcsec", "csc": "arccsc", "cot": "arccot", "ctg": "arcctg",
    "senh": "arcsenh", "sinh": "arcsinh", "cosh": "arccosh", "tanh": "arctanh", "tgh": "arctanh",
    "sech": "arcsech", "csch": "arccsch", "coth": "arccoth",
}

# Nombres que se suelen escribir y no son los de la lista: se sugiere el correcto
_ALIAS = {
    "seno": "sen", "coseno": "cos", "tangente": "tan", "secante": "sec", "cosecante": "csc",
    "cotangente": "cot", "logaritmo": "ln", "root": "sqrt",
    "sqr": "sqrt", "rad": "sqrt", "abs": "abs", "valor": "abs", "absoluto": "abs", "euler": "e",
    "arcoseno": "arcsen", "arcocoseno": "arccos", "arcotangente": "arctan", "tang": "tan",
}

# Marca de una casilla vacia del editor matematico (fraccion, exponente o raiz sin completar)
CASILLA_VACIA = "□"


class ErrorFuncion(ValueError):
    """Error de escritura en la funcion, con la posicion donde ocurrio."""


def normalizar(texto):
    """Limpia el texto para que el analizador acepte la escritura habitual de clase.
    Si queda un signo '=' (una ecuacion como sen(x) = −2x + 1) se conserva: Funcion la
    convierte en f(x) = 0 pasando todo al lado izquierdo."""
    if not texto or not texto.strip():
        raise ErrorFuncion("Escriba una función, por ejemplo: x^4 - 5x^3 + 0.5x^2 - 11x + 10")
    t = texto.strip().lower()
    # Se permite escribir "f(x) = ...", "f'(x) = ...", "y = ..." o "y' = ..."
    t = re.sub(r"^\s*(f\s*[′']?\s*\(\s*x\s*\)|y\s*[′']?)\s*=", "", t)
    # Simbolos de igualdad que pueden venir de otros programas
    for viejo in ("==", "≡", "＝"):
        t = t.replace(viejo, "=")
    for viejo, nuevo in (("−", "-"), ("–", "-"), ("—", "-"), ("×", "*"), ("·", "*"), ("∙", "*"),
                         ("÷", "/"), ("**", "^"), ("√", "sqrt"), ("π", "pi"),
                         ("[", "("), ("]", ")"), ("{", "("), ("}", ")")):
        t = t.replace(viejo, nuevo)
    # Superindices: x² -> x^2,  x⁻¹ -> x^-1
    t = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", lambda m: "^" + m.group(0).translate(_SUPERINDICES), t)
    # Coma decimal entre digitos: 0,5 -> 0.5
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    return t


def _sugerencia(palabra):
    """Nombre de funcion parecido a lo escrito: 'seno' -> 'sen', 'cso' -> 'cos', 'arctna' -> 'arctan'."""
    if palabra in _ALIAS:
        return _ALIAS[palabra]
    # Letras cambiadas de lugar: 'cso' -> 'cos', 'tna' -> 'tan'
    for nombre in FUNCIONES:
        if len(nombre) == len(palabra) and sorted(nombre) == sorted(palabra):
            return nombre
    parecidos = difflib.get_close_matches(palabra, list(FUNCIONES), n=1, cutoff=0.6)
    return parecidos[0] if parecidos else None


def _palabra_desconocida(t, i):
    """Mensaje para una letra o palabra que no es x, ni una constante, ni una funcion conocida."""
    inicio, fin = i, i
    while inicio > 0 and t[inicio - 1].isalpha():
        inicio -= 1
    while fin < len(t) and t[fin].isalpha():
        fin += 1
    completa, resto = t[inicio:fin], t[i:fin]
    for palabra in (completa, resto):
        sugerida = _sugerencia(palabra) if len(palabra) > 1 else None
        if sugerida and sugerida != palabra:
            return (f"No se reconoce '{palabra}'. ¿Quiso decir {sugerida}? Por ejemplo: "
                    f"{sugerida}(x)" if sugerida in FUNCIONES else f"No se reconoce '{palabra}'. ¿Quiso decir {sugerida}?")
    if len(resto) == 1:
        return (f"La letra '{resto}' (posición {i + 1}) no se puede usar: la única variable permitida es x. "
                "Si el ejercicio trae otra letra (y, a, k…), reemplácela por su valor numérico.")
    return (f"No se reconoce '{resto}' (posición {i + 1}). Use x como variable y funciones como sen, cos, tan, "
            "ln, log, sqrt o e^x; entre dos letras seguidas que no forman una función ponga '*'.")


def _revisar_agrupacion(t):
    """Revisa parentesis y barras de valor absoluto antes de analizar, para decir exactamente que falta."""
    profundidad = 0
    for i, c in enumerate(t):
        if c == "(":
            profundidad += 1
        elif c == ")":
            profundidad -= 1
            if profundidad < 0:
                raise ErrorFuncion(f"Sobra un paréntesis ')' en la posición {i + 1}: no tiene su '(' de apertura.")
    if profundidad == 1:
        raise ErrorFuncion("Falta cerrar un paréntesis: hay un '(' sin su ')'.")
    if profundidad > 1:
        raise ErrorFuncion(f"Falta cerrar {profundidad} paréntesis: hay {profundidad} '(' sin su ')'.")
    if t.count("|") % 2:
        raise ErrorFuncion("Falta una barra '|' del valor absoluto: se escriben en pares, como |x − 2|.")


def tokenizar(t):
    if CASILLA_VACIA in t:
        raise ErrorFuncion("Hay una casilla vacía (□) sin completar: llene el numerador, el denominador, el "
                           "exponente o la raíz que falta.")
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
                raise ErrorFuncion(_palabra_desconocida(t, i))
        elif c == "=":
            raise ErrorFuncion("La ecuación tiene más de un signo '='. Escriba una sola igualdad, "
                               "por ejemplo: sen(x) = -2x + 1")
        elif c == "°":
            raise ErrorFuncion("No se usan grados (°): las funciones trigonométricas trabajan en radianes "
                               "(30° se escribe pi/6, 90° se escribe pi/2).")
        elif c == ",":
            raise ErrorFuncion(f"Coma en la posición {i + 1}: la coma solo sirve como decimal entre dos dígitos (0,5). "
                               "Las funciones de este programa reciben un solo argumento.")
        elif c == "!":
            raise ErrorFuncion("El factorial (!) no se puede usar en f(x): escriba el número ya calculado (3! = 6).")
        else:
            raise ErrorFuncion(f"Carácter no permitido '{c}' en la posición {i + 1}.")
    if not tokens:
        raise ErrorFuncion("La función está vacía.")
    _revisar_agrupacion(t)
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
        self.inversas = []   # funciones escritas como tan⁻¹ x y leidas como arctan x

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
        # Permite la multiplicacion implicita: 5x, 2(x+1), x sen(x), (x-1)(x+2), 2|x|
        # (dentro de un valor absoluto, la barra cierra: |2x| no es 2·|x|)
        tok = self.ver()
        if tok is None:
            return False
        if tok[0] in ("num", "var", "const", "func"):
            return True
        return tok[0] == "op" and (tok[1] == "(" or (tok[1] == "|" and not self.dentro_abs))

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

    def _anterior(self):
        """Token anterior al que se acaba de consumir (para explicar que falta)."""
        indice = min(self.pos - 2, len(self.tokens) - 1)
        return self.tokens[indice] if 0 <= indice < len(self.tokens) else None

    def _falta_operando(self, tok):
        """Mensaje cuando se esperaba un numero, x, una funcion o un parentesis y llego otra cosa."""
        previo = self._anterior()
        if tok is None:
            if previo == ("op", "^"):
                return "Falta el exponente después de '^'."
            if previo is not None and previo[0] == "func":
                return f"Falta el argumento de {previo[1]}, por ejemplo {previo[1]}(x)."
            if previo == ("op", "|"):
                return "El valor absoluto está vacío: escriba algo entre las barras, como |x − 2|."
            if previo is not None and previo[0] == "op":
                return f"La función termina en '{previo[1]}': falta un término después."
            return "La función está incompleta: falta un término."
        simbolo = self._texto(tok)
        if tok == ("op", ")"):
            if previo == ("op", "("):
                return "Hay paréntesis vacíos '()': escriba algo adentro."
            if previo is not None and previo[0] == "func":
                return f"Falta el argumento de {previo[1]}, por ejemplo {previo[1]}(x)."
            if previo is not None and previo[0] == "op":
                return f"Falta un término entre '{previo[1]}' y ')'."
        if previo is None:
            return f"La función no puede empezar con '{simbolo}': falta un término antes."
        if previo[0] == "func":
            return f"Falta el argumento de {previo[1]}, por ejemplo {previo[1]}(x)."
        if previo == ("op", "("):
            return f"Falta un término antes de '{simbolo}' (justo después de '(')."
        if previo == ("op", "|"):
            return f"Falta un término antes de '{simbolo}' (justo después de '|')."
        if previo[0] == "op":
            return f"Hay dos operadores seguidos '{previo[1]} {simbolo}': falta un término entre ellos."
        return f"No se esperaba '{simbolo}' en esa posición."

    def primario(self):
        tok = self.consumir()
        if tok is None or (tok[0] == "op" and tok[1] not in "(|"):
            raise ErrorFuncion(self._falta_operando(tok))
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
            nombre = tok[1]
            exponente = None
            if self.es_op("^"):
                self.consumir()
                if self.ver() is None:
                    raise ErrorFuncion(f"Falta el exponente de {nombre} después de '^'.")
                exponente = self.unario() if self.es_op("(") or self.es_op("-") else self.primario()
                if _valor(exponente) == -1 and nombre in _INVERSAS:
                    # tan⁻¹ x es la funcion inversa (arctan x), no 1/tan x
                    self.inversas.append((nombre, _INVERSAS[nombre]))
                    nombre, exponente = _INVERSAS[nombre], None
            siguiente = self.ver()
            vacio = (self.es_op("(") and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == ("op", ")"))
            if siguiente is None or vacio or (siguiente[0] == "op" and siguiente[1] not in "(|"):
                raise ErrorFuncion(f"Falta el argumento de {nombre}: escríbalo después del nombre, "
                                   f"por ejemplo {nombre}(x).")
            if self.es_op("("):
                argumento = self.primario()
            else:
                argumento = self.potencia()
                # "sen 2x", "cos πx": el argumento sigue mientras haya numeros, x o constantes pegados
                while self.ver() is not None and self.ver()[0] in ("num", "var", "const"):
                    argumento = ("bin", "*", argumento, self.potencia(), True)
            nodo = ("func", nombre, argumento)
            return ("bin", "^", nodo, exponente, False) if exponente is not None else nodo
        if tok == ("op", "("):
            nodo = self.expresion()
            if not self.es_op(")"):
                raise ErrorFuncion("Falta cerrar un paréntesis ')'.")
            self.consumir()
            return nodo
        if tok == ("op", "|"):
            # Donde se espera un operando la barra siempre abre: ||x| − 2| es un valor absoluto anidado
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
    "arcsec": "F.asec", "asec": "F.asec", "arccsc": "F.acsc", "acsc": "F.acsc",
    "arccot": "F.acot", "acot": "F.acot", "arcctg": "F.acot",
    "senh": "Math.sinh", "sinh": "Math.sinh", "cosh": "Math.cosh", "tanh": "Math.tanh", "tgh": "Math.tanh",
    "sech": "F.sech", "csch": "F.csch", "coth": "F.coth",
    "arcsenh": "Math.asinh", "arcsinh": "Math.asinh", "asinh": "Math.asinh", "argsenh": "Math.asinh",
    "arccosh": "Math.acosh", "acosh": "Math.acosh", "argcosh": "Math.acosh",
    "arctanh": "Math.atanh", "atanh": "Math.atanh", "argtanh": "Math.atanh",
    "arcsech": "F.asech", "asech": "F.asech", "arccsch": "F.acsch", "acsch": "F.acsch",
    "arccoth": "F.acoth", "acoth": "F.acoth",
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
    if op == "/":
        return f"F.div({a}, {b})"   # 1/0 da NaN (en Python es un error), no Infinity
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
    "arcsec": r"\mathrm{arcsec}", "asec": r"\mathrm{arcsec}", "arccsc": r"\mathrm{arccsc}", "acsc": r"\mathrm{arccsc}",
    "arccot": r"\mathrm{arccot}", "acot": r"\mathrm{arccot}", "arcctg": r"\mathrm{arcctg}",
    "senh": r"\mathrm{senh}", "sinh": r"\sinh", "cosh": r"\cosh", "tanh": r"\tanh", "tgh": r"\mathrm{tgh}",
    "sech": r"\mathrm{sech}", "csch": r"\mathrm{csch}", "coth": r"\coth",
    "arcsenh": r"\mathrm{arcsenh}", "arcsinh": r"\mathrm{arcsinh}", "asinh": r"\mathrm{arcsinh}",
    "argsenh": r"\mathrm{argsenh}", "arccosh": r"\mathrm{arccosh}", "acosh": r"\mathrm{arccosh}",
    "argcosh": r"\mathrm{argcosh}", "arctanh": r"\mathrm{arctanh}", "atanh": r"\mathrm{arctanh}",
    "argtanh": r"\mathrm{argtanh}", "arcsech": r"\mathrm{arcsech}", "asech": r"\mathrm{arcsech}",
    "arccsch": r"\mathrm{arccsch}", "acsch": r"\mathrm{arccsch}", "arccoth": r"\mathrm{arccoth}",
    "acoth": r"\mathrm{arccoth}",
    "exp": r"\exp", "ln": r"\ln", "log": r"\log", "log10": r"\log_{10}", "log2": r"\log_{2}",
}


def _parentesis(texto):
    r"""Parentesis normales; solo crecen (\left( … \right)) si adentro hay una fraccion o una raiz.
    Con \left( alrededor de algo simple, mathtext los dibuja pequenos y desalineados: sen₍x₎."""
    if r"\frac" in texto or r"\sqrt" in texto:
        return r"\left(" + texto + r"\right)"
    return "(" + texto + ")"


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
        return _MATHTEXT_FUNC[nodo[1]] + _parentesis(interno), 5
    if tipo == "neg":
        texto, prio = _mt(nodo[1])
        return "-" + (texto if prio >= 2 else _parentesis(texto)), 3

    op = nodo[1]
    (ti, pi_), (td, pd) = _mt(nodo[2]), _mt(nodo[3])
    envolver = _parentesis
    if op == "^" and nodo[2][0] == "func" and nodo[2][1] in _MATHTEXT_FUNC and nodo[3][0] == "num":
        # sen²(x), sec²(x): el exponente se escribe junto al nombre de la funcion
        return _MATHTEXT_FUNC[nodo[2][1]] + "^{" + td + "}" + _parentesis(_mt(nodo[2][2])[0]), 4
    if op == "^":
        es_fraccion = nodo[2][0] == "bin" and nodo[2][1] == "/"   # (x/3)² necesita parentesis
        base = ti if pi_ >= 5 and nodo[2][0] != "func" and not es_fraccion else envolver(ti)
        return base + "^{" + td + "}", 4
    if op == "/":
        return r"\frac{" + ti + "}{" + td + "}", 5
    if op == "*":
        izq = ti if pi_ >= 2 else envolver(ti)
        der = td if pd >= 3 and nodo[3][0] != "neg" else envolver(td)
        if nodo[2][0] == "num" and nodo[3][0] == "bin" and nodo[3][1] == "*":
            der = td  # 2x·sen(x) en lugar de 2(x·sen(x))
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
_LATEX_GRIEGAS = {"alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta",
                  "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau", "upsilon",
                  "phi", "varphi", "chi", "psi", "omega", "Gamma", "Delta", "Theta", "Lambda", "Sigma", "Phi",
                  "Psi", "Omega"}
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
            return texto if texto.strip() else CASILLA_VACIA   # \frac{}{x}: casilla sin llenar
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
            return CASILLA_VACIA
        if nombre in FUNCIONES or nombre in ("ln", "log", "exp"):
            return nombre
        if nombre in ("circ", "degree"):
            return "°"
        if nombre in _LATEX_GRIEGAS:
            raise ErrorFuncion(f"La letra griega {nombre} no se puede usar: la única variable permitida es x "
                               "(si es un dato, reemplácela por su valor numérico).")
        if nombre in ("infty", "infin"):
            raise ErrorFuncion("∞ no es un número: f(x) solo puede tener números, x y funciones.")
        if nombre in ("le", "ge", "leq", "geq", "lt", "gt", "ne", "neq", "approx"):
            raise ErrorFuncion("Solo se aceptan igualdades (=): una desigualdad no tiene una raíz que buscar.")
        if nombre in ("pm", "mp"):
            raise ErrorFuncion("El símbolo ± no se puede usar: escriba por separado la versión con + y con −.")
        sugerida = _sugerencia(nombre)
        if sugerida:
            raise ErrorFuncion(f"No se reconoce '\\{nombre}'. ¿Quiso decir {sugerida}?")
        raise ErrorFuncion(f"No se reconoce el símbolo '\\{nombre}' en la función.")

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


# ----------------------------------------------------------------------
# Derivada simbolica (la usa Newton-Raphson): se aplican las reglas de
# derivacion sobre el arbol (suma, producto, cociente, potencia y regla de la
# cadena) y el resultado se simplifica para que se vea como en el cuaderno:
#   d/dx (x³ − x − 2) = 3x² − 1        d/dx (e^(−x) − x) = −e^(−x) − 1
# Tampoco usa librerias: solo construye otro arbol con las mismas tuplas.
# ----------------------------------------------------------------------
def _tiene_x(nodo):
    tipo = nodo[0]
    if tipo == "x":
        return True
    if tipo in ("num", "const"):
        return False
    if tipo in ("neg", "abs"):
        return _tiene_x(nodo[1])
    if tipo == "func":
        return _tiene_x(nodo[2])
    return _tiene_x(nodo[2]) or _tiene_x(nodo[3])


def _formato(valor):
    """Numero sin notacion cientifica ni ceros de mas: 3.0 -> '3', 0.25 -> '0.25'."""
    if valor == int(valor) and abs(valor) < 1e15:
        return str(int(valor))
    return f"{valor:.10f}".rstrip("0").rstrip(".")


def _num(valor):
    valor = round(valor, 12) + 0.0  # quita el ruido de punto flotante y el cero negativo
    if valor < 0:
        return ("neg", _num(-valor))
    return ("num", valor, _formato(valor))


def _valor(nodo):
    """Valor de un nodo que es solo un numero (o un numero negativo); None si tiene algo mas."""
    if nodo[0] == "num":
        return nodo[1]
    if nodo[0] == "neg" and nodo[1][0] == "num":
        return -nodo[1][1]
    return None


def _neg(a):
    va = _valor(a)
    if va is not None:
        return _num(-va)
    if a[0] == "neg":
        return a[1]
    return ("neg", a)


def _suma(a, b):
    va, vb = _valor(a), _valor(b)
    if va is not None and vb is not None:
        return _num(va + vb)
    if va == 0:
        return b
    if vb == 0:
        return a
    if b[0] == "neg":
        return _resta(a, b[1])
    if a[0] == "neg":
        return _resta(b, a[1])
    return _ordenar_suma(("bin", "+", a, b, False))


def _resta(a, b):
    va, vb = _valor(a), _valor(b)
    if va is not None and vb is not None:
        return _num(va - vb)
    if vb == 0:
        return a
    if va == 0:
        return _neg(b)
    if b[0] == "neg":
        return _suma(a, b[1])
    if a == b:
        return _num(0)
    return _ordenar_suma(("bin", "-", a, b, False))


# ----------------------------------------------------------------------
# Productos y cocientes como lista de factores: coeficiente · base₁^e₁ · base₂^e₂ …
# Asi se juntan las potencias de la misma base (sec(x)·sec(x)·tan(x) = sec²(x)·tan(x))
# y se cancelan factores comunes en un cociente (x²·cos(1/x)/x² = cos(1/x)).
# ----------------------------------------------------------------------
def _factores(nodo):
    """2x³·sen(x) -> (2, [(x, 3), (sen(x), 1)])."""
    valor = _valor(nodo)
    if valor is not None:
        return valor, []
    if nodo[0] == "neg":
        k, lista = _factores(nodo[1])
        return -k, lista
    if nodo[0] == "bin" and nodo[1] == "*":
        ka, la = _factores(nodo[2])
        kb, lb = _factores(nodo[3])
        return ka * kb, la + lb
    if nodo[0] == "bin" and nodo[1] == "^":
        exponente = _valor(nodo[3])
        if exponente is not None:
            return 1.0, [(nodo[2], exponente)]
    return 1.0, [(nodo, 1.0)]


def _juntar(lista):
    """Suma los exponentes de las bases repetidas, en el orden en que aparecen."""
    juntos = []
    for base, exponente in lista:
        for i, (otra, e) in enumerate(juntos):
            if otra == base:
                juntos[i] = (otra, e + exponente)
                break
        else:
            juntos.append((base, exponente))
    return [(b, round(e, 12)) for b, e in juntos if round(e, 12) != 0]


def _armar(coeficiente, lista):
    """Arbol de coeficiente · base₁^e₁ · base₂^e₂ … (el numero va adelante: 3x²·sen(x))."""
    coeficiente = round(coeficiente, 12) + 0.0
    if coeficiente == 0:
        return _num(0)
    if any(e < 0 for _, e in lista):
        # Exponentes negativos al denominador: −2x⁻³ = −2/x³     cos⁻²(x)·sen(x) = sen(x)/cos²(x)
        arriba = [(b, e) for b, e in lista if e > 0]
        abajo = [(b, -e) for b, e in lista if e < 0]
        return _cociente(_armar(coeficiente, arriba), _armar(1.0, abajo))
    resultado = None
    for base, exponente in lista:
        factor = _elevar(base, _num(exponente))
        resultado = factor if resultado is None else ("bin", "*", resultado, factor, False)
    if resultado is None:
        return _num(coeficiente)
    if abs(coeficiente) != 1:
        resultado = ("bin", "*", _num(abs(coeficiente)), resultado, True)
    return _neg(resultado) if coeficiente < 0 else resultado


def _producto(a, b):
    va, vb = _valor(a), _valor(b)
    if va is not None and vb is not None:
        return _num(va * vb)
    if va == 0 or vb == 0:
        return _num(0)
    if vb is not None:  # el numero va adelante: 3x en lugar de x·3
        a, b, va, vb = b, a, vb, va
    if va == 1:
        return b
    if va == -1:
        return _neg(b)
    if a[0] == "neg":
        return _neg(_producto(a[1], b))
    if b[0] == "neg":
        return _neg(_producto(a, b[1]))
    # Con un cociente: a·(p/q) = (a·p)/q     (p/q)·b = (p·b)/q     2·(3/x) = 6/x
    if b[0] == "bin" and b[1] == "/":
        return _cociente(_producto(a, b[2]), b[3])
    if a[0] == "bin" and a[1] == "/":
        return _cociente(_producto(a[2], b), a[3])
    if va is not None and _es_suma(b):
        return ("bin", "*", a, b, True)        # 3(x + 1): se deja asi, no se distribuye
    ka, la = _factores(a)
    kb, lb = _factores(b)
    return _armar(ka * kb, _juntar(la + lb))


def _base_exponente(nodo):
    """x³ -> (x, 3);  x -> (x, 1);  x^(algo con x) -> (x^(...), None)."""
    if nodo[0] == "bin" and nodo[1] == "^":
        exponente = _valor(nodo[3])
        return (nodo[2], exponente) if exponente is not None else (nodo, None)
    return nodo, 1.0


def _coeficiente(nodo):
    """Separa el numero que multiplica: 2√(x) -> (2, √(x));  x -> (1, x)."""
    if nodo[0] == "bin" and nodo[1] == "*" and _valor(nodo[2]) is not None:
        return _valor(nodo[2]), nodo[3]
    return 1.0, nodo


def _decimal_exacto(q):
    return abs(q * 1e6 - round(q * 1e6)) < 1e-6


def _cociente(a, b):
    va, vb = _valor(a), _valor(b)
    if va == 0:
        return _num(0)
    if vb == 1:
        return a
    if vb == -1:
        return _neg(a)
    if a == b:
        return _num(1)
    if va is not None and vb not in (None, 0):
        q = va / vb
        if _decimal_exacto(q):  # solo si da un decimal exacto (1/4 = 0.25, no 1/3)
            return _num(q)
        if va == int(va) and vb == int(vb):
            divisor = math.gcd(int(va), int(vb))   # 6/4 -> 3/2,  2/6 -> 1/3
            if divisor > 1:
                return _cociente(_num(va / divisor), _num(vb / divisor))
    if a[0] == "neg":
        return _neg(_cociente(a[1], b))
    if b[0] == "neg":
        return _neg(_cociente(a, b[1]))
    # (p/q)/b = p/(q·b)     a/(p/q) = a·q/p
    if a[0] == "bin" and a[1] == "/":
        return _cociente(a[2], _producto(a[3], b))
    if b[0] == "bin" and b[1] == "/":
        return _cociente(_producto(a, b[3]), b[2])
    if va is not None or vb is not None:
        if vb not in (None, 0):
            # Entre un numero: 2x/2 = x    3x/6 = 0.5x    2x/7 se deja asi
            k, resto = _coeficiente(a)
            if _decimal_exacto(k / vb):
                return _producto(_num(k / vb), resto)
        return ("bin", "/", a, b, False)
    # Se cancelan los factores comunes: 6x/x⁴ = 6/x³     2x/(x²·ln(10)) = 2/(x·ln(10))
    ka, la = _factores(a)
    kb, lb = _factores(b)
    la, lb = _juntar(la), _juntar(lb)
    arriba, abajo = [], list(lb)
    for base, exponente in la:
        for i, (otra, e) in enumerate(abajo):
            if otra == base:
                resto = round(exponente - e, 12)
                abajo.pop(i)
                if resto > 0:
                    arriba.append((base, resto))
                elif resto < 0:
                    abajo.insert(i, (base, -resto))
                break
        else:
            arriba.append((base, exponente))
    # Un exponente negativo cambia de lado: arcsen⁻²(x)/√(1 − x²) = 1/(arcsen²(x)·√(1 − x²))
    arriba, abajo = ([(base, e) for base, e in arriba if e > 0] + [(base, -e) for base, e in abajo if e < 0],
                     [(base, e) for base, e in abajo if e > 0] + [(base, -e) for base, e in arriba if e < 0])
    if _decimal_exacto(ka / kb):
        ka, kb = ka / kb, 1.0
    elif ka == int(ka) and kb == int(kb):
        divisor = math.gcd(int(ka), int(kb))
        ka, kb = ka / divisor, kb / divisor
    numerador, denominador = _armar(ka, arriba), _armar(kb, abajo)
    if _valor(denominador) == 1:
        return numerador
    if _valor(denominador) is not None or denominador[0] == "neg":
        return _cociente(numerador, denominador)
    return ("bin", "/", numerador, denominador, False)


def _elevar(a, b):
    va, vb = _valor(a), _valor(b)
    if vb == 0:
        return _num(1)
    if vb == 1:
        return a
    if va == 1:
        return _num(1)
    if va is not None and vb is not None and vb == int(vb) and abs(vb) <= 20 and not (va == 0 and vb < 0):
        r = va ** int(vb)
        if abs(r) < 1e12 and abs(r * 1e6 - round(r * 1e6)) < 1e-6:
            return _num(r)
    if a[0] == "bin" and a[1] == "^" and _exponente_entero(a[3]) and _exponente_entero(b):
        return _elevar(a[2], _num(_valor(a[3]) * vb))  # (x²)² = x⁴ (con exponentes enteros)
    return ("bin", "^", a, b, False)


# ----------------------------------------------------------------------
# Sumas: se juntan los terminos semejantes y, si todo es un polinomio en x,
# se desarrolla y se ordena por grado (solo si queda igual o mas corto):
#   2x·(x² + 1) − 2(x² − 1)·x = 4x        ln(x) + 1 − 1 = ln(x)
# ----------------------------------------------------------------------
_GRADO_MAXIMO = 30


def _polinomio(nodo):
    """Coeficientes {grado: valor} si nodo es un polinomio en x con decimales exactos; si no, None."""
    tipo = nodo[0]
    if tipo == "num":
        return {0: nodo[1]}
    if tipo == "x":
        return {1: 1.0}
    if tipo == "neg":
        p = _polinomio(nodo[1])
        return None if p is None else {g: -c for g, c in p.items()}
    if tipo != "bin":
        return None
    op = nodo[1]
    a = _polinomio(nodo[2])
    if a is None:
        return None
    if op == "/":
        divisor = _valor(nodo[3])
        if divisor in (None, 0):
            return None
        resultado = {g: c / divisor for g, c in a.items()}
        return resultado if all(_decimal_exacto(c) for c in resultado.values()) else None
    if op == "^":
        exponente = _valor(nodo[3])
        if exponente is None or exponente < 0 or exponente != int(exponente) \
                or max(a) * exponente > _GRADO_MAXIMO:
            return None
        resultado = {0: 1.0}
        for _ in range(int(exponente)):
            resultado = _multiplicar_polinomios(resultado, a)
        return resultado
    b = _polinomio(nodo[3])
    if b is None:
        return None
    if op == "*":
        if max(a) + max(b) > _GRADO_MAXIMO:
            return None
        return _multiplicar_polinomios(a, b)
    signo = 1 if op == "+" else -1
    resultado = dict(a)
    for g, c in b.items():
        resultado[g] = resultado.get(g, 0.0) + signo * c
    return resultado


def _multiplicar_polinomios(a, b):
    resultado = {}
    for g1, c1 in a.items():
        for g2, c2 in b.items():
            resultado[g1 + g2] = resultado.get(g1 + g2, 0.0) + c1 * c2
    return resultado


def _desde_polinomio(p):
    """Arbol del polinomio ordenado de mayor a menor grado: x² − x − 1.
    Con dos terminos y el primero negativo se escribe el positivo adelante: 1 − x² (no −x² + 1)."""
    resultado = None
    grados = [g for g in sorted(p, reverse=True) if round(p[g], 12) != 0]
    if len(grados) == 2 and p[grados[0]] < 0 < p[grados[1]]:
        grados.reverse()
    for grado in grados:
        c = round(p[grado], 12)
        termino = _num(abs(c)) if grado == 0 else _producto(_num(abs(c)), _elevar(("x",), _num(grado)))
        if resultado is None:
            resultado = termino if c > 0 else _neg(termino)
        else:
            resultado = ("bin", "+" if c > 0 else "-", resultado, termino, False)
    return resultado if resultado is not None else _num(0)


def _cantidad_terminos(nodo):
    return len(_terminos(nodo))


def _ordenar_suma(nodo):
    """Simplifica una suma solo si queda igual o mas corta (nunca la alarga)."""
    terminos = _terminos(nodo)
    p = _polinomio(nodo)
    if p is not None:
        ordenado = _desde_polinomio(p)
        return ordenado if _cantidad_terminos(ordenado) <= len(terminos) else nodo
    reducido, _ = _reducir(terminos)
    return reducido if _cantidad_terminos(reducido) < len(terminos) else nodo


def _f(nombre, argumento):
    return ("func", nombre, argumento)


def _derivar_funcion(nombre, u, du):
    """Regla de la cadena: d/dx g(u) = g'(u)·u'."""
    dos = _num(2)
    raiz_1_menos_u2 = _f("sqrt", _resta(_num(1), _elevar(u, dos)))
    if nombre in ("sen", "sin"):
        g = _f("cos", u)
    elif nombre == "cos":
        g = _neg(_f("sen", u))
    elif nombre in ("tan", "tg"):
        g = _elevar(_f("sec", u), dos)
    elif nombre == "sec":
        g = _producto(_f("sec", u), _f("tan", u))
    elif nombre == "csc":
        g = _neg(_producto(_f("csc", u), _f("cot", u)))
    elif nombre in ("cot", "ctg"):
        g = _neg(_elevar(_f("csc", u), dos))
    elif nombre in ("arcsen", "arcsin", "asin"):
        return _cociente(du, raiz_1_menos_u2)
    elif nombre in ("arccos", "acos"):
        return _neg(_cociente(du, raiz_1_menos_u2))
    elif nombre in ("arctan", "arctg", "atan"):
        return _cociente(du, _suma(_num(1), _elevar(u, dos)))
    elif nombre in ("arcsec", "asec"):
        return _cociente(du, _producto(("abs", u), _f("sqrt", _resta(_elevar(u, dos), _num(1)))))
    elif nombre in ("arccsc", "acsc"):
        return _neg(_cociente(du, _producto(("abs", u), _f("sqrt", _resta(_elevar(u, dos), _num(1))))))
    elif nombre in ("arccot", "acot", "arcctg"):
        return _neg(_cociente(du, _suma(_num(1), _elevar(u, dos))))
    elif nombre in ("senh", "sinh"):
        g = _f("cosh", u)
    elif nombre == "cosh":
        g = _f("senh", u)
    elif nombre in ("tanh", "tgh"):
        return _cociente(du, _elevar(_f("cosh", u), dos))
    elif nombre == "sech":
        g = _neg(_producto(_f("sech", u), _f("tanh", u)))
    elif nombre == "csch":
        g = _neg(_producto(_f("csch", u), _f("coth", u)))
    elif nombre == "coth":
        g = _neg(_elevar(_f("csch", u), dos))
    elif nombre in ("arcsenh", "arcsinh", "asinh", "argsenh"):
        return _cociente(du, _f("sqrt", _suma(_elevar(u, dos), _num(1))))
    elif nombre in ("arccosh", "acosh", "argcosh"):
        return _cociente(du, _f("sqrt", _resta(_elevar(u, dos), _num(1))))
    elif nombre in ("arctanh", "atanh", "argtanh"):
        return _cociente(du, _resta(_num(1), _elevar(u, dos)))
    elif nombre in ("arcsech", "asech"):
        return _neg(_cociente(du, _producto(u, raiz_1_menos_u2)))
    elif nombre in ("arccsch", "acsch"):
        return _neg(_cociente(du, _producto(("abs", u), _f("sqrt", _suma(_elevar(u, dos), _num(1))))))
    elif nombre in ("arccoth", "acoth"):
        return _cociente(du, _resta(_num(1), _elevar(u, dos)))
    elif nombre == "exp":
        g = _f("exp", u)
    elif nombre == "ln":
        if u[0] == "abs" or (u[0] == "func" and u[1] == "abs"):
            interno = u[1] if u[0] == "abs" else u[2]
            return _cociente(derivar(interno), interno)   # (ln|u|)' = u'/u
        return _cociente(du, u)
    elif nombre in ("log", "log10", "log2"):
        base = 2 if nombre == "log2" else 10
        return _cociente(du, _producto(u, _f("ln", _num(base))))
    elif nombre in ("sqrt", "raiz"):
        return _cociente(du, _producto(dos, _f("sqrt", u)))
    elif nombre == "cbrt":
        return _cociente(du, _producto(_num(3), _elevar(_f("cbrt", u), dos)))
    elif nombre == "abs":  # d|u| = u'·u / |u|
        return _producto(du, _cociente(u, ("abs", u)))
    else:
        raise ErrorFuncion(f"No se conoce la regla de derivación de {nombre}.")
    return _producto(du, g)


def derivar(nodo):
    """Devuelve el arbol de la derivada de nodo respecto a x, ya simplificado."""
    if not _tiene_x(nodo):
        return _num(0)
    tipo = nodo[0]
    if tipo == "x":
        return _num(1)
    if tipo == "neg":
        return _neg(derivar(nodo[1]))
    if tipo == "abs":
        return _derivar_funcion("abs", nodo[1], derivar(nodo[1]))
    if tipo == "func":
        return _derivar_funcion(nodo[1], nodo[2], derivar(nodo[2]))
    op, u, v = nodo[1], nodo[2], nodo[3]
    if op == "+":
        return _suma(derivar(u), derivar(v))
    if op == "-":
        return _resta(derivar(u), derivar(v))
    if op == "*":
        if not _tiene_x(u):          # (c·v)' = c·v'
            return _producto(u, derivar(v))
        if not _tiene_x(v):
            return _producto(v, derivar(u))
        return _suma(_producto(derivar(u), v), _producto(u, derivar(v)))
    if op == "/":
        if not _tiene_x(v):          # (u/c)' = u'/c
            return _cociente(derivar(u), v)
        cuadrado = _elevar(v, _num(2))
        if not _tiene_x(u):          # (c/v)' = −c·v'/v²
            return _neg(_cociente(_producto(u, derivar(v)), cuadrado))
        return _cociente(_resta(_producto(derivar(u), v), _producto(u, derivar(v))), cuadrado)
    # Potencia
    if not _tiene_x(v):              # (uⁿ)' = n·uⁿ⁻¹·u'
        signo, fraccion = (-1, v[1]) if v[0] == "neg" else (1, v)
        p, q = ((_valor(fraccion[2]), _valor(fraccion[3])) if fraccion[0] == "bin" and fraccion[1] == "/"
                else (None, None))
        if p is not None and q not in (None, 0) and not _decimal_exacto(p / q):
            # x^(1/3) -> x^(−2/3)/3: se conserva la fraccion para no escribir decimales periodicos
            p = signo * p
            n, n_menos_1 = _cociente(_num(p), _num(q)), _cociente(_num(p - q), _num(q))
        else:
            valor = _valor(v) if p is None else signo * p / q
            n = _num(valor) if valor is not None else v          # x^(3/2) -> 1.5x^0.5
            n_menos_1 = _num(valor - 1) if valor is not None else _resta(v, _num(1))
        return _producto(_producto(n, _elevar(u, n_menos_1)), derivar(u))
    if not _tiene_x(u):              # (aᵛ)' = v'·aᵛ·ln a   (con a = e, ln e = 1)
        factor = nodo if u == ("const", "e") else _producto(nodo, _f("ln", u))
        return _producto(derivar(v), factor)
    # (uᵛ)' = uᵛ·(v'·ln u + v·u'/u)
    return _producto(nodo, _suma(_producto(derivar(v), _f("ln", u)), _cociente(_producto(v, derivar(u)), u)))


# Texto legible (y que el mismo analizador vuelve a leer): 3x² − 1, −sen(x) − 1, 1/(2√(x))
_SUPERINDICE = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def _exponente_entero(nodo):
    v = _valor(nodo)
    return v is not None and v == int(v) and abs(v) < 1000


def _tx(nodo):
    """Devuelve (texto, prioridad): 1 suma/resta, 2 producto/cociente, 3 negativo, 4 potencia, 5 atomo."""
    tipo = nodo[0]
    if tipo == "num":
        return nodo[2], 5
    if tipo == "x":
        return "x", 5
    if tipo == "const":
        return ("π" if nodo[1] == "pi" else "e"), 5
    if tipo == "abs" or (tipo == "func" and nodo[1] == "abs"):
        return "|" + _tx(nodo[1] if tipo == "abs" else nodo[2])[0] + "|", 5
    if tipo == "func":
        nombre = "√" if nodo[1] in ("sqrt", "raiz") else nodo[1]
        return f"{nombre}({_tx(nodo[2])[0]})", 5
    if tipo == "neg":
        texto, prio = _tx(nodo[1])
        return "−" + (texto if prio >= 2 else f"({texto})"), 3

    op = nodo[1]
    (ti, pi_), (td, pd) = _tx(nodo[2]), _tx(nodo[3])
    if op == "^":
        if _exponente_entero(nodo[3]):
            exponente = _formato(_valor(nodo[3])).translate(_SUPERINDICE)
            if nodo[2][0] == "func" and nodo[2][1] not in ("abs", "sqrt", "raiz") and _valor(nodo[3]) > 0:
                # sec²(x): el analizador lo lee como (sec x)².  Con exponente negativo se escribe (tan(x))⁻¹,
                # porque tan⁻¹(x) seria la funcion inversa arctan(x)
                return ti.replace("(", exponente + "(", 1), 4
        else:
            exponente = "^" + (td if pd >= 5 else f"({td})")
        base = ti if pi_ >= 5 and nodo[2][0] != "func" else f"({ti})"
        return base + exponente, 4
    if op == "*":
        izq = ti if pi_ >= 2 else f"({ti})"
        der = td if pd >= 3 and nodo[3][0] != "neg" else f"({td})"
        if nodo[2][0] == "num" and nodo[3][0] == "bin" and nodo[3][1] == "*":
            der = td  # 2x·sen(x) en lugar de 2(x·sen(x)): el producto es asociativo
        # 3x², 2cos(x), −2x: el numero se escribe pegado (como en el cuaderno)
        if _valor(nodo[2]) is not None and (der[0].isalpha() or der[0] in "(|√π"):
            return izq + der, 2
        return izq + "·" + der, 2
    if op == "/":
        izq = ti if pi_ >= 2 else f"({ti})"
        der = td if pd >= 4 else f"({td})"
        return izq + "/" + der, 2
    der = td if pd > 1 and nodo[3][0] != "neg" else f"({td})"
    return ti + (" + " if op == "+" else " − ") + der, 1


def a_texto(arbol):
    return _tx(arbol)[0]


# ----------------------------------------------------------------------
# Ecuaciones que no estan igualadas a cero: izquierda = derecha.
# Como en el cuaderno, se pasan todos los terminos al lado izquierdo cambiando
# su signo y se reducen los terminos semejantes:
#   sen(x) = −2x + 1   ->   sen(x) − (−2x + 1) = 0   ->   sen(x) + 2x − 1 = 0
#   x³ = x + 2         ->   x³ − x − 2 = 0
# Las raices de f(x) = izquierda − derecha son las soluciones de la ecuacion.
# ----------------------------------------------------------------------
def _terminos(nodo, signo=1):
    """Separa una suma en sus terminos con signo: a − (b + c) -> [(+1, a), (−1, b), (−1, c)].
    Tambien distribuye un numero sobre un parentesis: 2(x + 1) -> [(+1, 2x), (+1, 2)]."""
    if nodo[0] == "neg":
        return _terminos(nodo[1], -signo)
    if nodo[0] == "bin" and nodo[1] in ("+", "-"):
        derecha = signo if nodo[1] == "+" else -signo
        return _terminos(nodo[2], signo) + _terminos(nodo[3], derecha)
    if nodo[0] == "bin" and nodo[1] == "*" and _valor(nodo[2]) is not None and _es_suma(nodo[3]):
        k = _valor(nodo[2])
        return [(s, _producto(_num(k), t)) for s, t in _terminos(nodo[3], signo)]
    if nodo[0] == "bin" and nodo[1] == "/" and _valor(nodo[3]) not in (None, 0) and _es_suma(nodo[2]) \
            and _decimal_exacto(1 / _valor(nodo[3])):
        k = 1 / _valor(nodo[3])
        return [(s, _producto(_num(k), t)) for s, t in _terminos(nodo[2], signo)]
    return [(signo, nodo)]


def _es_suma(nodo):
    while nodo[0] == "neg":
        nodo = nodo[1]
    return nodo[0] == "bin" and nodo[1] in ("+", "-")


def _separar_coeficiente(nodo):
    """2x³ -> (2, x³);  −3sen(x) -> (−3, sen(x));  x/2 -> (0.5, x);  5 -> (5, None)."""
    valor = _valor(nodo)
    if valor is not None:
        return valor, None
    if nodo[0] == "neg":
        k, parte = _separar_coeficiente(nodo[1])
        return -k, parte
    if nodo[0] == "bin" and nodo[1] == "*":
        for numero, resto in ((nodo[2], nodo[3]), (nodo[3], nodo[2])):
            k = _valor(numero)
            if k is not None:
                k2, parte = _separar_coeficiente(resto)
                return k * k2, parte
    divisor = _valor(nodo[3]) if nodo[0] == "bin" and nodo[1] == "/" else None
    if divisor not in (None, 0) and _decimal_exacto(1 / divisor):
        k, parte = _separar_coeficiente(nodo[2])   # x/2 = 0.5·x  (x/3 se deja igual: 0.333… no es exacto)
        return k / divisor, parte
    return 1.0, nodo


# Funciones definidas para todo x: si se cancelan no cambian el dominio de la ecuacion
_SIN_RESTRICCION = {"sen", "sin", "cos", "exp", "abs", "arctan", "arctg", "atan", "arccot", "acot", "arcctg",
                    "senh", "sinh", "cosh", "tanh", "tgh", "sech", "arcsenh", "arcsinh", "asinh", "argsenh", "cbrt"}


def _dominio_restringido(nodo):
    """True si la expresion no esta definida para algun x (ln x, √x, 1/x, tan x, x^0.5…)."""
    tipo = nodo[0]
    if tipo in ("num", "x", "const"):
        return False
    if tipo in ("neg", "abs"):
        return _dominio_restringido(nodo[1])
    if tipo == "func":
        return nodo[1] not in _SIN_RESTRICCION or _dominio_restringido(nodo[2])
    op, a, b = nodo[1], nodo[2], nodo[3]
    if op == "/" and _tiene_x(b):
        return True
    if op == "^" and _tiene_x(a):
        exponente = _valor(b)
        if exponente is None or exponente < 0 or exponente != int(exponente):
            return True
    return _dominio_restringido(a) or _dominio_restringido(b)


def _clave_termino(parte):
    """Misma clave para tan(x)·sec²(x) y sec²(x)·tan(x): son terminos semejantes."""
    _, lista = _factores(parte)
    return tuple(sorted(a_texto(_elevar(base, _num(e))) for base, e in _juntar(lista)))


def _reducir(terminos):
    """Junta los terminos semejantes (misma parte con x) y suma las constantes al final.
    Devuelve (arbol, cancelados): cancelados son las partes que se anularon (ln x − ln x)."""
    grupos = {}       # texto de la parte con x -> [coeficiente, parte]
    constante = 0.0
    for signo, termino in terminos:
        coeficiente, parte = _separar_coeficiente(termino)
        if parte is None:
            constante += signo * coeficiente
            continue
        clave = _clave_termino(parte)
        if clave not in grupos:
            grupos[clave] = [0.0, parte]
        grupos[clave][0] += signo * coeficiente
    resultado, cancelados = None, []
    sumandos = [(c, p) for c, p in grupos.values()] + [(constante, None)]
    for coeficiente, parte in sumandos:
        coeficiente = round(coeficiente, 12)
        if coeficiente == 0:
            if parte is not None:
                cancelados.append(parte)
            continue
        termino = _num(abs(coeficiente)) if parte is None else _producto(_num(abs(coeficiente)), parte)
        if resultado is None:
            resultado = termino if coeficiente > 0 else _neg(termino)
        else:
            resultado = ("bin", "+" if coeficiente > 0 else "-", resultado, termino, False)
    return (resultado if resultado is not None else _num(0)), cancelados


def _desarrollar(terminos):
    """Desarrolla los productos de polinomios cortos: x(x − 1) -> x² − x  (como en el cuaderno)."""
    resultado = []
    for signo, termino in terminos:
        p = _polinomio(termino) if termino[0] == "bin" and _tiene_x(termino) else None
        if p is not None:
            desarrollado = _terminos(_desde_polinomio(p), signo)
            if 1 < len(desarrollado) <= 4:
                resultado.extend(desarrollado)
                continue
        resultado.append((signo, termino))
    return resultado


def igualar_a_cero(izquierda, derecha):
    """Arbol de f(x) = izquierda − derecha, ya reducido, y la lista de terminos que al
    cancelarse quitarian una restriccion de dominio (ln x = ln x + x − 1 solo vale para x > 0)."""
    if _valor(derecha) == 0:
        arbol, cancelados = izquierda, []      # ya estaba igualada a cero: x³ − x − 2 = 0
    elif _valor(izquierda) == 0:
        arbol, cancelados = derecha, []        # 0 = x² − 4: se toma el lado derecho (mismas raices)
    else:
        terminos = _terminos(izquierda) + [(-s, t) for s, t in _terminos(derecha)]
        arbol, cancelados = _reducir(_desarrollar(terminos))
    p = _polinomio(arbol)
    if p is not None:
        # Polinomio: se desarrolla y se ordena por grado, como en el cuaderno: x(x − 1) − 2 = x² − x − 2.
        # Si al desarrollar salen muchos terminos ((x − 1)⁵ − 3) se deja como esta.
        ordenado = _desde_polinomio(p)
        if _cantidad_terminos(ordenado) <= max(_cantidad_terminos(arbol), 4):
            arbol = ordenado
    guardas = [parte for parte in cancelados if _dominio_restringido(parte)]
    if not _tiene_x(arbol):
        if _valor(arbol) == 0:
            raise ErrorFuncion("Al pasar todo a un lado queda 0 = 0: la igualdad se cumple para cualquier x"
                               + (" de su dominio" if guardas else "") + ", no hay una raíz que buscar.")
        raise ErrorFuncion(f"Al pasar todo a un lado queda {a_texto(arbol)} = 0, que nunca se cumple: "
                           "la ecuación no tiene solución.")
    return arbol, guardas


# Puntos donde se revisa que la funcion este definida en algun lugar (ln(−x² − 1) no lo esta en ninguno)
_PUNTOS_DOMINIO = sorted({k / 100 for k in range(-1000, 1001)}
                         | {signo * 10 ** (e / 4) for signo in (-1, 1) for e in range(-12, 25)})


class Funcion:
    """Funcion lista para evaluar, con su texto original y su version bonita.
    Acepta una expresion (x³ − x − 2) o una ecuacion (x³ = x + 2): en ese caso
    f(x) es el resultado de pasar todo al lado izquierdo y self.ecuacion guarda
    la ecuacion original para comprobar la raiz en los dos lados."""

    def __init__(self, texto, latex=False, nombre=r"f(x)", permitir_ecuacion=True, exigir_x=True):
        self.original = texto.strip()
        if latex:
            texto = latex_a_texto(texto)
        self.texto = texto
        self.normalizada = normalizar(texto)
        self.ecuacion = None
        self.avisos = []          # observaciones que no impiden usar la funcion
        self._inversas = []
        guardas = []
        if "=" in self.normalizada:
            if not permitir_ecuacion:
                raise ErrorFuncion("Aquí se escribe solo la expresión (sin el signo '=').")
            self.arbol, guardas = self._desde_ecuacion(self.normalizada)
        else:
            self.arbol = self._analizar(self.normalizada)
            if exigir_x and not _tiene_x(self.arbol):
                raise ErrorFuncion(f"La función no tiene x: f(x) = {a_texto(self.arbol)} es constante y no tiene "
                                   "una raíz que buscar. Escriba una expresión con x, por ejemplo x^2 - 4.")
        self._f = _compilar(self.arbol)
        self.mathtext = f"${nombre} = " + _mt(self.arbol)[0] + "$"
        self.javascript = _js(self.arbol)  # expresion en x para la grafica interactiva
        if guardas:
            # ln x = ln x + x − 1: al cancelar ln x quedaria f(x) = 1 − x, definida tambien para x ≤ 0.
            # f(x) se deja sin definir donde no lo estaba la ecuacion original, para no dar raices falsas.
            compiladas, sin_guarda = [_compilar(g) for g in guardas], self._f

            def con_dominio(x):
                for guarda in compiladas:
                    guarda(x)   # lanza ValueError / ZeroDivisionError fuera del dominio
                return sin_guarda(x)

            self._f = con_dominio
            self.javascript = "(" + self.javascript + "".join(f" + 0 * {_js(g)}" for g in guardas) + ")"
        self.legible = a_texto(self.arbol)
        self._derivada = None
        self._revisar(exigir_x)

    def _analizar(self, texto):
        analizador = _Analizador(tokenizar(texto))
        arbol = analizador.analizar()
        self._inversas += [par for par in analizador.inversas if par not in self._inversas]
        return arbol

    def _revisar(self, exigir_x):
        """Observaciones sobre lo escrito: notacion de inversa y dominio vacio."""
        for nombre, inversa in self._inversas:
            self.avisos.append(f"{nombre}⁻¹(x) se tomó como {inversa}(x), la función inversa (no como 1/{nombre}(x)). "
                               f"Para 1/{nombre}(x) escriba ({nombre} x)^(-1).")
        if exigir_x and not any(self.evaluar(x) is not None for x in _PUNTOS_DOMINIO):
            self.avisos.append("f(x) no da un número real en ningún punto probado entre −10⁶ y 10⁶ "
                               "(por ejemplo ln o √ de algo siempre negativo): revise la función.")

    def _desde_ecuacion(self, normalizada):
        izquierda_txt, _, derecha_txt = normalizada.partition("=")
        if not izquierda_txt.strip() or not derecha_txt.strip():
            lado = "izquierdo" if not izquierda_txt.strip() else "derecho"
            raise ErrorFuncion(f"Falta el lado {lado} de la ecuación. Ejemplo: sen(x) = -2x + 1")
        try:
            izquierda = self._analizar(izquierda_txt)
        except ErrorFuncion as error:
            raise ErrorFuncion(f"En el lado izquierdo de la ecuación: {error}") from None
        try:
            derecha = self._analizar(derecha_txt)
        except ErrorFuncion as error:
            raise ErrorFuncion(f"En el lado derecho de la ecuación: {error}") from None
        arbol, guardas = igualar_a_cero(izquierda, derecha)
        self.ecuacion = {
            "texto": f"{a_texto(izquierda)} = {a_texto(derecha)}",
            "izquierda": a_texto(izquierda),
            "derecha": a_texto(derecha),
            "resultado": f"f(x) = {a_texto(arbol)}",
        }
        self._lados = (_compilar(izquierda), _compilar(derecha))
        return arbol, guardas

    def evaluar_lados(self, x):
        """Valor de cada lado de la ecuacion original en x (para comprobar la solucion)."""
        if self.ecuacion is None:
            return None
        valores = []
        for lado in self._lados:
            try:
                valor = float(lado(float(x)))
            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                return None
            if math.isnan(valor) or math.isinf(valor):
                return None
            valores.append(valor)
        return tuple(valores)

    @classmethod
    def desde_arbol(cls, arbol, nombre=r"f^{\prime}(x)"):
        """Funcion armada directamente desde un arbol (por ejemplo, el de una derivada)."""
        funcion = cls.__new__(cls)
        funcion.arbol = arbol
        funcion.legible = funcion.texto = funcion.original = a_texto(arbol)
        funcion.normalizada = None
        funcion.ecuacion = None
        funcion.avisos = []
        funcion._f = _compilar(arbol)
        funcion.mathtext = f"${nombre} = " + _mt(arbol)[0] + "$"
        funcion.javascript = _js(arbol)
        funcion._derivada = None
        return funcion

    def derivada(self):
        """f'(x) calculada con las reglas de derivacion (se guarda para no repetir el calculo)."""
        if self._derivada is None:
            self._derivada = Funcion.desde_arbol(derivar(self.arbol))
        return self._derivada

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
