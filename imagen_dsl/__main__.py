"""Interfaz de línea de comandos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

from .derivation import (
    DerivationError,
    DerivationStep,
    Grammar,
    Strategy,
    build_derivation,
    render_tree,
    render_svg,
    yield_string,
)
from .examples import GRAMMAR, W1_STEPS, W2_STEPS


def _load_request(path: Path) -> tuple[Grammar, list[DerivationStep], Strategy]:
    try:
        request = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as error:
        raise DerivationError(f"No se pudo leer {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise DerivationError(
            f"JSON inválido en línea {error.lineno}, columna {error.colno}: "
            f"{error.msg}"
        ) from error

    if not isinstance(request, dict):
        raise DerivationError("El documento JSON debe ser un objeto.")
    start_symbol = request.get("start_symbol")
    strategy = request.get("strategy")
    productions = request.get("productions")
    raw_steps = request.get("steps")
    if not isinstance(start_symbol, str):
        raise DerivationError("'start_symbol' debe ser texto.")
    if strategy not in ("leftmost", "rightmost"):
        raise DerivationError("'strategy' debe ser 'leftmost' o 'rightmost'.")
    if not isinstance(productions, dict):
        raise DerivationError("'productions' debe ser un objeto JSON.")
    if not isinstance(raw_steps, list):
        raise DerivationError("'steps' debe ser una lista.")

    parsed_productions: dict[str, list[list[str]]] = {}
    for symbol, alternatives in productions.items():
        if not isinstance(symbol, str) or not isinstance(alternatives, list):
            raise DerivationError("Cada producción debe mapear texto a una lista.")
        parsed_alternatives: list[list[str]] = []
        for alternative in alternatives:
            if not isinstance(alternative, list):
                raise DerivationError(
                    f"Las alternativas de {symbol!r} deben ser listas de símbolos."
                )
            parsed_alternatives.append(alternative)
        parsed_productions[symbol] = parsed_alternatives

    steps: list[DerivationStep] = []
    for index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            raise DerivationError(f"El paso {index} debe ser un objeto.")
        symbol = raw_step.get("symbol")
        alternative = raw_step.get("alternative")
        if not isinstance(symbol, str):
            raise DerivationError(f"El paso {index}: 'symbol' debe ser texto.")
        if not isinstance(alternative, int) or isinstance(alternative, bool):
            raise DerivationError(
                f"El paso {index}: 'alternative' debe ser un entero."
            )
        steps.append(DerivationStep(symbol, alternative))

    return (
        Grammar(start_symbol, parsed_productions),
        steps,
        cast(Strategy, strategy),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Construye un árbol desde una derivación explícita en JSON."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--example", choices=("w1", "w2"))
    group.add_argument("json_file", nargs="?", type=Path)
    parser.add_argument(
        "--svg",
        action="store_true",
        help="Genera una imagen SVG del árbol de derivación.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Ruta del SVG (si se omite, se usa un nombre automático).",
    )
    args = parser.parse_args()

    try:
        if args.example == "w1":
            grammar, steps, strategy = GRAMMAR, W1_STEPS, "leftmost"
        elif args.example == "w2":
            grammar, steps, strategy = GRAMMAR, W2_STEPS, "rightmost"
        else:
            grammar, steps, strategy = _load_request(args.json_file)
        tree = build_derivation(grammar, steps, strategy)
        if args.svg or args.output:
            if args.output:
                output_path = args.output
            elif args.example:
                output_path = Path(f"arbol_{args.example}.svg")
            else:
                output_path = args.json_file.with_suffix(".svg")
            output_path.write_text(render_svg(tree), encoding="utf-8")
    except DerivationError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Error al guardar el archivo SVG: {error}", file=sys.stderr)
        return 2

    if args.svg or args.output:
        print(f"Árbol gráfico guardado en: {output_path.resolve()}")
    else:
        print(render_tree(tree))
    print(f"\nCadena terminal: {yield_string(tree)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
