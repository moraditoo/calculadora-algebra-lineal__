# Calculadora de álgebra lineal y métodos numéricos

Todo el programa está en Python y separado en `backend/` (cálculos) y `frontend/` (interfaz).
La interfaz usa NiceGUI con un tema de vidrio líquido blanco; las gráficas se hacen con matplotlib y ECharts,
y las fórmulas con KaTeX. Todas las librerías del navegador vienen incluidas: funciona sin internet.

## Instalación y uso

```
pip install -r requirements.txt
python main.py
```

Se abre el navegador en http://localhost:8080.

## Módulos (barra lateral)

| Grupo | Módulo |
| --- | --- |
| Métodos numéricos | Método de Bisección · Método de Regla Falsa · Newton-Raphson · Método de la Secante |
| Álgebra lineal | Sistemas lineales (Gauss-Jordan, Gauss, pivoteo) · Jacobi y Gauss-Seidel · Vectores Rⁿ · Matrices |
| Sistemas numéricos | Conversor de bases · Números romanos |

## Sistemas de ecuaciones lineales

Se escribe el sistema tal como viene en el ejercicio, una ecuación por línea (`-3x - y + 4z + 5w = -6`), o la matriz
aumentada [A | B]. Acepta x, y, z, w (en ese orden) o x1, x2… / x₁, x₂…, fracciones, decimales, variables en los dos
lados y signos copiados de un PDF (−). El resultado muestra primero lo importante:

1. **Solución** con números animados (o la solución general si hay infinitas, o "sin solución").
2. **Forma matricial A·X = B** dibujada con KaTeX y **det(A)**: si det(A) ≠ 0 la solución es única.
3. **Comprobación** sustituyendo en cada ecuación original.
4. **Procedimiento** (plegado): cada operación por fila con la fila que cambió resaltada.

Los tres métodos comparten el mismo código (`backend/algebra_lineal/sistemas.py`): Gauss solo intercambia filas si el
pivote es cero, el pivoteo parcial sube la fila de mayor |valor| y Gauss-Jordan llega a la forma escalonada reducida.

## Jacobi y Gauss-Seidel

Métodos iterativos para A·x = b, como en la presentación de clase. Se escribe el sistema (o la matriz), x⁽⁰⁾ (vacío =
vector cero), la tolerancia ε, el máximo de iteraciones y el criterio de parada: cambio ‖x⁽ᵏ⁺¹⁾ − x⁽ᵏ⁾‖∞ < ε,
residuo ‖b − Ax‖∞ < ε o ambos. Se puede ejecutar un método o **comparar ambos**.

- **Convergencia:** tabla de dominancia diagonal |aᵢᵢ| > Σ|aᵢⱼ| y radio espectral ρ(T) de cada método (converge si
  ρ < 1). Si el sistema no es diagonalmente dominante, se **reordenan las ecuaciones** (se puede desactivar): primero se
  busca un orden dominante y, si no existe, el de menor ρ. Si ρ < 1 pero se acaban las iteraciones, se estima cuántas
  faltan.
- **Iteraciones:** tabla k, x₁…xₙ, cambio y residuo.
- **Paso a paso:** la sustitución de cada componente con los números, igual que las diapositivas
  (`(6 + 2.272727 − 2(−1.100000)) / 10 = 1.047273`).
- **Gráficas (ECharts):** evolución de cada incógnita y error de los dos métodos en escala logarítmica.
- **Despeje y convergencia:** cada incógnita despejada (KaTeX), la fórmula general y la tabla de dominancia.

El ejemplo de clase (10x₁ − x₂ + 2x₃ = 6 …) da las mismas tablas que la presentación: Jacobi converge en 18 iteraciones
y Gauss-Seidel en 8 con ε = 10⁻⁶. Las tablas de las diapositivas 16 y 22 coinciden con el programa; los cálculos
sueltos de las diapositivas 15, 20 y 21 tienen erratas (por ejemplo x₂⁽²⁾ de Jacobi es 1.715909, no 1.704545, y
x₄⁽¹⁾ de Gauss-Seidel es 0.878864, no 0.751591).

## Matrices

Operaciones: **A⁻¹ y det(A)** (en una sola pasada de Gauss-Jordan sobre [A | I]; justifica la inversa con
det(A) ≠ 0 y comprueba A·A⁻¹ = I), det(A) por LU o cofactores, Aᵀ, c·A, (A⁻¹)⁻¹, x = A⁻¹b, A + B, A − B y A × B.
El tamaño se cambia con − y + (hasta 8 × 8) y la matriz se puede **pegar como texto** tal como viene en el ejercicio
(`[ -4 5 -4 5 ]` por fila). Las matrices del resultado se dibujan con fracciones (KaTeX) y el procedimiento queda plegado.

## Método de Bisección

1. **Función:** se escribe tal cual, como en el cuaderno, con el editor matemático (x⁴ − 5x³ + 0.5x² − 11x + 10). También hay un modo texto.
2. **Gráfica:** se marcan los intervalos donde f(x) cambia de signo (f(a)·f(b) < 0). Al escribir una función nueva el rango se ajusta solo para que se vean sus raíces (botón **Rango automático**). Las asíntotas (tan x, 1/x) se marcan y no se ofrecen como intervalo, y si f(x) = 0 justo en un punto de la tabla también se ofrece ese intervalo.
3. **Parámetros:** intervalo [a, b], precisión E, máximo de iteraciones y criterio de parada. Por defecto se usa el error |f(c)| < E, igual que la hoja de cálculo de clase (f(x) = x⁴ − 5x³ + 0.5x² − 11x + 10 en [0.6, 1] con E = 0.0001: 15 iteraciones, raíz 0.76393, error 0.00007). También se puede elegir el error absoluto Ea = |c nuevo − c anterior|, el relativo, el porcentual o b − a.
4. **Iteraciones:** cada iteración se explica (punto medio, f(c), signos, error, decisión) con su gráfica y la tabla completa.
5. **Conclusión:** iteraciones realizadas, solución y error, más las comprobaciones del algoritmo.

En el paso 1 hay **ejemplos resueltos** (clase, polinomios, e⁻ˣ − x, cos x − x, √3, ln x, tres raíces, Wallis y tan x con asíntotas): un clic los resuelve y va directo a las iteraciones; el icono de la gráfica solo los carga.

El botón **Guía paso a paso** resalta cada parte de la pantalla y explica para qué sirve.

## Método de Regla Falsa (falsa posición)

Tiene los mismos pasos que bisección (función, gráfica, parámetros, iteraciones, conclusión y algoritmo); lo que cambia es cómo se obtiene c: se une (a, f(a)) con (b, f(b)) con una recta y se toma su corte con el eje x:

```
c = b − f(b)·(a − b) / (f(a) − f(b))        (xr = xu − f(xu)(xl − xu) / (f(xl) − f(xu)))
```

1. **Bolzano:** antes de iterar se comprueba que f sea continua en [a, b] y que f(a)·f(b) < 0. Si la función es discontinua (tan x, 1/x) se avisa en la gráfica y no se acepta un intervalo que cruce la asíntota; en un tramo continuo que cumpla Bolzano sí se resuelve.
2. **Iteraciones:** cada una muestra la fórmula con los números, f(c), la comparación de signos f(a)·f(c), el error y la decisión, con una gráfica de la recta y su corte con el eje.
3. **Variante modificada:** si un extremo se estanca dos iteraciones seguidas, se divide a la mitad su f en la fórmula (con x¹⁰ − 1 en [0, 1.3] pasa de 39 a 12 iteraciones).
4. **Conclusión:** además de las comprobaciones del algoritmo avisa si el método avanzó por un solo lado y compara con las iteraciones de bisección.

El ejemplo de clase (x³ − 4.23603x² − 2.7362x − 13.09037 en [4.95, 5.5], error relativo < 0.0001) converge en 4 iteraciones a 5.2360505080, igual que en la presentación.

## Métodos abiertos: Newton-Raphson y Secante

Siguen la presentación de clase (métodos abiertos). Tienen los mismos 6 pasos que bisección, pero en lugar de un intervalo [a, b] usan valores iniciales y no necesitan Bolzano.

```
Newton-Raphson:  xₙ₊₁ = xₙ − f(xₙ) / f'(xₙ)
Secante:         xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / [f(xₙ) − f(xₙ₋₁)]
```

1. **Función y derivada:** se escribe f(x) y el programa calcula **f'(x) automáticamente** (reglas de la potencia, producto, cociente y cadena, sin librerías). Deriva polinomios, raíces, potencias con exponente fraccionario o variable (xˣ), exponenciales, logaritmos, |x|, trigonométricas, hiperbólicas y todas sus inversas, y simplifica el resultado. En Newton-Raphson también se puede escribir la derivada a mano; se compara con la calculada en varios puntos y se avisa si no coincide. La derivada se muestra en los pasos 1, 4 y 5 (expresión, f'(xₙ) en cada iteración y f'(raíz)).
2. **Gráfica:** los intervalos con cambio de signo sugieren x₀ (Newton: el extremo con |f| menor) o x₀ y x₁ (secante: los extremos).
3. **Parámetros:** x₀ (y x₁), tolerancia E y máximo de iteraciones. Se detiene con la primera de **dos condiciones**: el error es menor que E o se llega al máximo de iteraciones. Por defecto el error es el **absoluto** Ea = |xₙ₊₁ − xₙ|; también hay relativo, porcentual, residuo |f(xₙ₊₁)| o ambos.
4. **Iteraciones:** cada una muestra f(xₙ), f'(xₙ) (o la pendiente de la secante comparada con f'(xₙ)), la fórmula con los números, el residuo, el cambio y la decisión, con la gráfica de la tangente o la secante. Tabla como la de clase: n, xₙ, f(xₙ), f'(xₙ), xₙ₊₁, Ea y residuo.
5. **Conclusión:** raíz aproximada, residuo, iteraciones, error, la derivada usada y comprobaciones (residuo, tolerancia o máximo, división entre cero, divergencia, raíz múltiple).

El ejemplo de clase (x³ − x − 2) da lo mismo que la presentación: Newton con x₀ = 1.5 → 1.521739130, 1.521379806, 1.521379707 (3 iteraciones, E = 10⁻⁶); secante con x₀ = 1, x₁ = 2 → 1.333333, 1.462687, 1.531169, 1.520926, 1.521376, 1.521380… (7 iteraciones). También están la actividad colaborativa y la práctica integradora (x³ − 2x − 5) y ejemplos donde el método falla (ciclo, divergencia, raíz múltiple).

## Gráfica interactiva (pasos 2 de bisección y regla falsa)

La gráfica funciona como en GeoGebra: la curva se dibuja en el navegador y se recalcula en cada movimiento, así que se puede alejar o acercar sin límite práctico. **Rueda:** zoom en el punto del cursor (Shift + rueda: solo eje x; Alt + rueda: solo eje y) · **arrastrar:** mover · **pellizco:** zoom en pantallas táctiles · **doble clic:** acercar · al pasar el cursor se lee x y f(x). Los botones de la esquina acercan, alejan, ajustan el eje y a la curva o vuelven a la vista inicial. Las asíntotas y los saltos no se unen con líneas falsas. **Tabular la vista actual** usa la zona que se está viendo como nuevo rango para buscar intervalos con cambio de signo.

## Escribir la función: teclado y validación

La función se escribe en el **editor matemático** o como **texto**, y en los dos modos hay un **teclado de funciones** (sen, cos, tan, sec, csc, cot, sus inversas, senh, cosh, tanh y sus inversas, eˣ, ln, log, log₂, √, ∛, |x|, potencias, fracciones, π, = y teclas para mover el cursor o borrar). Cada tecla escribe donde está el cursor; en el editor deja una casilla para completar y en el texto deja el cursor dentro de los paréntesis. La derivada escrita a mano en Newton-Raphson tiene su propio teclado.

Mientras se escribe, el programa indica **✓ Bien escrita** o qué falta, por ejemplo: un paréntesis sin cerrar (o uno que sobra), una barra de valor absoluto sin pareja, el argumento de una función (sen()), el exponente después de ^, un término después de + o entre dos operadores, una casilla vacía del editor, una letra que no es x, un nombre mal escrito con su corrección (sem → ¿Quiso decir sen?), grados (30° → pi/6), comas, factoriales o desigualdades, y una función sin x. También avisa si f(x) no da un número real en ningún punto (ln(−x² − 1)).

La notación del cuaderno **tan⁻¹ x** (o sen⁻¹, cos⁻¹, senh⁻¹…) se lee como la **función inversa** arctan x, igual que escribir arctan x, y se avisa de esa lectura; para 1/tan x se escribe (tan x)⁻¹ o cot x. En el paso 3, x₀, x₁, E y el máximo de iteraciones se revisan al escribirlos y aceptan expresiones como pi/2, sqrt(2) o 10^-4.

## Ecuaciones sin igualar a cero

En todos los métodos de raíces (y en la pantalla principal) se puede escribir la ecuación completa, con el signo **=**. El programa pasa todo al lado izquierdo cambiando el signo de cada término, reduce los términos semejantes (y desarrolla los polinomios cortos) y muestra solo la **función que usa el método**:

```
sen(x) = −2x + 1     →   f(x) = sen(x) + 2x − 1
x³ = 2x + 5          →   f(x) = x³ − 2x − 5
x(x − 1) = 2         →   f(x) = x² − x − 2
0 = x² − 4           →   f(x) = x² − 4
```

Si al reducir se cancela un término que limita el dominio (ln x = ln x + x − 1), f(x) sigue sin estar definida donde no lo estaba la ecuación original, para no dar raíces falsas. En la conclusión de Newton-Raphson y de la secante la raíz se sustituye en los **dos lados** de la ecuación original para comprobar que dan el mismo número. Si la ecuación queda 0 = 0 o una constante (x = x, x = x + 1) se avisa que no hay raíz que buscar, y si aparece otra letra (y, a, k…) se pide reemplazarla por su valor: la única variable es x.

## Pantalla principal

- **Resolución rápida:** se escribe una función o una ecuación (hay pastillas con las del curso) y al instante se ve la función que usa el método, su gráfica interactiva y sus raíces aproximadas. Se elige la raíz y con un clic se abre Newton-Raphson, la secante, bisección o regla falsa con la función cargada, el intervalo marcado y el valor inicial propuesto. Enter abre Newton-Raphson.
- **Módulos:** todos los módulos en tarjetas compactas agrupadas, con su fórmula. Debajo de los métodos abiertos está
  plegada la comparación **¿Newton-Raphson o secante?** (tabla de la presentación e iteraciones del ejemplo de clase).
- **Buscador (Ctrl + K):** abre cualquier módulo escribiendo parte de su nombre.

## Decimales

En los pasos 3, 4 y 5 de los métodos, el control **Decimales (− / + / Auto)** cambia al instante cuántos decimales se ven en las tarjetas, la tabla y la conclusión.

## Estructura

```
main.py                         Arranca el programa (une backend y frontend)

backend/                        Lógica y cálculos (no tiene nada de interfaz)
  algebra_lineal/
    fracciones.py               Lectura y formato de fracciones exactas y determinante exacto
    sistemas.py                 Gauss, pivoteo parcial y Gauss-Jordan (un solo recorrido), clasificación y comprobación
    iterativos.py               Jacobi y Gauss-Seidel: dominancia, reordenamiento, radio espectral e iteraciones
    parser_ecuaciones.py        Lee sistemas escritos como texto (x, y, z, w o x1, x2…)
    vectores.py                 Operaciones en Rⁿ y combinación lineal
    matrices.py                 Inversa con det(A), determinante (cofactores y LU), x = A⁻¹b...
  sistemas_numericos/
    conversor.py                Conversión entre bases
    romanos.py                  Aritmética y conversión de números romanos
  metodos_numericos/
    analizador.py               Lee f(x) o una ecuación (izq = der) escrita tal cual o en LaTeX, la iguala a cero y calcula f'(x)
    biseccion.py                Tabulación, Bolzano, bisección y comprobaciones
    regla_falsa.py              Regla falsa clásica y modificada (reutiliza la tabulación y Bolzano)
    abiertos.py                 Lo común a los métodos abiertos (criterios, errores, comprobaciones)
    newton_raphson.py           Método de Newton-Raphson
    secante.py                  Método de la secante
    vista_rapida.py             Rango y raíces aproximadas para la pantalla principal
    graficas.py                 Gráficas con matplotlib

frontend/                       Interfaz gráfica en Python (NiceGUI)
  aplicacion.py                 Marco de vidrio, barra lateral, buscador (Ctrl + K) y registro de módulos
  componentes.py                Piezas visuales compartidas (también fórmulas KaTeX, números animados y gráficas ECharts)
  guia.py                       Guía paso a paso (driver.js)
  formato.py                    Formato de números
  estilos.css                   Tema de vidrio líquido y animaciones
  recursos/                     Librerías incluidas, funcionan sin internet: MathLive (editor matemático), driver.js
                                (guía), KaTeX (fórmulas), CountUp.js (números animados) y auto-animate (transiciones)
    realce/realce.js            Activa KaTeX, CountUp y auto-animate en cada elemento nuevo de la pantalla
    plano/plano.js              Gráfica interactiva de f(x) con zoom y paneo (hecha para este programa)
    teclado/teclado.js          Teclado de funciones que escribe en el editor matemático o en el texto
  modulos/
    inicio.py                   Pantalla principal (resolución rápida, métodos, comparación y herramientas)
    biseccion/                  Vista, estado, ejemplos resueltos y un archivo por paso (pasos/)
    regla_falsa/                Hereda la vista de bisección; solo cambia ejemplos, iteraciones, variante y algoritmo
    abiertos/                   Newton-Raphson y secante: heredan la vista de bisección (derivada, x₀, tabla, conclusión)
    ecuaciones.py               Sistemas lineales
    iterativos.py               Jacobi y Gauss-Seidel
    vectores.py · conversor.py · romanos.py
    matrices/                   Vista y dibujo de la expansión por cofactores
```

Las carpetas `__pycache__` no hacen falta: `main.py` le indica a Python que no las cree.
