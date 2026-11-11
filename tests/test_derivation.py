import unittest
import xml.etree.ElementTree as ET

from imagen_dsl.derivation import (
    DerivationError,
    DerivationStep,
    Grammar,
    build_derivation,
    render_tree,
    render_svg,
    yield_string,
)
from imagen_dsl.examples import GRAMMAR, W1_STEPS, W2_STEPS


class DerivationTests(unittest.TestCase):
    def test_w1_builds_leftmost_derivation(self) -> None:
        tree = build_derivation(GRAMMAR, W1_STEPS, "leftmost")
        self.assertIn("RECORTE", render_tree(tree))
        self.assertEqual(
            yield_string(tree),
            "imagen foto { recortar ( 10 , 20 , 300 , 200 ) ; "
            "filtro ( sepia ) }",
        )

    def test_w2_builds_rightmost_derivation(self) -> None:
        tree = build_derivation(GRAMMAR, W2_STEPS, "rightmost")
        self.assertIn("ESCALA", render_tree(tree))
        self.assertEqual(
            yield_string(tree),
            "imagen paisaje { escalar ( 800 , 600 ) ; rotar ( 90 ) ; "
            "filtro ( escala_grises ) }",
        )

    def test_rejects_step_that_violates_strategy(self) -> None:
        grammar = Grammar("S", {"S": [["A", "B"]], "A": [["a"]], "B": [["b"]]})
        with self.assertRaisesRegex(DerivationError, "se esperaba expandir 'A'"):
            build_derivation(
                grammar,
                [DerivationStep("S", 0), DerivationStep("B", 0)],
                "leftmost",
            )

    def test_rejects_incomplete_derivation(self) -> None:
        grammar = Grammar("S", {"S": [["A"]], "A": [["a"]]})
        with self.assertRaisesRegex(DerivationError, "Derivación incompleta"):
            build_derivation(grammar, [DerivationStep("S", 0)], "leftmost")

    def test_rejects_invalid_alternative(self) -> None:
        grammar = Grammar("S", {"S": [["a"]]})
        with self.assertRaisesRegex(DerivationError, "fuera de rango"):
            build_derivation(grammar, [DerivationStep("S", 1)], "leftmost")

    def test_svg_is_valid_and_contains_tree_nodes(self) -> None:
        tree = build_derivation(GRAMMAR, W1_STEPS, "leftmost")
        svg = render_svg(tree)
        document = ET.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        labels = [
            element.text
            for element in document.findall(".//svg:text", namespace)
        ]
        self.assertIn("PROGRAMA", labels)
        self.assertIn("recortar", labels)
        self.assertIn("sepia", labels)
        self.assertEqual(len(document.findall(".//svg:line", namespace)), len(labels) - 1)


if __name__ == "__main__":
    unittest.main()
