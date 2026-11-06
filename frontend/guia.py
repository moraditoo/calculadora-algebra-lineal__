# frontend/guia.py
# Guia paso a paso con driver.js: oscurece la pantalla, resalta un elemento
# y muestra una explicacion; con "Siguiente" pasa al siguiente elemento.
import json

from nicegui import ui


def selector(elemento):
    """Selector CSS de un elemento de NiceGUI segun su id en la pagina."""
    return f"#{elemento.html_id}"


def iniciar(pasos):
    """pasos: lista de (elemento o selector, titulo, descripcion)."""
    lista = []
    for objetivo, titulo, descripcion in pasos:
        # Se omiten los elementos que ya no estan en pantalla (se redibujaron)
        if objetivo is None or (not isinstance(objetivo, str) and objetivo.is_deleted):
            continue
        lista.append({
            "element": objetivo if isinstance(objetivo, str) else selector(objetivo),
            "popover": {"title": titulo, "description": descripcion},
        })
    if not lista:
        return
    configuracion = {
        "steps": lista,
        "showProgress": len(lista) > 1,
        "progressText": "{{current}} de {{total}}",
        "nextBtnText": "Siguiente →",
        "prevBtnText": "← Anterior",
        "doneBtnText": "Entendido",
        "popoverClass": "guia-popover",
        "overlayColor": "#0f172a",
        "overlayOpacity": 0.35,
        "stagePadding": 8,
        "stageRadius": 16,
        "smoothScroll": True,
    }
    ui.run_javascript(
        "if (window.driver && window.driver.js) {"
        f"  window.driver.js.driver({json.dumps(configuracion, ensure_ascii=False)}).drive();"
        "}"
    )


def resaltar(objetivo, titulo, descripcion):
    """Resalta un solo elemento importante (por ejemplo, la raiz recien calculada)."""
    iniciar([(objetivo, titulo, descripcion)])
