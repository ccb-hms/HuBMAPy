import datetime
import logging
import os
import sys
import pandas as pd
from py4j.java_gateway import JavaGateway, launch_gateway


class HuBMAPy:
    _DEFAULT_ANATOMICAL_STRUCTURE = "obo:UBERON_0000006"
    _DEFAULT_CELL_TYPE = "obo:CL_0000171"
    _DEFAULT_TISSUE_BLOCK = "<http://dx.doi.org/10.1016/j.trsl.2017.07.006#TissueBlock>"

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
        self._logger.info("Loading ontology...")
        io_helper = self._gateway.jvm.org.obolibrary.robot.IOHelper()
        ontology = io_helper.loadOntology(os.path.dirname(os.path.abspath(__file__)) + '/resources/ccf.owl')
        self._logger.info("...loaded HuBMAP ontology v" + self._get_ontology_version(ontology))
        self._logger.info("Reasoning over ontology...")
        reasoner_factory = self._gateway.jvm.org.semanticweb.elk.owlapi.ElkReasonerFactory()
        reason_operation = self._gateway.jvm.org.obolibrary.robot.ReasonOperation()
        reasoner_options = self._gateway.jvm.java.util.HashMap()
        reasoner_options.put("axiom-generators", "SubClass ClassAssertion PropertyAssertion")
        reason_operation.reason(ontology, reasoner_factory, reasoner_options)
        self._logger.info("...done")
        if save_reasoned_ontology:
            iri = self._gateway.jvm.org.semanticweb.owlapi.model.IRI
            reasoned_ontology_iri = iri.create("file:" + self._output_folder + "/ccf_reasoned.owl")
            ontology.getOWLOntologyManager().saveOntology(ontology, reasoned_ontology_iri)
        return ontology

    def _get_ontology_version(self, ontology):
        ontology_version = ''
        for annotation in ontology.getAnnotations():
            if str(annotation.getProperty()) == "owl:versionInfo":
                ontology_version = str(annotation.getValue().asLiteral().get().getLiteral())
        return ontology_version

    def load_query(self, query_file_name):
        query_file = open(os.path.dirname(os.path.abspath(__file__)) + '/queries/' + query_file_name)
        return query_file.read()

    def do_query(self, query, query_name='hubmap-query'):
        self._logger.debug("Executing query:\n" + query + "\n")
        timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
        query_results_file_name = self._output_folder + "/" + query_name + "-" + timestamp + ".csv"
        query_results_file = self._gateway.jvm.java.io.File(query_results_file_name)
        output_format = self._gateway.jvm.org.apache.jena.riot.Lang.CSV
        self._query_operation.runQuery(self._dataset, query, query_results_file, output_format)
        return pd.read_csv(query_results_file_name)

    def biomarkers_for_all_cell_types(self):
        query = self.load_query('biomarkers_for_all_cell_types.rq')
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types.__name__)

    def biomarkers_for_all_cell_types_in_anatomical_structure(self, anatomical_structure=_DEFAULT_ANATOMICAL_STRUCTURE):
        query = self.load_query('biomarkers_for_all_cell_types_in_anatomical_structure.rq')
        query = query.replace("?anatomical_structure", anatomical_structure)
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types_in_anatomical_structure.__name__)

    def biomarkers_for_cell_type_in_anatomical_structure(self, cell_type=_DEFAULT_CELL_TYPE,
                                                         anatomical_structure=_DEFAULT_ANATOMICAL_STRUCTURE):
        query = self.load_query('biomarkers_for_cell_type_in_anatomical_structure.rq')
        query = query.replace("?cell_type", cell_type)
        query = query.replace("?anatomical_structure", anatomical_structure)
        return self.do_query(query, query_name=self.biomarkers_for_cell_type_in_anatomical_structure.__name__)

    # TODO refactor to obtain tissues that collide with parts of the anatomical structure
    def tissue_blocks_in_anatomical_structure(self, anatomical_structure="obo:UBERON_0000948"):
        query = self.load_query('tissue_blocks_in_anatomical_structure.rq')
        query = query.replace("?anatomical_structure", anatomical_structure)
        return self.do_query(query, query_name=self.tissue_blocks_in_anatomical_structure.__name__)

    # TODO location of anatomical structure (filler of 'collides_with) is currently represented as a string literal
    def tissue_block_count_for_all_anatomical_structures(self):
        query = self.load_query('tissue_block_count_for_all_anatomical_structures.rq')
        return self.do_query(query, query_name=self.tissue_block_count_for_all_anatomical_structures.__name__)

    def anatomical_structures_in_tissue_block(self, tissue_block=_DEFAULT_TISSUE_BLOCK):
        query = self.load_query('anatomical_structures_in_tissue_block.rq')
        query = query.replace("?tissue_block", tissue_block)
        return self.do_query(query, query_name=self.anatomical_structures_in_tissue_block.__name__)

    def locations_of_all_cell_types(self):
        query = self.load_query('locations_of_all_cell_types.rq')
        return self.do_query(query, query_name=self.locations_of_all_cell_types.__name__)

    def evidence_for_specific_cell_type(self, cell_type=_DEFAULT_CELL_TYPE):
        query = self.load_query('evidence_for_specific_cell_type.rq')
        query = query.replace("?cell_type", cell_type)
        return self.do_query(query, query_name=self.evidence_for_specific_cell_type.__name__)

    def evidence_for_all_cell_types(self):
        query = self.load_query('evidence_for_all_cell_types.rq')
        return self.do_query(query, self.evidence_for_all_cell_types.__name__)

    @staticmethod
    def _logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
