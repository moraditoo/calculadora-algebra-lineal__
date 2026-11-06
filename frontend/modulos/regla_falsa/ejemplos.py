# frontend/modulos/regla_falsa/ejemplos.py
# Ejemplos resueltos de regla falsa (los de la presentacion de clase). Cada uno trae la
# funcion, el rango de la grafica (elegido para que la tabulacion encuentre justo el
# intervalo [a, b] del ejemplo), la precision E, el criterio y si usa la variante modificada.
#   latex -> como se carga en el editor matematico
#   texto -> como se muestra en la tarjeta
EJEMPLOS = [
    {
        "titulo": "Ejemplo de clase",
        "detalle": "El de la presentación: converge en 4 iteraciones",
        "latex": "x^3-4.23603x^2-2.73620x-13.09037", "texto": "x³ − 4.23603x² − 2.7362x − 13.09037",
        "x_min": "-1.1", "x_max": "7.7", "subintervalos": "16", "a": 4.95, "b": 5.5,
        "tolerancia": "0.0001", "criterio": "relativo",
    },
    {
        "titulo": "Comparar con bisección",
        "detalle": "La función del ejemplo de bisección (13 iteraciones)",
        "latex": "x^4-5x^3+0.5x^2-11x+10", "texto": "x⁴ − 5x³ + 0.5x² − 11x + 10",
        "x_min": "-1.65", "x_max": "6.05", "subintervalos": "14", "a": 0.55, "b": 1.1,
        "tolerancia": "0.0001", "criterio": "relativo",
    },
    {
        "titulo": "Convergencia lenta",
        "detalle": "x¹⁰ − 1: un extremo se estanca (unilateral)",
        "latex": "x^{10}-1", "texto": "x¹⁰ − 1",
        "x_min": "-1.3", "x_max": "1.3", "subintervalos": "2", "a": 0.0, "b": 1.3,
        "tolerancia": "0.01", "criterio": "porcentual",
    },
    {
        "titulo": "Falsa posición modificada",
        "detalle": "x¹⁰ − 1 dividiendo f a la mitad en el extremo estancado",
        "latex": "x^{10}-1", "texto": "x¹⁰ − 1",
        "x_min": "-1.3", "x_max": "1.3", "subintervalos": "2", "a": 0.0, "b": 1.3,
        "tolerancia": "0.01", "criterio": "porcentual", "modificada": True,
    },
    {
        "titulo": "Exponencial",
        "detalle": "e⁻ˣ = x, error relativo porcentual",
        "latex": "e^{-x}-x", "texto": "e⁻ˣ − x",
        "x_min": "-1", "x_max": "3", "subintervalos": "4", "a": 0.0, "b": 1.0,
        "tolerancia": "0.01", "criterio": "porcentual",
    },
    {
        "titulo": "Logaritmo",
        "detalle": "ln x desde [0.5, 5], como en la presentación",
        "latex": "\\ln\\left(x\\right)", "texto": "ln(x)",
        "x_min": "0.5", "x_max": "9.5", "subintervalos": "2", "a": 0.5, "b": 5.0,
        "tolerancia": "0.0001", "criterio": "relativo",
    },
    {
        "titulo": "Trigonométrica",
        "detalle": "cos x = x, error absoluto",
        "latex": "\\cos\\left(x\\right)-x", "texto": "cos(x) − x",
        "x_min": "-2", "x_max": "3", "subintervalos": "5", "a": 0.0, "b": 1.0,
        "tolerancia": "0.00001", "criterio": "absoluto",
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
        "detalle": "tan x − 2: discontinua, se resuelve en un tramo continuo",
        "latex": "\\tan\\left(x\\right)-2", "texto": "tan(x) − 2",
        "x_min": "0", "x_max": "5", "subintervalos": "10", "a": 1.0, "b": 1.5,
        "tolerancia": "0.0001", "criterio": "absoluto",
    },
]
