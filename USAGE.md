
# Breedbase Template Generator - Usage Guide

This package provides Python functions to generate Breedbase upload templates from diverse breeding trial data formats.

## Overview

Three main standalone functions generate the required templates:

1. **`generate_accessions_template()`** - Extracts unique varieties/accessions
2. **`generate_trials_template()`** - Creates plot-level trial structure
3. **`generate_observations_template()`** - Maps trait measurements to ontology terms

## Installation

Required packages:
```bash
pip install pandas openpyxl
```

## Quick Start

### Generate All Three Templates

```python
from generate_accessions import generate_accessions_template
from generate_trials import generate_trials_template
from generate_observations import generate_observations_template

# Input folder containing Excel/CSV files
input_folder = './data/input'

# Generate templates
accessions_df = generate_accessions_template(
    input_folder=input_folder,
    output_path='./output/accessions.xls'
)

trials_df = generate_trials_template(
    input_folder=input_folder,
    output_path='./output/trials.xls',
    program='University of Wisconsin Oat Yield Trial',
    experiment_code='UWOYT',
    year=2021
)

observations_df = generate_observations_template(
    input_folder=input_folder,
    output_path='./output/observations.xls',
    assets_folder='./assets',
    species='oat'
)
```

## Function Details

### 1. Generate Accessions Template

```python
def generate_accessions_template(input_folder: str, output_path: str = None) -> pd.DataFrame
```

**Purpose:** Extract unique accessions (varieties, lines, selections) from trial data.

**Parameters:**
- `input_folder` (str, required): Path to folder containing input files
- `output_path` (str, optional): Path to save output file (.xls, .xlsx, or .csv)

**Returns:** DataFrame with columns:
- `accession_name` (required)
- `species_name` (required)
- `purdy pedigree` (optional)
- `female_parent` (optional)
- `male_parent` (optional)
- `population_name` (optional)
- `organization_name` (optional)
- Other optional columns as found in data

**Example:**
```python
accessions_df = generate_accessions_template(
    input_folder='./data/trial_data',
    output_path='./output/accessions.xls'
)

print(f"Generated {len(accessions_df)} unique accessions")
```

**Features:**
- Automatically detects accession name column (variety, name, selection, etc.)
- Extracts pedigree information if available
- Parses female/male parents from pedigree strings
- Detects species from file content or metadata
- Removes duplicate accessions

---

### 2. Generate Trials Template

```python
def generate_trials_template(
    input_folder: str,
    output_path: str = None,
    program: str = 'PROGRAM',
    experiment_code: str = None,
    year: int = None
) -> pd.DataFrame
```

**Purpose:** Create plot-level trial structure with metadata for each experimental unit.

**Parameters:**
- `input_folder` (str, required): Path to folder containing input files
- `output_path` (str, optional): Path to save output file
- `program` (str, default='PROGRAM'): Breeding program name (used in breeding_program column)
- `experiment_code` (str, default=same as program): Code used in trial and plot names
- `year` (int, default=current year): Trial year

**Returns:** DataFrame with columns:
- `trial_name` (required) - Format: `{PROGRAM}_{YEAR}_{LOCATION}`
- `breeding_program` (required)
- `location` (required)
- `year` (required)
- `design_type` (required, default='RCBD')
- `description` (required)
- `accession_name` (required)
- `plot_number` (required)
- `block_number` (required)
- `plot_name` (required) - Format: `{trial_name}-PLOT_{plot_number}`
- `entry_number` (optional)
- `rep_number` (optional)
- `row_number` (optional)
- `col_number` (optional)

**Example:**
```python
trials_df = generate_trials_template(
    input_folder='./data/trial_data',
    output_path='./output/trials.xls',
    program='University of Wisconsin Oat Yield Trial',
    experiment_code='UWOYT',
    year=2021
)

print(f"Generated {len(trials_df)} plots across {trials_df['trial_name'].nunique()} trials")
```

**Command Line Usage:**
```bash
python generate_trials.py ./data/input ./output/trials.xls --program='UW Oat Trial' --code=UWOYT --year=2021
```

**Features:**
- Generates unique trial names per location
- Auto-generates plot names if not present
- Extracts entry numbers, reps, blocks, field positions
- Handles multiple files and sheets
- Detects pre-structured data formats

---

### 3. Generate Observations Template

```python
def generate_observations_template(
    input_folder: str,
    output_path: str = None,
    assets_folder: str = None,
    species: str = 'oat'
) -> pd.DataFrame
```

**Purpose:** Extract trait measurements and map to ontology terms with automatic unit conversion.

**Parameters:**
- `input_folder` (str, required): Path to folder containing input files
- `output_path` (str, optional): Path to save output file
- `assets_folder` (str, default='./assets'): Path to folder with ontologies and trait definitions
- `species` (str, default='oat'): Species for ontology matching ('oat', 'barley', 'wheat')

**Returns:** DataFrame with columns:
- `observationunit_name` (first column) - Links to `plot_name` from trials
- Trait columns with format: `"{Trait name} - {unit}|{ONTOLOGY_ID}"`
  - Example: `"Grain yield - g/m2|CO_350:0000260"`

**Example:**
```python
observations_df = generate_observations_template(
    input_folder='./data/trial_data',
    output_path='./output/observations.xls',
    assets_folder='./assets',
    species='oat'
)

trait_count = len(observations_df.columns) - 1
print(f"Generated {len(observations_df)} observations with {trait_count} traits")
```

**Command Line Usage:**
```bash
python generate_observations.py ./data/input ./output/observations.xls --assets=./assets --species=oat
```

**Features:**
- Matches trait names to ontology IDs using fuzzy matching
- Handles abbreviations (e.g., 'HD' → 'Heading date')
- Automatic unit conversion:
  - bu/A → g/m² (yield)
  - lb/bu → g/L (test weight)
  - inches → cm (height)
  - Date → Julian day
- Detects units from column names or separate unit rows
- Maps synonyms and variant trait names

---

## Supported Input Formats

The functions automatically detect and handle multiple formats:

### Format 1: Multi-Sheet Excel (Overall + Locations)
```
input_1.xlsx
├── Overall_Yield (summary)
├── Overall_TW (summary)
├── BelleMina (location data)
├── Brooksville (location data)
└── ...
```

### Format 2: Multi-File Excel (Cover + Page 2)
```
input_2_location1.xlsx
├── Cover (metadata)
└── Page 2 (data)

input_2_location2.xlsx
├── Cover
└── Page 2
```

### Format 3: Pre-Structured CSV
```
trial_name,location,year,accession_name,plot_number,trait1,trait2,...
TRIAL_2021_LOC1,Location1,2021,Variety1,101,45.2,32.1,...
```

### Format 4: Simple Excel (Trait Names + Units)
```
Row 1: Entry | Variety | Yield | Height | ...
Row 2: -     | -       | bu/A  | inches | ...
Row 3: 1     | Var1    | 85.2  | 36.5   | ...
```

### Format 5: Multi-Rep Excel
```
Complex headers with Rep 1, Rep 2, Rep 3 columns
Pedigree information included
Multiple dates per plot
```

## Assets Required

The `assets/` folder should contain:

```
assets/
├── trait-ontologies/
│   ├── oat.txt          # Oat trait ontology (CO_350)
│   ├── barley.txt       # Barley trait ontology
│   └── wheat.txt        # Wheat trait ontology
├── trait_abbreviations.xlsx
└── upload-template-column-definitions/
    ├── accessions-template-column-definitions.csv
    └── traits-template-column-definitions.csv
```

## Unit Conversions

The observations generator automatically converts units:

| Input Unit | Output Unit | Conversion | Notes |
|------------|-------------|------------|-------|
| bu/A (oats) | g/m² | × 3.586715 | Yield |
| kg/ha | g/m² | ÷ 10 | Yield |
| lb/bu | g/L | × 12.871981 | Test weight |
| inches | cm | × 2.54 | Height |
| Date | Julian day | Day of year (1-365) | Dates |
| % | % | 1 | No conversion |
| 0-9 rating | 0-9 rating | 1 | No conversion |

## Common Trait Mappings (Oats)

| Input Trait | Ontology ID | Output Format |
|-------------|-------------|---------------|
| Yield, GrYie | CO_350:0000260 | Grain yield - g/m2\|CO_350:0000260 |
| TW, Test Weight | CO_350:0000259 | Test weight - g/L\|CO_350:0000259 |
| HD, Heading | CO_350:0000270 | Heading date - Julian day\|CO_350:0000270 |
| HT, Height | CO_350:0000232 | Plant height - cm\|CO_350:0000232 |
| Lodging | CO_350:0005007 | Lodging severity - 0-9 Rating\|CO_350:0005007 |
| Crown Rust | CO_350:0005030 | Crown rust severity (plot) - 0-9 Rating\|CO_350:0005030 |
| Protein % | CO_350:0000161 | Grain protein content - percent\|CO_350:0000161 |

## Troubleshooting

### "No accessions found"
- Check that input files contain variety/accession name columns
- Verify column headers are in first few rows
- Ensure data rows are not empty

### "Could not match trait to ontology"
- Check species parameter matches your data ('oat', 'barley', 'wheat')
- Verify assets_folder path is correct
- Add trait abbreviations to `trait_abbreviations.xlsx`

### "Unit conversion failed"
- Check that input units are recognizable (bu/A, lb/bu, inches, etc.)
- Verify data contains numeric values, not text
- Review unit detection in column names

### Files not detected
- Ensure files have .xlsx, .xls, or .csv extensions
- Check file permissions
- Verify input_folder path is correct

## Advanced Usage

### Using the Main Generator Class

For more control, use the `BreedbaseTemplateGenerator` class:

```python
from generate_breedbase_templates import BreedbaseTemplateGenerator

generator = BreedbaseTemplateGenerator(
    input_folder='./data/input',
    assets_folder='./assets'
)

# Generate all templates at once
accessions, trials, observations = generator.generate_all_templates(
    output_folder='./output'
)

# Access parsed data
print(f"Parsed {len(generator.all_accessions)} accession records")
print(f"Parsed {len(generator.all_trials)} trial records")
print(f"Parsed {len(generator.all_observations)} observation records")
```

### Custom Trait Matching

```python
from trait_matcher import TraitMatcher

matcher = TraitMatcher(assets_folder='./assets')

# Match a single trait
match = matcher.match_trait(
    trait_name='Yield',
    unit='bu/A',
    species='oat'
)

print(f"Matched to: {match['ontology_id']}")
print(f"Full name: {match['full_name']}")
print(f"Target unit: {match['unit']}")
```

### Custom Unit Conversion

```python
from unit_converter import UnitConverter

converter = UnitConverter()

# Convert single value
yield_gm2 = converter.convert_value(85.2, 'bu/A', 'g/m2')
print(f"85.2 bu/A = {yield_gm2:.2f} g/m²")

# Convert date
julian_day = converter.date_to_julian('2021-06-15')
print(f"June 15 = day {julian_day}")

# Convert series
import pandas as pd
heights_cm = converter.convert_trait_column(
    pd.Series([32.5, 35.1, 29.8]),
    from_unit='inches',
    to_unit='cm'
)
```

## Example Workflow

Complete workflow from input to output:

```python
import os
from pathlib import Path

# Setup paths
project_dir = Path('./breedbase_project')
input_dir = project_dir / 'input'
output_dir = project_dir / 'output'
assets_dir = Path('./assets')

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Generate all templates
from generate_accessions import generate_accessions_template
from generate_trials import generate_trials_template
from generate_observations import generate_observations_template

print("Step 1: Generating accessions template...")
accessions = generate_accessions_template(
    str(input_dir),
    str(output_dir / 'accessions.xls')
)

print("\nStep 2: Generating trials template...")
trials = generate_trials_template(
    str(input_dir),
    str(output_dir / 'trials.xls'),
    program='University of Wisconsin Oat Yield Trial',
    experiment_code='UWOYT',
    year=2021
)

print("\nStep 3: Generating observations template...")
observations = generate_observations_template(
    str(input_dir),
    str(output_dir / 'observations.xls'),
    assets_folder=str(assets_dir),
    species='oat'
)

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Accessions:   {len(accessions):4d} unique varieties")
print(f"Trials:       {len(trials):4d} plots across {trials['trial_name'].nunique()} trials")
print(f"Observations: {len(observations):4d} plot observations")
print(f"Traits:       {len(observations.columns)-1:4d} traits measured")
print(f"\nOutput files saved to: {output_dir}/")
```

## Questions?

For more information, see:
- `training-guide.md` - Comprehensive training on format patterns
- `README.md` - Project overview
- Sample datasets in `assets/sample-datasets/`
