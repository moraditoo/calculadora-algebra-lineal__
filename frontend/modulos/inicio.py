# frontend/modulos/inicio.py
# Pantalla principal: presentacion del programa y acceso directo a cada modulo.
from nicegui import ui

from ..componentes import boton, caja, html, subtitulo, tarjeta
from ..formato import escapar

# Dibujo animado del encabezado: una curva y las rectas de la regla falsa acercandose a la raiz
ILUSTRACION = """
<svg viewBox="0 0 360 230" role="img" aria-label="Rectas de la regla falsa acercándose a la raíz">
  <defs>
    <linearGradient id="inicio-curva" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#8e8e93"/><stop offset="1" stop-color="#1d1d1f"/>
    </linearGradient>
  </defs>
  <g class="ejes">
    <line x1="14" y1="150" x2="346" y2="150"/>
    <line x1="40" y1="14" x2="40" y2="216"/>
  </g>
  <g class="rejilla-ilustracion">
    <line x1="100" y1="14" x2="100" y2="216"/><line x1="160" y1="14" x2="160" y2="216"/>
    <line x1="220" y1="14" x2="220" y2="216"/><line x1="280" y1="14" x2="280" y2="216"/>
    <line x1="14" y1="90" x2="346" y2="90"/><line x1="14" y1="30" x2="346" y2="30"/><line x1="14" y1="210" x2="346" y2="210"/>
  </g>
  <path class="curva" d="M 30 196 C 120 194, 190 178, 236 132 S 300 46, 336 18"/>
  <line class="secante s1" x1="62" y1="195" x2="330" y2="23"/>
  <line class="secante s2" x1="132" y1="185" x2="330" y2="23"/>
  <line class="secante s3" x1="175" y1="172" x2="330" y2="23"/>
  <circle class="extremo" cx="330" cy="23" r="5"/>
  <circle class="paso p1" cx="132" cy="150" r="4"/>
  <circle class="paso p2" cx="175" cy="150" r="4"/>
  <circle class="paso p3" cx="197" cy="150" r="4"/>
  <circle class="raiz-halo" cx="214.7" cy="150" r="13"/>
  <circle class="raiz" cx="214.7" cy="150" r="6"/>
  <text x="222" y="174">raíz</text>
  <text x="222" y="66">f(x)</text>
</svg>
"""

PASOS = [
    ("edit", "Escriba f(x)", "Con el editor matemático, tal como en el cuaderno: x⁴ − 5x³ + 0.5x² …"),
    ("travel_explore", "Explore la gráfica", "Acerque, aleje y mueva el plano; los intervalos con cambio de signo se marcan solos."),
    ("tune", "Elija [a, b] y E", "Se comprueba Bolzano: f continua y f(a)·f(b) < 0 antes de iterar."),
    ("checklist", "Vea cada iteración", "Tabla completa, explicación de cada cálculo y la conclusión con su error."),
]


def construir(grupos, abrir):
    """grupos: el registro de modulos de aplicacion.py; abrir(id) cambia al modulo elegido."""
    modulos = [m for _, lista in grupos for m in lista]

    with tarjeta("inicio-hero"):
        with caja("hero-texto"):
            html('<span class="insignia">Métodos numéricos · Álgebra lineal · Sistemas numéricos</span>')
            html("<h1>Calculadora de álgebra<br>y métodos numéricos</h1>")
            html("<p>Escriba la función como en el cuaderno, explore su gráfica y siga cada iteración "
                 "explicada paso a paso, desde la tabulación hasta la raíz.</p>")
            with caja("fila").style("gap:10px; margin-top:22px"):
                boton("Empezar con Regla Falsa", lambda: abrir("regla_falsa"), icono="timeline", principal=True)
                boton("Método de Bisección", lambda: abrir("biseccion"), icono="my_location")
        html(ILUSTRACION, "hero-ilustracion")

    with caja("cifras-inicio escalonado"):
        for valor, texto in ((str(len(modulos)), "módulos"),
                             (str(sum(len(lista) for titulo, lista in grupos if titulo == "Métodos numéricos")),
                              "métodos para raíces"),
                             ("6", "pasos guiados por método"),
                             ("0", "conexión a internet necesaria")):
            html(f'<div class="cifra mono">{valor}</div><div class="cifra-texto">{texto}</div>', "vidrio cifra-caja")

    with tarjeta("escalonado"):
        for titulo, lista in grupos:
            subtitulo(titulo).style("margin-top:4px" if titulo == grupos[0][0] else "")
            with caja("rejilla tres"):
                for m in lista:
                    tarjeta_modulo(m, abrir)

    with tarjeta("escalonado"):
        subtitulo("Cómo se trabaja con los métodos").style("margin-top:0")
        with caja("rejilla cuatro"):
            for indice, (icono, titulo, texto) in enumerate(PASOS, start=1):
                with caja("paso-inicio"):
                    with caja("fila").style("align-items:center; gap:10px; flex-wrap:nowrap"):
                        html(str(indice), "circulo")
                        ui.icon(icono, size="20px").classes("icono-paso")
                    html(f'<div class="que">{escapar(titulo)}</div><div class="como">{escapar(texto)}</div>')


def tarjeta_modulo(m, abrir):
    insignia = '<span class="insignia verde">NUEVO</span>' if m.nuevo else ""
    tarjeta_html = html(
        f'<div class="modulo-cabeza"><span class="modulo-icono"><span class="material-icons">{m.icono}</span></span>{insignia}</div>'
        f'<div class="opcion-titulo">{escapar(m.nombre)}</div>'
        f'<div class="opcion-detalle">{escapar(m.descripcion)}</div>'
        '<div class="modulo-abrir">Abrir <span class="material-icons">arrow_forward</span></div>',
        "opcion modulo-inicio")
    tarjeta_html.on("click", lambda: abrir(m.id))
