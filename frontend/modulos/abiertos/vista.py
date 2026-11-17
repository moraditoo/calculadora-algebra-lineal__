# frontend/modulos/abiertos/vista.py
# Vistas de los metodos abiertos: Newton-Raphson y secante.
# Heredan la vista de biseccion (barra de pasos, grafica, recorrido de iteraciones, decimales,
# guia) y cambian lo propio: valores iniciales en lugar de [a, b], la derivada f'(x),
# la explicacion de cada iteracion, la tabla, las graficas y la conclusion.
from nicegui import run, ui

from backend.metodos_numericos import graficas
from backend.metodos_numericos.biseccion import leer_numero
from backend.metodos_numericos import newton_raphson as metodo_newton
from backend.metodos_numericos import secante as metodo_secante
from ...formato import escapar
from ..biseccion.pasos import funcion, grafica, iteraciones as iteraciones_base
from ..biseccion.vista import VistaBiseccion
from .ejemplos import EJEMPLOS_NEWTON, EJEMPLOS_SECANTE
from .estado import NOMBRE_ERROR, EstadoAbierto
from .pasos import algoritmo, conclusion, derivada, eleccion, iteraciones, parametros


def construir_newton():
    return VistaNewton()


def construir_secante():
    return VistaSecante()


class VistaAbierta(VistaBiseccion):
    ESTADO = EstadoAbierto
    NOMBRES_ERROR = NOMBRE_ERROR
    PUNTO = "x"
    CRITERIO_DE_CLASE = "absoluto"
    NOTA_CRITERIO = ("Por defecto se usa el error absoluto Ea = |xₙ₊₁ − xₙ| (cambio entre aproximaciones). También "
                     "puede usar el relativo, el residuo |f(xₙ₊₁)| o ambos a la vez. El método se detiene cuando el "
                     "error es menor que E o cuando se llega al máximo de iteraciones.")
    AVISO_RAIZ_DOBLE = ("pero el método de {nombre} sí puede acercarse a ella (más lento): use un valor inicial "
                        "cerca de ese punto.")
    PASOS_DIBUJO = {1: funcion.construir, 2: grafica.construir, 3: parametros.construir,
                    4: iteraciones_base.construir, 5: conclusion.construir, 6: algoritmo.construir}
    USA_DERIVADA = True       # Newton-Raphson la necesita; la secante solo la muestra para comparar

    def __init__(self):
        self.refrescar_derivada = None  # lo llena el paso 1
        self._refrescar_paso2 = None    # lo llena el paso 2
        super().__init__()
        # Clic sobre la grafica interactiva: elige el valor inicial
        ui.on(f"{self.PREFIJO}_elegir", self._al_elegir_en_grafica)

    # ------------------------------------------------------------------
    # Paso 1: la derivada f'(x) debajo de la funcion
    # ------------------------------------------------------------------
    def despues_de_formula(self):
        derivada.seccion(self)

    def derivada_usada(self):
        e = self.estado
        return e.derivada_lista() if self.USA_DERIVADA else e.derivada_automatica()

    async def actualizar_formula(self):
        await super().actualizar_formula()
        await self.actualizar_derivada()

    async def actualizar_derivada(self):
        d = self.derivada_usada()
        self.estado.formula_derivada = await run.io_bound(graficas.formula, d.mathtext) if d else None
        if self.refrescar_derivada:
            self.refrescar_derivada()

    # ------------------------------------------------------------------
    # Paso 2: la grafica ubica la raiz y el USUARIO elige x0 (no se llena solo)
    # ------------------------------------------------------------------
    NOTA_INTERVALOS = ("En Newton-Raphson y la secante (métodos abiertos) el intervalo <b>solo sirve para ubicar la raíz</b>: "
                       "el método no lo conserva. Con él usted elige el valor inicial x₀ cerca de la raíz.")
    AYUDA_TARJETAS = ("Cada tarjeta es un tramo donde la curva cruza el eje x. Haga clic en una para ver la recomendación "
                      "de valor inicial en ese tramo; el valor lo elige usted.")

    def valores_elegidos(self):
        """{'x0': 1.5, 'x1': 2.0} con los valores iniciales que ya son numeros validos."""
        valores = {}
        for nombre in ("x0", "x1")[:self.VALORES]:
            try:
                valores[nombre] = leer_numero(getattr(self.estado, nombre), nombre)
            except ValueError:
                pass
        return valores

    def _intervalo_de_valores(self, intervalos):
        """El intervalo donde estan los valores iniciales elegidos (None si no estan en ninguno)."""
        valores = list(self.valores_elegidos().values())
        for iv in intervalos:
            if any(iv["a"] <= v <= iv["b"] for v in valores):
                return iv
        if len(valores) == 2:  # secante: x0 y x1 alrededor de la raiz
            bajo, alto = min(valores), max(valores)
            return next((iv for iv in intervalos if bajo <= iv["a"] and iv["b"] <= alto), None)
        return None

    def _usar_intervalo(self, intervalo, forzar=False):
        """Marca el intervalo. Los valores iniciales solo cambian si el usuario pidio la recomendacion."""
        e = self.estado
        e.intervalo_activo = intervalo["numero"] if intervalo else None
        if forzar and intervalo:
            for nombre, valor in self.valores_de_intervalo(intervalo).items():
                setattr(e, nombre, f"{valor:.12g}")

    def _intervalo_inicial(self, intervalos):
        return self._intervalo_de_valores(intervalos)

    async def _redibujar_grafica(self):
        e = self.estado
        e.grafica_general = await run.io_bound(graficas.grafica_funcion, e.funcion_lista(), e.tabulacion, e.intervalo_activo)

    async def elegir_intervalo(self, intervalo):
        """Clic en una tarjeta: se marca el intervalo y se muestra su recomendacion (x0 no cambia)."""
        self._usar_intervalo(intervalo)
        await self._redibujar_grafica()

    async def preparar_intervalo(self, intervalo):
        """Desde la pantalla principal: se marca el tramo de la raiz y se propone su valor inicial."""
        await self.aplicar_recomendacion(intervalo)

    async def aplicar_recomendacion(self, intervalo):
        """El usuario pidio usar el valor recomendado para ese intervalo."""
        self._usar_intervalo(intervalo, forzar=True)
        self.estado.siguiente = "x0"
        self.estado.limpiar_resultados(tambien_grafica=False)
        await self._redibujar_grafica()
        self.refrescar()

    async def _al_elegir_en_grafica(self, evento):
        """Clic sobre la grafica interactiva del paso 2: ese x es el valor inicial."""
        e = self.estado
        argumento = evento.args[0] if isinstance(evento.args, list) else evento.args
        try:
            x = float(argumento["x"])
        except (KeyError, TypeError, ValueError):
            return
        if e.paso != 2 or e.tabulacion is None:
            return
        nombre = e.siguiente if self.VALORES == 2 else "x0"
        setattr(e, nombre, f"{x:.12g}")
        if self.VALORES == 2:
            e.siguiente = "x1" if nombre == "x0" else "x0"
        e.limpiar_resultados(tambien_grafica=False)
        self._usar_intervalo(self._intervalo_de_valores(e.tabulacion["intervalos"]))
        self.refrescar()
        if self._refrescar_paso2:
            self._refrescar_paso2()
        await self._redibujar_grafica()

    def datos_plano_extra(self):
        nombres = {"x0": "x₀", "x1": "x₁"}
        marcas = [{"x": v, "texto": f"{nombres[n]} = {v:g}"} for n, v in self.valores_elegidos().items()]
        if self.VALORES == 2:
            ayuda = ("Haga clic sobre la gráfica para elegir los valores iniciales: el próximo clic elige "
                     + ("x₀" if self.estado.siguiente == "x0" else "x₁") + ".  Rueda: zoom · arrastrar: mover")
        else:
            ayuda = "Haga clic sobre la gráfica, cerca de donde la curva corta el eje x, para elegir x₀.  Rueda: zoom · arrastrar: mover"
        return {"eleccion": f"{self.PREFIJO}_elegir", "marcas": marcas, "ayuda": ayuda}

    def panel_bajo_intervalos(self, refrescar):
        self._refrescar_paso2 = refrescar
        eleccion.panel(self)

    def textos_continuar(self):
        valores = self.valores_elegidos()
        if len(valores) == self.VALORES:
            texto = ", ".join(f"{'x₀' if n == 'x0' else 'x₁'} = {v:g}" for n, v in valores.items())
            return f"Continuar con {texto}", None
        return "Escribir " + ("x₀ y x₁" if self.VALORES == 2 else "x₀") + " a mano", None

    # ------------------------------------------------------------------
    # Pasos 4 y 5
    # ------------------------------------------------------------------
    async def resolver(self):
        # Si se resuelve un ejemplo sin pasar por el paso 1, falta dibujar f'(x) para la conclusion
        if self.estado.formula_derivada is None and self.derivada_usada() is not None:
            await self.actualizar_derivada()
        await super().resolver()

    def grafica_resumen(self, f, resultado):
        return graficas.grafica_recorrido(f, resultado)

    def tabla_iteraciones(self, r, d, actual):
        return iteraciones.tabla(r, d, actual, self.PREFIJO)


class VistaNewton(VistaAbierta):
    NOMBRE = "Newton-Raphson"
    TITULO = "Método de Newton-Raphson"
    DESCRIPCION = ("Método abierto: desde un valor inicial x₀ se traza la recta tangente a la curva; donde corta el eje x "
                   "está la siguiente aproximación. La derivada f'(x) se calcula sola (o se puede escribir).")
    ICONO = "trending_up"
    PREFIJO = "newton"
    EJEMPLOS = EJEMPLOS_NEWTON
    VALORES = 1
    AVISO_RAIZ_EXACTA = "esa raíz ya es exacta: si x₀ es ese valor, Newton-Raphson la confirma de inmediato (f(x₀) = 0)."
    INTRO_ITERACIONES = ("Cada iteración traza la tangente en (xₙ, f(xₙ)) y toma su corte con el eje x como xₙ₊₁. "
                         "Use las flechas, el control deslizante, la tabla o <b>Reproducir</b>.")
    EXPLICACION_RENGLON = iteraciones.EXPLICACION_NEWTON

    def valores_de_intervalo(self, iv):
        """x0 recomendado: el extremo del intervalo donde |f| es menor (el mas cercano a la raiz),
        salvo que ahi la tangente sea horizontal (f' = 0)."""
        cercano, lejano = (iv["a"], iv["b"]) if abs(iv["fa"]) <= abs(iv["fb"]) else (iv["b"], iv["a"])
        df = self.derivada_usada()
        pendiente = df.evaluar(cercano) if df else None
        if df is not None and (pendiente is None or abs(pendiente) < 1e-12):
            cercano = lejano
        return {"x0": cercano}

    def calcular(self, f):
        e = self.estado
        df = e.derivada_lista()
        if df is None:
            raise ValueError(f"La derivada escrita en el paso 1 no es válida: {e.error_derivada}")
        resultado = metodo_newton.newton_raphson(f, df, e.x0, e.tolerancia, e.criterio, e.max_iteraciones)
        resultado["derivada_escrita"] = e.usar_derivada_escrita
        return resultado

    def renglones(self, it, r, d):
        return iteraciones.renglones_newton(it, r, d)

    def grafica_de_iteracion(self, f, it):
        return graficas.grafica_newton(f, it)

    def resumen_ejemplo(self, ejemplo):
        return f'x₀ = {ejemplo["x0"]:g} · {escapar(NOMBRE_ERROR[ejemplo["criterio"]])} &lt; {escapar(ejemplo["tolerancia"])}'


class VistaSecante(VistaAbierta):
    NOMBRE = "la secante"
    TITULO = "Método de la Secante"
    DESCRIPCION = ("Método abierto: con dos valores iniciales x₀ y x₁ se traza la recta secante; donde corta el eje x está "
                   "la nueva aproximación. No necesita la derivada: la pendiente se aproxima con dos puntos.")
    ICONO = "insights"
    PREFIJO = "secante"
    EJEMPLOS = EJEMPLOS_SECANTE
    VALORES = 2
    USA_DERIVADA = False
    AVISO_RAIZ_EXACTA = "esa raíz ya es exacta: si x₁ es ese valor, la secante la confirma de inmediato (f(x₁) = 0)."
    INTRO_ITERACIONES = ("Cada iteración une (xₙ₋₁, f(xₙ₋₁)) y (xₙ, f(xₙ)) con una recta secante; donde corta el eje x "
                         "está xₙ₊₁. Luego se desplazan las dos aproximaciones. "
                         "Use las flechas, el control deslizante, la tabla o <b>Reproducir</b>.")
    EXPLICACION_RENGLON = iteraciones.EXPLICACION_SECANTE

    def valores_de_intervalo(self, iv):
        """Como en clase: x0 y x1 son los extremos del intervalo donde cambia el signo."""
        return {"x0": iv["a"], "x1": iv["b"]}

    def calcular(self, f):
        e = self.estado
        df = f.derivada()  # no la usa la formula: solo sirve para comparar la pendiente de la secante
        resultado = metodo_secante.secante(f, e.x0, e.x1, e.tolerancia, e.criterio, e.max_iteraciones, df=df)
        # Para comparar: cuantas iteraciones necesita Newton-Raphson desde x0 con la misma tolerancia
        try:
            newton = metodo_newton.newton_raphson(f, df, e.x0, e.tolerancia, e.criterio, e.max_iteraciones)
            resultado["comparacion"] = ("Newton-Raphson", f"x₀ = {newton['x0']:g}",
                                        newton["total_iteraciones"], newton["convergio"])
        except ValueError:
            resultado["comparacion"] = None
        return resultado

    def renglones(self, it, r, d):
        return iteraciones.renglones_secante(it, r, d)

    def grafica_de_iteracion(self, f, it):
        return graficas.grafica_secante(f, it)

    def resumen_ejemplo(self, ejemplo):
        return (f'x₀ = {ejemplo["x0"]:g}, x₁ = {ejemplo["x1"]:g} · '
                f'{escapar(NOMBRE_ERROR[ejemplo["criterio"]])} &lt; {escapar(ejemplo["tolerancia"])}')
