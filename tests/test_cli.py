from pathlib import Path

from retail_owl_shacl_poc.cli import main


def test_cli_explains_results_and_exports_graph(tmp_path: Path, capsys):
    output = tmp_path / "result.ttl"

    main(output)

    printed = capsys.readouterr().out
    assert "Démonstration : les règles calculent une valeur à partir des retards." in printed
    assert "Un triplet se lit : sujet (expédition) — prédicat (relation) — objet (valeur)." in printed
    assert "riskBand désigne la propriété « bande de risque » calculée." in printed
    assert "Règle 1 : retard > 0 et < 3 jours -> « à surveiller »." in printed
    assert "Règle 2 : retard >= 3 jours -> « urgent »." in printed
    assert "shipment_on_time: retard=0 jour(s) -> aucune valeur de risque calculée" in printed
    assert 'triplet ajouté: sujet=shipment_watch ; prédicat=riskBand ; objet="à surveiller"@fr' in printed
    assert 'triplet ajouté: sujet=shipment_urgent ; prédicat=riskBand ; objet="urgent"@fr' in printed
    assert f"graphe résultat enregistré: {output}" in printed
    assert output.exists()
