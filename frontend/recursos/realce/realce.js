// recursos/realce/realce.js
// Activa solas las librerias de presentacion en todo elemento nuevo de la pagina:
//   [data-tex]        -> formula dibujada con KaTeX (data-bloque="1" para formula centrada)
//   [data-contar]     -> numero que sube hasta su valor con CountUp.js
//   .auto-animar      -> los hijos que entran, salen o se mueven se animan con auto-animate
// Python solo escribe esos atributos; aqui un MutationObserver los encuentra al aparecer.
(function () {
  const reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function dibujarTex(el) {
    el.dataset.listo = '1';
    if (!window.katex) { el.textContent = el.dataset.tex; return; }
    try {
      window.katex.render(el.dataset.tex, el, { displayMode: el.dataset.bloque === '1', throwOnError: false, strict: false });
    } catch (e) {
      el.textContent = el.dataset.tex;
    }
  }

  function contar(el) {
    el.dataset.listo = '1';
    const valor = parseFloat(el.dataset.contar);
    const decimales = parseInt(el.dataset.decimales || '0', 10);
    if (reducir || !window.countUp || !isFinite(valor)) return;
    const final = el.textContent;
    const animacion = new window.countUp.CountUp(el, valor, {
      decimalPlaces: decimales, duration: 1.1, useGrouping: false, useEasing: true,
      formattingFn: (n) => n.toFixed(decimales).replace('-', '−'),
    });
    if (!animacion.error) animacion.start(() => { el.textContent = final; });
  }

  function animar(el) {
    if (!window.autoAnimate || reducir) return;
    el.dataset.listo = '1';
    window.autoAnimate(el, { duration: 280, easing: 'cubic-bezier(0.22, 0.9, 0.24, 1)' });
  }

  function revisar(raiz) {
    if (!raiz || raiz.nodeType !== 1) return;
    const buscar = (selector, accion) => {
      if (raiz.matches(selector)) accion(raiz);
      raiz.querySelectorAll(selector).forEach(accion);
    };
    buscar('[data-tex]:not([data-listo])', dibujarTex);
    buscar('[data-contar]:not([data-listo])', contar);
    buscar('.auto-animar:not([data-listo])', animar);
  }

  function iniciar() {
    revisar(document.body);
    new MutationObserver((cambios) => {
      for (const cambio of cambios) cambio.addedNodes.forEach(revisar);
    }).observe(document.body, { childList: true, subtree: true });
  }

  // auto-animate es un modulo ES: avisa cuando termina de cargar
  window.addEventListener('autoanimate-listo', () => document.body && revisar(document.body));
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
