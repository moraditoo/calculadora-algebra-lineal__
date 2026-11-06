# frontend/modulos/regla_falsa/estado.py
# Estado de la regla falsa: el mismo de biseccion mas la variante elegida (clasica o modificada).
from dataclasses import dataclass

from ..biseccion.estado import Estado


@dataclass
class EstadoReglaFalsa(Estado):
    modificada: bool = False  # falsa posicion modificada: divide f a la mitad en el extremo estancado

    @classmethod
    def desde_ejemplo(cls, ejemplo):
        estado = super().desde_ejemplo(ejemplo)
        estado.modificada = ejemplo.get("modificada", False)
        return estado

    def cargar_ejemplo(self, ejemplo):
        super().cargar_ejemplo(ejemplo)
        self.modificada = ejemplo.get("modificada", False)
