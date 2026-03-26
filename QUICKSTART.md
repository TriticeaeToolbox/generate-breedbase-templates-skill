# Quick Start Guide

Get started with Breedbase template generation in 5 minutes!

## Prerequisites

```bash
# Install required packages
pip install pandas openpyxl
```

## Option 1: Run the Example (Fastest)

```bash
# Clone the repository
git clone https://github.com/TriticeaeToolbox/generate-breedbase-templates-skill.git
cd generate-breedbase-templates-skill

# Run the example with sample data
python example_usage.py
```

This will process sample data and create `example_output/` with the three templates.

## Option 2: Process Your Data

### Step 1: Prepare Your Input

Create a folder with your trial data files (Excel or CSV):

```
my_data/
├── trial_2021_location1.xlsx
├── trial_2021_location2.xlsx
└── ...
```

### Step 2: Run the Generator

**Python Script:**

```python
from generate_accessions import generate_accessions_template
from generate_trials import generate_trials_template
from generate_observations import generate_observations_template

# Set your parameters
INPUT_FOLDER = './my_data'
OUTPUT_FOLDER = './output'
PROGRAM = 'University of Wisconsin Oat Yield Trial'
EXPERIMENT_CODE = 'UWOYT'  # Used in trial/plot names
YEAR = 2021
SPECIES = 'oat'  # or 'barley', 'wheat'

# Generate templates
accessions = generate_accessions_template(
    input_folder=INPUT_FOLDER,
    output_path=f'{OUTPUT_FOLDER}/accessions.xls'
)

trials = generate_trials_template(
    input_folder=INPUT_FOLDER,
    output_path=f'{OUTPUT_FOLDER}/trials.xls',
    program=PROGRAM,
    experiment_code=EXPERIMENT_CODE,
    year=YEAR
)

observations = generate_observations_template(
    input_folder=INPUT_FOLDER,
    output_path=f'{OUTPUT_FOLDER}/observations.xls',
    assets_folder='./assets',
    species=SPECIES
)

print(f"✓ Generated {len(accessions)} accessions")
print(f"✓ Generated {len(trials)} trial plots")
print(f"✓ Generated {len(observations)} observations")
```

**Or use Command Line:**

```bash
# Generate accessions
python generate_accessions.py ./my_data ./output/accessions.xls

# Generate trials
python generate_trials.py ./my_data ./output/trials.xls --program='UW Oat Trial' --code=UWOYT --year=2021

# Generate observations
python generate_observations.py ./my_data ./output/observations.xls --species=oat
```

### Step 3: Review and Upload

1. Open the generated files in `output/`
2. Verify the data looks correct
3. Upload to Breedbase

## Common Parameters

### `program`
Your breeding program full name (e.g., 'University of Wisconsin Oat Yield Trial')
Used in the `breeding_program` column of trials template.

### `experiment_code`
Short code for trial/plot naming (e.g., 'UWOYT', 'SDSUOAT', 'EON')
If omitted, uses same value as `program`.

### `year`
Trial year (e.g., 2021, 2022)

### `species`
- `'oat'` - Avena sativa
- `'barley'` - Hordeum vulgare
- `'wheat'` - Triticum aestivum

## Input File Requirements

Your files should have:

✅ **Accession names** - Column with variety/line names
- Can be named: 'Variety', 'Name', 'Selection', 'Accession', 'Line', etc.

✅ **Trait measurements** - Columns with trait data
- Can be any trait names (will be matched to ontology)

✅ **Optional but helpful:**
- Entry numbers
- Pedigree information
- Rep/block numbers
- Units in column headers or separate row

## Supported Formats

The tool automatically handles:

- ✅ Multi-sheet Excel files
- ✅ Multiple separate Excel files
- ✅ CSV files
- ✅ Pre-structured data with trial columns
- ✅ Simple tables with trait names and units
- ✅ Complex multi-replicate designs

**No format conversion needed** - just point it at your data!

## Troubleshooting

### "No accessions found"

**Problem:** Can't find variety/accession column

**Fix:** Make sure you have a column with names like:
- 'Variety', 'Name', 'Accession', 'Selection', 'Line', etc.

### "Could not match trait"

**Problem:** Trait name not recognized

**Fix:**
1. Check species parameter is correct (`oat`, `barley`, or `wheat`)
2. Make sure `assets/` folder is present
3. Common trait abbreviations should work (HD, TW, Yield, etc.)

### Wrong units

**Problem:** Values seem incorrect (e.g., very large or small numbers)

**Fix:**
1. Check that units are in column headers: `Yield (bu/A)` or `Height (inches)`
2. Or include a units row below headers
3. Common units are auto-detected and converted

## What Gets Generated

### 1. Accessions Template (`accessions.xls`)
- Unique list of all varieties tested
- Species information
- Pedigree data (if available)

### 2. Trials Template (`trials.xls`)
- One row per plot
- Trial names: `{PROGRAM}_{YEAR}_{LOCATION}`
- Plot names: `{trial_name}-PLOT_{plot_number}`
- Experimental design metadata

### 3. Observations Template (`observations.xls`)
- One row per plot
- Trait columns with ontology IDs
- Format: `"Grain yield - g/m2|CO_350:0000260"`
- Units automatically converted

## Next Steps

Once you have templates:

1. **Review the data** - Check for any errors or unexpected values
2. **Verify trait mappings** - Ensure traits matched correctly to ontology
3. **Upload to Breedbase** - Use the Breedbase upload wizard
4. **Save for re-use** - Templates can be regenerated if source data changes

## Get Help

- 📖 **Full documentation:** [`USAGE.md`](USAGE.md)
- 🔧 **Technical details:** [`IMPLEMENTATION.md`](IMPLEMENTATION.md)
- 💡 **Example code:** [`example_usage.py`](example_usage.py)
- 📊 **Sample data:** `assets/sample-datasets/`

## Tips

💡 **Start with small test files** - Verify the output before processing large datasets

💡 **Check the sample datasets** - See `assets/sample-datasets/` for format examples

💡 **Review trait mappings** - Observations template shows which ontology ID each trait mapped to

💡 **Use consistent naming** - Helps with automatic column detection

💡 **Include units** - Either in column names or a separate row

## That's It!

You're ready to generate Breedbase templates. The system handles the complexity of format detection, trait matching, and unit conversion automatically.

For more control and customization, see the full [`USAGE.md`](USAGE.md) guide.
