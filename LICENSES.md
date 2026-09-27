# Licences des dépendances du POC

Cet inventaire sépare deux fermetures : les 14 paquets Python trouvés par `python -m pip freeze` dans l'environnement local (démo SHACL) et les 66 dépendances runtime Java/Maven résolues pour la démo SWRL facultative. La liste Maven avec versions/licences figure dans [`swrl-engine/THIRD-PARTY.txt`](swrl-engine/THIRD-PARTY.txt), et l'arbre exact dans [`swrl-engine/dependency-tree.txt`](swrl-engine/dependency-tree.txt). Le contrôle des 14 paquets Python et le rapport Maven final ne déclarent aucune licence GPL/AGPL ; le rapport Maven ne signale pas de licence inconnue. OWLAPI indique toutefois une licence duale Apache-2.0 ou LGPL-3.0, distincte de GPL.[51] Refaire l'audit sur les dépendances et l'environnement exacts de tout déploiement.

`Directe` signifie explicitement demandée dans les fichiers de dépendances ; `transitive` signifie installée comme dépendance d'un autre paquet. Les paquets de test ne sont pas requis par le runtime métier.

## Dépendances Python (démo SHACL)

| Paquet | Version | Licence déclarée | Catégorie / usage |
|---|---:|---|---|
| pyshacl | 0.40.1 | Apache-2.0 [11][19] | directe runtime : moteur SHACL-SPARQL |
| rdflib | 7.6.0 | BSD-3-Clause [17][20] | directe runtime : graphes RDF |
| owlrl | 7.6.2 | W3C Software Notice and License (2015-05-13) [13][21] | directe runtime Python : paquet présent, inférence non appelée par la démo SHACL ; SWRLAPI/Drools utilise un moteur OWL 2 RL distinct |
| html5rdf | 1.2.1 | MIT [24][30] | transitive runtime |
| importlib_metadata | 9.0.1 | Apache-2.0 [11] (métadonnées installées ; [page PyPI versionnée](https://pypi.org/project/importlib-metadata/9.0.1/)) | transitive runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause [25][31] | transitive runtime |
| prettytable | 3.18.0 | BSD-3-Clause [27] | transitive runtime |
| pyparsing | 3.3.3 | MIT [30] (métadonnées installées ; [page PyPI versionnée](https://pypi.org/project/pyparsing/3.3.3/)) | transitive runtime |
| wcwidth | 0.9.1 | MIT [30] (métadonnées installées ; [page PyPI versionnée](https://pypi.org/project/wcwidth/0.9.1/)) | transitive runtime |
| zipp | 4.1.0 | MIT [30] (métadonnées installées ; [page PyPI versionnée](https://pypi.org/project/zipp/4.1.0/)) | transitive runtime |
| pytest | 9.1.1 | MIT [22][30] | directe de développement/test uniquement |
| iniconfig | 2.3.0 | MIT [30] (métadonnées installées ; [page PyPI versionnée](https://pypi.org/project/iniconfig/2.3.0/)) | transitive de développement/test |
| pluggy | 1.6.0 | MIT [26][30] | transitive de développement/test |
| Pygments | 2.21.0 | BSD-2-Clause [28][31] | transitive de développement/test |

Les textes Apache-2.0, MIT et W3C 2015 accordent leurs permissions sans frais ou redevance, sous réserve de conserver les avis et de respecter les conditions.[11][30][32]

Les licences BSD ont également des conditions de redistribution et de conservation des notices ; vérifier le texte exact correspondant au paquet utilisé.[17][31]

La licence W3C d'OWL-RL n'est pas Apache/BSD/MIT : conserver son avis et confirmer qu'elle est compatible avec toute politique interne. OWL-RL 7.6.2 déclare précisément la notice W3C 2015 ; le W3C indique que cette édition a ensuite été remplacée, donc vérifier la notice applicable à la version distribuée.[13][21][32]

Ce relevé n'est pas un avis juridique.

Les métadonnées précises des paquets Python sont accessibles dans les liens PyPI de leur ligne. La fermeture Python transitive n'est pas verrouillée séparément ; une nouvelle résolution peut changer les versions ou licences. Le Maven SWRL épingle son moteur direct dans `swrl-engine/pom.xml`, mais ses transitives peuvent évoluer avec les versions amont : après toute modification, régénérer les rapports ci-dessus et refaire la revue. Le JDK et Maven doivent être installés séparément ; le dépôt ne les redistribue pas et le présent rapport Maven couvre les dépendances runtime, pas les outils de build. Les coûts d'infrastructure, de support commercial éventuel et d'hébergement ne sont pas évalués ici.

## Dépendances Java/Maven (démo SWRL facultative)

| Composant représentatif | Version résolue | Licence déclarée | Note |
|---|---:|---|---|
| SWRLAPI | 2.1.2 | BSD 2-Clause [46][47] | API pour charger et exécuter les règles SWRL |
| Moteur SWRLAPI basé sur Drools | 2.1.2 | BSD 2-Clause [46][60] | Intégration SWRLAPI/Drools effectivement exécutée |
| Drools Core / Compiler | 7.73.0.Final | Apache-2.0 [50] | Moteur de règles transitif |
| OWLAPI OSGi and Compatibility Distribution | 4.5.25 | Apache-2.0 OU LGPL-3.0 [49][51] | Licence duale ; l'option Apache-2.0 est disponible |
| MVEL | 2.5.2.Final | Apache-2.0 [52] | Version explicitement résolue par le POM |
| RDF4J | 3.7.7 | Eclipse Distribution License v1.0 (OSI-approved BSD-3-Clause) [63] | Dépendance transitive pour le traitement RDF |
| MXParser | 1.2.2 | Indiana University Extreme! Lab Software License [54][56] | Licence non standard ; conserver l'attribution et les conditions de redistribution décrites dans [`swrl-engine/NOTICE.md`](swrl-engine/NOTICE.md) |

Le rapport complet (`swrl-engine/THIRD-PARTY.txt`) contient 66 dépendances Java runtime, leurs versions et licences déclarées. Pour régénérer les rapports depuis la racine du dépôt :

```bash
mvn -B -q -f swrl-engine/pom.xml dependency:tree -Dscope=runtime -DoutputFile=target/dependency-tree.txt -DoutputType=text
mvn -B -q -f swrl-engine/pom.xml org.codehaus.mojo:license-maven-plugin:2.5.0:add-third-party -Dlicense.outputDirectory=target/license-report -Dlicense.failOnMissing=false
```

Les fichiers produits sont dans `swrl-engine/target/` ; comparer le résultat aux deux rapports versionnés avant de les remplacer. Le POM exclut les modules inutilisés par cette démonstration — le parseur mathématique JEP (GPL-3.0), des artefacts du Checker Framework et les API JAXB/Activation — ; les deux règles numériques de comparaison ont été exécutées avec cette fermeture réduite. Ne pas ajouter de built-ins ou de dépendances qui les nécessitent sans ré-auditer et retester.

Le rapport final ne présente aucune entrée GPL/AGPL ou licence inconnue. OWLAPI est dual Apache-2.0/LGPL-3.0 : l'option Apache-2.0 est disponible, tandis que LGPL-3.0 n'est pas GPL/AGPL. Aucune clause de redevance n'a été identifiée dans les licences déclarées de la fermeture résolue ; cela ne remplace pas une revue juridique. La licence MXParser exige de conserver ses mentions et conditions si son code est redistribué ; le POC ne vend ni ne fournit ses JAR.

## Sources

[11] https://www.apache.org/licenses/LICENSE-2.0.html
[13] https://github.com/RDFLib/OWL-RL/blob/master/LICENSE.txt
[17] https://github.com/RDFLib/rdflib/blob/main/LICENSE
[19] https://pypi.org/project/pyshacl/0.40.1
[20] https://pypi.org/project/rdflib/7.6.0
[21] https://pypi.org/project/owlrl/7.6.2
[22] https://pypi.org/project/pytest/9.1.1
[24] https://pypi.org/project/html5rdf/1.2.1
[25] https://pypi.org/project/packaging/26.3
[26] https://pypi.org/project/pluggy/1.6.0
[27] https://pypi.org/project/prettytable/3.18.0
[28] https://pypi.org/project/Pygments/2.21.0
[30] https://opensource.org/license/mit
[31] https://spdx.org/licenses/BSD-2-Clause.html
[32] https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document
[46] https://central.sonatype.com/artifact/edu.stanford.swrl/swrlapi-drools-engine/2.1.2
[47] https://central.sonatype.com/artifact/edu.stanford.swrl/swrlapi/2.1.2
[49] https://github.com/owlcs/owlapi
[50] https://github.com/kiegroup/drools/blob/main/LICENSE
[51] https://central.sonatype.com/artifact/net.sourceforge.owlapi/owlapi-osgidistribution/4.5.25
[52] https://central.sonatype.com/artifact/org.mvel/mvel2/2.5.2.Final
[54] https://central.sonatype.com/artifact/io.github.x-stream/mxparser/1.2.2
[56] https://raw.githubusercontent.com/x-stream/mxparser/master/LICENSE.txt
[60] https://github.com/protegeproject/swrlapi-drools-engine/blob/master/README.md
[63] https://www.eclipse.org/org/documents/edl-v10
