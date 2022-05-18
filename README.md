# HuBMAPy

A package to query the HuBMAP Human Reference Atlas Ontology. The package can be used programmatically or through a command-line interface.

## Installation

Install package using **pip** on the cloned repository folder:

```
pip3 install .
```

## Command Line Interface

`hubmapy -q QUERY [-o OUTPUT] [-n NAME] [-r]`

To display a help message with descriptions of tool arguments do:

`hubmapy -h` or `hubmapy --help`

### Required arguments
`-q QUERY` Input query file containing a single SPARQL query.

### Optional arguments

`-o OUTPUT` Path to output folder for the query results files.

`-n NAME`   Name of the query, to be included in the generated query results file.

`-r SAVE_REASONED_ONTOLOGY`   Save the ontology with its inferred axioms after reasoning.

## Programmatic Usage

Import the HuBMAPy library:

```
import hubmapy
```

Then use as follows:

```
hubmap = hubmapy.HuBMAPy()
```

From here various built-in queries can be performed, for example:

```
df = hubmap.biomarkers_for_all_cell_types()
```

where `df` is a data frame containing the query results.

Additionally, it is possible to perform user-specified queries as follows:
```
df = hubmap.do_user_query(query_file_path='...')
```

where `query_file_path` is an absolute path to a SPARQL query file.

## Built-in Queries

The package supports the following built-in queries:

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