import hubmapy

if __name__ == '__main__':
    hubmap = hubmapy.HuBMAPy()

    df_1 = hubmap.biomarkers_for_all_cell_types()
    print(df_1.head())

    # df_2 = query.biomarkers_for_all_cell_types_in_anatomical_structure(anatomical_structure='obo:UBERON_0002371')  # bone marrow
    # df_3 = query.biomarkers_for_cell_type_in_anatomical_structure(cell_type='obo:CL_0000787', anatomical_structure='obo:UBERON_0002371')  # memory B cell, bone marrow
    # df_4 = query.tissue_blocks_in_anatomical_structure(anatomical_structure='obo:UBERON_0002048')
    # df_5 = query.tissue_block_count_for_all_anatomical_structures()
    # df_6 = query.anatomical_structures_in_tissue_block(tissue_block='obo:UBERON_0002371')
    # df_7 = query.locations_of_all_cell_types()
    # df_8 = query.evidence_for_specific_cell_type(cell_type='obo:CL_0002394')  # i.e., publication DOIs
    # df_9 = query.evidence_for_all_cell_types()
