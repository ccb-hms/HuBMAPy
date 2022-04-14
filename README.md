# HuBMAPy

A package to perform queries against the HuBMAP Human Reference Atlas Ontology.

## Usage

Install package using **pip**:

```
pip3 install .
```

Import the HuBMAPy library:

```
import hubmapy
```

Then use as follows:

```
hubmap = hubmapy.HuBMAPy()
```

From here various queries can be performed, for example:

```
df = hubmap.biomarkers_for_all_cell_types()
```

where `df` is a data frame containing the query results.

## Supported Queries

Currently the library implements the following functions:

* biomarkers_for_all_cell_types()
* biomarkers_for_all_cell_types_in_anatomical_structure(**anatomical_structure**=`obo:UBERON_0002371`)  # bone marrow
* biomarkers_for_cell_type_in_anatomical_structure(**cell_type**=`obo:CL_0000787`, **anatomical_structure**=`obo:UBERON_0002371`)  # memory B cell, bone marrow
* tissue_blocks_in_anatomical_structure(**anatomical_structure**=`obo:UBERON_0002048`)
* tissue_block_count_for_all_anatomical_structures()
* anatomical_structures_in_tissue_block(**tissue_block**='...')
* locations_of_all_cell_types()
* evidence_for_specific_cell_type(**cell_type**=`obo:CL_0002394`)  # i.e., publication DOIs
* evidence_for_all_cell_types()

## Dependencies

* ROBOT v1.8.3 (https://github.com/ontodev/robot)
* CCF Ontology v2.0.0-alpha.11 (https://github.com/hubmapconsortium/ccf-ontology)