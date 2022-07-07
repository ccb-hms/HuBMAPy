import datetime
import logging
import os
import re
import sys
import pandas as pd
from py4j.java_gateway import JavaGateway


class HuBMAPy:
    _DEFAULT_ANATOMICAL_STRUCTURE = "obo:UBERON_0000006"
    _DEFAULT_CELL_TYPE = "obo:CL_0000171"
    _DEFAULT_TISSUE_BLOCK = "<http://dx.doi.org/10.1016/j.trsl.2017.07.006#TissueBlock>"
    _DEFAULT_BIOMARKERS = "hgnc:633,hgnc:637,hgnc:800"

    def __init__(self, output_folder=os.getcwd()):
        self._gateway = JavaGateway().launch_gateway(
            jarpath=os.path.dirname(os.path.abspath(__file__)) + '/resources/robot.jar',
            classpath='org.obolibrary.robot.PythonOperation',
            port=25333,
            die_on_exit=True)
        self._output_folder = output_folder
        self._logger = self._logger()
        self._query_operation = self._gateway.jvm.org.obolibrary.robot.QueryOperation()
        self._dataset = self._query_operation.loadOntologyAsDataset(self._load_ontology())
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

    def _load_ontology(self):
        self._logger.info("Loading and reasoning over ontology...")
        ontology_folder = os.path.dirname(os.path.abspath(__file__)) + '/resources/'
        self._reason('file:' + ontology_folder)  # Reason over ontology using the smores reasoner
        io_helper = self._gateway.jvm.org.obolibrary.robot.IOHelper()
        ontology = io_helper.loadOntology(ontology_folder + 'ccf-reasoned.owl')  # Load reasoned ontology for ROBOT
        self._logger.info("...done: HuBMAP ontology v" + self._get_ontology_version(ontology))
        return ontology

    def _reason(self, ontology_folder):
        reasoner_gateway = JavaGateway().launch_gateway(
            jarpath=os.path.dirname(os.path.abspath(__file__)) + '/resources/smores.jar',
            classpath='edu.harvard.hms.ccb.reasoner.ontology.smores.PythonGateway',
            port=25334,
            die_on_exit=True)
        reasoner = reasoner_gateway.jvm.edu.harvard.hms.ccb.reasoner.ontology.smores.Smores()
        results = reasoner.loadOntologyAndReason(ontology_folder + 'ccf.owl', 'elk', True, False)
        reasoned_ontology = results.getOntology()
        iri = reasoner_gateway.jvm.org.semanticweb.owlapi.model.IRI
        reasoned_ontology_iri = iri.create(ontology_folder + 'ccf-reasoned.owl')
        reasoned_ontology.getOWLOntologyManager().saveOntology(reasoned_ontology, reasoned_ontology_iri)

    def _get_ontology_version(self, ontology):
        ontology_version = ''
        for annotation in ontology.getAnnotations():
            if str(annotation.getProperty()) == "owl:versionInfo":
                ontology_version = str(annotation.getValue().asLiteral().get().getLiteral())
        return ontology_version

    def _load_query(self, query_file, built_in=True):
        if built_in:
            query = open(os.path.dirname(os.path.abspath(__file__)) + '/queries/' + query_file)
        else:
            query = open(query_file)
        return query.read()

    def do_query(self, query, query_name='hubmap_query'):
        """
        Execute the given query against the loaded ontology

        Parameters
        ----------
        query: str
            SPARQL query string
        query_name : str
            Name of the query to be included in the output query results file

        Returns
        ----------
        df
            Data frame containing the query results
        """
        self._logger.info("Executing query '" + query_name + "'...")
        self._logger.debug(" Query:\n" + query + "\n")
        query_results_file_name = self._output_folder + "/" + query_name + ".csv"
        query_results_file = self._gateway.jvm.java.io.File(query_results_file_name)
        output_format = self._gateway.jvm.org.apache.jena.riot.Lang.CSV
        self._query_operation.runQuery(self._dataset, query, query_results_file, output_format)
        self._logger.info("...done")
        return pd.read_csv(query_results_file_name)

    def do_query_from_file(self, query_file_path, query_name='user_query'):
        """
        Execute the query in the specified file against the loaded ontology

        Parameters
        ----------
        query_file_path: str
            Absolute path to a SPARQL query file
        query_name : str
            Name of the query to be included in the output query results file

        Returns
        ----------
        df
            Data frame containing the query results
        """
        query = self._load_query(query_file=query_file_path, built_in=False)
        return self.do_query(query=query, query_name=query_name)

    def biomarkers_for_all_cell_types(self):
        query = self._load_query('biomarkers_for_all_cell_types.rq')
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types.__name__)

    def biomarkers_for_all_cell_types_in_anatomical_structure(self, anatomical_structure=_DEFAULT_ANATOMICAL_STRUCTURE):
        query = self._load_query('biomarkers_for_all_cell_types_in_anatomical_structure.rq')
        query = re.sub(r'\?anatomical_structure\b', anatomical_structure, query)
        return self.do_query(query, query_name=self.biomarkers_for_all_cell_types_in_anatomical_structure.__name__)

    def biomarkers_for_cell_type_in_anatomical_structure(self, cell_type=_DEFAULT_CELL_TYPE,
                                                         anatomical_structure=_DEFAULT_ANATOMICAL_STRUCTURE):
        query = self._load_query('biomarkers_for_cell_type_in_anatomical_structure.rq')
        query = re.sub(r'\?cell_type\b', cell_type, query)
        query = re.sub(r'\?anatomical_structure\b', anatomical_structure, query)
        return self.do_query(query, query_name=self.biomarkers_for_cell_type_in_anatomical_structure.__name__)

    # TODO refactor to obtain tissues that collide with parts of the anatomical structure
    def tissue_blocks_in_anatomical_structure(self, anatomical_structure="obo:UBERON_0000948"):
        query = self._load_query('tissue_blocks_in_anatomical_structure.rq')
        query = re.sub(r'\?anatomical_structure\b', anatomical_structure, query)
        return self.do_query(query, query_name=self.tissue_blocks_in_anatomical_structure.__name__)

    # TODO location of anatomical structure (filler of 'collides_with) is currently represented as a string literal
    def tissue_block_count_for_all_anatomical_structures(self):
        query = self._load_query('tissue_block_count_for_all_anatomical_structures.rq')
        return self.do_query(query, query_name=self.tissue_block_count_for_all_anatomical_structures.__name__)

    def anatomical_structures_in_tissue_block(self, tissue_block=_DEFAULT_TISSUE_BLOCK):
        query = self._load_query('anatomical_structures_in_tissue_block.rq')
        query = re.sub(r'\?tissue_block\b', tissue_block, query)
        return self.do_query(query, query_name=self.anatomical_structures_in_tissue_block.__name__)

    def locations_of_all_cell_types(self):
        query = self._load_query('locations_of_all_cell_types.rq')
        return self.do_query(query, query_name=self.locations_of_all_cell_types.__name__)

    def evidence_for_specific_cell_type(self, cell_type=_DEFAULT_CELL_TYPE):
        query = self._load_query('evidence_for_specific_cell_type.rq')
        query = re.sub(r'\?cell_type\b', cell_type, query)
        return self.do_query(query, query_name=self.evidence_for_specific_cell_type.__name__)

    def evidence_for_all_cell_types(self):
        query = self._load_query('evidence_for_all_cell_types.rq')
        return self.do_query(query, self.evidence_for_all_cell_types.__name__)

    def cell_types_from_biomarkers(self, biomarkers=_DEFAULT_BIOMARKERS):
        query = self._load_query('cell_types_from_biomarkers.rq')
        query = re.sub(r'\?biomarkers\b', biomarkers, query)
        return self.do_query(query, query_name=self.cell_types_from_biomarkers.__name__)

    @staticmethod
    def _logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
