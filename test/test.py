import sys
import hubmapy
import traceback
import pandas as pd

EXPECTED_RESULTS_FOLDER = "expected-output/"
CURRENT_RESULTS_FOLDER = "current-output/"

AS_BONE_MARROW = 'obo:UBERON_0002371'
AS_LUNG = 'obo:UBERON_0002048'
CT_MEMORY_B_CELL = 'obo:CL_0000787'
CT_DENDRITIC_CELL = 'obo:CL_0002394'  # CD141-positive myeloid dendritic cell
TB_LUNG = '<https://gtexportal.org/home/tissue/Lung#MTissueBlocks>'


def read_query_results(query_file_name):
    return pd.read_csv(EXPECTED_RESULTS_FOLDER + query_file_name + ".csv")


def test_biomarkers_for_all_cell_types(query_engine):
    return _test_df_equality(
        query_engine.biomarkers_for_all_cell_types(),
        query_engine.biomarkers_for_all_cell_types.__name__)


def test_biomarkers_for_all_cell_types_in_anatomical_structure(query_engine):
    return _test_df_equality(
        query_engine.biomarkers_for_all_cell_types_in_anatomical_structure(anatomical_structure=AS_BONE_MARROW),
        query_engine.biomarkers_for_all_cell_types_in_anatomical_structure.__name__)


def test_biomarkers_for_cell_type_in_anatomical_structure(query_engine):
    return _test_df_equality(
        query_engine.biomarkers_for_cell_type_in_anatomical_structure(cell_type=CT_MEMORY_B_CELL,
                                                                      anatomical_structure=AS_BONE_MARROW),
        query_engine.biomarkers_for_cell_type_in_anatomical_structure.__name__)


def test_tissue_blocks_in_anatomical_structure(query_engine):
    return _test_df_equality(
        query_engine.tissue_blocks_in_anatomical_structure(anatomical_structure=AS_LUNG),
        query_engine.tissue_blocks_in_anatomical_structure.__name__)


def test_tissue_block_count_for_all_anatomical_structures(query_engine):
    return _test_df_equality(
        query_engine.tissue_block_count_for_all_anatomical_structures(),
        query_engine.tissue_block_count_for_all_anatomical_structures.__name__)


def test_anatomical_structures_in_tissue_block(query_engine):
    return _test_df_equality(
        query_engine.anatomical_structures_in_tissue_block(tissue_block=TB_LUNG),
        query_engine.anatomical_structures_in_tissue_block.__name__)


def test_locations_of_all_cell_types(query_engine):
    return _test_df_equality(
        query_engine.locations_of_all_cell_types(),
        query_engine.locations_of_all_cell_types.__name__)


def test_evidence_for_specific_cell_type(query_engine):
    return _test_df_equality(
        query_engine.evidence_for_specific_cell_type(cell_type=CT_DENDRITIC_CELL),
        query_engine.evidence_for_specific_cell_type.__name__)


def test_evidence_for_all_cell_types(query_engine):
    return _test_df_equality(
        query_engine.evidence_for_all_cell_types(),
        query_engine.evidence_for_all_cell_types.__name__)


def test_cell_types_from_biomarkers(query_engine):
    return _test_df_equality(
        query_engine.cell_types_from_biomarkers(),
        query_engine.cell_types_from_biomarkers.__name__)


def _test_df_equality(df, query_file_name):
    expected_df = read_query_results(query_file_name=query_file_name)
    try:
        pd.testing.assert_frame_equal(df, expected_df, check_names=False, check_like=True)
        return True
    except AssertionError:
        print("Test of query '" + query_file_name + "' FAILED!")
        print(traceback.format_exc())
        return False


def run_tests():
    """Checks whether the instantiated HuBMAPy module returns the same query results as the baseline expected results"""
    hubmap = hubmapy.HuBMAPy(output_folder=CURRENT_RESULTS_FOLDER)
    test_results = [test_biomarkers_for_all_cell_types(query_engine=hubmap),
                    test_biomarkers_for_all_cell_types_in_anatomical_structure(query_engine=hubmap),
                    test_biomarkers_for_cell_type_in_anatomical_structure(query_engine=hubmap),
                    test_tissue_blocks_in_anatomical_structure(query_engine=hubmap),
                    test_tissue_block_count_for_all_anatomical_structures(query_engine=hubmap),
                    test_anatomical_structures_in_tissue_block(query_engine=hubmap),
                    test_locations_of_all_cell_types(query_engine=hubmap),
                    test_evidence_for_specific_cell_type(query_engine=hubmap),
                    test_evidence_for_all_cell_types(query_engine=hubmap),
                    test_cell_types_from_biomarkers(query_engine=hubmap)]
    count_true = sum(test_results)
    print(str(count_true) + " / " + str(len(test_results)) + " tests passed")


def perform_queries():
    """Performs all queries to set a new baseline for expected query results"""
    hubmap = hubmapy.HuBMAPy(output_folder=EXPECTED_RESULTS_FOLDER)
    hubmap.biomarkers_for_all_cell_types()
    hubmap.biomarkers_for_all_cell_types_in_anatomical_structure(anatomical_structure=AS_BONE_MARROW)
    hubmap.biomarkers_for_cell_type_in_anatomical_structure(cell_type=CT_MEMORY_B_CELL,
                                                            anatomical_structure=AS_BONE_MARROW)
    hubmap.tissue_blocks_in_anatomical_structure(anatomical_structure=AS_LUNG)
    hubmap.tissue_block_count_for_all_anatomical_structures()
    hubmap.anatomical_structures_in_tissue_block(tissue_block=TB_LUNG)
    hubmap.locations_of_all_cell_types()
    hubmap.evidence_for_specific_cell_type(cell_type=CT_DENDRITIC_CELL)
    hubmap.evidence_for_all_cell_types()
    hubmap.cell_types_from_biomarkers()


if __name__ == '__main__':
    if "-q" in sys.argv:
        # perform all queries to set a new baseline for expected query results
        perform_queries()

    if "-t" in sys.argv:
        # run all tests to check whether this version of HuBMAPy outputs the expected query results
        run_tests()
