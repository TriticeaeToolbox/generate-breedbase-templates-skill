# Breedbase Template Generation - Quick Reference

## Comprehensive Training Guide
See `training-guide.md` for complete documentation including:
- Detailed format patterns for all 5 sample datasets
- Full unit conversion reference table
- Complete trait ontology mapping guide
- Step-by-step implementation workflow

## Key Quick Facts

### Three Templates Required
1. **Accessions**: Unique varieties (accession_name, species_name + pedigree)
2. **Trials**: Plot-level structure (trial_name, location, year, plot_number, etc.)
3. **Observations**: Trait measurements (observationunit_name + trait columns with ontology IDs)

### Critical Conversions (Oats)
- Yield: bu/A × 3.586715 = g/m² | kg/ha ÷ 10 = g/m²
- Test Weight: lb/bu × 12.871981 = g/L
- Height: inches × 2.54 = cm
- Dates: Convert to Julian day (1-365)

### Common Trait IDs (CO_350 Oat Ontology)
- Grain yield - g/m2: CO_350:0000260
- Test weight - g/L: CO_350:0000259
- Heading date - Julian day: CO_350:0000270
- Plant height - cm: CO_350:0000232
- Lodging severity - 0-9 Rating: CO_350:0005007
- Crown rust severity (plot) - 0-9 Rating: CO_350:0005030
- Grain protein content - percent: CO_350:0000161

### Species Names
- Oats: Avena sativa
- Barley: Hordeum vulgare
- Wheat: Triticum aestivum

### Trial Naming Pattern
`{PROGRAM}_{YEAR}_{LOCATION}` (e.g., UWOYT_2021_BelleMina)

### Plot Naming Pattern
`{trial_name}-PLOT_{plot_number}` (e.g., UWOYT_2021_BelleMina-PLOT_101)

### Key Resources Locations
- Column definitions: `assets/upload-template-column-definitions/`
- Trait ontologies: `assets/trait-ontologies/` (oat.txt, barley.txt, wheat.txt)
- Trait abbreviations: `assets/trait_abbreviations.xlsx`
- Sample datasets: `assets/sample-datasets/sample-1` through `sample-5`

### Input Format Recognition
- **Multi-sheet Excel**: Overall + location sheets (Sample 1)
- **Multi-file Excel**: Cover + Page 2 per location (Sample 2)
- **Pre-structured CSV**: Has trial columns + trait columns (Sample 3)
- **Simple Excel**: Entry, Variety, traits (Sample 4)
- **Multi-rep Excel**: Rep columns + pedigree (Sample 5)

### Workflow Summary
1. Identify format → 2. Extract accessions → 3. Build trials → 4. Match traits to ontology → 5. Convert units → 6. Build observations → 7. Validate → 8. Export .csv/.xls files
