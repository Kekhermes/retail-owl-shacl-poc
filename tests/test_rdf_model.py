from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL

ROOT = Path(__file__).resolve().parents[1]
EX = Namespace("https://example.org/retail#")


def load_model_graph() -> Graph:
    graph = Graph()
    graph.parse(str(ROOT / "rdf" / "ontology.ttl"), format="turtle")
    graph.parse(str(ROOT / "rdf" / "data.ttl"), format="turtle")
    return graph


def test_ontology_has_two_classes_one_object_property_and_two_data_properties():
    graph = load_model_graph()
    classes = set(graph.subjects(RDF.type, OWL.Class))
    object_properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
    datatype_properties = set(graph.subjects(RDF.type, OWL.DatatypeProperty))

    assert classes == {EX.Shipment, EX.Store}
    assert object_properties == {EX.deliveredTo}
    assert datatype_properties == {EX.delayDays, EX.riskBand}


def test_shipments_have_destination_and_integer_delay():
    graph = load_model_graph()

    assert (EX.shipment_watch, EX.deliveredTo, EX.store_main) in graph
    assert (EX.shipment_watch, EX.delayDays, None) in graph
    assert (EX.shipment_watch, RDFS.label, None) in graph


def test_ontology_labels_are_in_french():
    graph = load_model_graph()

    assert (EX.Shipment, RDFS.label, Literal("Expédition", lang="fr")) in graph
    assert (EX.riskBand, RDFS.label, Literal("bande de risque", lang="fr")) in graph
