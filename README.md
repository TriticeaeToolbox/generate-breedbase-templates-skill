# Generate Breedbase Templates

This repository provides tools for converting raw breeding trial data into standardized [Breedbase](https://breedbase.org/) upload templates. It includes both an [Agent Skill](https://agentskills.io) for AI-assisted conversion and standalone Python functions for direct programmatic use.

> [!WARNING]
> As with any AI-generated or automated output, the generated upload templates should be thoroughly checked for mistakes and errors before uploading to the database.

## Features

✨ **Format Agnostic** - Handles diverse input formats without hard-coded assumptions
- Multi-sheet Excel files
- Multi-file datasets
- Pre-structured CSV files
- Simple Excel spreadsheets
- Complex multi-replicate designs

🎯 **Automated Matching** - Intelligent trait and ontology mapping
- Automatic trait-to-ontology matching using fuzzy logic
- Unit detection and conversion
- Abbreviation expansion
- Support for oat, barley, and wheat ontologies

🔧 **Flexible Usage** - Multiple ways to use the tools
- AI Agent Skill for interactive conversion
- Standalone Python functions for scripting
- Command-line interface for batch processing

## Two Ways to Use

### Option 1: Agent Skill (AI-Assisted)

Use the AI agent skill for interactive, guided template generation with custom script creation.

**Installation** (for [Claude Code](https://code.claude.com/)):

```bash
mkdir -p ~/.claude/skills/generate-breedbase-templates
git clone https://github.com/TriticeaeToolbox/generate-breedbase-templates-skill.git ~/.claude/skills/generate-breedbase-templates
```

**Usage:**

1. Create a directory with your raw breeder data: `~/data/`
2. Navigate to the directory: `cd ~/data/`
3. Start Claude Code: `claude`
4. Run the skill: `/generate-breedbase-templates`

**Output:**
- `upload_templates/` - Breedbase template files (accessions, trials, observations)
- `bin/` - Custom Python scripts tailored to your data format
- `process.sh` - Shell script to regenerate templates

### Option 2: Standalone Python Functions

Use the Python functions directly in your own scripts or workflows.

**Installation:**

```bash
git clone https://github.com/TriticeaeToolbox/generate-breedbase-templates-skill.git
cd generate-breedbase-templates-skill
pip install -r requirements.txt
```

**Usage:**

```python
from generate_accessions import generate_accessions_template
from generate_trials import generate_trials_template
from generate_observations import generate_observations_template

# Generate all three templates
accessions_df = generate_accessions_template(
    input_folder='./data/input',
    output_path='./output/accessions.xls'
)

trials_df = generate_trials_template(
    input_folder='./data/input',
    output_path='./output/trials.xls',
    breeding_program='UWOYT',
    year=2021
)

observations_df = generate_observations_template(
    input_folder='./data/input',
    output_path='./output/observations.xls',
    assets_folder='./assets',
    species='oat'
)
```

**Command Line:**

```bash
# Generate accessions template
python generate_accessions.py ./data/input ./output/accessions.xls

# Generate trials template
python generate_trials.py ./data/input ./output/trials.xls --program=UWOYT --year=2021

# Generate observations template
python generate_observations.py ./data/input ./output/observations.xls --assets=./assets --species=oat
```

**See also:**
- [`USAGE.md`](USAGE.md) - Comprehensive usage guide for Python functions
- [`example_usage.py`](example_usage.py) - Complete working example
- [`IMPLEMENTATION.md`](IMPLEMENTATION.md) - Technical implementation details

## Generated Templates

The tool generates three Breedbase-compatible templates:

### 1. Accessions Template
Unique varieties/accessions with metadata
- Required: `accession_name`, `species_name`
- Optional: `purdy pedigree`, `female_parent`, `male_parent`, etc.

### 2. Trials Template
Plot-level trial structure
- Trial naming: `{PROGRAM}_{YEAR}_{LOCATION}`
- Plot naming: `{trial_name}-PLOT_{plot_number}`
- Includes experimental design, blocks, reps, field positions

### 3. Observations Template
Trait measurements with ontology IDs
- Column format: `{Trait name} - {unit}|{ONTOLOGY_ID}`
- Example: `Grain yield - g/m2|CO_350:0000260`
- Automatic unit conversion (bu/A → g/m², lb/bu → g/L, etc.)

## Supported Input Formats

The system automatically detects and handles:

1. **Multi-sheet Excel** - Overall summary + location sheets
2. **Multi-file Excel** - Cover page + data sheets per location
3. **Pre-structured CSV** - Already contains trial structure columns
4. **Simple Excel** - Trait names + units + data rows
5. **Multi-rep Excel** - Complex headers with replicate columns

See sample datasets in `assets/sample-datasets/` for examples.

## Unit Conversions

Automatic conversions for common breeding traits:

| Input Unit | Output Unit | Conversion | Trait |
|------------|-------------|------------|-------|
| bu/A (oats) | g/m² | × 3.586715 | Grain yield |
| kg/ha | g/m² | ÷ 10 | Grain yield |
| lb/bu | g/L | × 12.871981 | Test weight |
| inches | cm | × 2.54 | Plant height |
| Date | Julian day | Day of year | Heading date |

## Requirements

- Python 3.7+
- pandas >= 1.3.0
- openpyxl >= 3.0.0

## Documentation

- **[USAGE.md](USAGE.md)** - Detailed usage guide for Python functions
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture and design
- **[references/training-guide.md](references/training-guide.md)** - Comprehensive format patterns and examples

## Project Structure

```
generate-breedbase-templates-skill/
├── README.md                          # This file
├── USAGE.md                           # Python function usage guide
├── IMPLEMENTATION.md                  # Technical implementation details
├── requirements.txt                   # Python dependencies
│
├── generate_accessions.py             # Generate accessions template
├── generate_trials.py                 # Generate trials template
├── generate_observations.py           # Generate observations template
├── generate_breedbase_templates.py    # Main generator class
│
├── trait_matcher.py                   # Trait-to-ontology matching
├── unit_converter.py                  # Unit conversion utilities
├── example_usage.py                   # Complete usage example
│
├── assets/                            # Reference data
│   ├── trait-ontologies/              # OBO ontology files
│   │   ├── oat.txt
│   │   ├── barley.txt
│   │   └── wheat.txt
│   ├── trait_abbreviations.xlsx       # Trait abbreviation mappings
│   ├── upload-template-column-definitions/
│   └── sample-datasets/               # Example datasets
│       ├── sample-1/
│       ├── sample-2/
│       ├── sample-3/
│       ├── sample-4/
│       └── sample-5/
│
└── references/                        # Documentation
    └── training-guide.md              # Comprehensive format guide
```

## Contributing

Contributions are welcome! Areas for improvement:
- Additional species/crop ontologies
- New input format handlers
- Unit conversion additions
- Documentation improvements

## License

[Specify license]

## Support

For questions or issues:
- Open an issue on GitHub
- See documentation in `USAGE.md` and `IMPLEMENTATION.md`
- Review sample datasets in `assets/sample-datasets/`
