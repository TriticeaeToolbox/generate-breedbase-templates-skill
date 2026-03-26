"""
Generate Observations Template

Standalone function to extract trait measurements from breeding trial data
and generate a Breedbase-compatible observations upload template with ontology IDs.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import openpyxl
import re

# Import helper modules
try:
    from trait_matcher import TraitMatcher
    from unit_converter import UnitConverter
except ImportError:
    print("Warning: trait_matcher or unit_converter not found. Using basic functionality.")
    TraitMatcher = None
    UnitConverter = None


def generate_observations_template(input_folder: str, output_path: str = None,
                                  assets_folder: str = None,
                                  species: str = 'oat') -> pd.DataFrame:
    """
    Generate observations template from input data folder

    Args:
        input_folder: Path to folder containing input data files
        output_path: Optional path to save output file
        assets_folder: Path to assets folder with ontologies (default: ./assets)
        species: Species name for ontology matching ('oat', 'barley', 'wheat')

    Returns:
        DataFrame with observations template in Breedbase format
        (columns have format: "Trait name - unit|ONTOLOGY_ID")
    """
    input_path = Path(input_folder)

    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_folder}")

    # Initialize trait matcher if available
    trait_matcher = None
    if TraitMatcher and assets_folder:
        try:
            trait_matcher = TraitMatcher(assets_folder)
        except Exception as e:
            print(f"Warning: Could not initialize TraitMatcher: {e}")

    # Initialize unit converter
    unit_converter = UnitConverter() if UnitConverter else None

    # Collect all observations from all files
    all_observations = []
    trait_metadata = {}  # Track trait names and units

    # Process all Excel and CSV files
    for file_path in input_path.glob('*'):
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            observations, traits = _extract_observations_from_excel(file_path)
            all_observations.extend(observations)
            trait_metadata.update(traits)
        elif file_path.suffix.lower() == '.csv':
            observations, traits = _extract_observations_from_csv(file_path)
            all_observations.extend(observations)
            trait_metadata.update(traits)

    if not all_observations:
        print("Warning: No observation data found in input files")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(all_observations)

    # Ensure observationunit_name is first column
    if 'observationunit_name' in df.columns:
        cols = ['observationunit_name'] + [c for c in df.columns if c != 'observationunit_name']
        df = df[cols]

    # Map trait columns to ontology terms
    if trait_matcher:
        df = _map_traits_to_ontology(df, trait_matcher, trait_metadata, species, unit_converter)

    # Save if output path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)

        print(f"Observations template saved to: {output_path}")

    trait_count = len([c for c in df.columns if c != 'observationunit_name'])
    print(f"Generated {len(df)} observations with {trait_count} traits")
    return df


def _extract_observations_from_excel(file_path: Path) -> Tuple[List[Dict], Dict]:
    """Extract observations from an Excel file"""
    observations = []
    trait_metadata = {}

    try:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        # Check format
        if 'Cover' in sheet_names and 'Page 2' in sheet_names:
            # Extract location from filename for plot naming
            location_match = re.search(r'_([a-z_]+)\.xlsx?$', file_path.name, re.I)
            location = location_match.group(1).replace('_', '').title() if location_match else "Unknown"

            df = pd.read_excel(file_path, sheet_name='Page 2')
            obs, traits = _extract_observations_from_dataframe(df, location, file_path.name)
            observations.extend(obs)
            trait_metadata.update(traits)

        else:
            # Process each sheet
            for sheet_name in sheet_names:
                if 'overall' in sheet_name.lower() or 'summary' in sheet_name.lower():
                    continue

                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    obs, traits = _extract_observations_from_dataframe(df, sheet_name, file_path.name)
                    observations.extend(obs)
                    trait_metadata.update(traits)
                except Exception as e:
                    print(f"  Warning: Could not process sheet '{sheet_name}': {e}")
                    continue

    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")

    return observations, trait_metadata


def _extract_observations_from_csv(file_path: Path) -> Tuple[List[Dict], Dict]:
    """Extract observations from a CSV file"""
    try:
        df = pd.read_csv(file_path)
        location = file_path.stem.replace('_', ' ').title()
        return _extract_observations_from_dataframe(df, location, file_path.name)
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return [], {}


def _extract_observations_from_dataframe(df: pd.DataFrame, location: str,
                                        source_file: str) -> Tuple[List[Dict], Dict]:
    """Extract observations from a DataFrame"""
    observations = []
    trait_metadata = {}

    if df.empty:
        return observations, trait_metadata

    # Check if pre-structured (has observationunit_name)
    if 'observationunit_name' in df.columns:
        return _extract_pre_structured_observations(df)

    # Find accession/variety column
    name_col = _find_column(df, ['accession_name', 'variety', 'name', 'selection'])

    if not name_col:
        return observations, trait_metadata

    # Check if there's a units row (common pattern)
    units_row = None
    header_row = None

    for idx in range(min(5, len(df))):
        row_str = ' '.join(str(v).lower() for v in df.iloc[idx] if pd.notna(v))
        if any(kw in row_str for kw in ['entry', 'variety', 'name']):
            header_row = idx
            # Check if next row has units
            if idx + 1 < len(df):
                next_row = df.iloc[idx + 1]
                if _looks_like_units_row(next_row):
                    units_row = idx + 1
            break

    # Re-read with proper header if needed
    if header_row is not None and header_row > 0:
        # This is already loaded, but we'd need to skip rows in practice
        pass

    # Identify trait columns (non-structural columns)
    structural_keywords = ['entry', 'name', 'variety', 'selection', 'pedigree',
                          'number', 'origin', 'years', 'plot', 'rep', 'block']

    trait_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if not any(kw in col_lower for kw in structural_keywords):
            trait_columns.append(col)

    # Extract units for traits
    if units_row is not None:
        for trait_col in trait_columns:
            col_idx = df.columns.get_loc(trait_col)
            unit = str(df.iloc[units_row, col_idx]) if pd.notna(df.iloc[units_row, col_idx]) else ''
            trait_metadata[trait_col] = {'unit': unit, 'original_name': trait_col}
    else:
        # Try to infer units from column names
        for trait_col in trait_columns:
            unit = _extract_unit_from_column_name(trait_col)
            trait_metadata[trait_col] = {'unit': unit, 'original_name': trait_col}

    # Generate plot naming components
    location_clean = location.replace(' ', '').replace('_', '')
    trial_name = f"PROGRAM_2021_{location_clean}"  # Will be overridden if better info available

    # Process each row
    plot_number = 101
    for idx, row in df.iterrows():
        # Skip units row
        if units_row is not None and idx == units_row:
            continue

        acc_name = row.get(name_col)

        # Skip if no accession name or header
        if pd.isna(acc_name) or not str(acc_name).strip():
            continue

        acc_name = str(acc_name).strip()

        # Skip header rows
        if any(kw in acc_name.lower() for kw in ['name', 'variety', 'entry']):
            continue

        # Build observation record
        plot_name = f"{trial_name}-PLOT_{plot_number}"

        # Check if plot_name column exists
        if 'plot_name' in df.columns and pd.notna(row['plot_name']):
            plot_name = row['plot_name']

        observation = {'observationunit_name': plot_name}

        # Extract trait values
        for trait_col in trait_columns:
            value = row.get(trait_col)
            if pd.notna(value):
                # Store with original column name (will be mapped later)
                observation[trait_col] = value

        if len(observation) > 1:  # Has more than just observationunit_name
            observations.append(observation)
            plot_number += 1

    return observations, trait_metadata


def _extract_pre_structured_observations(df: pd.DataFrame) -> Tuple[List[Dict], Dict]:
    """Extract observations from pre-structured data"""
    observations = []
    trait_metadata = {}

    # Identify trait columns (everything except observationunit_name and structural columns)
    structural_cols = ['observationunit_name', 'trial_name', 'plot_name', 'accession_name',
                      'plot_number', 'block_number', 'rep_number', 'entry_number']

    trait_columns = [c for c in df.columns if c not in structural_cols]

    # Build trait metadata
    for trait_col in trait_columns:
        unit = _extract_unit_from_column_name(trait_col)
        trait_metadata[trait_col] = {'unit': unit, 'original_name': trait_col}

    # Extract observations
    for idx, row in df.iterrows():
        observation = {'observationunit_name': row.get('observationunit_name', '')}

        for trait_col in trait_columns:
            if pd.notna(row.get(trait_col)):
                observation[trait_col] = row[trait_col]

        if len(observation) > 1:
            observations.append(observation)

    return observations, trait_metadata


def _map_traits_to_ontology(df: pd.DataFrame, trait_matcher: 'TraitMatcher',
                            trait_metadata: Dict, species: str,
                            unit_converter: 'UnitConverter') -> pd.DataFrame:
    """Map trait columns to ontology terms and convert units"""
    # Get trait columns (all except observationunit_name)
    trait_columns = [c for c in df.columns if c != 'observationunit_name']

    column_mapping = {}  # old_name -> new_name

    for trait_col in trait_columns:
        # Get metadata
        metadata = trait_metadata.get(trait_col, {})
        original_unit = metadata.get('unit', '')

        # Match to ontology
        match = trait_matcher.match_trait(trait_col, original_unit, species)

        if match:
            # Format new column name: "Trait name - unit|ONTOLOGY_ID"
            ontology_col = f"{match['description']}|{match['ontology_id']}"
            column_mapping[trait_col] = ontology_col

            # Convert units if needed
            target_unit = match.get('unit', '')
            if original_unit and target_unit and unit_converter:
                try:
                    df[trait_col] = df[trait_col].apply(
                        lambda x: unit_converter.convert_value(x, original_unit, target_unit)
                    )
                except Exception as e:
                    print(f"  Warning: Could not convert units for {trait_col}: {e}")

        else:
            # No match found, keep original name with unit if available
            if original_unit:
                column_mapping[trait_col] = f"{trait_col} - {original_unit}"
            # else keep original name

    # Rename columns
    df = df.rename(columns=column_mapping)

    return df


def _looks_like_units_row(row: pd.Series) -> bool:
    """Check if a row looks like it contains units"""
    non_null = row[pd.notna(row)]
    if len(non_null) < 2:
        return False

    # Check for common unit patterns
    unit_patterns = [r'bu/a', r'lb/bu', r'kg/ha', r'g/m', r'julian', r'inch',
                    r'cm', r'%', r'0-9', r'1-5', r'rating']

    matches = 0
    for val in non_null:
        val_str = str(val).lower()
        if any(re.search(p, val_str) for p in unit_patterns):
            matches += 1

    return matches >= len(non_null) * 0.5  # At least 50% look like units


def _extract_unit_from_column_name(column_name: str) -> str:
    """Extract unit from column name"""
    col = str(column_name).lower()

    # Look for units in parentheses
    paren_match = re.search(r'\(([^)]+)\)', col)
    if paren_match:
        return paren_match.group(1).strip()

    # Look for common patterns
    if 'bu/a' in col or 'bu_a' in col:
        return 'bu/A'
    elif 'kg/ha' in col or 'kg_ha' in col:
        return 'kg/ha'
    elif 'g/m2' in col or 'g_m2' in col:
        return 'g/m2'
    elif 'lb/bu' in col or 'lb_bu' in col:
        return 'lb/bu'
    elif 'g/l' in col or 'g_l' in col:
        return 'g/L'
    elif 'inch' in col:
        return 'inches'
    elif col.endswith('_cm') or ' cm' in col:
        return 'cm'
    elif 'julian' in col:
        return 'Julian day'
    elif 'percent' in col or col.endswith('%') or col.endswith('_pct'):
        return '%'
    elif 'rating' in col or '0-9' in col or '1-5' in col:
        return 'rating'

    return ''


def _find_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    """Find a column matching any of the keywords"""
    for col in df.columns:
        col_lower = str(col).lower().strip().replace('_', '').replace(' ', '')
        for keyword in keywords:
            keyword_clean = keyword.lower().replace('_', '').replace(' ', '')
            if keyword_clean in col_lower or col_lower in keyword_clean:
                return col
    return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_observations.py <input_folder> [output_file] [--assets=ASSETS_PATH] [--species=SPECIES]")
        print("\nExample:")
        print("  python generate_observations.py ./data/input ./output/observations.xls --assets=./assets --species=oat")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None

    # Parse optional arguments
    assets_folder = None
    species = 'oat'

    for arg in sys.argv[2:]:
        if arg.startswith('--assets='):
            assets_folder = arg.split('=')[1]
        elif arg.startswith('--species='):
            species = arg.split('=')[1]

    if not assets_folder:
        # Default to ./assets
        assets_folder = str(Path(__file__).parent / 'assets')

    print(f"Generating observations template from: {input_folder}")
    print(f"  Assets folder: {assets_folder}")
    print(f"  Species: {species}\n")

    df = generate_observations_template(input_folder, output_file, assets_folder, species)

    if not output_file:
        print("\nPreview (first 10 rows, first 5 columns):")
        preview_cols = df.columns[:min(5, len(df.columns))]
        print(df[preview_cols].head(10).to_string())
        print(f"\n... ({len(df)} rows × {len(df.columns)} columns)")
