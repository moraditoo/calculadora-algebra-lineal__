// frontend/recursos/teclado/teclado.js
// Teclado de funciones del programa (sen, cos, ln, √, fracciones...). Cada tecla inserta su
// contenido donde esta el cursor: en LaTeX si el campo es el editor matematico (MathLive) o como
// texto si es un campo de texto normal. El campo se busca dentro del mismo contenedor
// marcado con data-zona-teclado, asi cada campo usa su propio teclado.
(function () {
  // En el texto de una tecla marca donde queda el cursor: sen(▮) deja el cursor entre los parentesis
  const CURSOR = '▮';

  function campoDe(tecla) {
    const zona = tecla.closest('[data-zona-teclado]');
    if (!zona) return null;
    return zona.querySelector('math-field') || zona.querySelector('input, textarea');
  }

  // Avisa a la aplicacion (y a Vue) que el contenido cambio
  function avisar(campo) {
    campo.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function enEditor(mf, tecla) {
    const accion = tecla.dataset.accion;
    mf.focus();
    if (accion === 'izquierda') mf.executeCommand('moveToPreviousChar');
    else if (accion === 'derecha') mf.executeCommand('moveToNextChar');
    else if (accion === 'borrar') mf.executeCommand('deleteBackward');
    else if (accion === 'limpiar') mf.value = '';
    else mf.insert(tecla.dataset.latex, { format: 'latex', selectionMode: 'placeholder', focus: true });
    if (accion !== 'izquierda' && accion !== 'derecha') avisar(mf);
  }

  function enTexto(entrada, tecla) {
    const accion = tecla.dataset.accion;
    const valor = entrada.value || '';
    // Si el campo no tenia el foco, se escribe al final
    const enfocado = document.activeElement === entrada;
    const inicio = enfocado ? entrada.selectionStart : valor.length;
    const fin = enfocado ? entrada.selectionEnd : valor.length;
    let nuevo = valor;
    let cursor = inicio;
    if (accion === 'izquierda') {
      cursor = Math.max(0, inicio - 1);
    } else if (accion === 'derecha') {
      cursor = Math.min(valor.length, fin + 1);
    } else if (accion === 'borrar') {
      const desde = inicio !== fin ? inicio : Math.max(0, inicio - 1);
      nuevo = valor.slice(0, desde) + valor.slice(fin);
      cursor = desde;
    } else if (accion === 'limpiar') {
      nuevo = '';
      cursor = 0;
    } else {
      let texto = tecla.dataset.texto;
      const seleccion = valor.slice(inicio, fin);
      const marca = texto.indexOf(CURSOR);
      if (marca >= 0) {
        // Con algo seleccionado queda adentro: x seleccionada + sen -> sen(x)
        texto = texto.replace(CURSOR, seleccion);
        cursor = seleccion ? inicio + texto.length : inicio + marca;
      } else {
        cursor = inicio + texto.length;
      }
      nuevo = valor.slice(0, inicio) + texto + valor.slice(fin);
    }
    entrada.focus();
    if (nuevo !== valor) {
      entrada.value = nuevo;
      avisar(entrada);
    }
    entrada.setSelectionRange(cursor, cursor);
    // Cuando la aplicacion confirma el valor, el campo vuelve a dibujarse y el cursor se va al final:
    // se coloca otra vez en su lugar (solo si el usuario no escribio nada mientras tanto)
    const fijar = function () {
      if (entrada.value === nuevo && document.activeElement === entrada) entrada.setSelectionRange(cursor, cursor);
    };
    [0, 60, 150, 300].forEach(function (espera) { setTimeout(fijar, espera); });
  }

  // Las teclas no le quitan el foco al campo (asi se conserva la posicion del cursor)
  document.addEventListener('mousedown', function (ev) {
    if (ev.target.closest && ev.target.closest('.tecla')) ev.preventDefault();
  });

  document.addEventListener('click', function (ev) {
    const tecla = ev.target.closest && ev.target.closest('.tecla');
    if (!tecla) return;
    const campo = campoDe(tecla);
    if (!campo) return;
    if (campo.tagName === 'MATH-FIELD') enEditor(campo, tecla);
    else enTexto(campo, tecla);
  });

  // Teclado virtual del editor matematico (el que aparece en pantallas tactiles):
  // primero las funciones con sus nombres en espanol, luego el numerico y el de letras.
  function tecla(etiqueta, latex) {
    return { label: etiqueta, insert: latex, class: 'small' };
  }
  function configurarTecladoVirtual() {
    const teclado = window.mathVirtualKeyboard;
    if (!teclado) return;
    teclado.layouts = [
      {
        label: 'f(x)',
        tooltip: 'Funciones',
        rows: [
          [tecla('sen', '\\operatorname{sen}\\left(#0\\right)'), tecla('cos', '\\cos\\left(#0\\right)'),
           tecla('tan', '\\tan\\left(#0\\right)'), tecla('sec', '\\sec\\left(#0\\right)'),
           tecla('csc', '\\csc\\left(#0\\right)'), tecla('cot', '\\cot\\left(#0\\right)'),
           '[separator]', tecla('ln', '\\ln\\left(#0\\right)'), tecla('log', '\\log\\left(#0\\right)')],
          [tecla('arcsen', '\\operatorname{arcsen}\\left(#0\\right)'), tecla('arccos', '\\arccos\\left(#0\\right)'),
           tecla('arctan', '\\arctan\\left(#0\\right)'), tecla('senh', '\\operatorname{senh}\\left(#0\\right)'),
           tecla('cosh', '\\cosh\\left(#0\\right)'), tecla('tanh', '\\tanh\\left(#0\\right)'),
           '[separator]', { latex: 'e^{#0}', class: 'small' }, { latex: '\\pi', class: 'small' }],
          [{ latex: '\\sqrt{#0}' }, { latex: '\\sqrt[3]{#0}' }, { latex: '\\left|#0\\right|' },
           { latex: '#@^{#?}' }, { latex: '#@^2' }, { latex: '\\frac{#@}{#?}' },
           '[separator]', '[(]', '[)]'],
          ['x', '=', '+', '-', '\\cdot', '[left]', '[right]', '[backspace]', '[hide-keyboard]'],
        ],
      },
      'numeric',
      'alphabetic',
    ];
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', configurarTecladoVirtual);
  else configurarTecladoVirtual();
})();
