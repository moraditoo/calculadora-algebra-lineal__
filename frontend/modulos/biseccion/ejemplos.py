# frontend/modulos/biseccion/ejemplos.py
# Ejemplos resueltos de biseccion. Cada uno trae la funcion, el rango de la grafica
# (elegido para que la tabulacion encuentre justo el intervalo [a, b] del ejemplo),
# la precision E y el criterio de parada.
#   latex -> como se carga en el editor matematico
#   texto -> como se muestra en la tarjeta
EJEMPLOS = [
    {
        "titulo": "Ejemplo de clase",
        "detalle": "El de la hoja de cálculo: error = |f(c)|",
        "latex": "x^4-5x^3+0.5x^2-11x+10", "texto": "x⁴ − 5x³ + 0.5x² − 11x + 10",
        "x_min": "-1.8", "x_max": "6.2", "subintervalos": "20", "a": 0.6, "b": 1.0,
        "tolerancia": "0.0001", "criterio": "funcion",
    },
    {
        "titulo": "Polinomio cúbico",
        "detalle": "Una sola raíz real, error absoluto",
        "latex": "x^3+4x^2-10", "texto": "x³ + 4x² − 10",
        "x_min": "-3", "x_max": "3", "subintervalos": "6", "a": 1.0, "b": 2.0,
        "tolerancia": "0.0001", "criterio": "absoluto",
    },
    {
        "titulo": "Exponencial",
        "detalle": "e⁻ˣ = x, error relativo porcentual",
        "latex": "e^{-x}-x", "texto": "e⁻ˣ − x",
        "x_min": "-1", "x_max": "3", "subintervalos": "4", "a": 0.0, "b": 1.0,
        "tolerancia": "0.01", "criterio": "porcentual",
    },
    {
        "titulo": "Trigonométrica",
        "detalle": "cos x = x, longitud del intervalo",
        "latex": "\\cos\\left(x\\right)-x", "texto": "cos(x) − x",
        "x_min": "-2", "x_max": "3", "subintervalos": "5", "a": 0.0, "b": 1.0,
        "tolerancia": "0.00001", "criterio": "intervalo",
    },
    {
        "titulo": "Raíz cuadrada de 3",
        "detalle": "√3 como raíz de x² − 3 (dos intervalos)",
        "latex": "x^2-3", "texto": "x² − 3",
        "x_min": "-3", "x_max": "3", "subintervalos": "6", "a": 1.0, "b": 2.0,
        "tolerancia": "0.00001", "criterio": "absoluto",
    },
    {
        "titulo": "Logaritmo",
        "detalle": "ln x no existe para x ≤ 0, error relativo",
        "latex": "\\ln\\left(x\\right)+x-2", "texto": "ln(x) + x − 2",
        "x_min": "-1", "x_max": "4", "subintervalos": "5", "a": 1.0, "b": 2.0,
        "tolerancia": "0.0001", "criterio": "relativo",
    },
    {
        "titulo": "Tres raíces",
        "detalle": "eˣ − 3x² cruza el eje tres veces",
        "latex": "e^{x}-3x^2", "texto": "eˣ − 3x²",
        "x_min": "-1", "x_max": "4", "subintervalos": "10", "a": 3.5, "b": 4.0,
        "tolerancia": "0.0001", "criterio": "absoluto",
    },
    {
        "titulo": "Ecuación de Wallis",
        "detalle": "x³ − 2x − 5, error absoluto",
        "latex": "x^3-2x-5", "texto": "x³ − 2x − 5",
        "x_min": "-3", "x_max": "4", "subintervalos": "7", "a": 2.0, "b": 3.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Con asíntotas",
        "detalle": "tan x − 2: los saltos no son raíces",
        "latex": "\\tan\\left(x\\right)-2", "texto": "tan(x) − 2",
        "x_min": "0", "x_max": "5", "subintervalos": "10", "a": 1.0, "b": 1.5,
        "tolerancia": "0.0001", "criterio": "absoluto",
    },
]
