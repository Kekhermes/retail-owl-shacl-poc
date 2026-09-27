# Glossaire de départ

Ce glossaire accompagne le POC [OWL + SHACL-SPARQL pour la logistique retail](guide-pedagogique.md). Il ne suppose pas de connaissance préalable. Les noms techniques sont conservés dans leur forme utilisée dans le code, puis expliqués en français.

## Données et vocabulaire

### RDF
**RDF** est un modèle de données du Web sémantique. Il décrit des faits sous forme de liens entre des ressources et des valeurs. Dans ce POC, les faits sont conservés dans des graphes RDF.

### Triplet
Un **triplet** est un fait composé de trois positions : **sujet — prédicat — objet**.

```text
shipment_watch — delayDays — 2
```

Cela se lit : « l'expédition `shipment_watch` a `2` jours de retard ». Le sujet est l'expédition, le prédicat est la relation/propriété, et l'objet est la valeur reliée au sujet.

> Attention : l'« objet » dans un triplet est le nom de la troisième position. Une **propriété objet** est une catégorie de relation OWL qui relie deux ressources ; les deux expressions ne veulent pas dire la même chose.

### Graphe RDF
Un **graphe RDF** est un ensemble de triplets. `rdf/data.ttl` contient les faits de départ ; le graphe résultat contient ces faits plus les triplets produits par les règles.

### URI et préfixe Turtle
Une URI identifie une ressource. Par exemple, l'identifiant complet de `Shipment` est `https://example.org/retail#Shipment`. Dans un fichier Turtle, le préfixe `ex:` permet d'écrire `ex:Shipment` en raccourci. Le préfixe ne change pas l'identifiant.

### Turtle
**Turtle** est une syntaxe textuelle lisible pour écrire RDF. Les fichiers `rdf/ontology.ttl`, `rdf/data.ttl` et `rdf/shapes.ttl` utilisent cette syntaxe. Le point `.` termine un fait ; le point-virgule `;` permet de réutiliser le même sujet pour plusieurs faits.

## Ontologie OWL

### Ontologie
Une **ontologie** décrit le vocabulaire d'un domaine : quelles catégories existent et quelles relations elles entretiennent. Ici, elle décrit des expéditions, des magasins, leurs destinations et les propriétés des expéditions.

### OWL 2
**OWL 2** est un langage du W3C pour décrire des ontologies, avec des classes, propriétés, individus et valeurs.[29] Dans ce POC, OWL 2 déclare les classes et propriétés. **Le programme ne lance pas de raisonneur OWL général** : les deux calculs de risque sont faits par les règles SHACL-SPARQL.

### Classe
Une **classe** est une catégorie d'éléments. `ex:Shipment` désigne la catégorie « expédition » et `ex:Store` la catégorie « magasin ».

### Individu (ou instance)
Un **individu** est un élément concret de la catégorie. `ex:shipment_watch` est un individu de la classe `ex:Shipment`; `ex:store_main` est un individu de la classe `ex:Store`.

### Propriété objet
Une **propriété objet** (`owl:ObjectProperty`) relie deux individus. Dans `ex:shipment_watch ex:deliveredTo ex:store_main`, `deliveredTo` relie l'expédition au magasin destinataire.

### Propriété de données
Une **propriété de données** (`owl:DatatypeProperty`) relie un individu à une valeur simple, comme un nombre ou un texte. `delayDays` relie une expédition à un nombre ; `riskBand` relie l'expédition à la catégorie de risque calculée.

### Domaine et portée (`rdfs:domain` / `rdfs:range`)
Le **domaine** décrit le type attendu du sujet d'une propriété ; la **portée** décrit le type attendu de sa valeur. Par exemple, `delayDays` concerne une `Shipment` et sa valeur est un entier. Ces déclarations décrivent le modèle ; ce POC n'utilise pas de raisonneur OWL pour en déduire automatiquement des faits.

### `rdfs:label` et `rdfs:comment`
`rdfs:label` fournit un nom lisible, ici en français (`@fr`). `rdfs:comment` donne une courte explication. Ils documentent le vocabulaire mais ne déclenchent pas de règle.

## Règles SHACL-SPARQL

### SHACL
**SHACL** est le langage du W3C pour décrire des formes appliquées à des données RDF. Le moteur `pySHACL` peut vérifier ces formes et prendre en charge des fonctions avancées comme l'exécution de règles.[1][2][3]

### Forme (`Shape`) et `sh:targetClass`
Une **forme** regroupe une portée et éventuellement des contraintes ou des règles. `sh:targetClass ex:Shipment` dit à quel type de nœuds la forme s'applique : ici, aux individus connus comme des expéditions.

### Nœud cible (focus node)
Le **nœud cible** est l'expédition courante examinée par une règle. Lorsque la règle examine `shipment_watch`, la variable `$this` représente cette expédition.

### SPARQL
**SPARQL** est le langage de requête pour rechercher et construire des données RDF. Une règle `sh:SPARQLRule` utilise une requête de type `CONSTRUCT`.[7]

- `WHERE` décrit les faits qu'il faut retrouver dans le graphe.
- `?days` est une variable : elle prend la valeur de `delayDays` trouvée pour l'expédition courante.
- `FILTER` garde uniquement les résultats qui satisfont la condition numérique, par exemple `?days > 0 && ?days < 3`.
- `CONSTRUCT` décrit le nouveau triplet à créer lorsque les conditions sont satisfaites.
- `$this` désigne le nœud cible fourni à la règle par la forme SHACL.

### `riskBand`
`riskBand` est le nom technique du prédicat « bande de risque ». Le résultat pour `shipment_watch` est le triplet :

```text
shipment_watch — riskBand — "à surveiller"@fr
```

`riskBand` n'est pas un type de triplet : c'est le prédicat (la propriété) de ce triplet.

### Fait calculé, inféré ou matérialisé
Un **fait calculé** (aussi appelé fait inféré ou matérialisé ici) est un triplet effectivement ajouté au graphe résultat. Par exemple, la règle ajoute `riskBand "urgent"@fr` à l'expédition qui a trois jours de retard. Le graphe de départ n'affirmait pas cette valeur.

### SHACL Advanced Features (SHACL-AF)
Les **SHACL Advanced Features** (fonctionnalités avancées de SHACL) sont un document complémentaire à SHACL Core. Les règles utilisées dans ce POC viennent de cette famille de fonctionnalités ; `advanced=True` demande à pySHACL de les activer. SHACL Core est une Recommendation du W3C, mais SHACL-AF est une Working Group Note : ce n'est pas le même statut normatif.[1][2] L'implémentation effective doit aussi être supportée par le moteur choisi.[3]

### W3C Recommendation, Working Group Note et Member Submission
- Une **Recommendation** est une spécification que le W3C a approuvée comme recommandation stable.
- Une **Working Group Note** est un document publié par un groupe de travail, sans statut de Recommendation.
- Une **Member Submission** est un document proposé au W3C ; elle ne devient pas automatiquement une Recommendation.

Ces statuts expliquent le statut documentaire d'une spécification. Ils ne signifient pas, à eux seuls, qu'une bibliothèque donnée fonctionne ou qu'elle est sous une licence donnée.

## Approches comparées

### SWRL
**SWRL** signifie *Semantic Web Rule Language*. C'est une proposition de langage de règles liée à OWL et inspirée d'un sous-ensemble de RuleML.[10] Le POC ne l'exécute pas : il utilise SHACL-SPARQL à la place.

### RuleML
**RuleML** signifie *Rule Markup Language*. C'est une famille de représentations pour exprimer et échanger des règles ; SWRL utilise une partie de RuleML dans sa proposition.[10] RuleML n'est pas, à lui seul, un moteur d'exécution pour les règles de ce POC.

### SPARQL `CONSTRUCT`
`CONSTRUCT` peut produire un nouveau graphe directement à partir d'un motif trouvé par SPARQL. C'est une alternative plus directe, mais elle ne donne pas à elle seule la structure des formes/cibles SHACL.

### OWL 2 RL
**OWL 2 RL** est un profil OWL conçu pour permettre un raisonnement fondé sur des règles. La bibliothèque `owlrl` fournit des inférences de ce profil ; elle ne remplace pas ici le calcul métier des seuils de retard. Le POC ne lance pas cette inférence.

## Licence

Une **licence sans redevance** ne demande pas de frais de licence, mais peut imposer de conserver des notices ou de respecter d'autres conditions. Le tableau du projet identifie les licences déclarées des dépendances directes ; avant un déploiement de production, il faut aussi examiner toutes les dépendances transitives et leurs avis.

## Sources

[1] https://www.w3.org/TR/shacl
[2] https://www.w3.org/TR/shacl-af
[3] https://github.com/RDFLib/pySHACL
[7] https://www.w3.org/TR/sparql11-query
[10] https://www.w3.org/submissions/SWRL
[29] https://www.w3.org/TR/owl2-overview
