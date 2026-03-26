"""
Generate Accessions Template

Standalone function to extract unique accessions from breeding trial data
and generate a Breedbase-compatible accessions upload template.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import openpyxl
import re


def generate_accessions_template(input_folder: str, output_path: str = None) -> pd.DataFrame:
    """
    Generate accessions template from input data folder

    Args:
        input_folder: Path to folder containing input data files (Excel, CSV)
        output_path: Optional path to save output file (.xls or .xlsx)

    Returns:
        DataFrame with accessions template in Breedbase format
    """
    input_path = Path(input_folder)

    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_folder}")

    # Collect all accessions from all files
    all_accessions = []

    # Process all Excel and CSV files
    for file_path in input_path.glob('*'):
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            accessions = _extract_accessions_from_excel(file_path)
            all_accessions.extend(accessions)
        elif file_path.suffix.lower() == '.csv':
            accessions = _extract_accessions_from_csv(file_path)
            all_accessions.extend(accessions)

    if not all_accessions:
        print("Warning: No accessions found in input files")
        return pd.DataFrame(columns=['accession_name', 'species_name'])

    # Convert to DataFrame
    df = pd.DataFrame(all_accessions)

    # Remove duplicates based on accession_name
    df = df.drop_duplicates(subset=['accession_name'], keep='first')

    # Ensure required columns exist
    if 'accession_name' not in df.columns:
        df['accession_name'] = ''
    if 'species_name' not in df.columns:
        df['species_name'] = 'Avena sativa'  # Default to oats

    # Order columns: required first, then optional
    required_cols = ['accession_name', 'species_name']
    optional_cols = [c for c in df.columns if c not in required_cols]
    df = df[required_cols + optional_cols]

    # Sort by accession name
    df = df.sort_values('accession_name').reset_index(drop=True)

    # Save if output path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)

        print(f"Accessions template saved to: {output_path}")

    print(f"Generated {len(df)} unique accessions")
    return df


def _extract_accessions_from_excel(file_path: Path) -> List[Dict]:
    """Extract accessions from an Excel file"""
    accessions = []

    try:
        # Load workbook to check sheets
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        # Process each sheet
        for sheet_name in sheet_names:
            # Skip summary sheets
            if 'overall' in sheet_name.lower() or 'summary' in sheet_name.lower():
                continue

            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_accessions = _extract_accessions_from_dataframe(df, file_path.name, sheet_name)
                accessions.extend(sheet_accessions)
            except Exception as e:
                print(f"  Warning: Could not process sheet '{sheet_name}': {e}")
                continue

    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")

    return accessions


def _extract_accessions_from_csv(file_path: Path) -> List[Dict]:
    """Extract accessions from a CSV file"""
    try:
        df = pd.read_csv(file_path)
        return _extract_accessions_from_dataframe(df, file_path.name)
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return []


def _extract_accessions_from_dataframe(df: pd.DataFrame, source_file: str,
                                       sheet_name: str = None) -> List[Dict]:
    """Extract accessions from a DataFrame"""
    accessions = []

    if df.empty:
        return accessions

    # Find accession name column
    name_col = _find_accession_column(df)

    if not name_col:
        return accessions

    # Detect species
    species = _detect_species(source_file, df)

    # Find pedigree column if exists
    pedigree_col = _find_column(df, ['pedigree', 'cross', 'parentage'])

    # Find other relevant columns
    population_col = _find_column(df, ['population', 'pop'])
    organization_col = _find_column(df, ['organization', 'org', 'institution'])
    synonym_col = _find_column(df, ['synonym', 'alias', 'aka'])
    generation_col = _find_column(df, ['generation', 'gen', 'filial'])
    origin_col = _find_column(df, ['origin', 'country', 'source'])

    # Extract accessions from each row
    for idx, row in df.iterrows():
        acc_name = row.get(name_col)

        # Skip if no accession name or header row
        if pd.isna(acc_name) or not str(acc_name).strip():
            continue

        acc_name = str(acc_name).strip()

        # Skip if looks like a header
        if any(kw in acc_name.lower() for kw in ['name', 'variety', 'entry', 'accession']):
            continue

        # Build accession record
        accession = {
            'accession_name': acc_name,
            'species_name': species
        }

        # Add pedigree if available
        if pedigree_col and pd.notna(row.get(pedigree_col)):
            pedigree = str(row[pedigree_col]).strip()
            if pedigree:
                accession['purdy pedigree'] = pedigree

                # Try to extract parents
                female, male = _parse_pedigree(pedigree)
                if female:
                    accession['female_parent'] = female
                if male:
                    accession['male_parent'] = male

        # Add other optional columns
        if population_col and pd.notna(row.get(population_col)):
            accession['population_name'] = str(row[population_col]).strip()

        if organization_col and pd.notna(row.get(organization_col)):
            accession['organization_name'] = str(row[organization_col]).strip()

        if synonym_col and pd.notna(row.get(synonym_col)):
            accession['synonym'] = str(row[synonym_col]).strip()

        if generation_col and pd.notna(row.get(generation_col)):
            accession['filial generation'] = str(row[generation_col]).strip()

        if origin_col and pd.notna(row.get(origin_col)):
            accession['country of origin'] = str(row[origin_col]).strip()

        accessions.append(accession)

    return accessions


def _find_accession_column(df: pd.DataFrame) -> Optional[str]:
    """Find the column containing accession names"""
    # Look for standard column names
    priority_keywords = [
        ['accession_name', 'accessionname'],
        ['variety', 'varieties'],
        ['name'],
        ['selection', 'line'],
        ['genotype', 'cultivar']
    ]

    for keywords in priority_keywords:
        col = _find_column(df, keywords)
        if col:
            return col

    return None


def _find_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    """Find a column matching any of the keywords"""
    for col in df.columns:
        col_lower = str(col).lower().strip()
        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col
    return None


def _detect_species(source_file: str, df: pd.DataFrame) -> str:
    """Detect species from file name or data content"""
    # Check file name
    text = source_file.lower()

    # Also check column names and first few rows
    if not df.empty:
        text += ' ' + ' '.join(str(c).lower() for c in df.columns)
        text += ' ' + ' '.join(str(v).lower() for v in df.iloc[0] if pd.notna(v))

    # Species detection
    if 'oat' in text:
        return 'Avena sativa'
    elif 'wheat' in text:
        return 'Triticum aestivum'
    elif 'barley' in text:
        return 'Hordeum vulgare'
    elif 'soybean' in text or 'soya' in text:
        return 'Glycine max'
    elif 'maize' in text or 'corn' in text:
        return 'Zea mays'
    elif 'rice' in text:
        return 'Oryza sativa'

    # Default to oats
    return 'Avena sativa'


def _parse_pedigree(pedigree: str) -> tuple:
    """
    Parse pedigree string to extract female and male parents

    Returns: (female_parent, male_parent)
    """
    if not pedigree or pd.isna(pedigree):
        return None, None

    pedigree = str(pedigree).strip()

    # Handle simple biparental: FEMALE/MALE
    if '/' in pedigree:
        parts = pedigree.split('/')
        # Clean up parts
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 2:
            female = parts[0]
            male = parts[1]
            return female, male

    return None, None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_accessions.py <input_folder> [output_file]")
        print("\nExample:")
        print("  python generate_accessions.py ./data/input ./output/accessions.xls")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Generating accessions template from: {input_folder}\n")
    df = generate_accessions_template(input_folder, output_file)

    if not output_file:
        print("\nPreview (first 10 rows):")
        print(df.head(10).to_string())
        print(f"\n... ({len(df)} total rows)")
