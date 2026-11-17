# frontend/aplicacion.py
# Marco principal: barra lateral con los modulos, buscador rapido (Ctrl + K) y el area de contenido.
from typing import Callable, NamedTuple

from nicegui import ui

from .componentes import caja, html
from .formato import escapar
from .modulos import abiertos, biseccion, conversor, ecuaciones, inicio, matrices, regla_falsa, romanos, vectores


class Modulo(NamedTuple):
    id: str
    nombre: str
    corto: str        # nombre en la barra lateral (cabe en una linea)
    icono: str
    construir: Callable
    nuevo: bool
    descripcion: str  # se muestra en la pantalla principal y en el buscador
    claves: str = ""  # palabras extra para el buscador


# Registro de modulos por grupo
GRUPOS = [
    ("Métodos abiertos", [
        Modulo("newton", "Método de Newton-Raphson", "Newton-Raphson", "trending_up", abiertos.construir_newton, True,
               "Desde x₀ sigue la recta tangente. Calcula f'(x) automáticamente.",
               "tangente derivada abierto raiz ecuacion"),
        Modulo("secante", "Método de la Secante", "Secante", "insights", abiertos.construir_secante, True,
               "Con x₀ y x₁ traza la recta secante, sin necesitar la derivada.",
               "secante abierto raiz ecuacion dos puntos"),
    ]),
    ("Métodos cerrados", [
        Modulo("biseccion", "Método de Bisección", "Bisección", "my_location", biseccion.construir, False,
               "Encierra la raíz en [a, b] y lo parte a la mitad hasta que el error sea menor que E.",
               "biseccion cerrado intervalo bolzano raiz"),
        Modulo("regla_falsa", "Método de Regla Falsa", "Regla falsa", "timeline", regla_falsa.construir, False,
               "Une (a, f(a)) y (b, f(b)) con una recta y usa su corte con el eje x. Incluye la variante modificada.",
               "falsa posicion cerrado intervalo raiz"),
    ]),
    ("Álgebra lineal", [
        Modulo("ecuaciones", "Ecuaciones lineales", "Sistemas lineales", "functions", ecuaciones.construir, False,
               "Resuelve Ax = b por Gauss-Jordan, pivoteo parcial o Gauss, con fracciones exactas.",
               "gauss jordan pivote sistema"),
        Modulo("vectores", "Vectores Rⁿ", "Vectores Rⁿ", "north_east", vectores.construir, False,
               "Operaciones con vectores y si b es combinación lineal de ellos.", "combinacion lineal"),
        Modulo("matrices", "Matrices y Ax = b", "Matrices", "grid_on", matrices.construir, False,
               "Inversa, determinante (cofactores y LU), producto y sistemas Ax = b.",
               "determinante inversa cofactores lu producto"),
    ]),
    ("Sistemas numéricos", [
        Modulo("conversor", "Conversor de bases", "Conversor de bases", "swap_horiz", conversor.construir, False,
               "Convierte números entre bases mostrando el procedimiento.", "binario octal hexadecimal"),
        Modulo("romanos", "Números romanos", "Números romanos", "account_balance", romanos.construir, False,
               "Convierte y opera con romanos del I al MMMCMXCIX.", "romano"),
    ]),
]
INICIO = "inicio"
METODOS_DE_RAICES = ("newton", "secante", "biseccion", "regla_falsa")


class Aplicacion:
    def __init__(self):
        self.activo = INICIO
        self.vistas = {}       # id -> contenedor de la vista (se muestra u oculta)
        self.instancias = {}   # id -> objeto de la vista (para cargarle una funcion desde el inicio)

        with caja("fondo"):
            for _ in range(5):
                ui.element("span")

        # Los paneles flotan sobre el fondo: asi el vidrio tiene algo que refractar
        with caja("marco"):
            self.menu()
            with caja("contenido"):
                # Todas las vistas se crean una vez; asi no se pierde lo escrito al cambiar de modulo
                with caja("vista entrar") as vista:
                    inicio.construir(GRUPOS, self.elegir, self.resolver_desde_inicio)
                self.vistas[INICIO] = vista
                for _, modulos in GRUPOS:
                    for modulo in modulos:
                        with caja("vista entrar") as vista:
                            self.instancias[modulo.id] = modulo.construir()
                        vista.set_visibility(modulo.id == self.activo)
                        self.vistas[modulo.id] = vista

        self.buscador()
        # Ctrl + K (o Cmd + K) abre el buscador desde cualquier parte. Se evita que el navegador
        # use el atajo para su propia barra de busqueda.
        ui.on("abrir_buscador", self.abrir_buscador)
        ui.add_body_html("""
<script>
  document.addEventListener('keydown', function (ev) {
    if ((ev.ctrlKey || ev.metaKey) && !ev.repeat && (ev.key === 'k' || ev.key === 'K')) {
      ev.preventDefault();
      if (window.emitEvent) window.emitEvent('abrir_buscador');
    }
  });
</script>
""")

    # ------------------------------------------------------------------
    # Barra lateral
    # ------------------------------------------------------------------
    @ui.refreshable_method
    def menu(self):
        with caja("vidrio lateral"):
            with caja("marca") as marca:
                html("∑", "logo")
                html("<h1>Calculadora</h1><p>Álgebra y métodos</p>", "nombre-marca")
            marca.style("cursor:pointer").on("click", lambda: self.elegir(INICIO))
            with caja("buscar-menu") as buscar:
                ui.icon("search")
                html("Buscar módulo", "buscar-texto")
                html("Ctrl K", "tecla")
            buscar.on("click", self.abrir_buscador)
            self.item_menu(INICIO, "Inicio", "space_dashboard")
            for titulo, modulos in GRUPOS:
                html(escapar(titulo), "grupo-menu")
                for modulo in modulos:
                    self.item_menu(modulo.id, modulo.corto, modulo.icono, modulo.nuevo)
            html('<div class="pie-menu">Funciona sin internet</div>')

    def item_menu(self, id_modulo, nombre, icono, nuevo=False):
        item = caja("item-menu" + (" activo" if id_modulo == self.activo else "")).mark(f"menu-{id_modulo}")
        with item:
            ui.icon(icono)
            html(escapar(nombre), "item-nombre")
            if nuevo and id_modulo != self.activo:
                html("", "punto-nuevo").props('title="Nuevo"')
        item.on("click", lambda m=id_modulo: self.elegir(m))

    def elegir(self, id_modulo):
        if id_modulo == self.activo:
            return
        self.vistas[self.activo].set_visibility(False)
        self.activo = id_modulo
        vista = self.vistas[id_modulo]
        vista.set_visibility(True)
        self.menu.refresh()
        # Se repite la animacion de entrada y se vuelve al inicio del contenido
        ui.run_javascript(
            f"const v = document.getElementById('{vista.html_id}');"
            "if (v) { v.classList.remove('entrar'); void v.offsetWidth; v.classList.add('entrar'); }"
            "document.querySelector('.contenido')?.scrollTo({top: 0, behavior: 'smooth'});"
        )

    async def resolver_desde_inicio(self, id_modulo, texto, x_cercano=None):
        """La pantalla principal pide resolver una funcion o ecuacion con un metodo de raices."""
        vista = self.instancias.get(id_modulo)
        if vista is None or not hasattr(vista, "abrir_con_funcion"):
            self.elegir(id_modulo)
            return
        if await vista.abrir_con_funcion(texto, x_cercano):
            self.elegir(id_modulo)

    # ------------------------------------------------------------------
    # Buscador rapido (Ctrl + K)
    # ------------------------------------------------------------------
    def _todos(self):
        lista = [("inicio", "Inicio", "space_dashboard", "Pantalla principal con la resolución rápida", "Inicio", "")]
        for grupo, modulos in GRUPOS:
            lista += [(m.id, m.nombre, m.icono, m.descripcion, grupo, m.claves) for m in modulos]
        return lista

    def buscador(self):
        self.consulta = ""
        with ui.dialog() as self.dialogo_buscar, caja("vidrio buscador"):
            with caja("buscador-cabeza"):
                ui.icon("search")
                self.entrada_buscar = ui.input(placeholder="Buscar un método o herramienta…",
                                               on_change=lambda e: self._filtrar(e.value or ""))
                self.entrada_buscar.props("borderless dense autofocus spellcheck=false").classes("buscador-entrada")
                self.entrada_buscar.on("keydown.enter", self._abrir_primero)
                html("Esc", "tecla")
            self.resultados_buscar()
            html('<div class="buscador-pie"><span class="tecla">Enter</span> abrir el primero &nbsp;·&nbsp; '
                 '<span class="tecla">Esc</span> cerrar</div>')

    def _coincidencias(self):
        palabras = self.consulta.lower().split()
        quitar = str.maketrans("áéíóúñ", "aeioun")
        resultado = []
        for item in self._todos():
            texto = " ".join(item[1:]).lower().translate(quitar)
            if all(p.translate(quitar) in texto for p in palabras):
                resultado.append(item)
        return resultado

    @ui.refreshable_method
    def resultados_buscar(self):
        coincidencias = self._coincidencias()
        with caja("buscador-lista"):
            if not coincidencias:
                html('<div class="texto-suave" style="padding:18px">No hay módulos con ese nombre.</div>')
            for indice, (id_modulo, nombre, icono, descripcion, grupo, _) in enumerate(coincidencias):
                with caja("buscador-item" + (" primero" if indice == 0 else "")) as fila:
                    html(f'<span class="material-icons">{icono}</span>', "buscador-icono")
                    html(f'<div class="buscador-nombre">{escapar(nombre)}</div>'
                         f'<div class="buscador-detalle">{escapar(descripcion)}</div>')
                    html(escapar(grupo), "buscador-grupo")
                fila.on("click", lambda m=id_modulo: self._ir_desde_buscador(m))

    def _filtrar(self, texto):
        self.consulta = texto
        self.resultados_buscar.refresh()

    def _abrir_primero(self):
        coincidencias = self._coincidencias()
        if coincidencias:
            self._ir_desde_buscador(coincidencias[0][0])

    def _ir_desde_buscador(self, id_modulo):
        self.dialogo_buscar.close()
        self.elegir(id_modulo)

    def abrir_buscador(self):
        self.consulta = ""
        self.entrada_buscar.value = ""
        self.resultados_buscar.refresh()
        self.dialogo_buscar.open()
        ui.run_javascript("setTimeout(() => document.querySelector('.buscador-entrada input')?.focus(), 120)")
