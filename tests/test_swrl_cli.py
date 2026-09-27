import shutil
from pathlib import Path

import pytest

from retail_owl_shacl_poc.swrl_demo import main

pytestmark = pytest.mark.skipif(
    any(shutil.which(name) is None for name in ("java", "javac", "mvn")),
    reason="La démo SWRL optionnelle requiert un JDK 11+ et Maven.",
)


def test_swrl_cli_explains_rule_matching_and_inferred_class_membership(tmp_path: Path, capsys):
    output = tmp_path / "swrl-result.ttl"

    main(output)

    printed = capsys.readouterr().out
    assert "Tous les atomes avant -> doivent être vrais pour que la conclusion soit inférée." in printed
    assert "Le moteur ajoute une appartenance à une classe dans l'ontologie." in printed
    assert "Les résultats SWRL sont des appartenances à des classes, pas des valeurs riskBand calculées par SHACL." in printed
    assert output.exists()
