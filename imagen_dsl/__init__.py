"""Interfaz pública para construir y visualizar árboles de derivación.

Reexporta los tipos que describen la gramática y sus pasos, la función que
construye el árbol y el renderizador SVG para que otros módulos puedan
importarlos desde ``imagen_dsl``.
"""

from .derivation import (
    DerivationError,
    DerivationStep,
    build_derivation,
    render_svg,
)

__all__ = ["DerivationError", "DerivationStep", "build_derivation", "render_svg"]
