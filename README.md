# POC pédagogique : OWL et règles SHACL en logistique retail

Ce petit projet local explique pas à pas comment représenter quelques faits de logistique retail et appliquer deux règles simples. Il est conçu pour débuter : **aucune connaissance préalable en ontologie, RDF ou règles métier n'est requise**.

## Ce que vous allez apprendre

- reconnaître un fait RDF sous forme de triplet sujet–prédicat–objet ;
- distinguer une classe (`Shipment`) d'un individu (`shipment_watch`) ;
- comprendre une propriété qui relie deux ressources (`deliveredTo`) et une propriété qui porte une valeur (`delayDays`) ;
- suivre la condition d'une règle jusqu'au fait ajouté au graphe ;
- situer OWL, SHACL-SPARQL, SWRL et RuleML sans les confondre.

## Avant de lancer

- Python 3.11 ;
- pas de service distant, de base de données, de conteneur ni de JVM ;
- le POC ne fait pas de requête réseau à l'exécution.

## Installer et lancer

Depuis ce répertoire :

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m retail_owl_shacl_poc
```

Le CLI explique les deux seuils et imprime le graphe résultat dans `artifacts/retail-logistics-result.ttl`.

Exemple de résultat attendu :

```text
Démonstration : les règles calculent une valeur à partir des retards.
Un triplet se lit : sujet (expédition) — prédicat (relation) — objet (valeur).
riskBand désigne la propriété « bande de risque » calculée.
Règle 1 : retard > 0 et < 3 jours -> « à surveiller ».
Règle 2 : retard >= 3 jours -> « urgent ».
shipment_on_time: retard=0 jour(s) -> aucune valeur de risque calculée
shipment_watch: retard=2 jour(s) -> à surveiller
  triplet ajouté: sujet=shipment_watch ; prédicat=riskBand ; objet="à surveiller"@fr
shipment_urgent: retard=3 jour(s) -> urgent
  triplet ajouté: sujet=shipment_urgent ; prédicat=riskBand ; objet="urgent"@fr
graphe résultat enregistré: artifacts/retail-logistics-result.ttl
```

## Lire d'abord

1. [Glossaire de départ](docs/glossaire.md) — les mots techniques traduits en français avec un exemple du POC.
2. [Lire la démo pas à pas](docs/guide-pedagogique.md) — le diagramme et le suivi manuel d'une expédition depuis les données jusqu'au triplet calculé.

## Périmètre des règles

| Retard de démonstration | Résultat |
|---:|---|
| 0 jour | aucun fait de risque calculé |
| 1 ou 2 jours | « à surveiller » |
| 3 jours ou plus | « urgent » |

Ces seuils sont des exemples pédagogiques à valider avec les métiers avant tout usage réel. L'absence de bande calculée à 0 jour ne constitue pas une preuve générale d'absence de risque.

## Important : ce POC n'exécute pas SWRL

Le moteur du POC exécute des règles **SHACL-SPARQL** avec pySHACL. SWRL et RuleML sont expliqués et comparés dans le guide, mais aucune règle SWRL ou RuleML n'est exécutée par ce projet. OWL décrit ici le vocabulaire et les propriétés ; le code ne lance pas de raisonneur OWL général.

## Licences

L'inventaire de [`LICENSES.md`](LICENSES.md) couvre les 14 paquets résolus (10 runtime, 4 de développement/test), pas uniquement les paquets directs.

Les versions épinglées de pySHACL et RDFLib déclarent respectivement Apache-2.0 et BSD-3-Clause.[19][20]

OWL-RL déclare la notice logicielle W3C ; ses conditions et les notices à conserver sont liées dans l'inventaire.[21][13]

L'audit local de ces 14 paquets n'a relevé aucune déclaration GPL/AGPL.

Les licences permettent un usage sans redevance, sous réserve de respecter leurs conditions et notices.[11][13][17]

Refaire l'audit de la fermeture des dépendances réellement déployées avant toute mise en production, car les versions transitives peuvent évoluer.

## Sources

[11] https://www.apache.org/licenses/LICENSE-2.0.html
[13] https://github.com/RDFLib/OWL-RL/blob/master/LICENSE.txt
[17] https://github.com/RDFLib/rdflib/blob/main/LICENSE
[19] https://pypi.org/project/pyshacl/0.40.1
[20] https://pypi.org/project/rdflib/7.6.0
[21] https://pypi.org/project/owlrl/7.6.2
