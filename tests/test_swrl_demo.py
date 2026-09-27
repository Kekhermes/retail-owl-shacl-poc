import shutil
from pathlib import Path

import pytest
from rdflib import Literal, Namespace, RDF, XSD

from retail_owl_shacl_poc.swrl_demo import run_swrl_demo

EX = Namespace("https://example.org/retail#")

pytestmark = pytest.mark.skipif(
    shutil.which("java") is None or shutil.which("javac") is None or shutil.which("mvn") is None,
    reason="La démo SWRL optionnelle requiert un JDK 11+ et Maven.",
)


def test_swrl_demo_infers_status_classes_without_applying_shacl_rules(tmp_path: Path):
    output = tmp_path / "retail-swrl-result.ttl"

    graph = run_swrl_demo(output)

    assert output.exists()
    assert (EX.shipment_watch, RDF.type, EX.WatchShipment) in graph
    assert (EX.shipment_urgent, RDF.type, EX.UrgentShipment) in graph
    assert (EX.shipment_on_time, RDF.type, EX.WatchShipment) not in graph
    assert (EX.shipment_on_time, RDF.type, EX.UrgentShipment) not in graph
    assert (EX.shipment_watch, EX.delayDays, Literal(2, datatype=XSD.integer)) in graph
    assert not list(graph.objects(EX.shipment_watch, EX.riskBand))
