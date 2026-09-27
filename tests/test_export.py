from pathlib import Path

from rdflib import Graph, Literal, Namespace

from retail_owl_shacl_poc.export import save_graph

EX = Namespace("https://example.org/retail#")


def test_save_graph_writes_a_parseable_turtle_file(tmp_path: Path):
    source = Graph()
    source.add((EX.shipment_watch, EX.riskBand, Literal("à surveiller", lang="fr")))
    destination = tmp_path / "result.ttl"

    returned_path = save_graph(source, destination)
    loaded = Graph().parse(str(destination), format="turtle")

    assert returned_path == destination
    assert (EX.shipment_watch, EX.riskBand, Literal("à surveiller", lang="fr")) in loaded
