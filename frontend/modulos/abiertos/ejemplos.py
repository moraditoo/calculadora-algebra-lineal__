# frontend/modulos/abiertos/ejemplos.py
# Ejemplos resueltos de los metodos abiertos (los de la presentacion de clase y otros que
# muestran cuando el metodo falla). El rango de la grafica se busca solo.
#   latex -> como se carga en el editor matematico
#   texto -> como se muestra en la tarjeta
EJEMPLOS_NEWTON = [
    {
        "titulo": "Ejemplo de clase",
        "detalle": "El de la presentación: f'(x) = 3x² − 1, converge en 3 iteraciones",
        "latex": "x^3-x-2", "texto": "x³ − x − 2", "x0": 1.5,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Actividad colaborativa 1",
        "detalle": "x³ − 2x − 5 = 0 con x₀ = 2",
        "latex": "x^3-2x-5", "texto": "x³ − 2x − 5", "x0": 2.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Raíz cuadrada de 2",
        "detalle": "√2 como raíz de x² − 2 (f'(x) = 2x)",
        "latex": "x^2-2", "texto": "x² − 2", "x0": 1.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Trigonométrica",
        "detalle": "cos x = x, f'(x) = −sen(x) − 1",
        "latex": "\\cos\\left(x\\right)-x", "texto": "cos(x) − x", "x0": 1.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Exponencial",
        "detalle": "e⁻ˣ = x, residuo |f(x)| < E",
        "latex": "e^{-x}-x", "texto": "e⁻ˣ − x", "x0": 0.0,
        "tolerancia": "0.000001", "criterio": "residuo",
    },
    {
        "titulo": "Logaritmo",
        "detalle": "ln x + x − 2, f'(x) = 1/x + 1",
        "latex": "\\ln\\left(x\\right)+x-2", "texto": "ln(x) + x − 2", "x0": 1.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Raíz múltiple",
        "detalle": "(x − 1)²: f'(raíz) = 0, la convergencia es lenta",
        "latex": "x^2-2x+1", "texto": "x² − 2x + 1", "x0": 2.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "No converge (ciclo)",
        "detalle": "Con x₀ = 0 las aproximaciones saltan entre 0 y 1",
        "latex": "x^3-2x+2", "texto": "x³ − 2x + 2", "x0": 0.0,
        "tolerancia": "0.000001", "criterio": "absoluto", "max_iteraciones": "20",
    },
    {
        "titulo": "Diverge",
        "detalle": "arctan x con x₀ = 1.5: cada tangente lo aleja más",
        "latex": "\\arctan\\left(x\\right)", "texto": "arctan(x)", "x0": 1.5,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
]

EJEMPLOS_SECANTE = [
    {
        "titulo": "Ejemplo de clase",
        "detalle": "El de la presentación: x₀ = 1, x₁ = 2",
        "latex": "x^3-x-2", "texto": "x³ − x − 2", "x0": 1.0, "x1": 2.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Práctica integradora",
        "detalle": "x³ − 2x − 5 = 0 con x₀ = 2 y x₁ = 3",
        "latex": "x^3-2x-5", "texto": "x³ − 2x − 5", "x0": 2.0, "x1": 3.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Raíz cuadrada de 2",
        "detalle": "√2 como raíz de x² − 2",
        "latex": "x^2-2", "texto": "x² − 2", "x0": 1.0, "x1": 2.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Trigonométrica",
        "detalle": "cos x = x sin derivar",
        "latex": "\\cos\\left(x\\right)-x", "texto": "cos(x) − x", "x0": 0.0, "x1": 1.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Exponencial",
        "detalle": "e⁻ˣ = x, residuo |f(x)| < E",
        "latex": "e^{-x}-x", "texto": "e⁻ˣ − x", "x0": 0.0, "x1": 1.0,
        "tolerancia": "0.000001", "criterio": "residuo",
    },
    {
        "titulo": "Logaritmo",
        "detalle": "ln x + x − 2",
        "latex": "\\ln\\left(x\\right)+x-2", "texto": "ln(x) + x − 2", "x0": 1.0, "x1": 2.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Sin encerrar la raíz",
        "detalle": "x₀ = 3, x₁ = 4: f(x₀)·f(x₁) > 0 y aun así converge",
        "latex": "x^3-x-2", "texto": "x³ − x − 2", "x0": 3.0, "x1": 4.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
    {
        "titulo": "Raíz múltiple",
        "detalle": "(x − 1)²: la secante también se vuelve lenta",
        "latex": "x^2-2x+1", "texto": "x² − 2x + 1", "x0": 2.0, "x1": 3.0,
        "tolerancia": "0.000001", "criterio": "absoluto",
    },
]
