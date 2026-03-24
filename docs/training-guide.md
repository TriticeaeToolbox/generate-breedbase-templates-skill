# Comprehensive Training Guide: Generating Breedbase Upload Templates

## Overview
Transform breeder-provided trial data (various formats) into three standardized upload templates:
1. **Accessions template** - Variety/germplasm metadata
2. **Trials template** - Plot-level trial structure
3. **Observations template** - Trait measurements per plot

## Core Concepts

### Required Resources
- **Column definition files**: Define required/optional columns for accessions and trials templates
  - `assets/upload-template-column-definitions/accessions-template-column-definitions.csv`
  - `assets/upload-template-column-definitions/traits-template-column-definitions.csv`

- **Trait ontologies**: OBO format files with trait definitions and IDs (CO_350:XXXXXXX)
  - `assets/trait-ontologies/oat.txt` (~300KB)
  - `assets/trait-ontologies/barley.txt`
  - `assets/trait-ontologies/wheat.txt`

- **Trait abbreviations**: Maps common abbreviations to full trait names
  - `assets/trait_abbreviations.xlsx`

### Three Output Templates

#### 1. Accessions Template
Unique list of all varieties/accessions tested.

**Required columns:**
- `accession_name` - Unique variety/selection/line name
- `species_name` - Genus and species (e.g., "Avena sativa" for oats)

**Common optional columns:**
- `purdy pedigree` - Pedigree string (e.g., "FEMALE/MALE" or complex crosses)
- `female_parent` - Female parent accession name (auto-created if doesn't exist)
- `male_parent` - Male parent accession name (auto-created if doesn't exist)
- `description`, `population_name`, `organization_name`, `synonym`, etc.

**Key logic:**
- Extract unique accessions across all input files
- Parse pedigrees to extract parents when possible
- Determine species from trial description/metadata (e.g., "Oat Trial" → Avena sativa)

#### 2. Trials Template
Plot-level metadata for each experimental unit.

**Required columns:**
- `trial_name` - Unique across database (format: `{PROGRAM}_{YEAR}_{LOCATION}`)
- `breeding_program` - Program name (must exist in database)
- `location` - Location name (must exist in database)
- `year` - Trial year (integer)
- `design_type` - Experimental design (RCBD, CRD, Alpha, etc.)
- `description` - Free text description
- `accession_name` - Variety being tested
- `plot_number` - Sequential plot number
- `block_number` - Block number (use 1 if not designed)
- `plot_name` - Unique plot ID (auto-generate if missing)

**Common optional columns:**
- `plot_width`, `plot_length`, `field_size`
- `planting_date`, `harvest_date` (YYYY-MM-DD format) - **IMPORTANT to include if found**
- `trial_type` - e.g., "phenotyping_trial"
- `is_a_control` - 1 if control, 0 otherwise
- `rep_number` - Replicate number
- `row_number`, `col_number` - Grid coordinates (important for field maps)
- `entry_number` - Trial-specific entry number

**Key logic:**
- `plot_name` auto-generated as: `{trial_name}-PLOT_{plot_number}`
- Multiple replicate plots can exist for same accession
- Start plot numbers at 101, 201, etc. by block
- Block numbers start at 1

#### 3. Observations Template
Trait measurements with ontology IDs.

**Column format:** `{trait_name} - {description}|{ONTOLOGY_ID}`
- Example: `"Grain yield - g/m2|CO_350:0000260"`

**First column:** `observationunit_name` - Links to `plot_name` from trials template

**Key logic:**
- Each row represents one plot
- Columns are trait variables with standardized units
- Empty cells for missing data
- All trait values converted to ontology units

## Input Data Format Patterns

### Format 1: Multi-Sheet Excel with Location Sheets
**Example:** Sample 1 (UWOYT)

**Structure:**
- "Overall" summary sheets with pedigrees and means
- Location-specific sheets with trait data
- Some sheets have full metadata (title, cooperator, plot size), others are simple tables

**Parsing approach:**
1. Identify location sheets (vs. overall summary sheets)
2. For each location sheet:
   - Extract title row to get trial description
   - Find header row (contains trait names)
   - Find units row (contains units like "bu/A", "lb/bu", "Julian")
   - Extract data rows (Entry, Name/Variety, trait values...)
3. Extract pedigrees from "Overall" sheets
4. Generate trials for each location × accession combination

**Common traits:**
- Yield (bu/A), TW/Test Weight (lb/bu), Heading (Julian), Height (in or cm)
- Lodging (0-9), Growth Habit (0-9), Disease ratings (0-9, %)

### Format 2: Multiple Files (One per Location)
**Example:** Sample 2 (SDS Oat Trials)

**Structure:**
- Separate .xlsx file for each location
- Each file has "Cover" sheet (metadata) and "Page 2" (data)
- Table format with variety names and yearly yields

**Parsing approach:**
1. Process each file separately
2. Extract location from filename or Cover sheet
3. Parse data table on "Page 2":
   - Row with trait names (Height, Lodging, Test Wt, etc.)
   - Rows with variety names and values
4. Create separate trial for each location
5. Handle multi-year data (2019, 2020, 2021 yields) - use most recent year or create separate trials

**Common traits:**
- Height (in), Lodging (1-5), Test Wt (lbs), Yield by year (bu/a)

### Format 3: CSV Already Standardized
**Example:** Sample 3 (UEOPN)

**Structure:**
- CSV with trial structure columns already present
- Columns include: trial_name, breeding_program, location, year, design_type, accession_name, plot_number, block_number, etc.
- Followed by trait measurement columns

**Parsing approach:**
1. Read CSV directly
2. Split columns into:
   - Trial structure (matches trials template columns)
   - Trait measurements (everything else)
3. Extract accessions from accession_name column
4. Map trait columns to ontology terms
5. Convert units as needed

**Common traits:**
- heading_date, plant_height_cm, Crown_rust_severity_%, lodging_severity_1to5
- grain_yield_g/sqm, test_weight_lb/bu, groat_percent, protein%, betaglucan%, oil%
- Kernel measurements (WK_Length_Average, WK_Width_Average, WK_Area_Average, etc.)

### Format 4: Simple Single-Sheet Excel
**Example:** Sample 4 (Davis)

**Structure:**
- Single sheet with simple table
- Row 1: Trait names
- Row 2: Units
- Data rows: Entry, Variety/Selection, trait values

**Parsing approach:**
1. Identify header rows (trait names, units)
2. Parse data rows starting after headers
3. Extract entry numbers and variety names
4. Map traits and units to ontology terms
5. Trial metadata may need to be inferred or provided separately

**Common traits:**
- Mean Yield (kg/ha), Heading (Date Mean), Plant Height (inches)
- test weight (lb./bu.), Protein/Fiber/Fat % (Dry Basis)

### Format 5: Multi-Rep Excel with Formulas
**Example:** Sample 5 (EON)

**Structure:**
- Complex headers spanning multiple rows
- Individual replicate columns (Rep 1, Rep 2, Rep 3)
- Calculated mean columns (may contain Excel formulas)
- Pedigree information included
- Multiple dates per plot (for different reps)

**Parsing approach:**
1. Parse complex multi-row headers
2. Identify replicate structure
3. Extract variety names and pedigrees
4. Calculate means if formulas present (or use provided means)
5. Handle date variations (average or use first date)
6. Create plots for each rep or summary plots

**Common traits:**
- Grain Yield in Kg/plot (by rep), Heading Date (multiple dates), Observations (notes)

## Unit Conversions

### Critical Conversions

#### Yield
- **bu/A → g/m²:** Multiply by **3.586715** (oats specific)
- **kg/ha → g/m²:** Divide by **10** (universal: 1 ha = 10,000 m²)

#### Test Weight (Grain Density)
- **lb/bu → g/L:** Multiply by **12.871981** (≈ 12.87)

#### Height
- **inches → cm:** Multiply by **2.54**

#### Dates
- **Date → Julian day:** Extract day of year (1-365/366)
  - Use `.timetuple().tm_yday` for Python datetime
  - January 1 = day 1

#### No Conversion Needed
- **Percentages (%):** Stay as-is
- **Rating scales (0-9, 1-5, etc.):** Stay as-is
- **Counts and ratios:** Stay as-is

### Conversion Reference Table
| Input Unit | Output Unit | Conversion Factor | Notes |
|------------|-------------|-------------------|-------|
| bu/A (oats) | g/m² | × 3.586715 | Oat-specific |
| kg/ha | g/m² | ÷ 10 | Universal |
| lb/bu | g/L | × 12.871981 | Test weight |
| inches | cm | × 2.54 | Height |
| Date | Julian day | day of year | 1-365/366 |
| % | % | 1 | No conversion |
| 0-9 rating | 0-9 rating | 1 | No conversion |

## Trait Ontology Matching

### Process
1. **Identify trait name** from input data (may be abbreviated)
2. **Identify input unit** from data or header
3. **Look up in trait abbreviations file** if abbreviated
4. **Search ontology file** for matching trait
5. **Find variable term** with matching units (CO_350:XXXXXXX)
6. **Build column header:** `{trait_name} - {description}|{ONTOLOGY_ID}`

### Common Trait Mappings (Oats - CO_350 Ontology)

#### Core Agronomic Traits
| Input Trait | Common Units | Ontology Term | Ontology ID | Output Unit |
|-------------|--------------|---------------|-------------|-------------|
| Yield, GrYie, Grain Yield | bu/A, kg/ha, g/m² | Grain yield - g/m2 | CO_350:0000260 | g/m² |
| TW, Test Weight, Test Wt | lb/bu, g/L | Test weight - g/L | CO_350:0000259 | g/L |
| HD, Heading, Heading Date | Julian, Date, days | Heading date - Julian day | CO_350:0000270 | Julian day |
| HT, Height, Plant Height | inches, cm | Plant height - cm | CO_350:0000232 | cm |

#### Disease and Stress
| Input Trait | Common Units | Ontology Term | Ontology ID | Output Unit |
|-------------|--------------|---------------|-------------|-------------|
| Lodging | 0-9, 1-5, % | Lodging severity - 0-9 Rating | CO_350:0005007 | 0-9 |
| Lodging Incidence | % | Lodging incidence - percent | CO_350:0000165 | % |
| Crown Rust | 0-9, % | Crown rust severity (plot) - 0-9 Rating | CO_350:0005030 | 0-9 |
| Crown Rust (%) | % | Crown rust severity - percent | CO_350:0000516 | % |
| Stem Rust | 0-9, % | Stem rust severity (plot) - 0-9 Rating | CO_350:0005046 | 0-9 |
| Leaf Blotch | 0-9 | Leaf blotch severity - 0-9 disease severity scale | CO_350:0000174 | 0-9 |
| BYDV, Barley Yellow Dwarf | 0-9 | Barley yellow dwarf virus severity - 0-9 Rating | CO_350:0005011 | 0-9 |
| Winter Stress | 0-9 | Winter stress severity - 0-9 Rating | CO_350:0005003 | 0-9 |
| Freeze Damage | 0-9 | Freeze damage severity - 0-9 Rating | CO_350:0005001 | 0-9 |

#### Morphological Traits
| Input Trait | Common Units | Ontology Term | Ontology ID | Output Unit |
|-------------|--------------|---------------|-------------|-------------|
| Growth Habit | 0-9 | Growth habit - 0-9 Rating | CO_350:0005052 | 0-9 |
| Snapback | 1-9 | Snapback - 1-9 snapback scale | CO_350:0000217 | 1-9 |

#### Quality Traits
| Input Trait | Common Units | Ontology Term | Ontology ID | Output Unit |
|-------------|--------------|---------------|-------------|-------------|
| Protein, Grain Protein | % | Grain protein content - percent | CO_350:0000161 | % |
| Groat Protein | % | Groat protein content - percent | CO_350:0000164 | % |
| Fiber, Dietary Fiber | % | Dietary fiber content - total - percent | CO_350:0000158 | % |
| Fat, Lipid, Oil | % | Lipid content - percent | CO_350:0000574 | % |
| Groat Oil | % | Groat oil content - percent | CO_350:0000163 | % |
| Beta-glucan, Betaglucan | % | Beta-glucan content - dry weight basis - percent | CO_350:0000156 | % |
| Groat %, Groat Content | % | Groat content (machine dehulled) - percent | CO_350:0000162 | % |
| TKW, 1000 Kernel Weight | g | Thousand grain weight - g | CO_350:0000251 | g |
| Plump (5.5/64) | % | Grain plumpness - 5.5/64 plump - % | CO_350:0005051 | % |
| Mid (5.0/64) | % | Grain plumpness - 5.0/64 plump - % | CO_350:0005049 | % |
| Thins (<5.0/64) | % | Grain plumpness - 5.0/64 thin - % | CO_350:0005050 | % |

#### Kernel Measurements
| Input Trait | Common Units | Ontology Term | Ontology ID | Output Unit |
|-------------|--------------|---------------|-------------|-------------|
| WK_Length_Average | mm | Whole kernel average length - mm | CO_350:0005115 | mm |
| WK_Width_Average | mm | Whole kernel average width - mm | CO_350:0005116 | mm |
| WK_LW_Ratio_Average | mm/mm | Whole kernel average length/width ratio - mm/mm | CO_350:0005117 | mm/mm |
| WK_Area_Average | mm² | Whole kernel average area - mm2 | CO_350:0005118 | mm² |
| WK_Perimeter_Average | mm | Whole kernel average perimeter - mm | CO_350:0005119 | mm |

### Ontology File Structure (OBO Format)
```
[Term]
id: CO_350:0000260
name: Grain yield - g/m2
namespace: oat_trait_variable
def: "TRAIT: Total weight of grains harvested per unit area. METHOD: Measurement of the total weight of whole grains harvested per unit area. SCALE: g/m2" []
relationship: variable_of CO_350:0000006
relationship: variable_of CO_350:0000007
```

**Key components:**
- `id`: The ontology ID to use in column headers
- `name`: The exact trait name with units
- `namespace`: Use `*_trait_variable` terms (not `*_trait_trait` or `*_trait_method`)
- `def`: Definition including trait, method, and scale

## Species Determination

### Common Species
- **Oats:** Avena sativa
- **Barley:** Hordeum vulgare
- **Wheat:** Triticum aestivum

### Detection Methods
1. Look for keywords in trial name/description:
   - "Oat" → Avena sativa
   - "Barley" → Hordeum vulgare
   - "Wheat" → Triticum aestivum
2. Check filename patterns
3. Use appropriate ontology file (oat.txt, barley.txt, wheat.txt)

## Trial Naming Conventions

### Observed Patterns
- `{PROGRAM}_{YEAR}_{LOCATION}` (e.g., "UWOYT_2021_BelleMina")
- `{PROGRAM}-{CROP}-{YEAR}-{LOCATION}` (e.g., "SDS-OAT-2021-BATH")
- `{PROGRAM}_{YEAR}_{LOCATION}` (e.g., "UEOPN_2023_Davis")

### Location Name Formatting
- Remove spaces for trial name (e.g., "Belle Mina, AL" → "BelleMina")
- Keep original format for location column (e.g., "Belle Mina, AL")

### Breeding Program Examples
- "Uniform Winter Oat Yield Nursery" (UWOYT)
- "Uniform Oat Performance Nursery" (UEOPN)
- "SDS" (South Dakota State)

## Implementation Workflow

### Step-by-Step Process
1. **Identify input format** - Determine which pattern matches
2. **Extract metadata** - Trial name, location, year, breeding program
3. **Parse accessions** - Build unique list with pedigrees
4. **Build trials structure** - Create plot-level records
5. **Match traits to ontology** - Find IDs and standardize names
6. **Convert units** - Apply conversion factors
7. **Build observations** - Link trait values to plots
8. **Validate** - Check required fields, unique IDs
9. **Export** - Write three .xls/.xlsx files

### Validation Checks
- All required columns present
- No duplicate accession_names
- No duplicate plot_names
- All plot_names in observations exist in trials
- All trait columns have ontology IDs
- Date formats correct (YYYY-MM-DD)
- Numeric fields are numeric
- Trial design types valid (RCBD, CRD, Alpha, etc.)

### Common Issues & Solutions
1. **Missing pedigrees** - Leave parent columns empty
2. **Multiple date formats** - Convert all to YYYY-MM-DD
3. **Ambiguous trait names** - Check abbreviations file
4. **No block design** - Use block_number = 1
5. **Missing plot numbers** - Generate sequentially (101, 102, 103...)
6. **Formulas in cells** - Calculate or extract computed values
7. **Multiple reps** - Create separate plots for each rep
8. **Multi-year data** - Focus on primary year or create separate trials

## Output File Formats
- All outputs can be .xls or .xlsx
- Use descriptive filenames:
  - `output_{N}_accessions.xls`
  - `output_{N}_trials.xls`
  - `output_{N}_observations.xls`
- Include headers as first row
- No empty columns between data columns
- Missing data represented as empty cells (not "NA" or null text)

## Summary Checklist
- [ ] Identify crop/species
- [ ] Parse all input files/sheets
- [ ] Extract unique accessions with pedigrees
- [ ] Generate trial names and metadata
- [ ] Create plot-level records with unique plot_names
- [ ] Match all traits to ontology terms
- [ ] Convert all units to standard scales
- [ ] Build observations with ontology IDs in headers
- [ ] Validate required fields and uniqueness
- [ ] Export three template files
