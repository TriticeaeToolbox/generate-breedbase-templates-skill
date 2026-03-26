"""
Generate Trials Template

Standalone function to extract plot-level trial structure from breeding trial data
and generate a Breedbase-compatible trials upload template.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import openpyxl
import re


def generate_trials_template(input_folder: str, output_path: str = None,
                             program: str = 'PROGRAM',
                             experiment_code: str = None,
                             year: int = None) -> pd.DataFrame:
    """
    Generate trials template from input data folder

    Args:
        input_folder: Path to folder containing input data files
        output_path: Optional path to save output file
        program: Breeding program name for breeding_program column (default: 'PROGRAM')
        experiment_code: Code used in trial and plot names (default: same as program)
                        Example: program='University of Wisconsin Oat Yield Trial',
                                experiment_code='UWOYT' results in trial names like 'UWOYT_2021_Location'
        year: Trial year (default: current year)

    Returns:
        DataFrame with trials template in Breedbase format
    """
    input_path = Path(input_folder)

    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_folder}")

    if year is None:
        year = datetime.now().year

    # Use program as experiment_code if not specified (backward compatibility)
    if experiment_code is None:
        experiment_code = program

    # Collect all trial data from all files
    all_trials = []

    # Process all Excel and CSV files
    for file_path in input_path.glob('*'):
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            trials = _extract_trials_from_excel(file_path, program, experiment_code, year)
            all_trials.extend(trials)
        elif file_path.suffix.lower() == '.csv':
            trials = _extract_trials_from_csv(file_path, program, experiment_code, year)
            all_trials.extend(trials)

    if not all_trials:
        print("Warning: No trial data found in input files")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(all_trials)

    # Ensure required columns exist with defaults
    required_columns = {
        'trial_name': '',
        'breeding_program': program,
        'location': 'Unknown',
        'year': year,
        'design_type': 'RCBD',
        'description': '',
        'accession_name': '',
        'plot_number': 0,
        'block_number': 1,
        'plot_name': ''
    }

    for col, default_val in required_columns.items():
        if col not in df.columns:
            df[col] = default_val

    # Generate plot_name if missing
    if 'plot_name' not in df.columns or df['plot_name'].isna().any():
        df['plot_name'] = df.apply(
            lambda row: f"{row['trial_name']}-PLOT_{row['plot_number']}"
            if pd.notna(row.get('trial_name')) and pd.notna(row.get('plot_number'))
            else '',
            axis=1
        )

    # Order columns: required first, then optional
    required_cols = list(required_columns.keys())
    optional_cols = [c for c in df.columns if c not in required_cols]
    df = df[required_cols + optional_cols]

    # Sort by trial_name, then plot_number
    df = df.sort_values(['trial_name', 'plot_number']).reset_index(drop=True)

    # Save if output path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)

        print(f"Trials template saved to: {output_path}")

    print(f"Generated {len(df)} trial plots across {df['trial_name'].nunique()} trials")
    return df


def _extract_trials_from_excel(file_path: Path, program: str, experiment_code: str, year: int) -> List[Dict]:
    """Extract trial data from an Excel file"""
    trials = []

    try:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        # Check for multi-file format (Cover + Page 2)
        if 'Cover' in sheet_names and 'Page 2' in sheet_names:
            # Extract location from filename
            location_match = re.search(r'_([a-z_]+)\.xlsx?$', file_path.name, re.I)
            location = location_match.group(1).replace('_', ' ').title() if location_match else "Unknown"

            df = pd.read_excel(file_path, sheet_name='Page 2')
            sheet_trials = _extract_trials_from_dataframe(
                df, location, program, experiment_code, year, file_path.name
            )
            trials.extend(sheet_trials)

        else:
            # Process each sheet as a separate location
            for sheet_name in sheet_names:
                # Skip summary sheets
                if 'overall' in sheet_name.lower() or 'summary' in sheet_name.lower():
                    continue

                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheet_trials = _extract_trials_from_dataframe(
                        df, sheet_name, program, experiment_code, year, file_path.name
                    )
                    trials.extend(sheet_trials)
                except Exception as e:
                    print(f"  Warning: Could not process sheet '{sheet_name}': {e}")
                    continue

    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")

    return trials


def _extract_trials_from_csv(file_path: Path, program: str, experiment_code: str, year: int) -> List[Dict]:
    """Extract trial data from a CSV file"""
    try:
        df = pd.read_csv(file_path)
        location = file_path.stem.replace('_', ' ').title()
        return _extract_trials_from_dataframe(df, location, program, experiment_code, year, file_path.name)
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return []


def _extract_trials_from_dataframe(df: pd.DataFrame, location: str, program: str,
                                   experiment_code: str, year: int, source_file: str) -> List[Dict]:
    """Extract trial data from a DataFrame"""
    trials = []

    if df.empty:
        return trials

    # Check if pre-structured (already has trial columns)
    if 'trial_name' in df.columns and 'plot_number' in df.columns:
        # Data is already structured, just extract it
        return _extract_pre_structured_trials(df)

    # Find accession/variety column
    name_col = _find_column(df, ['accession_name', 'accessionname', 'variety',
                                  'name', 'selection', 'genotype'])

    if not name_col:
        return trials

    # Find entry number column
    entry_col = _find_column(df, ['entry', 'entry_number', 'entryno', 'no'])

    # Find rep/block columns
    rep_col = _find_column(df, ['rep', 'replicate', 'replication'])
    block_col = _find_column(df, ['block', 'blk'])

    # Find row/col for field position
    row_col = _find_column(df, ['row', 'row_number'])
    col_col = _find_column(df, ['col', 'column', 'col_number'])

    # Generate trial name using experiment_code
    location_clean = location.replace(' ', '').replace('_', '')
    trial_name = f"{experiment_code}_{year}_{location_clean}"

    # Detect trial description from top of file
    description = f"Trial at {location}"
    if len(df) > 0:
        first_cell = str(df.iloc[0, 0]) if pd.notna(df.iloc[0, 0]) else ''
        if first_cell and not any(kw in first_cell.lower() for kw in ['entry', 'name', 'variety']):
            description = first_cell

    # Process each row as a plot
    plot_number = 101
    for idx, row in df.iterrows():
        acc_name = row.get(name_col)

        # Skip if no accession name or header row
        if pd.isna(acc_name) or not str(acc_name).strip():
            continue

        acc_name = str(acc_name).strip()

        # Skip if looks like header
        if any(kw in acc_name.lower() for kw in ['name', 'variety', 'entry', 'accession']):
            continue

        # Build trial record
        trial = {
            'trial_name': trial_name,
            'breeding_program': program,
            'location': location,
            'year': year,
            'design_type': 'RCBD',  # Default to RCBD
            'description': description,
            'accession_name': acc_name,
            'plot_number': plot_number,
            'block_number': 1,  # Default to block 1
            'plot_name': f"{trial_name}-PLOT_{plot_number}"
        }

        # Add entry number if available
        if entry_col and pd.notna(row.get(entry_col)):
            try:
                trial['entry_number'] = int(row[entry_col])
            except:
                pass

        # Add rep/block info
        if rep_col and pd.notna(row.get(rep_col)):
            try:
                trial['rep_number'] = int(row[rep_col])
            except:
                pass

        if block_col and pd.notna(row.get(block_col)):
            try:
                trial['block_number'] = int(row[block_col])
            except:
                pass

        # Add field position
        if row_col and pd.notna(row.get(row_col)):
            try:
                trial['row_number'] = int(row[row_col])
            except:
                pass

        if col_col and pd.notna(row.get(col_col)):
            try:
                trial['col_number'] = int(row[col_col])
            except:
                pass

        trials.append(trial)
        plot_number += 1

    return trials


def _extract_pre_structured_trials(df: pd.DataFrame) -> List[Dict]:
    """Extract trials from pre-structured data (CSV with trial columns)"""
    trials = []

    # Map columns
    trial_columns = ['trial_name', 'breeding_program', 'location', 'year',
                     'design_type', 'description', 'accession_name', 'plot_number',
                     'block_number', 'plot_name', 'entry_number', 'rep_number',
                     'row_number', 'col_number', 'plot_width', 'plot_length',
                     'field_size', 'planting_date', 'harvest_date']

    for idx, row in df.iterrows():
        trial = {}

        for col in trial_columns:
            if col in df.columns and pd.notna(row[col]):
                trial[col] = row[col]

        if trial:
            trials.append(trial)

    return trials


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
        print("Usage: python generate_trials.py <input_folder> [output_file] [--program=PROGRAM] [--code=CODE] [--year=YYYY]")
        print("\nExample:")
        print("  python generate_trials.py ./data/input ./output/trials.xls --program='UW Oat Trial' --code=UWOYT --year=2021")
        print("\nArguments:")
        print("  --program  Breeding program name (used in breeding_program column)")
        print("  --code     Experiment code (used in trial/plot names, defaults to program)")
        print("  --year     Trial year (defaults to current year)")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None

    # Parse optional arguments
    program = 'PROGRAM'
    experiment_code = None
    year = None

    for arg in sys.argv[2:]:
        if arg.startswith('--program='):
            program = arg.split('=', 1)[1]
        elif arg.startswith('--code='):
            experiment_code = arg.split('=', 1)[1]
        elif arg.startswith('--year='):
            try:
                year = int(arg.split('=')[1])
            except:
                pass

    print(f"Generating trials template from: {input_folder}")
    print(f"  Breeding program: {program}")
    print(f"  Experiment code:  {experiment_code or program}")
    print(f"  Year: {year or datetime.now().year}\n")

    df = generate_trials_template(input_folder, output_file, program, experiment_code, year)

    if not output_file:
        print("\nPreview (first 10 rows):")
        print(df.head(10).to_string())
        print(f"\n... ({len(df)} total rows)")
