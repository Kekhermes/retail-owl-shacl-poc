# POC pédagogique : OWL, SHACL-SPARQL et SWRL en logistique retail

Ce projet local explique pas à pas comment représenter des faits de logistique retail et appliquer des règles. Il conserve la démonstration initiale OWL/RDF + SHACL-SPARQL et ajoute une démonstration SWRL distincte, facultative. Il est conçu pour débuter : **aucune connaissance préalable en ontologie, RDF ou règles métier n'est requise**.

## Ce que vous allez apprendre

- reconnaître un fait RDF sous forme de triplet sujet–prédicat–objet ;
- distinguer une classe (`Shipment`) d'un individu (`shipment_watch`) ;
- comprendre une propriété qui relie deux ressources (`deliveredTo`) et une propriété qui porte une valeur (`delayDays`) ;
- suivre une règle jusqu'au résultat qu'elle ajoute ou infère ;
- comparer les résultats SHACL (`riskBand`) et SWRL (appartenance à une classe) sans confondre les deux moteurs.

## Avant de lancer

- Python 3.11 pour la démonstration SHACL existante ;
- un JDK 11+ (`java` et `javac`) et Apache Maven uniquement pour la démonstration SWRL facultative ;
- aucun service distant, aucune base de données ni conteneur ;
- la commande SHACL par défaut ne requiert ni JVM ni accès réseau. La première exécution SWRL peut télécharger ses dépendances Java épinglées depuis Maven Central.

## Installer et lancer

Depuis ce répertoire :

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m retail_owl_shacl_poc
```

La suite complète lance aussi le test d'intégration SWRL si un JDK 11+ et Maven sont présents ; sans eux, ce test est ignoré. Lorsqu'il s'exécute, Maven peut télécharger les dépendances Java au premier lancement.

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

## Démonstration facultative SWRL

Depuis la racine du projet, avec l'environnement Python activé et un JDK 11+ ainsi que Maven installés :

```bash
python -m retail_owl_shacl_poc.swrl_demo
```

Cette commande exécute les deux règles SWRL avec le moteur optionnel SWRLAPI + Drools, puis écrit `artifacts/retail-swrl-result.ttl`. Elle utilise les mêmes faits de départ que la démo SHACL, mais **n'exécute pas `shapes.ttl`** : les conclusions sont des types `WatchShipment` et `UrgentShipment`, pas les valeurs texte `riskBand` calculées par SHACL.[42][60]

SWRL est une proposition de langage publiée comme Member Submission du W3C, et non comme Recommendation.[10]

## Lire d'abord

1. [Glossaire de départ](docs/glossaire.md) — les mots techniques traduits en français avec un exemple du POC.
2. [Lire la démo SHACL pas à pas](docs/guide-pedagogique.md) — le diagramme et le suivi manuel d'une expédition depuis les données jusqu'au triplet calculé.
3. [Découvrir SWRL](docs/guide-swrl.md) — règles, moteur optionnel, calculs illustrés et comparaison avec SHACL.

## Périmètre des règles

| Retard de démonstration | Résultat |
|---:|---|
| 0 jour | aucun fait de risque calculé |
| 1 ou 2 jours | « à surveiller » |
| 3 jours ou plus | « urgent » |

Ces seuils sont des exemples pédagogiques à valider avec les métiers avant tout usage réel. L'absence de bande calculée à 0 jour ne constitue pas une preuve générale d'absence de risque.

## Deux moteurs, deux résultats différents

La commande par défaut (`python -m retail_owl_shacl_poc`) conserve la démonstration initiale : elle exécute les règles SHACL-SPARQL avec pySHACL et ajoute des valeurs `riskBand` au graphe. La commande facultative `python -m retail_owl_shacl_poc.swrl_demo` exécute séparément des règles SWRL avec SWRLAPI + Drools. Le moteur Drools se décrit comme un moteur de règles SWRL et un raisonneur OWL 2 RL ; il ne faut pas le présenter comme un raisonneur complet OWL 2 DL.[60]

La démo SWRL ajoute une appartenance à `WatchShipment` ou `UrgentShipment`, pas une valeur `riskBand`. SWRL est une Member Submission du W3C, pas une Recommendation.[10]

## Licences

`LICENSES.md` distingue les 14 paquets Python résolus (10 runtime, 4 développement/test) et les 66 dépendances runtime Java/Maven de la démo SWRL facultative, inventoriées dans [`swrl-engine/THIRD-PARTY.txt`](swrl-engine/THIRD-PARTY.txt). SWRLAPI + Drools sont épinglés en version 2.1.2 et déclarent BSD-2-Clause.[46][47][60]

La fermeture OWLAPI 4.5.25 est duale Apache-2.0/LGPL-3.0 ; elle propose l'option Apache-2.0.[49][51]

Une dépendance transitive, MXParser, impose aussi une attribution, conservée dans [`swrl-engine/NOTICE.md`](swrl-engine/NOTICE.md).[54][56]

Le contrôle du rapport Maven final n'a trouvé aucune entrée GPL/AGPL ni licence inconnue dans la fermeture Java résolue. Certaines dépendances amont sous GPL ont été exclues car inutiles aux deux règles de comparaison exécutées ici ; toute extension des règles ou des bibliothèques nécessite un nouvel audit. Les notices restent obligatoires et ce relevé n'est pas un avis juridique.

L'inventaire couvre les dépendances, pas la licence du code de ce POC. Refaire l'audit des dépendances réellement déployées avant tout usage en production.

## Sources

[10] https://www.w3.org/submissions/SWRL
[42] https://github.com/protegeproject/swrlapi-drools-engine
[46] https://central.sonatype.com/artifact/edu.stanford.swrl/swrlapi-drools-engine/2.1.2
[47] https://central.sonatype.com/artifact/edu.stanford.swrl/swrlapi/2.1.2
[49] https://github.com/owlcs/owlapi
[51] https://central.sonatype.com/artifact/net.sourceforge.owlapi/owlapi-osgidistribution/4.5.25
[54] https://central.sonatype.com/artifact/io.github.x-stream/mxparser/1.2.2
[56] https://raw.githubusercontent.com/x-stream/mxparser/master/LICENSE.txt
[60] https://github.com/protegeproject/swrlapi-drools-engine/blob/master/README.md
