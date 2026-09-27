package org.kekhermes.retail;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.swrlapi.core.SWRLRuleEngine;
import org.swrlapi.factory.SWRLAPIFactory;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** Exécute les règles SWRL optionnelles sur les faits RDF fournis par Python. */
public final class SWRLDemo {
  private SWRLDemo() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3) {
      throw new IllegalArgumentException("Attendu : ontology.owl resultat.owl regles.txt");
    }

    Path inputPath = Path.of(args[0]);
    Path outputPath = Path.of(args[1]).toAbsolutePath();
    Path rulesPath = Path.of(args[2]);

    OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
    OWLOntology ontology = manager.loadOntologyFromOntologyDocument(inputPath.toFile());
    SWRLRuleEngine ruleEngine = SWRLAPIFactory.createSWRLRuleEngine(ontology);

    int ruleCount = 0;
    for (String sourceLine : Files.readAllLines(rulesPath, StandardCharsets.UTF_8)) {
      String line = sourceLine.trim();
      if (line.isEmpty() || line.startsWith("#")) {
        continue;
      }

      int separator = line.indexOf('|');
      if (separator < 1 || separator == line.length() - 1) {
        throw new IllegalArgumentException("Ligne de règle invalide : " + sourceLine);
      }

      String name = line.substring(0, separator).trim();
      String rule = line.substring(separator + 1).trim();
      ruleEngine.createSWRLRule(name, rule);
      ruleCount++;
    }

    if (ruleCount == 0) {
      throw new IllegalArgumentException("Aucune règle SWRL n'a été définie.");
    }

    // infer() charge les faits et règles, exécute le moteur, puis réécrit les inférences dans l'ontologie.
    ruleEngine.infer();
    Files.createDirectories(outputPath.getParent());
    manager.saveOntology(ontology, new RDFXMLDocumentFormat(), IRI.create(outputPath.toUri()));
    System.out.println("Règles SWRL exécutées : " + ruleCount);
  }
}
