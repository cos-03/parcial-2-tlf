"""Construcción y renderizado de árboles a partir de pasos de derivación."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Literal

Strategy = Literal["leftmost", "rightmost"]


class DerivationError(ValueError):
    """Error en la gramática o en los pasos de una derivación."""


@dataclass(frozen=True)
class DerivationStep:
    symbol: str
    alternative: int


@dataclass
class Node:
    symbol: str
    children: list[Node] | None = None
    alternative: int | None = None


@dataclass(frozen=True)
class Grammar:
    start_symbol: str
    productions: dict[str, list[list[str]]]

    def validate(self) -> None:
        if not self.start_symbol:
            raise DerivationError("El símbolo inicial no puede estar vacío.")
        if self.start_symbol not in self.productions:
            raise DerivationError(
                f"El símbolo inicial {self.start_symbol!r} no tiene producciones."
            )
        if not self.productions:
            raise DerivationError("La gramática debe incluir producciones.")
        for symbol, alternatives in self.productions.items():
            if not symbol:
                raise DerivationError("Una producción tiene un símbolo vacío.")
            if not alternatives:
                raise DerivationError(
                    f"El no terminal {symbol!r} debe tener al menos una alternativa."
                )
            for index, rhs in enumerate(alternatives):
                if not isinstance(rhs, list) or any(
                    not isinstance(item, str) or not item for item in rhs
                ):
                    raise DerivationError(
                        f"La alternativa {index} de {symbol!r} debe ser "
                        "una lista de símbolos no vacíos."
                    )


def _next_expandable(
    node: Node, nonterminals: set[str], strategy: Strategy
) -> Node | None:
    if node.children is None:
        return node if node.symbol in nonterminals else None
    children = node.children if strategy == "leftmost" else reversed(node.children)
    for child in children:
        candidate = _next_expandable(child, nonterminals, strategy)
        if candidate is not None:
            return candidate
    return None


def _remaining_nonterminal(node: Node, nonterminals: set[str]) -> str | None:
    if node.children is None:
        return node.symbol if node.symbol in nonterminals else None
    for child in node.children:
        remaining = _remaining_nonterminal(child, nonterminals)
        if remaining is not None:
            return remaining
    return None


def build_derivation(
    grammar: Grammar, steps: list[DerivationStep], strategy: Strategy
) -> Node:
    """Aplica los pasos indicados y devuelve el árbol terminal completo."""
    grammar.validate()
    if strategy not in ("leftmost", "rightmost"):
        raise DerivationError("La estrategia debe ser 'leftmost' o 'rightmost'.")

    root = Node(grammar.start_symbol)
    nonterminals = set(grammar.productions)

    for step_number, step in enumerate(steps, start=1):
        target = _next_expandable(root, nonterminals, strategy)
        if target is None:
            raise DerivationError(
                f"El paso {step_number} no se puede aplicar: "
                "la derivación ya no tiene no terminales."
            )
        if step.symbol != target.symbol:
            raise DerivationError(
                f"Paso {step_number}: se esperaba expandir {target.symbol!r} "
                f"según {strategy}, pero se indicó {step.symbol!r}."
            )
        alternatives = grammar.productions[target.symbol]
        if not 0 <= step.alternative < len(alternatives):
            raise DerivationError(
                f"Paso {step_number}: alternativa {step.alternative} fuera "
                f"de rango para {target.symbol!r}."
            )
        target.alternative = step.alternative
        target.children = [
            Node(symbol) for symbol in alternatives[step.alternative]
        ]

    remaining = _remaining_nonterminal(root, nonterminals)
    if remaining is not None:
        raise DerivationError(
            f"Derivación incompleta: todavía falta expandir {remaining!r}."
        )
    return root


def render_tree(root: Node) -> str:
    """Representa el árbol con conectores de texto."""
    lines = [root.symbol]

    def visit(node: Node, prefix: str) -> None:
        if node.children is None:
            return
        for index, child in enumerate(node.children):
            is_last = index == len(node.children) - 1
            connector = "`-- " if is_last else "|-- "
            lines.append(prefix + connector + child.symbol)
            visit(child, prefix + ("    " if is_last else "|   "))

    visit(root, "")
    return "\n".join(lines)


def render_svg(root: Node) -> str:
    """Renderiza el árbol como SVG independiente y escalable."""
    box_height = 38
    horizontal_gap = 24
    vertical_gap = 92
    padding = 28
    positions: dict[int, tuple[float, float, float]] = {}

    def label(node: Node) -> str:
        symbol = node.symbol
        if len(symbol) >= 2 and symbol[0] == symbol[-1] == '"':
            return symbol[1:-1]
        return symbol

    def measure(node: Node) -> tuple[float, int]:
        node_width = max(76, len(label(node)) * 9 + 28)
        if not node.children:
            return float(node_width), 0
        child_sizes = [measure(child) for child in node.children]
        children_width = sum(width for width, _ in child_sizes)
        children_width += horizontal_gap * (len(child_sizes) - 1)
        return max(float(node_width), children_width), 1 + max(
            depth for _, depth in child_sizes
        )

    tree_width, depth = measure(root)
    svg_width = tree_width + 2 * padding
    svg_height = (depth + 1) * vertical_gap + 2 * padding

    def position(node: Node, left: float, level: int) -> None:
        subtree_width, _ = measure(node)
        box_width = max(76, len(label(node)) * 9 + 28)
        center = left + subtree_width / 2
        top = padding + level * vertical_gap
        positions[id(node)] = (center, top, float(box_width))

        if not node.children:
            return
        children_widths = [measure(child)[0] for child in node.children]
        children_total = sum(children_widths) + horizontal_gap * (
            len(children_widths) - 1
        )
        child_left = center - children_total / 2
        for child, child_width in zip(node.children, children_widths):
            position(child, child_left, level + 1)
            child_left += child_width + horizontal_gap

    position(root, padding, 0)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width:.0f}" height="{svg_height:.0f}" '
        f'viewBox="0 0 {svg_width:.0f} {svg_height:.0f}" '
        f'role="img" aria-labelledby="title description">',
        "<title id=\"title\">Árbol de derivación</title>",
        "<desc id=\"description\">Árbol sintáctico generado desde una derivación.</desc>",
        "<style>",
        "text{font-family:Segoe UI,Arial,sans-serif}",
        ".edge{stroke:#94a3b8;stroke-width:2}",
        ".nonterminal{fill:#e0e7ff;stroke:#4f46e5;stroke-width:2}",
        ".terminal{fill:#ecfdf5;stroke:#059669;stroke-width:2}",
        ".nonterminal-text{fill:#312e81;font-size:14px;font-weight:600}",
        ".terminal-text{fill:#065f46;font-size:14px}",
        "</style>",
        '<rect width="100%" height="100%" rx="14" fill="#f8fafc"/>',
    ]

    def draw_edges(node: Node) -> None:
        if not node.children:
            return
        parent_x, parent_y, _ = positions[id(node)]
        for child in node.children:
            child_x, child_y, _ = positions[id(child)]
            lines.append(
                f'<line class="edge" x1="{parent_x:.1f}" '
                f'y1="{parent_y + box_height:.1f}" x2="{child_x:.1f}" '
                f'y2="{child_y:.1f}"/>'
            )
            draw_edges(child)

    draw_edges(root)
    nodes = [root]
    while nodes:
        node = nodes.pop()
        nodes.extend(reversed(node.children or []))
        center, top, box_width = positions[id(node)]
        is_nonterminal = node.children is not None
        node_class = "nonterminal" if is_nonterminal else "terminal"
        text_class = "nonterminal-text" if is_nonterminal else "terminal-text"
        lines.extend(
            [
                f'<rect class="{node_class}" x="{center - box_width / 2:.1f}" '
                f'y="{top:.1f}" width="{box_width:.1f}" height="{box_height}" '
                'rx="9"/>',
                f'<text class="{text_class}" x="{center:.1f}" '
                f'y="{top + 24:.1f}" text-anchor="middle">'
                f"{escape(label(node))}</text>",
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines)


def yield_string(root: Node) -> str:
    """Concatena las hojas del árbol, separadas por espacios."""
    if root.children is None:
        if len(root.symbol) >= 2 and root.symbol[0] == root.symbol[-1] == '"':
            return root.symbol[1:-1]
        return root.symbol
    return " ".join(
        token
        for child in root.children
        for token in [yield_string(child)]
        if token
    )
