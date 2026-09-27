from pathlib import Path

from pyshacl import shacl_rules
from rdflib import Graph

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_demo_graph() -> Graph:
    """Charge les faits RDF puis renvoie un graphe enrichi par les règles SHACL."""
    data_graph = Graph()
    data_graph.parse(str(PROJECT_ROOT / "rdf" / "ontology.ttl"), format="turtle")
    data_graph.parse(str(PROJECT_ROOT / "rdf" / "data.ttl"), format="turtle")

    shapes_graph = Graph()
    shapes_graph.parse(str(PROJECT_ROOT / "rdf" / "shapes.ttl"), format="turtle")

    return shacl_rules(data_graph, shacl_graph=shapes_graph, advanced=True)
