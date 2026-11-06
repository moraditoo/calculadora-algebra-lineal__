# backend/sistemas_numericos/romanos.py
import re

class OperacionesRomanos:
    # Tabla de equivalencias ordenadas para descomposicion posicional
    TABLA_CONVERSION = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]

    # Expresion regular para validar sintaxis estricta de numeros romanos
    REGEX_ROMANO = r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

    @classmethod
    def validar_romano(cls, s):
        texto = s.strip().upper()
        # Validar cadena no vacia
        if not texto:
            raise ValueError("El campo del numero romano no puede estar vacio.")
        # Validar caracteres permitidos
        caracteres_validos = set("MDCLXVI")
        if not set(texto).issubset(caracteres_validos):
            raise ValueError(f"Caracteres invalidos en '{texto}'. Solo se admiten M, D, C, L, X, V, I.")
        # Validar reglas de formacion y repeticion gramatical romana
        if not re.match(cls.REGEX_ROMANO, texto):
            raise ValueError(f"'{texto}' no cumple las reglas de formacion de numerales romanos.")
        return texto

    @classmethod
    def romano_a_arabigo(cls, texto_romano):
        rom = cls.validar_romano(texto_romano)
        valores = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
        total = 0
        i = 0
        pasos = []
        # Evaluar pares sustractivos o valores directos
        while i < len(rom):
            val_actual = valores[rom[i]]
            if i + 1 < len(rom) and valores[rom[i + 1]] > val_actual:
                val_sig = valores[rom[i + 1]]
                par = rom[i:i+2]
                resta = val_sig - val_actual
                total += resta
                pasos.append(f"Par sustractivo {par}: {val_sig} - {val_actual} = {resta}")
                i += 2
            else:
                total += val_actual
                pasos.append(f"Simbolo {rom[i]} = {val_actual}")
                i += 1
        return total, pasos

    @classmethod
    def arabigo_a_romano(cls, n):
        # Validar rango numerico estandar
        if not isinstance(n, int):
            raise ValueError("El valor debe ser un numero entero.")
        if n <= 0:
            raise ValueError("El sistema romano no contempla el numero cero ni valores negativos.")
        if n > 3999:
            raise ValueError(f"El valor {n} excede el limite estandar de la numeracion romana (maximo 3999).")
        resto = n
        resultado = ""
        desglose = []
        # Descomposicion por valores posicionales
        for val, rom in cls.TABLA_CONVERSION:
            while resto >= val:
                resultado += rom
                resto -= val
                desglose.append(f"{val} -> {rom}")
        return resultado, desglose

    @classmethod
    def resolver_entrada(cls, entrada):
        s = str(entrada).strip().upper()
        if not s:
            raise ValueError("Ingrese un valor numerico o romano.")
        # Deteccion de arabigo
        if s.isdigit():
            val = int(s)
            rom, _ = cls.arabigo_a_romano(val)
            return val, rom
        # Deteccion de romano
        val, _ = cls.romano_a_arabigo(s)
        return val, s

    @classmethod
    def suma(cls, a_input, b_input):
        val_a, rom_a = cls.resolver_entrada(a_input)
        val_b, rom_b = cls.resolver_entrada(b_input)
        total = val_a + val_b
        # Validar desbordamiento superior
        if total > 3999:
            raise ValueError(f"La suma ({total}) supera el limite representable de 3999.")
        rom_total, _ = cls.arabigo_a_romano(total)
        pasos = [
            f"1. Identificacion de operandos: {rom_a} ({val_a}) y {rom_b} ({val_b}).",
            f"2. Suma aritmetica equivalente: {val_a} + {val_b} = {total}.",
            f"3. Conversion posicional a romano: {total} = {rom_total}."
        ]
        return {
            "romano_a": rom_a,
            "romano_b": rom_b,
            "resultado_romano": rom_total,
            "resultado_arabigo": total,
            "pasos": pasos
        }

    @classmethod
    def resta(cls, a_input, b_input):
        val_a, rom_a = cls.resolver_entrada(a_input)
        val_b, rom_b = cls.resolver_entrada(b_input)
        # Salida anticipada si el minuendo es menor o igual al sustraendo
        if val_a <= val_b:
            raise ValueError(
                f"Resta invalida ({rom_a} - {rom_b}): El minuendo ({val_a}) debe ser estrictamente mayor "
                f"que el sustraendo ({val_b}) porque los romanos no usaban el cero ni negativos."
            )
        total = val_a - val_b
        rom_total, _ = cls.arabigo_a_romano(total)
        pasos = [
            f"1. Identificacion de operandos: {rom_a} ({val_a}) y {rom_b} ({val_b}).",
            f"2. Validacion de existencia positiva: {val_a} > {val_b}.",
            f"3. Resta aritmetica: {val_a} - {val_b} = {total}.",
            f"4. Numeral romano resultante: {total} = {rom_total}."
        ]
        return {
            "romano_a": rom_a,
            "romano_b": rom_b,
            "resultado_romano": rom_total,
            "resultado_arabigo": total,
            "pasos": pasos
        }

    @classmethod
    def multiplicacion(cls, a_input, b_input):
        val_a, rom_a = cls.resolver_entrada(a_input)
        val_b, rom_b = cls.resolver_entrada(b_input)
        total = val_a * val_b
        if total > 3999:
            raise ValueError(f"El producto ({total}) excede el limite estandar romano de 3999.")
        rom_total, _ = cls.arabigo_a_romano(total)
        # Definicion de multiplicacion como sumas repetidas sucesivas
        if val_b <= 8:
            representacion_suma = " + ".join([rom_a] * val_b)
            representacion_num = " + ".join([str(val_a)] * val_b)
        else:
            representacion_suma = f"{rom_a} + {rom_a} + ... + {rom_a} ({val_b} veces)"
            representacion_num = f"{val_a} + {val_a} + ... + {val_a} ({val_b} sumandos)"
        pasos = [
            f"1. Factores: {rom_a} ({val_a}) multiplicado por {rom_b} ({val_b}).",
            f"2. Definicion formal de multiplicacion como suma repetida:",
            f"   {rom_a} × {rom_b} = {representacion_suma}",
            f"3. Evaluacion aritmetica: {representacion_num} = {total}.",
            f"4. Conversion a numeral romano: {total} = {rom_total}."
        ]
        return {
            "romano_a": rom_a,
            "romano_b": rom_b,
            "resultado_romano": rom_total,
            "resultado_arabigo": total,
            "pasos": pasos
        }

    @classmethod
    def conversion_bidireccional(cls, entrada):
        s = str(entrada).strip().upper()
        if not s:
            raise ValueError("Por favor ingrese un valor para convertir.")
        # Rama arabigo a romano
        if s.isdigit():
            val = int(s)
            rom, desglose = cls.arabigo_a_romano(val)
            return {
                "direccion": "Arabigo a Romano",
                "entrada": str(val),
                "resultado": rom,
                "pasos": desglose
            }
        # Rama romano a arabigo
        val, pasos = cls.romano_a_arabigo(s)
        return {
            "direccion": "Romano a Arabigo",
            "entrada": s,
            "resultado": str(val),
            "pasos": pasos
        }