# frontend/modulos/biseccion/vista.py
# Vista del metodo de biseccion: barra de pasos, tarjetas de resultado y panel.
# Sirve de base para los otros metodos cerrados (regla falsa): cada uno hereda esta
# clase y solo cambia sus textos, ejemplos, el calculo y los pasos que son distintos.
from nicegui import run, ui

from backend.metodos_numericos import biseccion as metodo
from backend.metodos_numericos import graficas
from ... import guia
from ...componentes import caja, encabezado, html, tarjeta
from ...formato import con_signo, escapar, numero
from .ejemplos import EJEMPLOS
from .estado import NOMBRE_ERROR, PASOS, Estado
from .pasos import algoritmo, conclusion, funcion, grafica, iteraciones, parametros


def construir():
    return VistaBiseccion()


class VistaBiseccion:
    # Lo que cambia de un metodo cerrado a otro
    NOMBRE = "bisección"                    # dentro de frases: "Ejecutar bisección"
    TITULO = "Método de Bisección"
    DESCRIPCION = ("Método cerrado para encontrar raíces de f(x) = 0: se grafica la función, se toma un intervalo "
                   "donde cambia de signo y se divide a la mitad hasta que el error sea menor que E.")
    ICONO = "my_location"
    PREFIJO = "biseccion"                   # ids de las filas y evento de clic en la tabla (unicos por metodo)
    EJEMPLOS = EJEMPLOS
    ESTADO = Estado
    CRITERIO_DE_CLASE = "funcion"           # el criterio que usa la hoja de clase (insignia "como en clase")
    NOTA_CRITERIO = ("En la hoja de clase el error de cada iteración es |f(c)|. También puede usar el error "
                     "absoluto Ea = |c nuevo − c anterior|. En cada iteración se compara con E y se itera "
                     "hasta que el error sea menor que E.")
    AVISO_RAIZ_EXACTA = ("esa raíz ya es exacta y bisección la confirma en la primera iteración (f(c) = 0). "
                         "Para ver más iteraciones use «Rango automático» o cambie los subintervalos.")
    AVISO_RAIZ_DOBLE = "así que el método de {nombre} no puede encerrar esa raíz."
    INTRO_ITERACIONES = ("Cada iteración divide el intervalo a la mitad y se queda con la mitad donde f cambia de signo. "
                         "Use las flechas, el control deslizante, la tabla o <b>Reproducir</b>.")
    EXPLICACION_RENGLON = iteraciones.EXPLICACION_RENGLON
    PASOS_DIBUJO = {1: funcion.construir, 2: grafica.construir, 3: parametros.construir,
                    4: iteraciones.construir, 5: conclusion.construir, 6: algoritmo.construir}
    NOMBRES_ERROR = NOMBRE_ERROR            # nombre corto de cada criterio de parada
    PUNTO = "c"                             # como se llama la aproximacion en las tarjetas: f(c) = ...

    def calcular(self, f):
        e = self.estado
        return metodo.biseccion(f, e.a, e.b, e.tolerancia, e.criterio, e.max_iteraciones)

    def renglones(self, it, r, d):
        """Explicacion de una iteracion (paso 4)."""
        return iteraciones.renglones(it, r, d)

    def grafica_de_iteracion(self, f, it):
        return graficas.grafica_iteracion(f, it)

    def grafica_resumen(self, f, resultado):
        """Grafica de todas las iteraciones juntas (en biseccion, la escalera de intervalos)."""
        return graficas.grafica_iteraciones(f, resultado)

    def tabla_iteraciones(self, r, d, actual):
        return iteraciones.tabla_iteraciones(r, d, actual, self.PREFIJO)

    def resumen_ejemplo(self, ejemplo):
        """Ultima linea de la tarjeta de un ejemplo resuelto (paso 1)."""
        return (f'[{ejemplo["a"]:g}, {ejemplo["b"]:g}] · '
                f'{escapar(self.NOMBRES_ERROR[ejemplo["criterio"]])} &lt; {escapar(ejemplo["tolerancia"])}')

    def despues_de_formula(self):
        """Algo mas que dibujar en el paso 1 debajo de la funcion (biseccion no tiene)."""

    def opciones_metodo(self):
        """Controles extra del paso 3 propios de cada metodo (biseccion no tiene)."""

    def aviso_conclusion(self, resultado):
        """Observacion extra del paso 5 propia de cada metodo (biseccion no tiene)."""

    # Paso 2: lo que cambia entre metodos cerrados y abiertos
    NOTA_INTERVALOS = ("En un método cerrado el intervalo elegido es el [a, b] inicial: se conserva el cambio de signo "
                       "en cada iteración y por eso la convergencia está garantizada.")
    AYUDA_TARJETAS = ("Haga clic en el intervalo que quiere resolver. f(a) y f(b) tienen signos distintos: "
                      "por el teorema de Bolzano hay una raíz dentro.")

    def datos_plano_extra(self):
        """Datos extra para la grafica interactiva (biseccion no tiene)."""
        return {}

    def panel_bajo_intervalos(self, refrescar):
        """Algo mas que dibujar debajo de las tarjetas de intervalos (biseccion no tiene)."""

    def textos_continuar(self):
        """(boton principal, boton secundario o None) al final del paso 2."""
        activo = self.estado.intervalo_activo
        if activo:
            return f"Continuar con I{activo}", "Escribir mi propio intervalo"
        return "Escribir el intervalo a mano", None

    def __init__(self):
        self.estado = self.ESTADO.desde_ejemplo(self.EJEMPLOS[0])
        self.kpi_recien_calculado = False
        self.pasos_guia = []          # elementos que explica el boton "Guía paso a paso"
        self.refrescos_iteracion = ()  # se llenan en el paso 4

        with tarjeta():
            encabezado(self.TITULO, self.DESCRIPCION, self.ICONO, al_pedir_guia=lambda: guia.iniciar(self.pasos_guia))
            self.barra_pasos()
        self.tarjetas_resultado()
        self.panel()
        # Contenedor fijo (nunca se redibuja) para los temporizadores de la vista
        self.anclaje = ui.element("div")
        with self.anclaje:
            self.reproductor = ui.timer(1.6, self._avanzar_reproduccion, active=False)
        # Clic en una fila de la tabla de iteraciones (se emite desde el HTML de la tabla)
        ui.on(f"{self.PREFIJO}_fila", self._al_elegir_fila)
        # La grafica interactiva avisa que parte se ve despues de moverla o hacer zoom
        ui.on(f"{self.PREFIJO}_vista", self._al_mover_plano)

    def _al_mover_plano(self, evento):
        argumento = evento.args[0] if isinstance(evento.args, list) else evento.args
        try:
            x0, x1 = float(argumento["xmin"]), float(argumento["xmax"])
        except (KeyError, TypeError, ValueError):
            return
        if x0 < x1:
            self.estado.vista_plano = (x0, x1)

    async def _al_elegir_fila(self, evento):
        argumento = evento.args[0] if isinstance(evento.args, list) else evento.args
        self.reproductor.deactivate()
        await self.ver_iteracion(argumento)

    # ------------------------------------------------------------------
    # Partes de la vista
    # ------------------------------------------------------------------
    @ui.refreshable_method
    def barra_pasos(self):
        with caja("barra-pasos"):
            for numero_paso, nombre in PASOS:
                clases = "paso-b"
                if numero_paso == self.estado.paso:
                    clases += " activo"
                elif not self.disponible(numero_paso):
                    clases += " bloqueado"
                elif self._completado(numero_paso):
                    clases += " hecho"
                marca = "✓" if "hecho" in clases else ("?" if numero_paso == 6 else numero_paso)
                elemento = html(f'<span class="num">{marca}</span>{escapar(nombre)}', clases).mark(f"paso-{numero_paso}")
                elemento.on("click", lambda n=numero_paso: self.ir_a(n))

    @ui.refreshable_method
    def tarjetas_resultado(self):
        r = self.estado.resultado
        d = self.estado.decimales
        animar = " numero-nuevo" if self.kpi_recien_calculado else ""
        self.kpi_recien_calculado = False
        if r and "veredicto" in r:   # metodos abiertos: converge o diverge
            estado_metodo = {"converge": "Converge", "lenta": "Converge lento (sin llegar a E)",
                             "diverge": "Diverge"}[r["veredicto"]["tipo"]]
        elif r:
            estado_metodo = "Converge" if r["convergio"] else "No converge"
        else:
            estado_metodo = "Sin calcular"
        datos = [
            ("Iteraciones", str(r["total_iteraciones"]) if r else "—", estado_metodo),
            ("Raíz aproximada", numero(r["raiz"], d) if r else "—",
             f"f({self.PUNTO}) = {con_signo(r['f_raiz'], 6)}" if r else "Complete el paso 3"),
            ("Error", numero(r["error_final"], d) if r else "—",
             (f"{self.NOMBRES_ERROR[r['criterio']]} {'<' if r['convergio'] else '≥'} E = {r['tolerancia']:g}") if r else f"E = {self.estado.tolerancia}"),
        ]
        self.tarjeta_raiz = None
        with caja("kpis escalonado"):
            for titulo, valor, pie in datos:
                elemento = html(f'<div class="k-titulo">{titulo}</div><div class="k-valor mono{animar}">{escapar(valor)}</div>'
                                f'<span class="chip{" azul" if r else ""}">{escapar(pie)}</span>',
                                "vidrio kpi" + ("" if r else " vacio"))
                if titulo == "Raíz aproximada":
                    self.tarjeta_raiz = elemento

    @ui.refreshable_method
    def panel(self):
        with tarjeta("escalonado"):
            self.pasos_guia = []
            self.PASOS_DIBUJO[self.estado.paso](self)

    # ------------------------------------------------------------------
    # Navegacion entre pasos
    # ------------------------------------------------------------------
    def disponible(self, numero_paso):
        if numero_paso in (1, 3, 6):
            return True
        if numero_paso == 2:
            return self.estado.funcion_lista() is not None
        return self.estado.resultado is not None

    def _completado(self, numero_paso):
        e = self.estado
        return {1: e.funcion_lista() is not None, 2: e.tabulacion is not None,
                3: e.resultado is not None, 4: e.resultado is not None}.get(numero_paso, False)

    def ir_a(self, numero_paso):
        if not self.disponible(numero_paso):
            motivo = "Primero escriba una función válida." if numero_paso == 2 else "Primero ejecute el método en el paso 3."
            ui.notify(motivo, position="top", type="warning")
            return
        if numero_paso == self.estado.paso:
            return
        self.estado.paso = numero_paso
        self.reproductor.deactivate()
        self.barra_pasos.refresh()
        self.panel.refresh()

    def refrescar(self):
        """Actualiza la barra de pasos y las tarjetas sin volver a dibujar el panel."""
        self.barra_pasos.refresh()
        self.tarjetas_resultado.refresh()

    # ------------------------------------------------------------------
    # Acciones (las graficas se generan en otro hilo para no congelar la pagina)
    # ------------------------------------------------------------------
    async def actualizar_formula(self):
        f = self.estado.funcion_lista()
        self.estado.formula = await run.io_bound(graficas.formula, f.mathtext) if f else None
        self.barra_pasos.refresh()

    async def graficar(self, ajustar_rango=False):
        """Tabula y grafica f(x). Con ajustar_rango (o si la funcion acaba de cambiar) primero
        busca un rango donde se vean las raices."""
        e = self.estado
        f = e.funcion_lista()
        if f is None:
            ui.notify(e.error_funcion or "La función no es válida.", type="negative", position="top")
            return False
        e.aviso_rango = None
        if ajustar_rango or e.rango_automatico:
            e.rango_automatico = False
            rango = await run.io_bound(metodo.buscar_rango, f)
            if rango:
                e.x_min, e.x_max = f"{rango['x_min']:.12g}", f"{rango['x_max']:.12g}"
                e.subintervalos = str(rango["subintervalos"])
                e.aviso_rango = (f"El rango se ajustó automáticamente a [{e.x_min}, {e.x_max}] con {e.subintervalos} "
                                 "subintervalos para que se vean las raíces de esta función. Puede cambiarlo arriba.")
            else:
                e.aviso_rango = ("No se encontró ningún cambio de signo entre −1000 y 1000: "
                                 f"parece que f(x) no tiene raíces reales que el método de {self.NOMBRE} pueda encerrar.")
        try:
            tabulacion = await run.io_bound(metodo.tabular, f, e.x_min, e.x_max, e.subintervalos)
        except ValueError as error:
            ui.notify(str(error), type="negative", position="top")
            return False
        e.limpiar_resultados()
        e.tabulacion = tabulacion
        if tabulacion["intervalos"]:
            self._usar_intervalo(self._intervalo_inicial(tabulacion["intervalos"]))
        e.grafica_general = await run.io_bound(graficas.grafica_funcion, f, tabulacion, e.intervalo_activo)
        self.refrescar()
        return True

    def _intervalo_inicial(self, intervalos):
        """El intervalo del ejemplo cargado si aparece en la tabulacion; si no, el primero donde
        la biseccion tiene que iterar (uno con raiz exacta se resuelve en la primera iteracion)."""
        preferido = self.estado.intervalo_preferido
        if preferido:
            for iv in intervalos:
                if abs(iv["a"] - preferido[0]) < 1e-9 and abs(iv["b"] - preferido[1]) < 1e-9:
                    return iv
        return next((iv for iv in intervalos if iv["exacta"] is None), intervalos[0])

    def _usar_intervalo(self, intervalo):
        self.estado.intervalo_activo = intervalo["numero"]
        self.estado.a, self.estado.b = f"{intervalo['a']:.12g}", f"{intervalo['b']:.12g}"

    async def cargar_ejemplo(self, ejemplo, resolver=False):
        """Carga un ejemplo resuelto: va a la grafica, o directo a las iteraciones si se pide resolverlo."""
        self.estado.cargar_ejemplo(ejemplo)
        self.reproductor.deactivate()
        if not resolver:
            self.refrescar()
            self.ir_a(2)
            return
        if await self.graficar():
            await self.resolver()

    async def preparar_intervalo(self, intervalo):
        """Deja elegido un intervalo al abrir el metodo desde la pantalla principal."""
        await self.elegir_intervalo(intervalo)

    async def abrir_con_funcion(self, texto, x_cercano=None):
        """La pantalla principal manda una funcion o una ecuacion escrita como texto: se carga,
        se grafica y queda elegido el intervalo de la raiz pedida (o el primero). Devuelve True si se pudo."""
        e = self.estado
        self.reproductor.deactivate()
        e.nueva_funcion(texto, False)
        if e.funcion_lista() is None:
            ui.notify(e.error_funcion or "La función no es válida.", type="negative", position="top")
            return False
        if not await self.graficar():
            return False
        intervalos = e.tabulacion["intervalos"]
        if intervalos:
            if x_cercano is None:
                intervalo = next((iv for iv in intervalos if iv["exacta"] is None), intervalos[0])
            else:
                intervalo = min(intervalos, key=lambda iv: 0 if iv["a"] <= x_cercano <= iv["b"]
                                else min(abs(iv["a"] - x_cercano), abs(iv["b"] - x_cercano)))
            await self.preparar_intervalo(intervalo)
        await self.actualizar_formula()
        e.paso = 2
        self.barra_pasos.refresh()
        self.tarjetas_resultado.refresh()
        self.panel.refresh()
        return True

    async def elegir_intervalo(self, intervalo):
        e = self.estado
        self._usar_intervalo(intervalo)
        e.grafica_general = await run.io_bound(graficas.grafica_funcion, e.funcion_lista(), e.tabulacion, e.intervalo_activo)

    async def resolver(self):
        e = self.estado
        f = e.funcion_lista()
        if f is None:
            ui.notify("Primero escriba una función válida en el paso 1.", type="negative", position="top")
            return
        try:
            resultado = self.calcular(f)
        except ValueError as error:
            ui.notify(str(error), type="negative", position="top", multi_line=True)
            return
        e.limpiar_resultados(tambien_grafica=False)
        e.resultado = resultado
        e.grafica_escalera = await run.io_bound(self.grafica_resumen, f, resultado)
        e.grafica_error = await run.io_bound(graficas.grafica_error, resultado)
        if e.tabulacion:
            raiz = resultado["raiz"] if resultado["convergio"] or "a_inicial" in resultado else None
            e.grafica_general = await run.io_bound(graficas.grafica_funcion, f, e.tabulacion, e.intervalo_activo, raiz)
        await self.cargar_grafica_iteracion(1)
        self.kpi_recien_calculado = True
        self.refrescar()
        self.ir_a(4)
        # Se remarca el resultado mas importante (con una pausa para que la tarjeta ya este dibujada)
        titulo = "Raíz encontrada"
        mensaje = (f"Después de {resultado['total_iteraciones']} iteraciones la raíz aproximada es "
                   f"{numero(resultado['raiz'], e.decimales)}. Abajo se explica cada iteración.")
        veredicto = resultado.get("veredicto")
        if veredicto and veredicto["tipo"] != "converge":
            titulo = "El método " + ("diverge" if veredicto["tipo"] == "diverge" else "no alcanzó E")
            mensaje = f"{veredicto['explicacion']} Abajo se explica cada iteración."
        with self.anclaje:
            ui.timer(0.6, lambda: guia.resaltar(self.tarjeta_raiz, titulo, mensaje), once=True)

    async def cargar_grafica_iteracion(self, k):
        e = self.estado
        if k not in e.graficas_iteracion:
            it = e.resultado["iteraciones"][k - 1]
            e.graficas_iteracion[k] = await run.io_bound(self.grafica_de_iteracion, e.funcion_lista(), it)
        return e.graficas_iteracion[k]

    # ------------------------------------------------------------------
    # Recorrido de las iteraciones (paso 4)
    # ------------------------------------------------------------------
    async def ver_iteracion(self, k):
        e = self.estado
        if not e.resultado:
            return
        k = max(1, min(e.resultado["total_iteraciones"], int(k)))
        await self.cargar_grafica_iteracion(k)
        e.iteracion_vista = k
        iteraciones.al_cambiar_iteracion(self)

    async def _avanzar_reproduccion(self):
        e = self.estado
        if not e.resultado or e.paso != 4 or e.iteracion_vista >= e.resultado["total_iteraciones"]:
            self.reproductor.deactivate()
            iteraciones.al_cambiar_iteracion(self)
            return
        await self.ver_iteracion(e.iteracion_vista + 1)

    async def alternar_reproduccion(self):
        e = self.estado
        if self.reproductor.active:
            self.reproductor.deactivate()
        else:
            if e.iteracion_vista >= e.resultado["total_iteraciones"]:
                await self.ver_iteracion(1)
            self.reproductor.activate()
        iteraciones.al_cambiar_iteracion(self)
