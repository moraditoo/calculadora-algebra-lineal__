# main.py
# Punto de entrada: python main.py  (abre la calculadora en el navegador)
import sys

# Python no crea las carpetas __pycache__ (son solo una cache, no hacen falta)
sys.dont_write_bytecode = True

from pathlib import Path

from nicegui import app, ui

from frontend.aplicacion import Aplicacion

CARPETA = Path(__file__).parent / "frontend"
RECURSOS = CARPETA / "recursos"

# Librerias del navegador incluidas en el proyecto (funcionan sin internet):
#   MathLive  -> editor para escribir la funcion como en el cuaderno
#   driver.js -> guia que resalta paso a paso las partes importantes
#   plano.js  -> grafica interactiva de f(x) con zoom y paneo (hecha para este programa)
#   teclado.js -> teclado de funciones (sen, cos, ln, √...) que escribe en el editor o en el texto
#   KaTeX      -> formulas y matrices bien dibujadas en los resultados (usa las fuentes de MathLive)
#   CountUp.js -> los numeros de los resultados suben hasta su valor
#   auto-animate -> transiciones suaves cuando aparecen o desaparecen partes de la pantalla
#   realce.js  -> activa KaTeX, CountUp y auto-animate en cada elemento nuevo (hecho para este programa)
#   (las graficas de convergencia usan ECharts, que ya viene incluido en NiceGUI)
app.add_static_files("/recursos", RECURSOS)
LIBRERIAS = """
<link rel="stylesheet" href="/recursos/driver/driver.css">
<link rel="stylesheet" href="/recursos/katex/katex.min.css">
<script src="/recursos/driver/driver.js.iife.js"></script>
<script src="/recursos/mathlive/mathlive.min.js"></script>
<script src="/recursos/katex/katex.min.js"></script>
<script src="/recursos/countup/countUp.umd.js"></script>
<script type="module">
  import autoAnimate from '/recursos/autoanimate/index.mjs';
  window.autoAnimate = autoAnimate;
  window.dispatchEvent(new Event('autoanimate-listo'));
</script>
<script src="/recursos/realce/realce.js"></script>
<script src="/recursos/plano/plano.js"></script>
<script src="/recursos/teclado/teclado.js"></script>
<script>
  // Se configura cuando ya existe el documento (MathLive lo necesita) y antes de crear los editores
  document.addEventListener('DOMContentLoaded', function () {
    const MF = window.MathfieldElement || (window.MathLive && window.MathLive.MathfieldElement);
    if (MF) { MF.fontsDirectory = '/recursos/mathlive/fonts'; MF.soundsDirectory = null; }
  });
</script>
"""


# Filtro de refraccion del vidrio liquido: ondula levemente lo que se ve detras de cada panel
FILTRO_VIDRIO = """
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="refraccion" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.006 0.009" numOctaves="2" seed="7" result="ondas"/>
    <feGaussianBlur in="ondas" stdDeviation="2.5" result="ondas_suaves"/>
    <feDisplacementMap in="SourceGraphic" in2="ondas_suaves" scale="38" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
"""


def inicio():
    """Se ejecuta por cada pestana que abre el programa."""
    ui.add_head_html(LIBRERIAS)
    ui.add_body_html(FILTRO_VIDRIO)
    ui.add_css(CARPETA / "estilos.css")
    Aplicacion()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        inicio,
        title="Calculadora · Álgebra y métodos numéricos",
        port=8080,
        reload=False,
        language="es",
        favicon="∑",
        show="--sin-navegador" not in sys.argv,
    )
