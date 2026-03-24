# Sample Dataset Analysis

Detailed analysis of all 5 sample datasets showing input → output transformations.

## Sample 1: UWOYT (Uniform Winter Oat Yield Trial) 2020-21

### Input Structure
- **File**: `input_1.xlsx`
- **Format**: Multi-sheet Excel with 14 sheets
- **Sheets**:
  - Summary sheets: Overall_Yield, Overall_TW, Overall_HD, Overall_Ht
  - Location sheets: BelleMina, Brooksville, Clayton, CollegeStation, McGregor, Plains, Raleigh, Salisbury, Quincy, Winnsboro_BatonRouge

### Location Sheet Structure (e.g., Winnsboro_BatonRouge)
```
Row 1: USDA-ARS Uniform Winter Oat Trial 2020-21 - Louisiana
Row 2: [blank], [blank], Yield, Rank, TW, Growth Habit, Heading, Lodging, BYDV, Crown rust, ...
Row 3: Entry, Name, bu/A, [blank], lb/bu, [blank], Julian, 0-9, 0-9, 0-9, ...
Row 4: 1, Gerard 224, 93.09, 3, 32.9, 4, 91.5, 1, [blank], 2.5, ...
Row 5: 2, FLLA09015SBS-U1, 74.92, 14, 31.15, 6, 89.75, 7.5, [blank], 2, ...
```

### Overall Sheet Structure (e.g., Overall_Yield)
```
Row 1: Entry, Name, Pedigree, Yield Rank, Overall Yield (bu/acre), BelleMina, Brooksville, ...
Row 2: 1, Gerard 224, Rodgers/Txab29923//Rodgers (=NC03-2421v), 4, 104.92, 96.68, 85.29, ...
```

### Output - Accessions Template
25 unique accessions extracted:
```csv
accession_name,species_name,purdy pedigree,female_parent,male_parent
Gerard 224,Avena sativa,Rodgers/Txab29923//Rodgers (=NC03-2421v),,
FLLA09015SBS-U1,Avena sativa,FL0210-J1/MN06023,FL0210-J1,MN06023
LA99016,Avena sativa,TX96M1385/SECTLA495,,
```

### Output - Trials Template
9 trials × 25 plots = 225 total plots:
```csv
trial_name,breeding_program,location,year,design_type,description,accession_name,plot_number,plot_name
UWOYT_2021_BelleMina,Uniform Winter Oat Yield Nursery,"Belle Mina, AL",2021,RCBD,2021 UWOYT @ Belle Mina,Gerard 224,101,UWOYT_2021_BelleMina-PLOT_101
UWOYT_2021_Winnsboro,Uniform Winter Oat Yield Nursery,"Winnsboro, LA",2021,RCBD,2021 UWOYT @ Winnsboro,Gerard 224,101,UWOYT_2021_Winnsboro-PLOT_101
```

### Output - Observations Template
13 trait columns (all CO_350 oat ontology):
```csv
observationunit_name,Grain yield - g/m2|CO_350:0000260,Test weight - g/L|CO_350:0000259,Heading date - Julian day|CO_350:0000270,...
UWOYT_2021_Winnsboro-PLOT_101,333.90,423.49,91.5,...
```

### Conversions Applied
- Yield: 93.09 bu/A × 3.586715 = 333.90 g/m²
- Test Weight: 32.9 lb/bu × 12.871981 = 423.49 g/L
- Heading: 91.5 Julian (no conversion)

---

## Sample 2: SDS Oat Variety Trials 2021

### Input Structure
- **Files**: 7 separate .xlsx files (one per location)
  - input_2_bath.xlsx, input_2_beresford.xlsx, input_2_brookings.xlsx,
  - input_2_pierre.xlsx, input_2_south_shore.xlsx, input_2_wall.xlsx, input_2_winner.xlsx
- **Format**: Each file has Cover sheet + Page 2 data sheet

### Data Sheet Structure (Page 2)
```
Row 1: Table 1. 2021 oat variety performance trial results (average of 4 replications) at Bath, SD.
Row 2: Entries are sorted by overall 3-year yield...
Row 3: Variety, Height (in), Lodging* (1-5), Test Wt (lbs), 2019 (bu/a), 2020 (bu/a), 2021 (bu/a), ...
Row 4: CS Camden, 25.25, 1, 30.4, 123.45, 180.19, 136.23, ...
Row 5: Deon, 23.25, 1, 33.475, 132, 182.29, 110.71, ...
```

### Output - Accessions Template
23 unique accessions:
```csv
accession_name,species_name
CS Camden,Avena sativa
Deon,Avena sativa
Warrior,Avena sativa
```

### Output - Trials Template
7 trials × ~23 plots each:
```csv
trial_name,breeding_program,location,year,design_type,description,accession_name,plot_number,plot_name
SDS-OAT-2021-BATH,SDS,Bath,2021,RCBD,SDS Oat Variety Trial 2021 @ Bath,CS Camden,101,SDS-OAT-2021-BATH-PLOT_101
```

### Output - Observations Template
4 trait columns + multi-year yields:
```csv
observationunit_name,Plant height - cm|CO_350:0000232,Lodging severity - 0-9 Rating|CO_350:0005007,Test weight - g/L|CO_350:0000259,Grain yield - g/m2|CO_350:0000260
SDS-OAT-2021-BATH-PLOT_101,64.135,1,391.35,488.51
```

### Conversions Applied
- Height: 25.25 in × 2.54 = 64.135 cm
- Test Weight: 30.4 lb/bu × 12.871981 = 391.35 g/L
- Yield (2021): 136.23 bu/A × 3.586715 = 488.51 g/m²
- Lodging: 1 (1-5 scale) → 1 (0-9 scale, no conversion needed)

---

## Sample 3: UEOPN (Uniform Early Oat Performance Nursery) 2022

### Input Structure
- **Files**: 3 CSV files
  - input_3_ueo.csv, input_3_mcon.csv, input_3_umo.csv
- **Format**: Already partially standardized with trial structure columns

### CSV Structure
```csv
trial_name,breeding_program,location,year,design_type,description,plot_name,accession_name,plot_number,block_number,rep_number,row_number,col_number,heading_date,plant_height_cm,Crown_rust_severity_%,grain_yield_g/sqm,test_weight _lb/bu,test_weight _g/L,groat_percent,thousand_kernel_weight_g,plump_%,groat_protein_%,groat_betaglucan_%,groat_oil_%,WK_Length_Average,WK_Width_Average,...
UEOPN_2022_Volga,SDS,Volga,2022,RCBD,UEOPN 2022 @ Volga,UEOPN_2022_Volga-PLOT_101,IL15-5752,101,1,1,1,1,2022-04-21,103.2,5.4,582.3,35.6,458.3,71.2,33.4,84.5,11.8,3.9,5.2,9.234,2.945,...
```

### Output - Accessions Template
~68 unique accessions per file

### Output - Trials Template
Directly maps trial structure columns from CSV

### Output - Observations Template
21 trait columns (most granular quality data):
```csv
observationunit_name,Heading date - Julian day|CO_350:0000270,Plant height - cm|CO_350:0000232,Crown rust severity - percent|CO_350:0000516,Snapback - 1-9 snapback scale|CO_350:0000217,Lodging severity - 0-9 Rating|CO_350:0005007,Grain yield - g/m2|CO_350:0000260,Test weight - g/L|CO_350:0000259,Groat content (machine dehulled) - percent|CO_350:0000162,Thousand grain weight - g|CO_350:0000251,Grain plumpness - 5.5/64 plump - %|CO_350:0005051,Grain plumpness - 5.0/64 plump - %|CO_350:0005049,Grain plumpness - 5.0/64 thin - %|CO_350:0005050,Groat protein content - percent|CO_350:0000164,Beta-glucan content - dry weight basis - percent|CO_350:0000156,Groat oil content - percent|CO_350:0000163,Whole kernel average length - mm|CO_350:0005115,Whole kernel average width - mm|CO_350:0005116,Whole kernel average length/width ratio - mm/mm|CO_350:0005117,Whole kernel average area - mm2|CO_350:0005118,Whole kernel average perimeter - mm|CO_350:0005119
UEOPN_2022_Volga-PLOT_101,112,103.2,5.4,,,582.3,458.3,71.2,33.4,84.5,,,11.8,3.9,5.2,9.234,2.945,3.135,23.699,26.981
```

### Conversions Applied
- Heading date: 2022-04-21 → Julian day 111 (April 21 = day 111 of year)
- Height: Already in cm (103.2 cm)
- Test weight: Data has both lb/bu (35.6) and g/L (458.3) - use g/L value
- Yield: Already in g/m² (582.3)
- Most quality traits: Already in correct units (%, g, mm)

---

## Sample 4: UEOPN (Davis) 2023

### Input Structure
- **File**: `input_4.xlsx`
- **Format**: Single sheet with simple table structure

### Sheet Structure
```
Row 1: [blank], [blank], Mean Yield, Heading, Plant Height, test weight, Protein %, Fiber %, Fat %, [blank], [blank], Rank
Row 2: Entry, Variety/Selection, kg/ha, Date Mean, (inches) Mean, lb./bu., Dry Basis, Dry Basis, Dry Basis, [blank], [blank], Entry
Row 3: 1, IL15-5271, 5120.0, 2023-05-04, 45.5, 41.54, 11.85, 13.0, 5.53, [blank], [blank], 29
Row 4: 2, IL15-5752, 5655.0, 2023-05-04, 46.125, 44.07, 10.18, 13.5, 4.94, [blank], [blank], 3
```

### Output - Accessions Template
29 accessions

### Output - Trials Template
Single trial with 29 plots:
```csv
trial_name,breeding_program,location,year,design_type,description,accession_name,plot_number,plot_name
UEOPN_2023_Davis,Uniform Oat Performance Nursery,"Davis, CA",2023,RCBD,Uniform Early Oat Performance Nursery,IL15-5271,101,UEOPN_2023_Davis-PLOT_101
```

### Output - Observations Template
6 trait columns (no yield - may not be in output):
```csv
observationunit_name,Heading date - Julian day|CO_350:0000270,Plant height - cm|CO_350:0000232,Test weight - g/L|CO_350:0000259,Grain protein content - percent|CO_350:0000161,Dietary fiber content - total - percent|CO_350:0000158,Lipid content - percent|CO_350:0000574
UEOPN_2023_Davis-PLOT_101,124,115.57,534.74,11.85,13.0,5.53
```

### Conversions Applied
- Heading: 2023-05-04 → Julian day 124 (May 4 = 31+28+31+30+4 = day 124)
- Height: 45.5 in × 2.54 = 115.57 cm
- Test weight: 41.54 lb/bu × 12.871981 = 534.74 g/L
- Protein/Fiber/Fat: No conversion (stay as %)
- Yield: 5120 kg/ha ÷ 10 = 512 g/m² (not included in observations output)

---

## Sample 5: EON (Early Oat Nursery) 2020-21

### Input Structure
- **File**: `input_5.xlsx`
- **Format**: Single sheet with multi-rep structure

### Sheet Structure
```
Row 1: EON 2020/21
Row 2: [blank], Number, Ori-, Variety, [blank], Grain Yield in Kg/plot, [blank], [blank], Grain, Observations, Heading  Date, [blank], [blank]
Row 3: [blank], of years, gin, or, Pedigree, Rep 1, Rep 2, Rep 3, Yield, [blank], [blank], [blank], [blank]
Row 4: [blank], in Nursery, [blank], Selection, [blank], [blank], [blank], [blank], Mean, [blank], [blank], [blank], [blank]
Row 5: EON 1, 3, IL, IL 14-7952, IL09-2756/IL05-11942, 2.415, 2.67, 1.535, =AVERAGE(F5:H5), Nice plot, 2021-04-16, 2021-04-16, 2021-04-17
Row 6: EON 2, new, IL, IL 14-4822, IL07-8273/Reins, 1.74, 1.905, 1.01, =AVERAGE(F6:H6), [blank], 2021-04-24, 2021-04-23, 2021-04-24
```

### Output - Accessions Template
23 accessions with pedigrees:
```csv
accession_name,species_name,purdy pedigree,female_parent,male_parent
IL 14-7952,Avena sativa,IL09-2756/IL05-11942,IL09-2756,IL05-11942
IL 14-4822,Avena sativa,IL07-8273/Reins,IL07-8273,Reins
```

### Output - Trials Template
Single trial with 69 plots (23 accessions × 3 reps):
```csv
trial_name,breeding_program,location,year,design_type,description,accession_name,plot_number,rep_number,plot_name
UEOPN_2021_Davis,Uniform Oat Performance Nursery,"Davis, CA",2021,RCBD,Uniform Early Oat Performance Nursery,IL 14-7952,101,1,UEOPN_2021_Davis-PLOT_101
UEOPN_2021_Davis,Uniform Oat Performance Nursery,"Davis, CA",2021,RCBD,Uniform Early Oat Performance Nursery,IL 14-7952,201,2,UEOPN_2021_Davis-PLOT_201
UEOPN_2021_Davis,Uniform Oat Performance Nursery,"Davis, CA",2021,RCBD,Uniform Early Oat Performance Nursery,IL 14-7952,301,3,UEOPN_2021_Davis-PLOT_301
```

### Output - Observations Template
3 trait columns:
```csv
observationunit_name,Grain yield - g/m2|CO_350:0000260,Heading date - Julian day|CO_350:0000270,Plant height - cm|CO_350:0000232
UEOPN_2021_Davis-PLOT_101,2415.0,106,,
UEOPN_2021_Davis-PLOT_201,2670.0,106,,
UEOPN_2021_Davis-PLOT_301,1535.0,107,,
```

### Conversions Applied
- Yield: Kg/plot values used directly (plot size not specified, so kept as provided)
  - Note: In reality, would need plot size to convert to g/m²
- Heading: 2021-04-16 → Julian day 106 (April 16 = 31+28+31+16 = day 106)
- Multiple dates per accession (one per rep) - averaged or used first date
- Height: Not provided in this dataset

---

## Key Patterns Across All Samples

### Consistent Elements
1. All use oat ontology (CO_350)
2. All convert to g/m² for yield, g/L for test weight, cm for height
3. All use Julian days for heading dates
4. Plot names follow {trial_name}-PLOT_{plot_number} format
5. Trial names include program/location/year

### Variable Elements
1. Input format varies widely (multi-sheet, multi-file, CSV, simple table, multi-rep)
2. Number of traits ranges from 3 (Sample 5) to 21 (Sample 3)
3. Some have pedigrees in input, others don't
4. Some have multiple reps, others don't
5. Some traits already standardized (Sample 3), others need full conversion

### Critical Success Factors
1. Correctly identify format pattern
2. Find and parse pedigree information when available
3. Match trait names to ontology (handling abbreviations, multi-row headers)
4. Apply correct conversion factors (species-specific for yield)
5. Generate unique, consistent naming for trials and plots
6. Link observations back to correct plots via observationunit_name
