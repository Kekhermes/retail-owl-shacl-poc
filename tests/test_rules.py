from rdflib import Literal, Namespace

from retail_owl_shacl_poc.engine import build_demo_graph

EX = Namespace("https://example.org/retail#")


def test_rules_add_expected_risk_bands_only_for_delayed_shipments():
    graph = build_demo_graph()
    actual = {
        subject: set(graph.objects(subject, EX.riskBand))
        for subject in (EX.shipment_on_time, EX.shipment_watch, EX.shipment_urgent)
    }

    assert actual == {
        EX.shipment_on_time: set(),
        EX.shipment_watch: {Literal("à surveiller", lang="fr")},
        EX.shipment_urgent: {Literal("urgent", lang="fr")},
    }
