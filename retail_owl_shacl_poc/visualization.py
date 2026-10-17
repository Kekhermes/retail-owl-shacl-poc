import html
import json
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

EX = Namespace("https://example.org/retail#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def _local_name(uri: URIRef | str) -> str:
    """Extrait le nom local lisible d'un URI."""
    uri_str = str(uri)
    if "#" in uri_str:
        return uri_str.split("#")[-1]
    return uri_str.rstrip("/").split("/")[-1]


def _get_label(graph: Graph, node: URIRef | str) -> str:
    """Renvoie le rdfs:label français ou le nom local d'un nœud."""
    labels = list(graph.objects(URIRef(str(node)), RDFS.label))
    for lbl in labels:
        if isinstance(lbl, Literal) and lbl.language == "fr":
            return str(lbl)
    if labels:
        return str(labels[0])
    return _local_name(node)


def _get_comment(graph: Graph, node: URIRef | str) -> str:
    """Renvoie le commentaire rdfs:comment ou une chaîne vide."""
    comments = list(graph.objects(URIRef(str(node)), RDFS.comment))
    for comment in comments:
        if isinstance(comment, Literal) and comment.language == "fr":
            return str(comment)
    if comments:
        return str(comments[0])
    return ""


def generate_mermaid_ontology(ontology_graph: Graph) -> str:
    """Génère la syntaxe Mermaid classDiagram pour l'ontologie OWL."""
    lines = [
        "classDiagram",
        "    direction LR",
    ]

    classes = sorted(
        set(ontology_graph.subjects(RDF.type, OWL.Class)),
        key=_local_name,
    )

    # Récupérer les propriétés de données associées aux classes (par rdfs:domain)
    datatype_props = sorted(
        set(ontology_graph.subjects(RDF.type, OWL.DatatypeProperty)),
        key=_local_name,
    )
    class_attributes: dict[str, list[str]] = {cls: [] for cls in classes}
    for prop in datatype_props:
        domain = ontology_graph.value(prop, RDFS.domain)
        prop_range = ontology_graph.value(prop, RDFS.range)
        type_str = _local_name(prop_range) if prop_range else "string"
        name_str = _local_name(prop)
        if domain and domain in class_attributes:
            class_attributes[domain].append(f"+{type_str} {name_str}")

    # Déclaration des classes et de leurs attributs
    for cls in classes:
        cls_name = _local_name(cls)
        lines.append(f"    class {cls_name} {{")
        for attr in class_attributes.get(cls, []):
            lines.append(f"        {attr}")
        lines.append("    }")

    # Relations de sous-classe (subClassOf)
    for subclass, _, superclass in ontology_graph.triples((None, RDFS.subClassOf, None)):
        if (subclass, RDF.type, OWL.Class) in ontology_graph or isinstance(subclass, URIRef):
            sub_name = _local_name(subclass)
            super_name = _local_name(superclass)
            lines.append(f"    {super_name} <|-- {sub_name} : subClassOf")

    # Relations d'objet (ObjectProperty)
    object_props = sorted(
        set(ontology_graph.subjects(RDF.type, OWL.ObjectProperty)),
        key=_local_name,
    )
    for prop in object_props:
        domain = ontology_graph.value(prop, RDFS.domain)
        prop_range = ontology_graph.value(prop, RDFS.range)
        prop_name = _local_name(prop)
        if domain and prop_range:
            dom_name = _local_name(domain)
            rng_name = _local_name(prop_range)
            lines.append(f"    {dom_name} --> {rng_name} : {prop_name}")

    return "\n".join(lines) + "\n"


def _build_vis_data(graph: Graph) -> dict[str, list[dict[str, Any]]]:
    """Construit les nœuds et les arêtes pour la bibliothèque vis-network."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    # 1. Classes OWL (T-Box)
    classes = set(graph.subjects(RDF.type, OWL.Class))

    # Récupérer les propriétés de données par classe
    datatype_props = sorted(
        set(graph.subjects(RDF.type, OWL.DatatypeProperty)),
        key=_local_name,
    )
    class_attributes: dict[str, list[str]] = {str(cls): [] for cls in classes}
    for prop in datatype_props:
        domain = graph.value(prop, RDFS.domain)
        prop_range = graph.value(prop, RDFS.range)
        p_name = _local_name(prop)
        t_name = _local_name(prop_range) if prop_range else "Literal"
        if domain and str(domain) in class_attributes:
            class_attributes[str(domain)].append(f"+ {p_name} : {t_name}")

    for cls in classes:
        cls_id = str(cls)
        name = _local_name(cls)
        label = _get_label(graph, cls)
        comment = _get_comment(graph, cls)
        node_ids.add(cls_id)

        attrs = class_attributes.get(cls_id, [])
        attr_text = ("\n────────────\n" + "\n".join(attrs)) if attrs else ""
        display_label = f"«Class»\n{label}\n({name}){attr_text}"

        nodes.append({
            "id": cls_id,
            "label": display_label,
            "title": f"<b>Classe OWL :</b> {name}<br><b>Label :</b> {label}<br><b>URI :</b> {cls_id}<br>{comment}",
            "group": "tbox_class",
            "category": "tbox",
            "raw_name": name,
            "comment": comment,
            "shape": "box",
            "color": {"background": "#1e40af", "border": "#1d4ed8"},
            "font": {"color": "#ffffff", "face": "Inter, sans-serif", "bold": True},
        })

    # 2. Relations de sous-classes
    for sub, _, sup in graph.triples((None, RDFS.subClassOf, None)):
        edges.append({
            "from": str(sub),
            "to": str(sup),
            "label": "subClassOf",
            "category": "tbox",
            "arrows": {"to": {"type": "triangle"}},
            "dashes": True,
            "color": {"color": "#60a5fa"},
            "font": {"background": "#0f172a", "color": "#93c5fd"},
        })

    # 3. Object Properties (T-Box)
    for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
        domain = graph.value(prop, RDFS.domain)
        prop_range = graph.value(prop, RDFS.range)
        p_label = _get_label(graph, prop)
        p_comment = _get_comment(graph, prop)
        if domain and prop_range:
            edges.append({
                "from": str(domain),
                "to": str(prop_range),
                "label": p_label,
                "title": f"<b>ObjectProperty :</b> {_local_name(prop)}<br>{p_comment}",
                "category": "tbox",
                "arrows": "to",
                "color": {"color": "#38bdf8"},
                "font": {"background": "#0f172a", "color": "#7dd3fc"},
                "width": 2,
            })

    # 4. Individus / Faits (A-Box)
    individuals: set[URIRef] = set()
    for s, p, o in graph.triples((None, RDF.type, None)):
        if o != OWL.Class and o != OWL.Ontology and o != OWL.ObjectProperty and o != OWL.DatatypeProperty:
            if isinstance(s, URIRef):
                individuals.add(s)

    for ind in sorted(individuals, key=_local_name):
        ind_id = str(ind)
        name = _local_name(ind)
        label = _get_label(graph, ind)
        comment = _get_comment(graph, ind)
        types = [_local_name(t) for t in graph.objects(ind, RDF.type)]
        types_str = ", ".join(types)

        delays = list(graph.objects(ind, EX.delayDays))
        delay_val = str(delays[0]) if delays else None

        risks = list(graph.objects(ind, EX.riskBand))
        risk_val = ", ".join([str(r) for r in risks]) if risks else None

        details = [f"<b>Individu :</b> {name}", f"<b>Libellé :</b> {label}", f"<b>Type(s) :</b> {types_str}"]
        if delay_val is not None:
            details.append(f"<b>Retard constaté :</b> {delay_val} jour(s)")
        if risk_val:
            details.append(f"<b>Bande de risque (calculée) :</b> {risk_val}")

        node_color = "#059669" if "Store" in types_str else "#d97706"
        if risk_val == "urgent" or "UrgentShipment" in types_str:
            node_color = "#dc2626"
        elif risk_val == "à surveiller" or "WatchShipment" in types_str:
            node_color = "#ea580c"

        node_ids.add(ind_id)
        nodes.append({
            "id": ind_id,
            "label": f"{label}\n({name})",
            "title": "<br>".join(details),
            "group": "abox_individual",
            "category": "abox",
            "raw_name": name,
            "comment": comment,
            "delay": delay_val,
            "risk": risk_val,
            "types": types,
            "shape": "dot",
            "size": 24,
            "color": {"background": node_color, "border": "#ffffff"},
            "font": {"color": "#f8fafc", "face": "Inter, sans-serif"},
        })

        # Relier l'individu à son type de classe
        for t in graph.objects(ind, RDF.type):
            t_str = str(t)
            if t_str in node_ids:
                edges.append({
                    "from": ind_id,
                    "to": t_str,
                    "label": "rdf:type",
                    "category": "instance_of",
                    "arrows": "to",
                    "dashes": True,
                    "color": {"color": "#64748b"},
                    "font": {"background": "#0f172a", "color": "#94a3b8", "size": 10},
                })

        # Relier aux autres individus via deliveredTo
        for dest in graph.objects(ind, EX.deliveredTo):
            edges.append({
                "from": ind_id,
                "to": str(dest),
                "label": "deliveredTo",
                "category": "abox",
                "arrows": "to",
                "color": {"color": "#10b981"},
                "font": {"background": "#0f172a", "color": "#6ee7b7"},
                "width": 2,
            })

    return {"nodes": nodes, "edges": edges}


def generate_interactive_html(
    graph: Graph,
    output_path: str | Path,
    title: str = "Ontologie & Données Retail — Visualisation Interactive",
) -> Path:
    """Génère une page HTML autonome avec Vis.js pour explorer le modèle et les faits."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = _build_vis_data(graph)
    data_json = json.dumps(data, indent=2, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        header {{
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}
        .header-title {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 9999px;
            background: #1e3a8a;
            color: #93c5fd;
            border: 1px solid #3b82f6;
        }}
        .controls {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        button {{
            background: var(--surface-hover);
            color: var(--text);
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        button:hover {{
            background: var(--primary);
            border-color: var(--primary);
        }}
        button.active {{
            background: var(--primary);
            border-color: var(--primary);
        }}
        .search-box {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 10px;
            color: var(--text);
            font-size: 13px;
            outline: none;
            width: 180px;
        }}
        .search-box:focus {{
            border-color: var(--primary);
        }}
        #container {{
            flex: 1;
            display: flex;
            position: relative;
            overflow: hidden;
        }}
        #network {{
            flex: 1;
            height: 100%;
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        }}
        #sidebar {{
            width: 330px;
            background: var(--surface);
            border-left: 1px solid var(--border);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            overflow-y: auto;
        }}
        .card {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
        }}
        .card h4 {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
            font-size: 12px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        .legend-circle {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .details-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--primary);
        }}
        .details-item {{
            margin-bottom: 8px;
            font-size: 13px;
            line-height: 1.4;
        }}
        .details-label {{
            color: var(--text-muted);
            font-size: 11px;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <h2 style="font-size: 17px; font-weight: 600;">Logistique Retail</h2>
            <span class="badge">OWL + SHACL + SWRL</span>
        </div>
        <div class="controls">
            <button id="btn-all" class="active" onclick="filterGraph('all')">Tout voir</button>
            <button id="btn-tbox" onclick="filterGraph('tbox')">Ontologie seule (T-Box)</button>
            <button id="btn-abox" onclick="filterGraph('abox')">Données & Règles (A-Box)</button>
            <button onclick="network.fit({{animation: true}})">Recentrer</button>
            <input type="text" id="search" class="search-box" placeholder="Rechercher..." oninput="searchNode(this.value)">
        </div>
    </header>

    <div id="container">
        <div id="network"></div>
        <aside id="sidebar">
            <div class="card">
                <h4>Élément sélectionné</h4>
                <div id="selection-details">
                    <p style="font-size: 13px; color: var(--text-muted);">Cliquez sur un nœud ou une relation dans le graphe pour inspecter ses axiomes, annotations et faits.</p>
                </div>
            </div>

            <div class="card">
                <h4>Légende</h4>
                <div class="legend-item">
                    <span class="legend-dot" style="background: #1e40af;"></span>
                    <span>Classe OWL (Vocabulaire T-Box)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-circle" style="background: #059669;"></span>
                    <span>Magasin (Individu)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-circle" style="background: #d97706;"></span>
                    <span>Expédition (À l'heure)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-circle" style="background: #ea580c;"></span>
                    <span>Expédition (À surveiller)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-circle" style="background: #dc2626;"></span>
                    <span>Expédition (Urgente)</span>
                </div>
            </div>

            <div class="card">
                <h4>Règles pédagogiques</h4>
                <p style="font-size: 12px; color: var(--text-muted); line-height: 1.4;">
                    • <b>SHACL-SPARQL</b> calcule les valeurs <code>riskBand</code> ("à surveiller" dès 1 jour de retard, "urgent" dès 3 jours).<br>
                    • <b>SWRL</b> infère le classement ontologique dans <code>WatchShipment</code> ou <code>UrgentShipment</code>.
                </p>
            </div>
        </aside>
    </div>

    <script>
        const rawData = {data_json};

        let currentFilter = 'all';
        let nodesDataset = new vis.DataSet(rawData.nodes);
        let edgesDataset = new vis.DataSet(rawData.edges);

        const container = document.getElementById('network');
        const options = {{
            nodes: {{
                font: {{ color: '#ffffff', size: 13 }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                font: {{ align: 'horizontal', size: 11, strokeWidth: 0 }},
                smooth: {{ type: 'cubicBezier', forceDirection: 'none' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }}
            }},
            physics: {{
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -70,
                    centralGravity: 0.015,
                    springLength: 130,
                    springConstant: 0.08,
                    damping: 0.85
                }},
                stabilization: {{ iterations: 200 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100
            }}
        }};

        const network = new vis.Network(container, {{ nodes: nodesDataset, edges: edgesDataset }}, options);

        function showDetails(nodeId) {{
            const node = rawData.nodes.find(n => n.id === nodeId);
            const container = document.getElementById('selection-details');
            if (!node) {{
                container.innerHTML = '<p style="font-size: 13px; color: var(--text-muted);">Aucun élément sélectionné.</p>';
                return;
            }}

            let html = `<div class="details-title">${{node.raw_name || node.label.replace(/\\n/g, ' — ')}}</div>`;
            html += `<div class="details-item"><div class="details-label">Identifiant / URI</div><code>${{node.id}}</code></div>`;
            if (node.comment) {{
                html += `<div class="details-item"><div class="details-label">Description (rdfs:comment)</div>${{node.comment}}</div>`;
            }}
            if (node.types) {{
                html += `<div class="details-item"><div class="details-label">Types RDF</div>${{node.types.join(', ')}}</div>`;
            }}
            if (node.delay !== undefined && node.delay !== null) {{
                html += `<div class="details-item"><div class="details-label">Jours de retard</div><b>${{node.delay}} jour(s)</b></div>`;
            }}
            if (node.risk) {{
                html += `<div class="details-item"><div class="details-label">Bande de risque déduite</div><span style="color:#f87171; font-weight:bold;">${{node.risk}}</span></div>`;
            }}
            container.innerHTML = html;
        }}

        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                showDetails(params.nodes[0]);
            }}
        }});

        function filterGraph(mode) {{
            currentFilter = mode;
            document.querySelectorAll('.controls button').forEach(b => b.classList.remove('active'));
            if (mode === 'all') document.getElementById('btn-all').classList.add('active');
            if (mode === 'tbox') document.getElementById('btn-tbox').classList.add('active');
            if (mode === 'abox') document.getElementById('btn-abox').classList.add('active');

            let filteredNodes = rawData.nodes;
            let filteredEdges = rawData.edges;

            if (mode === 'tbox') {{
                filteredNodes = rawData.nodes.filter(n => n.category === 'tbox');
                const nodeIds = new Set(filteredNodes.map(n => n.id));
                filteredEdges = rawData.edges.filter(e => e.category === 'tbox' && nodeIds.has(e.from) && nodeIds.has(e.to));
            }} else if (mode === 'abox') {{
                filteredNodes = rawData.nodes.filter(n => n.category === 'abox');
                const nodeIds = new Set(filteredNodes.map(n => n.id));
                filteredEdges = rawData.edges.filter(e => e.category === 'abox' && nodeIds.has(e.from) && nodeIds.has(e.to));
            }}

            nodesDataset.clear();
            nodesDataset.add(filteredNodes);
            edgesDataset.clear();
            edgesDataset.add(filteredEdges);
            network.fit({{ animation: true }});
        }}

        function searchNode(query) {{
            if (!query) return;
            const q = query.toLowerCase();
            const match = rawData.nodes.find(n => (n.raw_name && n.raw_name.toLowerCase().includes(q)) || (n.label && n.label.toLowerCase().includes(q)));
            if (match) {{
                network.focus(match.id, {{ scale: 1.2, animation: true }});
                network.selectNodes([match.id]);
                showDetails(match.id);
            }}
        }}
    </script>
</body>
</html>
"""
    path.write_text(html_content, encoding="utf-8")
    return path


def export_visualizations(
    graph: Graph,
    output_dir: str | Path = "artifacts",
) -> dict[str, Path]:
    """Génère et sauvegarde le diagramme Mermaid et la page HTML interactive."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    mermaid_content = generate_mermaid_ontology(graph)
    mermaid_path = out / "ontology.mmd"
    mermaid_path.write_text(mermaid_content, encoding="utf-8")

    html_path = generate_interactive_html(graph, out / "ontology-graph.html")

    return {
        "mermaid": mermaid_path,
        "html": html_path,
    }


def cli() -> None:
    """CLI autonome pour générer uniquement les visualisations."""
    from .engine import build_demo_graph

    graph = build_demo_graph()
    artifacts = export_visualizations(graph)
    print(f"diagramme Mermaid enregistré: {artifacts['mermaid']}")
    print(f"visualisation interactive HTML enregistrée: {artifacts['html']}")


if __name__ == "__main__":
    cli()
