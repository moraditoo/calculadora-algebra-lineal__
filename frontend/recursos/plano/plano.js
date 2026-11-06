// frontend/recursos/plano/plano.js
// Plano cartesiano interactivo (al estilo de GeoGebra) para la grafica de f(x).
// La curva se recalcula en el navegador en cada movimiento, asi que se puede alejar
// o acercar sin limite practico y siempre se ve nitida.
//   Rueda: zoom en el punto del cursor (Shift + rueda: solo eje x, Alt + rueda: solo eje y)
//   Arrastrar: mover el plano     Pellizco (pantalla tactil): zoom     Doble clic: acercar ahi
// La funcion llega ya traducida desde Python (analizador.py: solo numeros, x y funciones de Math).
(function () {
  'use strict';

  const COLOR = {
    tinta: '#3a3a3c', suave: '#a1a1a6', acento: '#1d1d1f', positivo: '#2e7d5b', negativo: '#b3261e',
    rejilla: 'rgba(60, 60, 67, 0.13)', rejillaFina: 'rgba(60, 60, 67, 0.05)', texto: '#5f6368',
  };
  const FUENTE = "600 11px Inter, 'Segoe UI', system-ui, sans-serif";

  // Funciones auxiliares que usa la expresion traducida (mismo comportamiento que en Python)
  const F = {
    pot: (b, e) => (b === 0 && e < 0 ? NaN : Math.pow(b, e)),  // base negativa con exponente fraccionario -> NaN
    sec: (v) => 1 / Math.cos(v),
    csc: (v) => 1 / Math.sin(v),
    cot: (v) => 1 / Math.tan(v),
  };

  function compilar(expresion) {
    const fn = new Function('x', 'F', '"use strict"; return ' + expresion + ';');
    return (x) => {
      const y = fn(x, F);
      return Number.isFinite(y) ? y : NaN;  // fuera del dominio, division por cero o desborde: no se dibuja
    };
  }

  // Paso "redondo" para la rejilla: 1, 2 o 5 por una potencia de 10
  function pasoRedondo(bruto) {
    const p = Math.pow(10, Math.floor(Math.log10(bruto)));
    const m = bruto / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  }

  const SUPER = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' };

  // Numero de un eje: decimales segun el paso; notacion cientifica si es muy grande o muy chico
  function etiquetaEje(v, paso) {
    if (Math.abs(v) < paso * 1e-6) return '0';
    if (paso >= 1e5 || paso < 1e-4) {
      const [mantisa, exponente] = v.toExponential(2).split('e');
      const m = String(parseFloat(mantisa));
      const ex = String(parseInt(exponente, 10)).split('').map((c) => SUPER[c]).join('');
      return (m === '1' ? '' : m === '-1' ? '−' : m.replace('-', '−') + '·') + '10' + ex;
    }
    const decimales = Math.max(0, Math.ceil(-Math.log10(paso) - 1e-9));
    return v.toFixed(decimales).replace('-', '−');
  }

  // Numero para la lectura del cursor (6 cifras significativas, sin ceros de mas)
  function numeroCorto(v) {
    if (!Number.isFinite(v)) return 'no definida';
    if (v !== 0 && (Math.abs(v) >= 1e7 || Math.abs(v) < 1e-5)) return v.toExponential(4).replace('-', '−');
    return String(parseFloat(v.toPrecision(7))).replace('-', '−');
  }

  // Limites del eje y que no se dejan arrastrar por asintotas o valores enormes
  function limitesY(f, x0, x1) {
    const ys = [];
    for (let i = 0; i <= 800; i++) {
      const y = f(x0 + (x1 - x0) * i / 800);
      if (Number.isFinite(y)) ys.push(y);
    }
    if (!ys.length) return [-1, 1];
    ys.sort((a, b) => a - b);
    let bajo = ys[0], alto = ys[ys.length - 1];
    const q05 = ys[Math.floor(0.05 * (ys.length - 1))], q95 = ys[Math.floor(0.95 * (ys.length - 1))];
    if (alto - bajo > 25 * Math.max(q95 - q05, 1e-12)) {
      const extra = 0.6 * Math.max(q95 - q05, 1e-9);
      bajo = q05 - extra; alto = q95 + extra;
    }
    bajo = Math.min(bajo, 0); alto = Math.max(alto, 0);
    if (alto - bajo < 1e-15) { bajo -= 1; alto += 1; }
    const margen = 0.1 * (alto - bajo);
    return [bajo - margen, alto + margen];
  }

  // La vista de cada grafica se recuerda mientras no cambie la funcion ni el rango tabulado
  const memoria = {};

  class Plano {
    constructor(caja, datos) {
      this.caja = caja;
      this.lienzo = document.createElement('canvas');
      this.ctx = this.lienzo.getContext('2d');
      caja.appendChild(this.lienzo);

      const botones = [['mas', 'Acercar', 'add'], ['menos', 'Alejar', 'remove'],
                       ['alto', 'Ajustar el eje y a la curva', 'height'], ['inicio', 'Vista inicial', 'home']];
      const barra = document.createElement('div');
      barra.className = 'controles-zoom';
      barra.innerHTML = botones.map(([accion, titulo, icono]) =>
        `<button type="button" data-accion="${accion}" title="${titulo}"><span class="material-icons">${icono}</span></button>`).join('');
      caja.appendChild(barra);
      barra.addEventListener('click', (ev) => {
        const boton = ev.target.closest('button');
        if (boton) this.accion(boton.dataset.accion);
      });
      barra.addEventListener('pointerdown', (ev) => ev.stopPropagation());

      this.lectura = document.createElement('div');
      this.lectura.className = 'lectura-plano mono';
      caja.appendChild(this.lectura);

      this.punteros = new Map();
      this.cursor = null;
      this.eventos();
      new ResizeObserver(() => this.dibujar()).observe(caja);
      this.actualizar(datos);
    }

    actualizar(datos) {
      this.datos = datos;
      this.f = compilar(datos.expr);
      this.firma = `${datos.expr}|${datos.xmin}|${datos.xmax}`;
      const guardada = memoria[datos.clave];
      this.vista = guardada && guardada.firma === this.firma ? { ...guardada.vista } : this.vistaInicial();
      this.dibujar();
    }

    vistaInicial() {
      const [y0, y1] = limitesY(this.f, this.datos.xmin, this.datos.xmax);
      return { x0: this.datos.xmin, x1: this.datos.xmax, y0, y1 };
    }

    // ---------------- Conversiones entre el plano y la pantalla ----------------
    X(x) { return (x - this.vista.x0) / (this.vista.x1 - this.vista.x0) * this.ancho; }
    Y(y) { return this.alto - (y - this.vista.y0) / (this.vista.y1 - this.vista.y0) * this.alto; }
    xDe(px) { return this.vista.x0 + px / this.ancho * (this.vista.x1 - this.vista.x0); }
    yDe(py) { return this.vista.y0 + (this.alto - py) / this.alto * (this.vista.y1 - this.vista.y0); }

    // Zoom con centro en el pixel (px, py); factor < 1 acerca y > 1 aleja
    zoom(factor, px, py, ejes = 'xy') {
      const v = this.vista;
      const x = this.xDe(px), y = this.yDe(py);
      const nueva = { ...v };
      if (ejes.includes('x')) { nueva.x0 = x - (x - v.x0) * factor; nueva.x1 = x + (v.x1 - x) * factor; }
      if (ejes.includes('y')) { nueva.y0 = y - (y - v.y0) * factor; nueva.y1 = y + (v.y1 - y) * factor; }
      // Limites para no perder precision de punto flotante
      const valido = (a, b) => {
        const ancho = b - a, escala = Math.max(1, Math.abs(a), Math.abs(b));
        return ancho > 1e-11 * escala && ancho < 1e14;
      };
      if (valido(nueva.x0, nueva.x1) && valido(nueva.y0, nueva.y1)) {
        this.vista = nueva;
        this.cambio();
      }
    }

    mover(dx, dy) {
      const v = this.vista;
      const ux = dx / this.ancho * (v.x1 - v.x0), uy = dy / this.alto * (v.y1 - v.y0);
      this.vista = { x0: v.x0 - ux, x1: v.x1 - ux, y0: v.y0 + uy, y1: v.y1 + uy };
      this.cambio();
    }

    accion(nombre) {
      if (nombre === 'mas') this.zoom(1 / 1.6, this.ancho / 2, this.alto / 2);
      else if (nombre === 'menos') this.zoom(1.6, this.ancho / 2, this.alto / 2);
      else if (nombre === 'inicio') { this.vista = this.vistaInicial(); this.cambio(); }
      else if (nombre === 'alto') {
        const [y0, y1] = limitesY(this.f, this.vista.x0, this.vista.x1);
        this.vista = { ...this.vista, y0, y1 };
        this.cambio();
      }
    }

    // Guarda la vista, redibuja y avisa al servidor (para «Tabular la vista actual»)
    cambio() {
      memoria[this.datos.clave] = { firma: this.firma, vista: { ...this.vista } };
      this.dibujar();
      clearTimeout(this.temporizador);
      this.temporizador = setTimeout(() => {
        if (window.emitEvent && this.datos.evento) {
          window.emitEvent(this.datos.evento, { xmin: this.vista.x0, xmax: this.vista.x1 });
        }
      }, 300);
    }

    // ---------------- Raton y pantalla tactil ----------------
    eventos() {
      const c = this.lienzo;
      const local = (ev) => { const r = c.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top]; };

      c.addEventListener('wheel', (ev) => {
        ev.preventDefault();
        const [px, py] = local(ev);
        const delta = ev.deltaY * (ev.deltaMode === 1 ? 16 : ev.deltaMode === 2 ? 400 : 1);
        const ejes = ev.shiftKey ? 'x' : ev.altKey ? 'y' : 'xy';
        // Con Shift algunos navegadores mandan el giro en deltaX
        const giro = ev.shiftKey && !delta ? ev.deltaX : delta;
        this.zoom(Math.exp(giro * 0.0015), px, py, ejes);
      }, { passive: false });

      c.addEventListener('dblclick', (ev) => {
        const [px, py] = local(ev);
        this.zoom(0.5, px, py);
      });

      c.addEventListener('pointerdown', (ev) => {
        c.setPointerCapture(ev.pointerId);
        this.punteros.set(ev.pointerId, local(ev));
        this.caja.classList.add('arrastrando');
      });

      c.addEventListener('pointermove', (ev) => {
        const actual = local(ev);
        if (!this.punteros.has(ev.pointerId)) {  // solo pasa el cursor: se muestra el punto de la curva
          this.cursor = actual;
          this.dibujar();
          return;
        }
        const anterior = this.punteros.get(ev.pointerId);
        if (this.punteros.size === 1) {
          this.mover(actual[0] - anterior[0], actual[1] - anterior[1]);
        } else if (this.punteros.size === 2) {
          // Pellizco: la distancia entre los dos dedos marca el zoom
          const otro = [...this.punteros.entries()].find(([id]) => id !== ev.pointerId)[1];
          const antes = Math.hypot(anterior[0] - otro[0], anterior[1] - otro[1]);
          const ahora = Math.hypot(actual[0] - otro[0], actual[1] - otro[1]);
          if (antes > 0 && ahora > 0) this.zoom(antes / ahora, (actual[0] + otro[0]) / 2, (actual[1] + otro[1]) / 2);
        }
        this.punteros.set(ev.pointerId, actual);
        this.cursor = null;
      });

      const soltar = (ev) => {
        this.punteros.delete(ev.pointerId);
        if (!this.punteros.size) this.caja.classList.remove('arrastrando');
      };
      c.addEventListener('pointerup', soltar);
      c.addEventListener('pointercancel', soltar);
      c.addEventListener('pointerleave', () => { this.cursor = null; this.dibujar(); });
    }

    // ---------------- Dibujo ----------------
    dibujar() {
      const ancho = this.caja.clientWidth, alto = this.caja.clientHeight;
      if (!ancho || !alto) return;  // la vista esta oculta: se dibuja al aparecer
      const dpr = window.devicePixelRatio || 1;
      if (this.lienzo.width !== Math.round(ancho * dpr) || this.lienzo.height !== Math.round(alto * dpr)) {
        this.lienzo.width = Math.round(ancho * dpr);
        this.lienzo.height = Math.round(alto * dpr);
      }
      this.ancho = ancho; this.alto = alto;
      const ctx = this.ctx;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, ancho, alto);

      this.rejilla();
      this.intervalos();
      this.asintotas();
      this.curva();
      this.raices();
      this.puntoCursor();
    }

    lineasEje(eje) {
      const v = this.vista;
      const [a, b, pixeles] = eje === 'x' ? [v.x0, v.x1, this.ancho] : [v.y0, v.y1, this.alto];
      const paso = pasoRedondo((b - a) / Math.max(2, pixeles / 95));
      const mantisa = Math.round(paso / Math.pow(10, Math.floor(Math.log10(paso))));
      const fino = paso / (mantisa === 2 ? 4 : 5);
      return { paso, fino, a, b };
    }

    rejilla() {
      const ctx = this.ctx, W = this.ancho, H = this.alto;
      const ex = this.lineasEje('x'), ey = this.lineasEje('y');

      // Lineas finas y principales
      for (const [e, color] of [[ex, COLOR.rejillaFina], [ey, COLOR.rejillaFina]]) {
        ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.beginPath();
        for (let i = Math.ceil(e.a / e.fino); i <= Math.floor(e.b / e.fino); i++) {
          if (e === ex) { const p = Math.round(this.X(i * e.fino)) + 0.5; ctx.moveTo(p, 0); ctx.lineTo(p, H); }
          else { const p = Math.round(this.Y(i * e.fino)) + 0.5; ctx.moveTo(0, p); ctx.lineTo(W, p); }
        }
        ctx.stroke();
      }
      ctx.strokeStyle = COLOR.rejilla; ctx.beginPath();
      for (let i = Math.ceil(ex.a / ex.paso); i <= Math.floor(ex.b / ex.paso); i++) {
        const p = Math.round(this.X(i * ex.paso)) + 0.5; ctx.moveTo(p, 0); ctx.lineTo(p, H);
      }
      for (let i = Math.ceil(ey.a / ey.paso); i <= Math.floor(ey.b / ey.paso); i++) {
        const p = Math.round(this.Y(i * ey.paso)) + 0.5; ctx.moveTo(0, p); ctx.lineTo(W, p);
      }
      ctx.stroke();

      // Ejes x e y (si se ven)
      const origenX = this.X(0), origenY = this.Y(0);
      ctx.strokeStyle = COLOR.tinta; ctx.lineWidth = 1.3; ctx.beginPath();
      if (origenY >= 0 && origenY <= H) { ctx.moveTo(0, Math.round(origenY) + 0.5); ctx.lineTo(W, Math.round(origenY) + 0.5); }
      if (origenX >= 0 && origenX <= W) { ctx.moveTo(Math.round(origenX) + 0.5, 0); ctx.lineTo(Math.round(origenX) + 0.5, H); }
      ctx.stroke();

      // Numeros de los ejes: pegados al eje, o al borde si el eje quedo fuera de la vista
      ctx.font = FUENTE; ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)'; ctx.fillStyle = COLOR.texto;
      const texto = (t, x, y) => { ctx.strokeText(t, x, y); ctx.fillText(t, x, y); };
      const filaX = Math.min(Math.max(origenY + 5, 4), H - 16);
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      for (let i = Math.ceil(ex.a / ex.paso); i <= Math.floor(ex.b / ex.paso); i++) {
        const p = this.X(i * ex.paso);
        if (i === 0 && origenX >= 0 && origenX <= W) continue;
        if (p < 14 || p > W - 14) continue;
        texto(etiquetaEje(i * ex.paso, ex.paso), p, filaX);
      }
      let columnaY, alineacion;
      if (origenX < 40) { columnaY = 6; alineacion = 'left'; }
      else if (origenX > W - 6) { columnaY = W - 6; alineacion = 'right'; }
      else { columnaY = origenX - 6; alineacion = 'right'; }
      ctx.textAlign = alineacion; ctx.textBaseline = 'middle';
      for (let i = Math.ceil(ey.a / ey.paso); i <= Math.floor(ey.b / ey.paso); i++) {
        const p = this.Y(i * ey.paso);
        if (i === 0 || p < 10 || p > H - 10) continue;
        texto(etiquetaEje(i * ey.paso, ey.paso), columnaY, p);
      }
      if (origenX >= 0 && origenX <= W && origenY >= 0 && origenY <= H) {
        ctx.textAlign = 'right'; ctx.textBaseline = 'top';
        texto('0', origenX - 5, origenY + 5);
      }
      ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    }

    intervalos() {
      const ctx = this.ctx, H = this.alto;
      for (const iv of this.datos.intervalos || []) {
        const a = this.X(iv.a), b = this.X(iv.b);
        if (b < 0 || a > this.ancho) continue;
        ctx.fillStyle = iv.activo ? 'rgba(58, 58, 60, 0.12)' : 'rgba(58, 58, 60, 0.05)';
        ctx.fillRect(a, 0, Math.max(b - a, 1), H);
        ctx.setLineDash([4, 3]); ctx.lineWidth = 1;
        ctx.strokeStyle = iv.activo ? 'rgba(58, 58, 60, 0.6)' : 'rgba(58, 58, 60, 0.25)';
        ctx.beginPath(); ctx.moveTo(a + 0.5, 0); ctx.lineTo(a + 0.5, H); ctx.moveTo(b + 0.5, 0); ctx.lineTo(b + 0.5, H); ctx.stroke();
        ctx.setLineDash([]);
        // Etiqueta I1, I2... (solo si cabe)
        const nombre = 'I' + iv.numero;
        ctx.font = "800 10.5px Inter, 'Segoe UI', system-ui, sans-serif";
        const w = ctx.measureText(nombre).width + 12;
        if (b - a > w * 0.6 || iv.activo) {
          const cx = (a + b) / 2;
          ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
          ctx.strokeStyle = iv.activo ? COLOR.tinta : COLOR.suave; ctx.lineWidth = iv.activo ? 1.4 : 0.8;
          ctx.beginPath(); ctx.roundRect(cx - w / 2, 46, w, 18, 9); ctx.fill(); ctx.stroke();
          ctx.fillStyle = iv.activo ? COLOR.acento : COLOR.suave; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText(nombre, cx, 55.5);
          ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
        }
        for (const [x, y] of [[iv.a, iv.fa], [iv.b, iv.fb]]) this.punto(x, y, y > 0 ? COLOR.positivo : COLOR.negativo, 4);
      }
    }

    asintotas() {
      const ctx = this.ctx;
      for (const x of this.datos.asintotas || []) {
        const p = this.X(x);
        if (p < 0 || p > this.ancho) continue;
        ctx.strokeStyle = 'rgba(179, 38, 30, 0.55)'; ctx.lineWidth = 1.2; ctx.setLineDash([2, 3]);
        ctx.beginPath(); ctx.moveTo(p + 0.5, 0); ctx.lineTo(p + 0.5, this.alto); ctx.stroke(); ctx.setLineDash([]);
        ctx.save(); ctx.translate(p - 4, this.alto - 10); ctx.rotate(-Math.PI / 2);
        ctx.font = FUENTE; ctx.fillStyle = 'rgba(179, 38, 30, 0.8)'; ctx.fillText('asíntota', 0, 0);
        ctx.restore();
      }
    }

    curva() {
      const ctx = this.ctx, f = this.f, H = this.alto, v = this.vista;
      const n = Math.ceil(this.ancho * 1.5);
      // Punto en pantalla; lo que se sale mucho se recorta para que el lienzo no reciba valores enormes
      const P = (x, y) => [this.X(x), Math.max(-4 * H, Math.min(5 * H, this.Y(y)))];
      ctx.strokeStyle = COLOR.tinta; ctx.lineWidth = 2.3; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
      ctx.beginPath();
      let anterior = null, xHueco = null;  // xHueco: ultima x donde f no estaba definida
      for (let i = 0; i <= n; i++) {
        const x = v.x0 + (v.x1 - v.x0) * i / n;
        const y = f(x);
        if (!Number.isFinite(y)) {
          // La rama llega hasta el borde del dominio (por ejemplo ln x cerca de 0)
          if (anterior) ctx.lineTo(...P(...this.borde(anterior.x, anterior.y, x)));
          anterior = null; xHueco = x;
          continue;
        }
        const py = this.Y(y);
        if (!anterior) {
          if (xHueco !== null) { ctx.moveTo(...P(...this.borde(x, y, xHueco))); ctx.lineTo(...P(x, y)); }
          else ctx.moveTo(...P(x, y));
        } else if (Math.abs(py - anterior.py) > 30) {
          // Cambio brusco: se revisa si es una asintota o un salto (no se unen los puntos)
          const s = this.salto(anterior.x, anterior.y, x, y);
          if (s) {
            ctx.lineTo(...P(s.a, s.fa));   // la rama de la izquierda sigue hasta la discontinuidad
            ctx.moveTo(...P(s.b, s.fb));   // y la de la derecha empieza justo despues
          }
          ctx.lineTo(...P(x, y));
        } else {
          ctx.lineTo(...P(x, y));
        }
        anterior = { x, y, py };
      }
      ctx.stroke();
    }

    // Biseccion entre dos puntos: se sigue la mitad donde f cambia mas. Si al final el cambio
    // sigue siendo visible, hay una discontinuidad y se devuelve el ultimo punto de cada lado.
    salto(a, fa, b, fb) {
      for (let k = 0; k < 48; k++) {
        const m = (a + b) / 2;
        if (m <= a || m >= b) break;
        const fm = this.f(m);
        if (!Number.isFinite(fm)) return { a, fa, b, fb };
        if (Math.abs(fm - fa) >= Math.abs(fb - fm)) { b = m; fb = fm; } else { a = m; fa = fm; }
      }
      return Math.abs(this.Y(fb) - this.Y(fa)) > 1.5 ? { a, fa, b, fb } : null;
    }

    // Ultimo punto definido entre x (definida) y xFuera (no definida)
    borde(x, y, xFuera) {
      for (let k = 0; k < 48; k++) {
        const m = (x + xFuera) / 2;
        if (m === x || m === xFuera) break;
        const fm = this.f(m);
        if (Number.isFinite(fm)) { x = m; y = fm; } else xFuera = m;
      }
      return [x, y];
    }

    punto(x, y, color, radio) {
      const px = this.X(x), py = this.Y(y);
      if (px < -radio || px > this.ancho + radio || py < -radio || py > this.alto + radio) return;
      const ctx = this.ctx;
      ctx.fillStyle = color; ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(px, py, radio, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
    }

    burbuja(texto, px, py) {
      const ctx = this.ctx;
      ctx.font = "700 11px Inter, 'Segoe UI', system-ui, sans-serif";
      const w = ctx.measureText(texto).width + 16, h = 22;
      const x = Math.min(Math.max(px + 10, 4), this.ancho - w - 4);
      const y = Math.min(Math.max(py - h - 10, 4), this.alto - h - 4);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'; ctx.strokeStyle = COLOR.suave; ctx.lineWidth = 0.8;
      ctx.beginPath(); ctx.roundRect(x, y, w, h, 11); ctx.fill(); ctx.stroke();
      ctx.fillStyle = COLOR.acento; ctx.textBaseline = 'middle'; ctx.fillText(texto, x + 8, y + h / 2 + 0.5);
      ctx.textBaseline = 'alphabetic';
    }

    raices() {
      const ctx = this.ctx;
      for (const r of this.datos.raices || []) {
        const px = this.X(r.x), py = this.Y(0);
        if (px < 0 || px > this.ancho || py < 0 || py > this.alto) continue;
        ctx.fillStyle = 'rgba(29, 29, 31, 0.12)';
        ctx.beginPath(); ctx.arc(px, py, 10, 0, 2 * Math.PI); ctx.fill();
        this.punto(r.x, 0, COLOR.acento, 5);
        this.burbuja(r.texto, px, py);
      }
    }

    puntoCursor() {
      if (!this.cursor) {
        this.lectura.textContent = 'Rueda: zoom · arrastrar: mover · Shift + rueda: solo eje x · doble clic: acercar';
        return;
      }
      const x = this.xDe(this.cursor[0]), y = this.f(x);
      this.lectura.textContent = `x = ${numeroCorto(x)}    f(x) = ${numeroCorto(y)}`;
      if (!Number.isFinite(y)) return;
      const ctx = this.ctx, px = this.X(x), py = this.Y(y);
      ctx.strokeStyle = 'rgba(58, 58, 60, 0.35)'; ctx.lineWidth = 1; ctx.setLineDash([3, 3]);
      ctx.beginPath(); ctx.moveTo(px + 0.5, this.Y(0)); ctx.lineTo(px + 0.5, py); ctx.stroke(); ctx.setLineDash([]);
      this.punto(x, y, y > 0 ? COLOR.positivo : y < 0 ? COLOR.negativo : COLOR.acento, 5);
    }
  }

  window.Plano = {
    // Crea (o actualiza) el plano dentro del elemento con ese id; espera a que exista en la pagina
    montar(id, datos, intentos = 0) {
      const caja = document.getElementById(id);
      if (!caja) {
        if (intentos < 120) setTimeout(() => window.Plano.montar(id, datos, intentos + 1), 25);
        return;
      }
      if (caja._plano) caja._plano.actualizar(datos);
      else caja._plano = new Plano(caja, datos);
    },
  };
})();
