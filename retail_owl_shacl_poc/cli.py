from pathlib import Path

from rdflib import Namespace

from .engine import build_demo_graph
from .export import save_graph

EX = Namespace("https://example.org/retail#")
SHIPMENTS = (
    ("shipment_on_time", EX.shipment_on_time),
    ("shipment_watch", EX.shipment_watch),
    ("shipment_urgent", EX.shipment_urgent),
)


def main(output_path: str | Path = Path("artifacts/retail-logistics-result.ttl")) -> None:
    graph = build_demo_graph()
    destination = save_graph(graph, output_path)

    print("Démonstration : les règles calculent une valeur à partir des retards.")
    print("Un triplet se lit : sujet (expédition) — prédicat (relation) — objet (valeur).")
    print("riskBand désigne la propriété « bande de risque » calculée.")
    print("Règle 1 : retard > 0 et < 3 jours -> « à surveiller ».")
    print("Règle 2 : retard >= 3 jours -> « urgent ».")

    for label, shipment in SHIPMENTS:
        delay = next(graph.objects(shipment, EX.delayDays))
        risk_values = sorted(graph.objects(shipment, EX.riskBand), key=str)
        risk_bands = [str(value) for value in risk_values]
        if not risk_bands:
            print(f"{label}: retard={delay} jour(s) -> aucune valeur de risque calculée")
            continue

        print(f"{label}: retard={delay} jour(s) -> {', '.join(risk_bands)}")
        for risk_value in risk_values:
            print(
                "  triplet ajouté: "
                f"sujet={label} ; prédicat=riskBand ; objet={risk_value.n3()}"
            )

    print(f"graphe résultat enregistré: {destination}")
