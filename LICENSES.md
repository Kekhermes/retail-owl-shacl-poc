# Licences des dépendances du POC

Cet inventaire reflète les 14 paquets trouvés par `python -m pip freeze` dans l'environnement Python local au moment du contrôle. Les champs `License`, `License-Expression` et classifieurs des métadonnées installées ont été examinés ; aucune licence GPL ou AGPL n'y est déclarée. La résolution des dépendances peut évoluer : refaire le contrôle sur l'environnement exact de tout déploiement.

`Directe` signifie explicitement demandée dans les fichiers de dépendances ; `transitive` signifie installée comme dépendance d'un autre paquet. Les paquets de test ne sont pas requis par le runtime métier.

| Paquet | Version | Licence déclarée | Catégorie / usage |
|---|---:|---|---|
| pyshacl | 0.40.1 | Apache-2.0 [11][19] | directe runtime : moteur SHACL-SPARQL |
| rdflib | 7.6.0 | BSD-3-Clause [17][20] | directe runtime : graphes RDF |
| owlrl | 7.6.2 | W3C Software Notice and License (2015-05-13) [13][21] | directe runtime : support OWL 2 RL ; inférence non appelée par la démo |
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

Les métadonnées précises des autres paquets actuellement résolus sont disponibles dans les liens PyPI de leur ligne. Le POC ne verrouille pas séparément la fermeture transitive : une nouvelle résolution peut donc changer les versions ou licences. Avant un usage en production, régénérer l'inventaire sur l'environnement cible, contrôler les notices et demander une revue juridique si nécessaire. Les coûts d'infrastructure, de support commercial éventuel et d'hébergement ne sont pas évalués ici.

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
