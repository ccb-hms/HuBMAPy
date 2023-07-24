# HuBMAPy

A package to interact with the [HuBMAP Human Reference Atlas Ontology](https://github.com/hubmapconsortium/ccf-ontology). The package can be used to perform ontology queries programmatically or through a command-line interface.

## Installation

Clone the repository:
```
git clone https://github.com/ccb-hms/HuBMAPy.git
```

Install package using **pip** on the cloned repository folder:

```
pip3 install .
```

## Command Line Interface

`hubmapy -q QUERY [-o OUTPUT] [-n NAME]`

To display a help message with descriptions of tool arguments do:

`hubmapy -h` or `hubmapy --help`

### Required arguments
`-q QUERY` Input query file containing a single SPARQL query.

### Optional arguments

`-o OUTPUT` Path to output folder for the query results files.

`-n NAME`   Name of the query, to be included in the generated query results file.

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

Additionally, it is possible to perform arbitrary queries specified by users:
```
df = hubmap.do_query_from_file(query_file_path='...')
```

where `query_file_path` is an absolute path to a SPARQL query file. Or:

```
df = hubmap.do_query(query='...', query_name='...')
```
where `query` is a string containing a SPARQL query.


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
* cell_types_from_biomarkers(**biomarkers**=`[hgnc:633,hgnc:800]`)

## Dependencies

* ROBOT v1.8.3 (https://github.com/ontodev/robot)
* CCF Ontology v2.0.0-alpha.18 (https://github.com/hubmapconsortium/ccf-ontology)
