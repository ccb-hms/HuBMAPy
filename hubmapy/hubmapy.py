import datetime
import logging
import os
import sys
import pandas as pd
from py4j.java_gateway import JavaGateway, launch_gateway


class HuBMAPy:
    PREFIXES = "PREFIX ccf: <http://purl.org/ccf/>\n" + \
               "PREFIX obo: <http://purl.obolibrary.org/obo/>\n" + \
               "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" + \
               "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" + \
               "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" + \
               "PREFIX dc: <http://purl.org/dc/terms/>\n"
    DEFAULT_ANATOMICAL_STRUCTURE = "obo:UBERON_0000006"
    DEFAULT_CELL_TYPE = "obo:CL_0000171"
    DEFAULT_TISSUE_BLOCK = "<http://dx.doi.org/10.1016/j.trsl.2017.07.006#TissueBlock>"

    def __init__(self, output_folder=os.getcwd(), save_reasoned_ontology=False):
        launch_gateway(jarpath=os.path.dirname(os.path.abspath(__file__)) + '/resources/robot.jar',
                       classpath='org.obolibrary.robot.PythonOperation',
                       port=25333,
                       die_on_exit=True)
        self._gateway = JavaGateway()
        self._output_folder = output_folder
        self._logger = self._logger()
        self._query_operation = self._gateway.jvm.org.obolibrary.robot.QueryOperation()
        self._dataset = self._query_operation.loadOntologyAsDataset(self._load_ontology(save_reasoned_ontology))
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

    def _load_ontology(self, save_reasoned_ontology):
        self._logger.info("Loading Ontology...")
        io_helper = self._gateway.jvm.org.obolibrary.robot.IOHelper()
        ontology = io_helper.loadOntology(os.path.dirname(os.path.abspath(__file__)) + '/resources/ccf.owl')

        self._logger.info("Reasoning over ontology...")
        reasoner_factory = self._gateway.jvm.org.semanticweb.elk.owlapi.ElkReasonerFactory()
        reason_operation = self._gateway.jvm.org.obolibrary.robot.ReasonOperation()
        options_map = self._gateway.jvm.java.util.HashMap()
        options_map.put("axiom-generators", "SubClass ClassAssertion PropertyAssertion")
        reason_operation.reason(ontology, reasoner_factory, options_map)

        if save_reasoned_ontology:
            iri = self._gateway.jvm.org.semanticweb.owlapi.model.IRI
            reasoned_ontology_iri = iri.create("file:" + self._output_folder + "/ccf_reasoned.owl")
            ontology.getOWLOntologyManager().saveOntology(ontology, reasoned_ontology_iri)
        return ontology

    def do_query(self, query, query_name='hubmap-query'):
        self._logger.debug("Executing query:\n" + query + "\n")
        timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
        query_results_file_name = self._output_folder + "/" + query_name + "-" + timestamp + ".csv"
        query_results_file = self._gateway.jvm.java.io.File(query_results_file_name)
        output_format = self._gateway.jvm.org.apache.jena.riot.Lang.CSV
        self._query_operation.runQuery(self._dataset, query, query_results_file, output_format)
        return pd.read_csv(query_results_file_name)

    # https://gist.github.com/rsgoncalves/c3dd13630807331bf571d4556fc4537f
    def biomarkers_for_all_cell_types(self):
        query = self.PREFIXES + "SELECT ?ct ?ct_lbl ?marker ?marker_lbl WHERE {\n" + \
                "?ct rdfs:subClassOf [ \n" + \
                "  owl:onProperty obo:RO_0015004 ; \n" \
                "  owl:someValuesFrom ?marker_set ] ;\n" + \
                "  rdfs:label ?ct_lbl ;\n" + \
                "  ccf:ccf_located_in ?as .\n" \
                "  ?as rdfs:label ?as_lbl .\n" + \
                "?marker_set owl:intersectionOf ?list .\n" + \
                "?list rdf:rest*/rdf:first [\n" + \
                "  owl:onProperty ccf:has_marker_component ; \n" + \
                "  owl:someValuesFrom ?marker ] .\n" + \
                "?marker rdfs:label ?marker_lbl }"
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types.__name__)

    # https://gist.github.com/rsgoncalves/b36dc685e4917593ac7c6a32cfd367d7
    def biomarkers_for_all_cell_types_in_anatomical_structure(self, anatomical_structure=DEFAULT_ANATOMICAL_STRUCTURE):
        query = self.PREFIXES + "SELECT (?ct as ?cell_type) (?ct_lbl as ?cell_type_name) ?marker (?marker_lbl as ?marker_name) WHERE {\n" + \
                "?ct rdfs:subClassOf [\n" + \
                "  owl:onProperty obo:RO_0015004 ;\n" + \
                "  owl:someValuesFrom ?marker_set ] ;\n" + \
                "  rdfs:label ?ct_lbl ;\n" + \
                "  ccf:ccf_located_in " + anatomical_structure + " .\n" + \
                "?marker_set owl:intersectionOf ?list .\n" + \
                "?list rdf:rest*/rdf:first [\n" + \
                "  owl:onProperty ccf:has_marker_component ; \n" + \
                "  owl:someValuesFrom ?marker ] .\n" + \
                "?marker rdfs:label ?marker_lbl }"
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types_in_anatomical_structure.__name__)

    # https://gist.github.com/rsgoncalves/ffebc784cdfb306c729d221deb1c2074
    def biomarkers_for_cell_type_in_anatomical_structure(self, cell_type=DEFAULT_CELL_TYPE,
                                                         anatomical_structure=DEFAULT_ANATOMICAL_STRUCTURE):
        query = self.PREFIXES + "SELECT ?ct_lbl ?as_lbl ?marker ?marker_lbl WHERE {\n" + \
                cell_type + " rdfs:subClassOf [\n" + \
                "  owl:onProperty obo:RO_0015004 ;\n" + \
                "  owl:someValuesFrom ?marker_set ] ;\n" + \
                "  rdfs:label ?ct_lbl ;\n" + \
                "  ccf:ccf_located_in " + anatomical_structure + " .\n" + \
                anatomical_structure + " rdfs:label ?as_lbl .\n" + \
                "?marker_set owl:intersectionOf ?list .\n" + \
                "?list rdf:rest*/rdf:first [\n" + \
                "  owl:onProperty ccf:has_marker_component ; \n" + \
                "  owl:someValuesFrom ?marker ] .\n" + \
                "?marker rdfs:label ?marker_lbl }"
        return self.do_query(query, query_name=self.biomarkers_for_cell_type_in_anatomical_structure.__name__)

    # https://gist.github.com/rsgoncalves/2b450da4dd0cbb1dc13f8bf7929b6d2e
    # TODO refactor to obtain tissues that collide with parts of the anatomical structure
    def tissue_blocks_in_anatomical_structure(self, anatomical_structure="obo:UBERON_0000948"):
        query = self.PREFIXES + "SELECT (?tb as ?tissue_block) ?donor ?donor_sex WHERE {\n" + \
                "?tb rdf:type ccf:tissue_block ; \n" + \
                "  ccf:has_registration_location [ ccf:collides_with " + anatomical_structure + " ] ; \n" + \
                "  ccf:comes_from ?donor . \n" + \
                "?donor ccf:has_biological_sex [ rdfs:label ?donor_sex ] }"
        return self.do_query(query, query_name=self.tissue_blocks_in_anatomical_structure.__name__)

    # https://gist.github.com/rsgoncalves/fe919eb2f33071df9da06d01469b5e41
    # TODO location of anatomical structure (filler of 'collides_with) is currently represented as a string literal
    def tissue_block_count_for_all_anatomical_structures(self):
        query = self.PREFIXES + "SELECT (count(?tb) as ?tissue_block_count) ?as_lbl ?as WHERE { \n" + \
                "?tb rdf:type ccf:tissue_block ; \n" + \
                "  ccf:has_registration_location [ ccf:collides_with ?as ] . \n" + \
                "BIND(IRI(?as) as ?as_iri) . \n" + \
                "?as_iri rdfs:label ?as_lbl } \n" + \
                "GROUP BY ?as ?as_lbl"
        return self.do_query(query, query_name=self.tissue_block_count_for_all_anatomical_structures.__name__)

    def anatomical_structures_in_tissue_block(self, tissue_block=DEFAULT_TISSUE_BLOCK):
        query = self.PREFIXES + "SELECT ?as ?as_lbl ?donor ?donor_sex WHERE { \n" + \
                tissue_block + " rdf:type ccf:tissue_block ; \n" + \
                "ccf:has_registration_location [ ccf:collides_with ?as ] ; \n" + \
                "ccf:comes_from ?donor . \n" + \
                "OPTIONAL { ?as rdfs:label ?as_lbl }\n" + \
                "OPTIONAL { ?donor ccf:has_biological_sex [ rdfs:label ?donor_sex ] } }"
        return self.do_query(query, query_name=self.anatomical_structures_in_tissue_block.__name__)

    # https://gist.github.com/rsgoncalves/3d318acdba74e39ee8e92f0b367c1f5f
    def locations_of_all_cell_types(self):
        query = self.PREFIXES + "SELECT ?ct ?ct_lbl ?as ?as_lbl WHERE { \n" + \
                "?ct ccf:ccf_located_in ?as . \n" + \
                "?ct rdfs:label ?ct_lbl . \n" + \
                "?as rdfs:label ?as_lbl } "
        return self.do_query(query, query_name=self.locations_of_all_cell_types.__name__)

    # https://gist.github.com/rsgoncalves/7181d9087a143085faa3f2b561d04051
    def evidence_for_specific_cell_type(self, cell_type=DEFAULT_CELL_TYPE):
        query = self.PREFIXES + "SELECT ?doi WHERE { \n" + \
                "[ rdf:type owl:Axiom ; \n" + \
                "  owl:annotatedSource " + cell_type + " ; \n" + \
                "  owl:annotatedProperty rdfs:subClassOf ; \n" + \
                "  dc:references ?doi ] }"
        return self.do_query(query, query_name=self.evidence_for_specific_cell_type.__name__)

    # https://gist.github.com/rsgoncalves/2268669a85e0a96d87e5a91a77be78f2
    def evidence_for_all_cell_types(self):
        query = self.PREFIXES + "SELECT ?ct_lbl ?ct ?doi WHERE { \n" + \
                "[ rdf:type owl:Axiom ; \n" + \
                "  owl:annotatedSource ?ct ; \n" + \
                "  owl:annotatedProperty rdfs:subClassOf ; \n" + \
                "  dc:references ?doi ] . \n" + \
                "?ct rdfs:label ?ct_lbl }"
        return self.do_query(query, self.evidence_for_all_cell_types.__name__)

    @staticmethod
    def _logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
