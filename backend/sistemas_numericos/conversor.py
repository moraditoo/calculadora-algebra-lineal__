# backend/sistemas_numericos/conversor.py

class ConversorSistemas:
    TABLA_OCT_BIN = {
        '0': '000', '1': '001', '2': '010', '3': '011',
        '4': '100', '5': '101', '6': '110', '7': '111'
    }
    TABLA_BIN_OCT = {v: k for k, v in TABLA_OCT_BIN.items()}

    TABLA_HEX_BIN = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011',
        '4': '0100', '5': '0101', '6': '0110', '7': '0111',
        '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
        'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
    }
    TABLA_BIN_HEX = {v: k for k, v in TABLA_HEX_BIN.items()}

    @classmethod
    def validar_entrada(cls, num_str, base_nombre):
        s = num_str.strip().upper()
        if not s:
            raise ValueError("El campo numérico no puede estar vacío.")

        bases_validas = {
            "Binario": ("01", 2),
            "Octal": ("01234567", 8),
            "Decimal": ("0123456789", 10),
            "Hexadecimal": ("0123456789ABCDEF", 16)
        }

        if base_nombre not in bases_validas:
            raise ValueError(f"Base '{base_nombre}' no soportada.")

        permitidos, base_num = bases_validas[base_nombre]
        for car in s:
            if car not in permitidos:
                raise ValueError(
                    f"Carácter inválido '{car}' para base {base_nombre} ({base_num}). "
                    f"Dígitos permitidos: {permitidos}"
                )
        return s

    @classmethod
    def a_decimal(cls, num_str, base):
        digitos = "0123456789ABCDEF"
        total = 0
        potencias = []
        productos = []
        n = len(num_str)

        for i, c in enumerate(num_str):
            pot = n - 1 - i
            val = digitos.index(c)
            total += val * (base ** pot)
            potencias.append(f"{val}×{base}^{pot}")
            productos.append(f"{val * (base ** pot)}")

        return total, " + ".join(potencias), " + ".join(productos)

    @classmethod
    def de_decimal(cls, val_dec, base):
        if val_dec == 0:
            return "0", ["0 ÷ {} = 0 (Cociente: 0, Resto: 0)".format(base)]

        digitos = "0123456789ABCDEF"
        temp = val_dec
        res = ""
        divisiones = []

        while temp > 0:
            cociente = temp // base
            resto = temp % base
            char_resto = digitos[resto]
            divisiones.append(f"{temp}/{base} = {cociente}, resto = {char_resto}")
            res = char_resto + res
            temp = cociente

        return res, divisiones

    @classmethod
    def convertir(cls, num_str, origen, destino):
        s = cls.validar_entrada(num_str, origen)
        bases = {"Decimal": 10, "Binario": 2, "Octal": 8, "Hexadecimal": 16}
        subindices = {"Decimal": "10", "Binario": "2", "Octal": "8", "Hexadecimal": "16"}

        b_in = bases[origen]
        b_out = bases[destino]

        # Equivalencias simultáneas en todas las bases para el recuadro inferior
        val_dec_global, _, _ = cls.a_decimal(s, b_in)
        otras_bases = {
            "Binario": cls.de_decimal(val_dec_global, 2)[0] if val_dec_global > 0 else "0",
            "Octal": cls.de_decimal(val_dec_global, 8)[0] if val_dec_global > 0 else "0",
            "Decimal": str(val_dec_global),
            "Hexadecimal": cls.de_decimal(val_dec_global, 16)[0] if val_dec_global > 0 else "0"
        }

        # Misma base
        if origen == destino:
            return {
                "resultado": s,
                "encabezado": f"({s})_{subindices[origen]} = ({s})_{subindices[destino]}",
                "pasos": [
                    f"El número ya se encuentra en la base seleccionada ({origen}).",
                    f"Resultado: ({s})_{subindices[destino]}"
                ],
                "otras_bases": otras_bases
            }

        pasos = []
        resultado_final = ""

        # =========================================================================
        # 1. BINARIO A OCTAL (Agrupación directa de 3 en 3 bits desde la derecha)
        # =========================================================================
        if origen == "Binario" and destino == "Octal":
            faltantes = (3 - (len(s) % 3)) % 3
            bin_padd = ("0" * faltantes) + s
            bloques_3 = [bin_padd[i:i+3] for i in range(0, len(bin_padd), 3)]

            pasos.append(f"Paso 1: Escribe el número binario:\n({bin_padd})_2")
            pasos.append(
                f"Agrupar los dígitos en conjuntos de tres comenzando del LSB (derecha) "
                f"añadiendo ceros a la izquierda del último dígito si no hay suficientes dígitos para hacer un conjunto de tres:\n\n"
                f"{' '.join(bloques_3)}"
            )

            desglose = [f"{b}={cls.TABLA_BIN_OCT[b]}" for b in bloques_3]
            resultado_final = "".join([cls.TABLA_BIN_OCT[b] for b in bloques_3]).lstrip('0') or "0"

            pasos.append(
                f"Paso 2: Utilice la tabla siguiente para convertir cada conjunto de tres en un dígito octal. En este caso:\n\n"
                f"{', '.join(desglose)}.\n\n"
                f"Así, el número {s} en binario es equivalente a {resultado_final} en octal."
            )
            pasos.append(
                "Para pasar de binario a octal utilice la tabla siguiente:\n"
                "Bin:   000  001  010  011  100  101  110  111\n"
                "Octal:   0    1    2    3    4    5    6    7"
            )

        # =========================================================================
        # 2. OCTAL A BINARIO (Expansión directa de cada dígito a 3 bits)
        # =========================================================================
        elif origen == "Octal" and destino == "Binario":
            pasos.append(
                "Paso 1: Busque cada dígito octal para obtener el grupo equivalente de tres dígitos binarios. "
                "Puede usar la tabla siguiente para realizar estas conversiones."
            )
            pasos.append(
                "Tabla de conversión octal a binario:\n"
                "Oct:   0    1    2    3    4    5    6    7\n"
                "Bin: 000  001  010  011  100  101  110  111"
            )

            desglose = [f"({d})_8 = ({cls.TABLA_OCT_BIN[d]})_2" for d in s]
            pasos.append("\n".join(desglose))

            bin_agrupado = " ".join([cls.TABLA_OCT_BIN[d] for d in s])
            bin_raw = "".join([cls.TABLA_OCT_BIN[d] for d in s])
            resultado_final = bin_raw.lstrip('0') or "0"

            pasos.append(
                f"Paso 2: Agrupe cada valor del paso 1 para hacer un número binario:\n\n"
                f"{bin_agrupado}\n\n"
                f"Así, ({resultado_final})_2 es el equivalente binario a ({s})_8 (respuesta)."
            )

        # =========================================================================
        # 3. BINARIO A HEXADECIMAL (Agrupación directa de 4 en 4 bits)
        # =========================================================================
        elif origen == "Binario" and destino == "Hexadecimal":
            faltantes = (4 - (len(s) % 4)) % 4
            bin_padd = ("0" * faltantes) + s
            bloques_4 = [bin_padd[i:i+4] for i in range(0, len(bin_padd), 4)]

            pasos.append(f"Paso 1: Escriba el número binario:\n({bin_padd})_2")
            pasos.append(
                f"Agrupe todos los dígitos del binario en conjuntos de cuatro comenzando por el LSB (extremo derecho)"
                + (f", agregando {faltantes} cero(s) a la izquierda:" if faltantes > 0 else ":")
                + f"\n\n{' '.join(bloques_4)}"
            )

            desglose = [f"{b}={cls.TABLA_BIN_HEX[b]}" for b in bloques_4]
            resultado_final = "".join([cls.TABLA_BIN_HEX[b] for b in bloques_4]).lstrip('0') or "0"

            pasos.append(
                f"Paso 2: Convierta cada grupo de cuatro al correspondiente hexadecimal:\n\n"
                f"{', '.join(desglose)}.\n\n"
                f"Así, {s} en binario es equivalente a {resultado_final} en hexadecimal."
            )
            pasos.append(
                "Tabla de conversión binario a hexadecimal:\n"
                "Bin:  0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111\n"
                "Hexa:    0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F"
            )

        # =========================================================================
        # 4. HEXADECIMAL A BINARIO (Expansión de cada símbolo a 4 bits)
        # =========================================================================
        elif origen == "Hexadecimal" and destino == "Binario":
            pasos.append(
                "Paso 1: Busque cada dígito hexadecimal para obtener su equivalente en cuatro dígitos binarios."
            )
            desglose = [f"({d})_16 = ({cls.TABLA_HEX_BIN[d]})_2" for d in s]
            pasos.append("\n".join(desglose))

            bin_agrupado = " ".join([cls.TABLA_HEX_BIN[d] for d in s])
            bin_raw = "".join([cls.TABLA_HEX_BIN[d] for d in s])
            resultado_final = bin_raw.lstrip('0') or "0"

            pasos.append(
                f"Paso 2: Agrupe cada cuarteto obtenido:\n\n"
                f"{bin_agrupado}\n\n"
                f"Así, ({resultado_final})_2 es el equivalente binario al número hexadecimal ({s})_16."
            )

        # =========================================================================
        # 5. OCTAL A HEXADECIMAL (Octal -> 3 bits -> Cuartetos de 4 bits -> Hexa)
        # =========================================================================
        elif origen == "Octal" and destino == "Hexadecimal":
            pasos.append(
                "Paso 1: Busca cada dígito octal para obtener el grupo equivalente de tres dígitos binarios. "
                "Puedes usar la tabla a continuación para realizar estas conversiones.\n"
                "Tabla de conversión octal a binario:\n"
                "Oct:   0    1    2    3    4    5    6    7\n"
                "Bin: 000  001  010  011  100  101  110  111"
            )

            desglose_oct = [f"({d})_8 = ({cls.TABLA_OCT_BIN[d]})_2" for d in s]
            pasos.append("\n".join(desglose_oct))

            bin_agrupado = " ".join([cls.TABLA_OCT_BIN[d] for d in s])
            bin_raw = "".join([cls.TABLA_OCT_BIN[d] for d in s])
            pasos.append(
                f"Paso 2: Agrupe cada valor del paso 1 para hacer un número binario.\n\n"
                f"{bin_agrupado}\n"
                f"({s})_8 = ({bin_raw})_2"
            )

            faltantes = (4 - (len(bin_raw) % 4)) % 4
            bin_padd = ("0" * faltantes) + bin_raw
            bloques_4 = [bin_padd[i:i+4] for i in range(0, len(bin_padd), 4)]

            pasos.append(
                f"Paso 3: Ahora convierta el número binario del paso 2 en hexa agrupando todos los dígitos del "
                f"binario en conjuntos de cuatro comenzando por el LSB (extremo derecho).\n\n"
                f"{' '.join(bloques_4)}\n\n"
                + (f"Nota: agregue ceros a la izquierda del último dígito si no hay suficientes dígitos para formar un conjunto de cuatro." if faltantes > 0 else "")
            )

            desglose_hex = [f"{b}={cls.TABLA_BIN_HEX[b]}" for b in bloques_4]
            resultado_final = "".join([cls.TABLA_BIN_HEX[b] for b in bloques_4]).lstrip('0') or "0"

            pasos.append(
                f"Paso 4: Convierta cada grupo de cuatro al correspondiente hexadecimal (use la tabla a continuación):\n\n"
                f"{', '.join(desglose_hex)}.\n\n"
                f"Así, {s} en octal es equivalente a {resultado_final} en hexadecimal."
            )
            pasos.append(
                "Para convertir de formato binario a hexadecimal, use la siguiente tabla:\n"
                "Bin:  0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111\n"
                "Hexa:    0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F"
            )

        # =========================================================================
        # 6. HEXADECIMAL A OCTAL (Hexa -> 4 bits -> Ternas de 3 bits -> Octal)
        # =========================================================================
        elif origen == "Hexadecimal" and destino == "Octal":
            pasos.append("Paso 1: Convierta cada dígito hexadecimal en cuatro dígitos binarios:")
            desglose_hex = [f"({d})_16 = ({cls.TABLA_HEX_BIN[d]})_2" for d in s]
            pasos.append("\n".join(desglose_hex))

            bin_raw = "".join([cls.TABLA_HEX_BIN[d] for d in s])
            pasos.append(f"Paso 2: Concatene el valor binario resultante: ({bin_raw})_2")

            faltantes = (3 - (len(bin_raw) % 3)) % 3
            bin_padd = ("0" * faltantes) + bin_raw
            bloques_3 = [bin_padd[i:i+3] for i in range(0, len(bin_padd), 3)]

            pasos.append(
                f"Paso 3: Reagrupe en bloques de tres dígitos comenzando desde la derecha (LSB):\n\n"
                f"{' '.join(bloques_3)}"
                + (f" (agregando {faltantes} cero(s) a la izquierda)" if faltantes > 0 else "")
            )

            desglose_oct = [f"{b}={cls.TABLA_BIN_OCT[b]}" for b in bloques_3]
            resultado_final = "".join([cls.TABLA_BIN_OCT[b] for b in bloques_3]).lstrip('0') or "0"

            pasos.append(
                f"Paso 4: Convierta cada terna en su correspondiente dígito octal:\n\n"
                f"{', '.join(desglose_oct)}.\n\n"
                f"Así, {s} en hexadecimal es equivalente a {resultado_final} en octal."
            )

        # =========================================================================
        # 7. CUALQUIER BASE A DECIMAL (Combinación Lineal Ponderada)
        # =========================================================================
        elif destino == "Decimal":
            val_dec, paso_pot, paso_prod = cls.a_decimal(s, b_in)
            nombre_base = "binario" if b_in == 2 else "octal" if b_in == 8 else "hexadecimal"

            pasos.append(f"Paso 1: Escribe el número {nombre_base}:\n\n{s}")
            pasos.append(
                f"Paso 2: Multiplica cada dígito del número {nombre_base} por la potencia correspondiente de {b_in} (Combinación Lineal):\n\n"
                f"{paso_pot}"
            )
            pasos.append(f"Paso 3: Resuelve las potencias:\n\n{paso_prod}")
            
            resultado_final = str(val_dec)
            pasos.append(
                f"Paso 4: Suma los números escritos arriba:\n\n"
                f"{paso_prod} = {resultado_final}.\n\n"
                f"Este es el equivalente decimal al número {nombre_base} {s}."
            )

        # =========================================================================
        # 8. DECIMAL A CUALQUIER BASE (Divisiones Sucesivas)
        # =========================================================================
        elif origen == "Decimal":
            val_dec = int(s)
            nombre_dest = "binario" if b_out == 2 else "octal" if b_out == 8 else "hexadecimal"
            res_base, divisiones = cls.de_decimal(val_dec, b_out)

            pasos.append(f"Paso 1: Divida ({s})_10 sucesivamente por {b_out} hasta que el cociente sea igual a 0:\n\n" + "\n".join(divisiones))
            resultado_final = res_base
            pasos.append(
                f"Paso 2: Lee de abajo hacia arriba como {resultado_final}. "
                f"Este es el equivalente {nombre_dest} al número decimal {s} (Respuesta)."
            )

        return {
            "resultado": resultado_final,
            "encabezado": f"({s})_{subindices[origen]} = ({resultado_final})_{subindices[destino]}",
            "pasos": pasos,
            "otras_bases": otras_bases
        }