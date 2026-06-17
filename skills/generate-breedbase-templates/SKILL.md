---
name: generate-breedbase-templates
description: Generate breedbase upload templates from a set of breeder-provided data
allowed-tools: Bash(mkdir:*) Bash(python:*) Bash(python3:*) Read
---

## Overview

This skill is used to reformat spreadsheet files (Excel or CSV files) that contain trial data from plant breeders in arbitrary formats into standardized templates used to upload into a plant breeding database, Breedbase. Use the trial data provided by the user to generate 3 different upload templates:
1) **accessions** = metadata about the breeding germplasm / lines / accessions
2) **trials** = metadata about the trials to observe the germplasm and the plots within the trials
3) **observations** = data from the trait observations recorded in each plot.

## Training Documentation

The `references/` directory contains comprehensive training documentation based on analysis of all sample datasets:

### [training-guide.md](references/training-guide.md)
**Complete implementation reference** covering:
- Three output templates (accessions, trials, observations) detailed specifications
- Five input format patterns with parsing strategies for each
- Complete unit conversion reference table with formulas
- Trait ontology matching guide with 30+ common trait mappings
- Step-by-step implementation workflow from parsing to export
- Validation checks, common issues, and solutions

**Use this for**: Complete implementation reference, understanding conversion formulas, trait ontology lookups

### [sample-analysis.md](references/sample-analysis.md)
**Detailed input→output transformations** for all 5 sample datasets:
- **Sample 1 (UWOYT)**: Multi-sheet Excel with location-specific data - shows how to parse location sheets and extract pedigrees from overall sheets
- **Sample 2 (SDS)**: Multiple files (one per location) - demonstrates handling multi-file inputs with Cover + data sheets
- **Sample 3 (UEOPN)**: Pre-structured CSV format - example of already-standardized data with 21 quality traits
- **Sample 4 (Davis)**: Simple single-sheet format - basic table structure with date conversions
- **Sample 5 (EON)**: Multi-rep structure with pedigrees - complex multi-row headers and replicate handling

Each sample includes: input structure breakdown, output examples, specific conversions applied, and key patterns.

**Use this for**: Understanding how different input formats map to outputs, seeing real conversion examples

### [quick-reference.md](references/quick-reference.md)
**Concise cheat sheet** with:
- Critical conversion factors
- Most common trait ontology IDs
- Naming patterns for trials and plots
- Resource file locations
- Workflow summary

**Use this for**: Quick lookups during implementation, reference for common conversions and IDs

## Assets

The `assets` directory contains resources that you can use to learn how to generate the breedbase upload templates, such as:
- `sample-datasets/` - sample datasets already converted into upload templates
- `upload-template-column-definitions/` - definitions of the column headers for the accessions and trials upload templates, including which columns are required and which columns are recommended (these columns should be included if there are values for them in the original data).
- `trait-ontologies/` - trait ontology definitions.  This contains .obo files for the trait ontologies for wheat, oat, and barley.


### Sample Datasets

The `assets/sample-datasets` directory contains 5 sample datasets that have been correctly formatted into upload templates.  The files in the input subdirectory of each sample dataset includes the raw breeder data that need to be converted.  The output subdirectory of each sample dataset contains the correctly formatted accessions, trials, and observations upload templates for that set of input data. The relevant data might be in more than one file, for example, divided by location or experiment.  It is also possible for a single file to have multiple tabs.  You must use all the tabs that have relevant data.  Each input dataset enables you to generate the three upload templates for accessions, trials, and observations.  Use these sample datasets to train yourself on how to properly generate the required upload templates.

### Upload Template Column Definitions

The `assets/upload-templates-column-definitions` directory contains files with the column header definitions for the accessions and trials upload templates.

The accessions template columns are defined in the `accessions-template-column-definitions.csv` file. The trials template columns are defined in the `trials-template-column-definitions.csv` file.  These files define the names of the column headers, descriptions of the data contained in each column, and whether or not the column is required in the template.

Columns marked as required must be in the generated upload template and must have a value for each row.  If an optional column does not have any data, it can be removed from the upload template.

### Trait Ontology Definitions

The `assets/trait-ontologies` directory contains trait ontology .txt files for wheat, barley, and oats. These .txt files contain the official ontology trait names. A trait ontology file is a plain-text file that contains the ontology terms in [Term] blocks.  Each of the traits recorded by the breeder should be associated with a single ontology variable term.  A variable term is defined by having a 'variable_of' relationship in the ontology file.  The column headers in the observations upload template should include both the trait name and id of the variable term in the ontology. The column header should follow the format of "name|id". For example, the wheat grain yield trait would be formatted as "Grain yield - kg/ha|CO_321:0001218".

The `assets/trait_abbreviations.xlsx` file contains common abbreviations that breeders might use for trait names - there is one worksheet for each crop. These abbreviations might be found in the breeder data, but should be converted to the full trait ontology name when generating the observations template.

## Accessions Upload Template

Sometimes an accession name synonym will be in parentheses in the data - this should be removed from the `accession_name` in the upload template and added to the `synonym` column (which can contain multiple synonyms separated by a comma).

Sometimes the data will include summary statistics (such as mean, average, standard deviation, SD, CV, or LSD) at the bottom of the table. Summary statistics should not be included in the templates.

Always include pedigree information when available - often a Purdy pedigree string in the format of FEMALE/MALE parents, where "FEMALE" and "MALE" are the accession names of the female and male parents.  When a Purdy pedigree string is provided in the excel file, parse simple FEMALE/MALE parents (that only include a single /) into the separate parent names and include them as `female_parent` and `male_parent` in the accession template and set the `cross_type` to "biparental".

## Trials Upload Template

The `trial_name` should include an experiment code (or breeding program abbreviation), year, and town name from the location in the format "experiment_year_location" (each component separated by a '_' with no spaces).  If you don't know the experiment code, ask the user to provide one.  For example, a Mississippi Valley Barley Nursery trial from 2018 with a location of Fargo, ND should have the trial_name set to "MVBN_2018_Fargo".

The `plot_name` should include the `trial_name` and the `plot_number` in the format of "trial_name-PLOT_plot_number".  For example, plot 101 from trial MVBN_2018_Fargo should have the plot_name "MVBN_2018_Fargo-PLOT_101".

Use the plot numbers provided in the breeder data.  If the breeder data does not provide plot numbers, start the first plot with plot number 1 if there is only 1 rep of plots.  If there are multiple reps of plots, use plot numbers 101, 102, ... in the first rep, 201, 202, ... in the second rep, etc.

## Observations Upload Template

The observations template should have at least two columns. The first column, labeled `observationunit_name` should include the plot name used in the `plot_name` column in the trials template. Then, there should be one column added for each trait observed in the trial. The trait column header should include the official ontology trait name for the observed trait. There should be one row for each plot and one column for each trait.

In the breeder data, sometimes a trait name in one column spans multiple rows.  The first row might include the trait name (or an abbreviation for the trait name) and the second row might include the units or scale used to record the trait.   For example, the word “Kernel” might be in the cell above the words “Weight (mg)”.  In that case, interpret those two cells together as indicating a single trait.  Merge up to three rows of one column to get the full trait name.  Implement this multi-row header propagation to ensure trait names retain their full meaning in ontology mapping. Be careful that when you do this propagation that the resulting trait makes sense.  For example, “Protein rowed” doesn’t make sense.

Sometimes it is not clear what scale the breeder data is in for a trait - in that case look at the trait values in the column to try to determine the scale.  For example, lodging might be on a 0-9 rating scale or a 0-100 percentage scale - if there are values greater than 9, then it is likely using the percentage scale.

Sometimes heading date or maturity date might be recorded as the number of days from a specific reference date. For example, if the data indicates that 5/31=0, then May 31st is the reference date and the trait data is the number of days from this reference day and the data should be converted into the Julian day.

If the breeder trait data is using a different scale than the scale defined in the trait ontology term, convert the trait values to the ontology scale before adding the value to the observations template. The scale used in a trait ontology term is defined in the trait name.  For example, the trait ontology term for grain yield is "Grain Yield - kg/ha" and the scale is "kg/ha".  When converting yields, it is important to use the correct weight for the crop - barley is 48 pounds per bushel, oats are 32 pounds per bushel, and wheat is 60 pounds per bushel.

When generating the observations template, return a mapping of the trait names used in the breeder data to the ontology trait names used as column headers in the observation template.  If you are unsure of which trait ontology term to use for each breeder trait, you should ask the user to confirm the match.  Always indicate which trait values have been converted from the units of the breeder data to the units of the ontology term.  Include the formula used for any conversions that are made and double-check to make sure the conversion formula is correct.

## Output

The final output should always include the generated accessions, trials, and observations templates as .csv files and save them to an `upload_templates` subdirectory.

Any scripts used to generate the upload templates should be stored in a `bin` subdirectory.  Always include a `process.sh` bash script in the `bin` directory that can be used to reprocess the data and regenerate the upload template files.