"""Démo SWRL optionnelle; la démo SHACL principale reste indépendante."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from rdflib import Graph, Namespace, RDF

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EX = Namespace("https://example.org/retail#")
RULES_PATH = PROJECT_ROOT / "swrl" / "rules.txt"
MAVEN_PROJECT = PROJECT_ROOT / "swrl-engine" / "pom.xml"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "retail-swrl-result.ttl"
SHIPMENTS = (
    (EX.shipment_on_time, "à l'heure"),
    (EX.shipment_watch, "à surveiller"),
    (EX.shipment_urgent, "urgent"),
)
RISK_CLASSES = (
    (EX.WatchShipment, "WatchShipment (à surveiller)"),
    (EX.UrgentShipment, "UrgentShipment (urgent)"),
)


class SWRLDemoError(RuntimeError):
    """Erreur compréhensible rencontrée par la démo SWRL optionnelle."""


def _source_graph() -> Graph:
    """Charge les faits communs sans lancer les règles SHACL."""
    graph = Graph()
    for filename in ("ontology.ttl", "data.ttl", "swrl-classes.ttl"):
        graph.parse(str(PROJECT_ROOT / "rdf" / filename), format="turtle")
    graph.bind("ex", EX, replace=True)
    return graph


def _rules() -> list[tuple[str, str]]:
    parsed = []
    for line in RULES_PATH.read_text(encoding="utf-8").splitlines():
        source = line.strip()
        if not source or source.startswith("#"):
            continue
        name, separator, expression = source.partition("|")
        if not separator or not name.strip() or not expression.strip():
            raise SWRLDemoError(f"Ligne de règle SWRL invalide : {line}")
        parsed.append((name.strip(), expression.strip()))
    return parsed


def run_swrl_demo(output_path: str | Path | None = None) -> Graph:
    """Exécute SWRLAPI/Drools et renvoie le graphe avec les classes inférées."""
    missing = [name for name in ("java", "javac", "mvn") if shutil.which(name) is None]
    if missing:
        raise SWRLDemoError(
            "La démo SWRL optionnelle nécessite un JDK 11+ (java et javac) et Maven; introuvable(s) : "
            + ", ".join(missing)
            + ". La démo Python/SHACL reste utilisable sans eux."
        )

    destination = Path(output_path) if output_path is not None else DEFAULT_OUTPUT
    if not destination.is_absolute():
        destination = PROJECT_ROOT / destination
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    graph = _source_graph()
    with tempfile.TemporaryDirectory(prefix="retail-swrl-") as temporary_directory:
        temporary = Path(temporary_directory)
        input_ontology = temporary / "input.owl"
        inferred_ontology = temporary / "inferred.owl"
        graph.serialize(destination=str(input_ontology), format="xml")

        command = [
            "mvn",
            "-B",
            "-q",
            "-f",
            str(MAVEN_PROJECT),
            f"-Dretail.swrl.input={input_ontology}",
            f"-Dretail.swrl.output={inferred_ontology}",
            f"-Dretail.swrl.rules={RULES_PATH}",
            "compile",
            "exec:exec",
        ]
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        detail = "\n".join(
            part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
        )
        if completed.returncode:
            raise SWRLDemoError(
                "Le moteur SWRL (SWRLAPI/Drools) a échoué. "
                "Vérifie l'accès Maven Central et les dépendances Java.\n"
                + detail
            )
        if not inferred_ontology.is_file():
            raise SWRLDemoError("Le moteur SWRL n'a pas produit son ontologie résultat.")

        result = Graph()
        result.parse(str(inferred_ontology), format="xml")

    result.bind("ex", EX, replace=True)
    result.serialize(destination=str(destination), format="turtle")
    return result


def main(output_path: str | Path | None = None) -> Graph:
    graph = run_swrl_demo(output_path)
    destination = Path(output_path) if output_path is not None else DEFAULT_OUTPUT
    if not destination.is_absolute():
        destination = PROJECT_ROOT / destination
    destination = destination.resolve()

    print("Démonstration SWRL : des règles classent les expéditions à partir de l'ontologie OWL.")
    print("Dans le corps, ^ signifie ET; -> sépare le SI du ALORS; ?s et ?days sont des variables.")
    print("Tous les atomes avant -> doivent être vrais pour que la conclusion soit inférée.")
    print("Le moteur ajoute une appartenance à une classe dans l'ontologie.")
    print("swrlb:greaterThan et les autres built-ins sont des comparaisons numériques.")
    for name, expression in _rules():
        print(f"Règle {name} : {expression}")

    for shipment, description in SHIPMENTS:
        delay = graph.value(shipment, EX.delayDays)
        inferred = [label for class_iri, label in RISK_CLASSES if (shipment, RDF.type, class_iri) in graph]
        conclusion = ", ".join(inferred) if inferred else "aucune classe de risque inférée"
        print(f"{shipment.split('#')[-1]}: retard={delay} jour(s) -> {conclusion}")

    print("Les résultats SWRL sont des appartenances à des classes, pas des valeurs riskBand calculées par SHACL.")
    print(f"graphe résultat enregistré: {destination}")
    return graph


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Exécute la démonstration SWRL optionnelle.")
    parser.add_argument(
        "--output",
        default=None,
        help="fichier Turtle résultat (défaut : artifacts/retail-swrl-result.ttl)",
    )
    arguments = parser.parse_args()
    main(arguments.output)


if __name__ == "__main__":
    _cli()
