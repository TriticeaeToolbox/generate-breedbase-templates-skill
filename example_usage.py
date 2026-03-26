#!/usr/bin/env python3
"""
Example usage of Breedbase Template Generator functions

This script demonstrates how to use the three standalone functions
to generate Breedbase upload templates from trial data.
"""

from pathlib import Path
from generate_accessions import generate_accessions_template
from generate_trials import generate_trials_template
from generate_observations import generate_observations_template


def main():
    """Main example workflow"""

    print("="*70)
    print(" BREEDBASE TEMPLATE GENERATOR - EXAMPLE USAGE")
    print("="*70)
    print()

    # Configuration
    # NOTE: Update these paths to match your setup
    input_folder = './assets/sample-datasets/sample-1/input'
    output_folder = './example_output'
    assets_folder = './assets'

    program = 'University of Wisconsin Oat Yield Trial'
    experiment_code = 'UWOYT'  # Used in trial and plot names
    year = 2021
    species = 'oat'

    # Create output directory
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Input folder:     {input_folder}")
    print(f"Output folder:    {output_folder}")
    print(f"Assets folder:    {assets_folder}")
    print(f"Program:          {program}")
    print(f"Experiment code:  {experiment_code}")
    print(f"Year:             {year}")
    print(f"Species:          {species}")
    print()

    # -------------------------------------------------------------------------
    # STEP 1: Generate Accessions Template
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("STEP 1: Generating Accessions Template")
    print("-" * 70)

    accessions_output = output_path / 'accessions.xls'

    try:
        accessions_df = generate_accessions_template(
            input_folder=input_folder,
            output_path=str(accessions_output)
        )

        print(f"\n✓ Success! Generated {len(accessions_df)} unique accessions")
        print(f"  Saved to: {accessions_output}")

        print("\n  Preview (first 5 rows):")
        print("  " + "-" * 66)
        preview = accessions_df.head(5).to_string(index=False)
        for line in preview.split('\n'):
            print(f"  {line}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return

    print()

    # -------------------------------------------------------------------------
    # STEP 2: Generate Trials Template
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("STEP 2: Generating Trials Template")
    print("-" * 70)

    trials_output = output_path / 'trials.xls'

    try:
        trials_df = generate_trials_template(
            input_folder=input_folder,
            output_path=str(trials_output),
            program=program,
            experiment_code=experiment_code,
            year=year
        )

        n_trials = trials_df['trial_name'].nunique()
        n_locations = trials_df['location'].nunique()

        print(f"\n✓ Success! Generated {len(trials_df)} plot records")
        print(f"  Trials:    {n_trials}")
        print(f"  Locations: {n_locations}")
        print(f"  Saved to: {trials_output}")

        print("\n  Preview (first 5 rows, key columns):")
        print("  " + "-" * 66)
        key_cols = ['trial_name', 'location', 'accession_name', 'plot_number', 'plot_name']
        available_cols = [c for c in key_cols if c in trials_df.columns]
        preview = trials_df[available_cols].head(5).to_string(index=False)
        for line in preview.split('\n'):
            print(f"  {line}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return

    print()

    # -------------------------------------------------------------------------
    # STEP 3: Generate Observations Template
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("STEP 3: Generating Observations Template")
    print("-" * 70)

    observations_output = output_path / 'observations.xls'

    try:
        observations_df = generate_observations_template(
            input_folder=input_folder,
            output_path=str(observations_output),
            assets_folder=assets_folder,
            species=species
        )

        n_traits = len(observations_df.columns) - 1  # Exclude observationunit_name

        print(f"\n✓ Success! Generated {len(observations_df)} observation records")
        print(f"  Traits measured: {n_traits}")
        print(f"  Saved to: {observations_output}")

        print("\n  Trait columns (with ontology IDs):")
        print("  " + "-" * 66)
        trait_cols = [c for c in observations_df.columns if c != 'observationunit_name']
        for i, col in enumerate(trait_cols[:10], 1):  # Show first 10 traits
            # Truncate long column names
            col_display = col if len(col) <= 60 else col[:57] + '...'
            print(f"  {i:2d}. {col_display}")
        if len(trait_cols) > 10:
            print(f"  ... and {len(trait_cols) - 10} more traits")

        print("\n  Preview (first 3 rows, first 5 columns):")
        print("  " + "-" * 66)
        preview_cols = observations_df.columns[:min(5, len(observations_df.columns))]
        preview = observations_df[preview_cols].head(3).to_string(index=False)
        for line in preview.split('\n'):
            print(f"  {line}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return

    print()

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print()
    print(f"  ✓ Accessions template:   {len(accessions_df):4d} unique varieties")
    print(f"  ✓ Trials template:       {len(trials_df):4d} plot records")
    print(f"  ✓ Observations template: {len(observations_df):4d} observations")
    print()
    print(f"All templates saved to: {output_folder}/")
    print()
    print("Next steps:")
    print("  1. Review the generated templates")
    print("  2. Verify trait mappings in observations template")
    print("  3. Upload templates to Breedbase")
    print()


if __name__ == '__main__':
    main()
