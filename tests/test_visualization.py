from pathlib import Path

from rdflib import Graph

from retail_owl_shacl_poc.engine import build_demo_graph
from retail_owl_shacl_poc.visualization import (
    generate_mermaid_ontology,
    generate_interactive_html,
    export_visualizations,
)

ROOT = Path(__file__).resolve().parents[1]


def test_generate_mermaid_ontology_contains_classes_and_properties():
    ontology_graph = Graph()
    ontology_graph.parse(str(ROOT / "rdf" / "ontology.ttl"), format="turtle")

    mermaid_code = generate_mermaid_ontology(ontology_graph)

    assert "classDiagram" in mermaid_code or "class" in mermaid_code
    assert "Shipment" in mermaid_code
    assert "Store" in mermaid_code
    assert "deliveredTo" in mermaid_code
    assert "delayDays" in mermaid_code
    assert "riskBand" in mermaid_code


def test_generate_mermaid_ontology_supports_swrl_subclasses():
    full_ontology = Graph()
    full_ontology.parse(str(ROOT / "rdf" / "ontology.ttl"), format="turtle")
    full_ontology.parse(str(ROOT / "rdf" / "swrl-classes.ttl"), format="turtle")

    mermaid_code = generate_mermaid_ontology(full_ontology)

    assert "WatchShipment" in mermaid_code
    assert "UrgentShipment" in mermaid_code
    # Inheritance relationship in Mermaid
    assert "Shipment <|-- WatchShipment" in mermaid_code or "WatchShipment --|> Shipment" in mermaid_code or "subClassOf" in mermaid_code


def test_generate_interactive_html_creates_valid_html_file(tmp_path: Path):
    graph = build_demo_graph()
    output_html = tmp_path / "ontology-graph.html"

    result_path = generate_interactive_html(graph, output_html)

    assert result_path == output_html
    assert output_html.exists()
    content = output_html.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "vis-network" in content or "vis.Network" in content
    assert "Shipment" in content
    assert "store_main" in content
    assert "shipment_watch" in content
    assert "à surveiller" in content


def test_export_visualizations_creates_all_artifacts(tmp_path: Path):
    graph = build_demo_graph()
    artifacts = export_visualizations(graph, output_dir=tmp_path)

    assert "mermaid" in artifacts
    assert "html" in artifacts
    assert artifacts["mermaid"].exists()
    assert artifacts["html"].exists()
