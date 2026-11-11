"""Gramática y derivaciones demostrativas del informe."""

from .derivation import DerivationStep, Grammar

GRAMMAR = Grammar(
    start_symbol="PROGRAMA",
    productions={
        "PROGRAMA": [['"imagen"', "IDENT", '"{"', "OPERACIONES", '"}"']],
        "OPERACIONES": [
            ["OPERACION"],
            ["OPERACION", '";"', "OPERACIONES"],
        ],
        "OPERACION": [["RECORTE"], ["ESCALA"], ["ROTACION"], ["FILTRO"]],
        "RECORTE": [
            ['"recortar"', '"("', "NUM", '","', "NUM", '","', "NUM", '","', "NUM", '")"']
        ],
        "ESCALA": [['"escalar"', '"("', "NUM", '","', "NUM", '")"']],
        "ROTACION": [['"rotar"', '"("', "NUM", '")"']],
        "FILTRO": [['"filtro"', '"("', "NOMBRE_FILTRO", '")"']],
        "NOMBRE_FILTRO": [
            ['"desenfoque"'],
            ['"nitidez"'],
            ['"escala_grises"'],
            ['"sepia"'],
        ],
        "IDENT": [["foto"], ["paisaje"]],
        "NUM": [["10"], ["20"], ["300"], ["200"], ["800"], ["600"], ["90"]],
    },
)

W1_STEPS = [
    DerivationStep("PROGRAMA", 0),
    DerivationStep("IDENT", 0),
    DerivationStep("OPERACIONES", 1),
    DerivationStep("OPERACION", 0),
    DerivationStep("RECORTE", 0),
    DerivationStep("NUM", 0),
    DerivationStep("NUM", 1),
    DerivationStep("NUM", 2),
    DerivationStep("NUM", 3),
    DerivationStep("OPERACIONES", 0),
    DerivationStep("OPERACION", 3),
    DerivationStep("FILTRO", 0),
    DerivationStep("NOMBRE_FILTRO", 3),
]

W2_STEPS = [
    DerivationStep("PROGRAMA", 0),
    DerivationStep("OPERACIONES", 1),
    DerivationStep("OPERACIONES", 1),
    DerivationStep("OPERACIONES", 0),
    DerivationStep("OPERACION", 3),
    DerivationStep("FILTRO", 0),
    DerivationStep("NOMBRE_FILTRO", 2),
    DerivationStep("OPERACION", 2),
    DerivationStep("ROTACION", 0),
    DerivationStep("NUM", 6),
    DerivationStep("OPERACION", 1),
    DerivationStep("ESCALA", 0),
    DerivationStep("NUM", 5),
    DerivationStep("NUM", 4),
    DerivationStep("IDENT", 1),
]
