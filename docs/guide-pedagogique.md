# Lire la démo pas à pas

Ce parcours n'exige aucune connaissance préalable de l'ontologie, de RDF ou des moteurs de règles. Il suit une seule question : **qu'est-ce qu'une règle ajoute au graphe pour une expédition dont le retard est connu ?** Les mots techniques sont définis dans le [glossaire](glossaire.md).

## 1. Le petit problème métier

Nous avons trois expéditions destinées au même magasin : une à l'heure, une avec deux jours de retard et une avec trois jours. Pour apprendre à écrire des règles, nous illustrons le classement suivant :

| Expédition | Retard connu | Résultat SHACL de la commande par défaut |
|---|---:|---|
| `shipment_on_time` | 0 jour | aucune bande calculée |
| `shipment_watch` | 2 jours | « à surveiller » |
| `shipment_urgent` | 3 jours | « urgent » |

Ces seuils sont inventés pour apprendre ; ils ne constituent pas une politique retail prête à déployer.

## 2. Le chemin suivi par les données

```mermaid
flowchart LR
    O["ontology.ttl : vocabulaire OWL"] --> G["graphe RDF source : vocabulaire + faits"]
    A["data.ttl : trois expéditions"] --> G
    G --> P["pySHACL + shapes.ttl"]
    P --> R["résultat SHACL : triplets riskBand"]
    R --> C["commande SHACL + fichier Turtle"]
    G --> X["extension SWRL : swrl-classes.ttl"]
    X --> J["SWRLAPI + Drools (Java)"]
    S["swrl/rules.txt : règles SWRL"] --> J
    J --> I["résultat SWRL : types inférés"]
    I --> W["commande SWRL + fichier Turtle"]
```

- `ontology.ttl` nomme les types de choses et leurs propriétés : deux classes, une relation entre expédition et magasin, et deux propriétés de données.
- `data.ttl` contient les faits fournis au départ. La commande SHACL transmet à pySHACL le vocabulaire de `ontology.ttl` et ces faits ; la commande SWRL réutilise aussi ces entrées.
- `shapes.ttl` contient les deux règles SHACL-SPARQL de la démonstration initiale.
- `rdf/swrl-classes.ttl` ajoute les deux classes de résultat SWRL, uniquement à la démonstration facultative.
- RDFLib lit les graphes RDF ; pySHACL traite les règles SHACL-SPARQL activées par `advanced=True`. La commande SWRL passe un graphe indépendant au moteur Java SWRLAPI + Drools.
- Chaque commande produit son propre graphe Turtle : SHACL ajoute `riskBand`, tandis que SWRL ajoute des appartenances à `WatchShipment` ou `UrgentShipment`.

## 3. Lire un premier triplet

Dans `rdf/data.ttl`, la ligne `ex:delayDays 2` exprime un fait sur l'expédition courante. En forme développée :

```text
sujet : shipment_watch
prédicat : delayDays (jours de retard)
objet : 2
```

Un triplet se lit donc « l'expédition `shipment_watch` a 2 jours de retard ». Le mot `objet` désigne ici la troisième position du triplet, pas une classe métier. La relation avec le magasin s'écrit elle aussi en triplet :

```text
shipment_watch — deliveredTo — store_main
```

`deliveredTo` relie deux ressources : c'est pourquoi l'ontologie la déclare propriété objet. `delayDays` relie l'expédition à un nombre : c'est une propriété de données.

## 4. Lire le vocabulaire OWL

Dans `rdf/ontology.ttl` :

- `Shipment` et `Store` sont des **classes**, c'est-à-dire des catégories.
- `shipment_watch`, `shipment_on_time`, `shipment_urgent` et `store_main` sont des **individus**, c'est-à-dire des exemples concrets.
- `deliveredTo` relie deux individus (une expédition à un magasin).
- `delayDays` donne le nombre de jours de retard.
- `riskBand` est la propriété où l'on rangera la catégorie calculée (« bande de risque »).

Les `rdfs:label` et `rdfs:comment` donnent des noms et explications en français. Le domaine et la portée documentent le type attendu des sujets et valeurs. La commande SHACL n'appelle pas de raisonneur OWL général ; la commande SWRL utilise un moteur séparé du profil OWL 2 RL, décrit plus loin.[60]

## 5. Traduire les deux règles

### Règle 1 — retard à surveiller

En français courant : « Pour chaque expédition dont on connaît le nombre de jours de retard, si ce nombre est supérieur à zéro et inférieur à trois, ajouter la bande “à surveiller”. »

La règle dans `rdf/shapes.ttl` est une requête SPARQL `CONSTRUCT` attachée à une forme SHACL :

```sparql
CONSTRUCT {
    $this <https://example.org/retail#riskBand> "à surveiller"@fr .
}
WHERE {
    $this <https://example.org/retail#delayDays> ?days .
    FILTER (?days > 0 && ?days < 3)
}
```

- `$this` est l'expédition examinée.
- Le motif `delayDays ?days` cherche le nombre connu pour cette expédition.
- `FILTER` compare ce nombre aux seuils.
- Si le filtre est vrai, `CONSTRUCT` crée le triplet avec `riskBand` et le texte français `"à surveiller"@fr`.

### Règle 2 — retard urgent

En français courant : « Si l'expédition a au moins trois jours de retard, ajouter la bande “urgent”. » La règle utilise le même motif de retard, mais son filtre est `?days >= 3` et son résultat est `riskBand "urgent"@fr`.

Les **SHACL Advanced Features** sont les fonctionnalités avancées de SHACL qui décrivent notamment ces règles. pySHACL ne les active que parce que le code appelle `shacl_rules(..., advanced=True)`. SHACL-AF est une Working Group Note, pas une Recommendation W3C ; voir le [glossaire](glossaire.md#shacl-advanced-features-shacl-af) pour les statuts.

## 6. Faire le calcul soi-même

1. Pour `shipment_on_time`, `$this` est `shipment_on_time` et `?days` vaut 0. `0 > 0` est faux ; la première règle ne crée rien. `0 >= 3` est faux ; la seconde ne crée rien.
2. Pour `shipment_watch`, `?days` vaut 2. `2 > 0` et `2 < 3` sont vrais ; le graphe reçoit :

   ```text
   shipment_watch — riskBand — "à surveiller"@fr
   ```

3. Pour `shipment_urgent`, `?days` vaut 3. La première condition `?days < 3` est fausse ; la deuxième condition `3 >= 3` est vraie. Le graphe reçoit :

   ```text
   shipment_urgent — riskBand — "urgent"@fr
   ```

Quand aucun triplet `riskBand` n'est créé pour le retard nul, cela signifie seulement que ces deux règles n'ont rien calculé. Cela ne prouve pas que toutes les interprétations possibles de « aucun risque » sont vraies.

## 7. Exécuter le POC

Depuis la racine du projet, avec l'environnement virtuel activé :

```bash
python -m retail_owl_shacl_poc
```

Le CLI annonce les conditions des deux règles, précise ce qu'est un triplet et traduit `riskBand` par « bande de risque ». Il montre ensuite les deux triplets ajoutés et le chemin du fichier `artifacts/retail-logistics-result.ttl`. Ouvrir ce fichier avec un éditeur de texte pour retrouver les faits sous forme Turtle.

## 8. Vérifier en changeant une donnée

1. Dans `rdf/data.ttl`, remplacer temporairement `ex:delayDays 2` par `ex:delayDays 3` pour `shipment_watch`.
2. Lancer `python -m retail_owl_shacl_poc`.
3. Observer que `shipment_watch` reçoit désormais `urgent` au lieu de « à surveiller ».
4. Remettre la valeur 2 et relancer pour revenir au résultat d'origine.

Cela montre le lien entre le fait d'entrée, le filtre numérique et le triplet créé.

## 9. Deux approches de règles, deux résultats

OWL décrit le vocabulaire. La règle exécutée par pySHACL est attachée à une forme SHACL et construit ici une valeur `riskBand`. La commande facultative SWRLAPI/Drools exécute des règles SWRL dans une ontologie OWL et ajoute des appartenances à des classes ; l'API décrit `infer()` comme l'import des faits et règles, leur exécution et l'écriture des connaissances inférées dans l'ontologie.[44]

SWRL est une Member Submission du W3C, pas une Recommendation.[10] Le moteur Drools de SWRLAPI est présenté comme un moteur SWRL et raisonneur OWL 2 RL ; ce n'est pas un raisonneur complet OWL 2 DL.[60]

| Approche | Exécutée par quelle commande ? | Ce qu'elle ajoute dans ce POC | Limite / statut |
|---|---|---|---|
| SHACL-SPARQL | `python -m retail_owl_shacl_poc` | Une valeur `riskBand`, par exemple `"à surveiller"@fr` | Utilise les règles SHACL-AF prises en charge par pySHACL ; SHACL Core est une Recommendation et SHACL-AF une Working Group Note.[1][2] |
| SWRL | `python -m retail_owl_shacl_poc.swrl_demo` | Un type OWL, `WatchShipment` ou `UrgentShipment` | Moteur Java/Maven optionnel, version SWRLAPI/Drools épinglée ; capacités du moteur à ne pas généraliser au-delà de son profil OWL 2 RL.[42][46][60] |
| SPARQL `CONSTRUCT` | Non exécutée séparément | Pourrait construire des triplets RDF à partir d'un motif SPARQL | Alternative plus directe, mais sans les cibles/formes SHACL de cette démo. SPARQL 1.1 est une Recommendation.[7] |
| OWL 2 RL / paquet Python `owlrl` | La bibliothèque Python n'est pas appelée par ces commandes | Pas de résultat produit par ce paquet dans le POC | À distinguer du moteur SWRLAPI/Drools, qui annonce lui-même une prise en charge OWL 2 RL.[6][21][60] |
| RuleML | Présenté, non exécuté | Aucun résultat dans le POC | Une représentation de règles n'est pas, à elle seule, un moteur d'exécution.[10] |

Les deux démonstrations sont indépendantes et relisent les mêmes faits d'entrée ; elles n'appellent pas l'une l'autre. Elles illustrent la différence entre une propriété de données produite par SHACL et une appartenance à une classe inférée par SWRL. Pour la lecture guidée de la règle et les précautions sur le moteur Java, voir le [guide SWRL](guide-swrl.md).

## 10. Où apprendre les termes

Voir [Glossaire de départ](glossaire.md) pour les définitions de triplet, classe, individu, propriété objet, propriété de données, SHACL-AF, SWRL, RuleML et licence sans redevance.

## Sources

[1] https://www.w3.org/TR/shacl
[2] https://www.w3.org/TR/shacl-af
[6] https://www.w3.org/TR/owl2-profiles
[7] https://www.w3.org/TR/sparql11-query
[10] https://www.w3.org/submissions/SWRL
[21] https://pypi.org/project/owlrl/7.6.2
[42] https://github.com/protegeproject/swrlapi-drools-engine
[44] https://github.com/protegeproject/swrlapi/blob/master/src/main/java/org/swrlapi/core/SWRLRuleEngine.java
[46] https://central.sonatype.com/artifact/edu.stanford.swrl/swrlapi-drools-engine/2.1.2
[60] https://github.com/protegeproject/swrlapi-drools-engine/blob/master/README.md
