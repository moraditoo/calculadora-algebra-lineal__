# frontend/aplicacion.py
# Marco principal: barra lateral con los modulos y el area de contenido.
from typing import Callable, NamedTuple

from nicegui import ui

from .componentes import caja, html
from .formato import escapar
from .modulos import biseccion, conversor, ecuaciones, inicio, matrices, regla_falsa, romanos, vectores


class Modulo(NamedTuple):
    id: str
    nombre: str
    icono: str
    construir: Callable
    nuevo: bool
    descripcion: str  # se muestra en la pantalla principal


# Registro de modulos por grupo
GRUPOS = [
    ("Métodos numéricos", [
        Modulo("biseccion", "Método de Bisección", "my_location", biseccion.construir, False,
               "Encierra la raíz en [a, b] y lo parte a la mitad hasta que el error sea menor que E."),
        Modulo("regla_falsa", "Método de Regla Falsa", "timeline", regla_falsa.construir, True,
               "Une (a, f(a)) y (b, f(b)) con una recta y usa su corte con el eje x. Incluye la variante modificada."),
    ]),
    ("Álgebra lineal", [
        Modulo("ecuaciones", "Ecuaciones lineales", "functions", ecuaciones.construir, False,
               "Resuelve Ax = b por Gauss-Jordan, pivoteo parcial o Gauss, con fracciones exactas."),
        Modulo("vectores", "Vectores Rⁿ", "north_east", vectores.construir, False,
               "Operaciones con vectores y si b es combinación lineal de ellos."),
        Modulo("matrices", "Matrices y Ax = b", "grid_on", matrices.construir, False,
               "Inversa, determinante (cofactores y LU), producto y sistemas Ax = b."),
    ]),
    ("Sistemas numéricos", [
        Modulo("conversor", "Conversor de bases", "swap_horiz", conversor.construir, False,
               "Convierte números entre bases mostrando el procedimiento."),
        Modulo("romanos", "Números romanos", "account_balance", romanos.construir, False,
               "Convierte y opera con romanos del I al MMMCMXCIX."),
    ]),
]
INICIO = "inicio"


class Aplicacion:
    def __init__(self):
        self.activo = INICIO
        self.vistas = {}

        with caja("fondo"):
            for _ in range(5):
                ui.element("span")

        # Los paneles flotan sobre el fondo: asi el vidrio tiene algo que refractar
        with caja("marco"):
            self.menu()
            with caja("contenido"):
                # Todas las vistas se crean una vez; asi no se pierde lo escrito al cambiar de modulo
                with caja("vista entrar") as vista:
                    inicio.construir(GRUPOS, self.elegir)
                self.vistas[INICIO] = vista
                for _, modulos in GRUPOS:
                    for modulo in modulos:
                        with caja("vista entrar") as vista:
                            modulo.construir()
                        vista.set_visibility(modulo.id == self.activo)
                        self.vistas[modulo.id] = vista

    @ui.refreshable_method
    def menu(self):
        with caja("vidrio lateral"):
            with caja("marca") as marca:
                html("∑", "logo")
                html("<h1>Calculadora</h1><p>Álgebra y métodos</p>", "nombre-marca")
            marca.style("cursor:pointer").on("click", lambda: self.elegir(INICIO))
            self.item_menu(INICIO, "Inicio", "home")
            for titulo, modulos in GRUPOS:
                html(escapar(titulo), "grupo-menu")
                for modulo in modulos:
                    self.item_menu(modulo.id, modulo.nombre, modulo.icono, modulo.nuevo)

    def item_menu(self, id_modulo, nombre, icono, nuevo=False):
        item = caja("item-menu" + (" activo" if id_modulo == self.activo else "")).mark(f"menu-{id_modulo}")
        with item:
            ui.icon(icono)
            html(escapar(nombre))
            if nuevo and id_modulo != self.activo:
                html("NUEVO", "nuevo")
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
