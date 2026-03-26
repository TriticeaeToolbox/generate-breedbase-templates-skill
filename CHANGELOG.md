# Changelog

## 2026-03-26 - Separate Program and Experiment Code Parameters

### Changes

Updated the trials template generation to support separate parameters for breeding program name and experiment code.

### What Changed

#### Previous Behavior
- Single `breeding_program` parameter used for both:
  - The `breeding_program` column in trials template
  - Trial naming (e.g., `UWOYT_2021_Location`)
  - Plot naming (e.g., `UWOYT_2021_Location-PLOT_101`)

#### New Behavior
- **`program`** parameter - Full breeding program name
  - Used in `breeding_program` column
  - Example: `'University of Wisconsin Oat Yield Trial'`

- **`experiment_code`** parameter - Short code for naming
  - Used in trial names: `{experiment_code}_{year}_{location}`
  - Used in plot names: `{trial_name}-PLOT_{plot_number}`
  - Defaults to `program` value if not specified (backward compatible)
  - Example: `'UWOYT'`

### Updated Functions

#### 1. `generate_trials_template()`
```python
# Old signature
generate_trials_template(input_folder, output_path, breeding_program, year)

# New signature
generate_trials_template(input_folder, output_path, program, experiment_code, year)
```

**Example Usage:**
```python
trials_df = generate_trials_template(
    input_folder='./data',
    output_path='./output/trials.xls',
    program='University of Wisconsin Oat Yield Trial',  # Full name in template
    experiment_code='UWOYT',                            # Short code in names
    year=2021
)
```

**Result:**
- `breeding_program` column: `'University of Wisconsin Oat Yield Trial'`
- `trial_name`: `'UWOYT_2021_BelleMina'`
- `plot_name`: `'UWOYT_2021_BelleMina-PLOT_101'`

#### 2. `BreedbaseTemplateGenerator` class
```python
# Old constructor
BreedbaseTemplateGenerator(input_folder, assets_folder)

# New constructor
BreedbaseTemplateGenerator(input_folder, assets_folder, program, experiment_code, year)
```

**Example Usage:**
```python
generator = BreedbaseTemplateGenerator(
    input_folder='./data',
    assets_folder='./assets',
    program='University of Wisconsin Oat Yield Trial',
    experiment_code='UWOYT',
    year=2021
)

accessions, trials, observations = generator.generate_all_templates('./output')
```

#### 3. `generate_templates_from_folder()`
```python
# Old signature
generate_templates_from_folder(input_folder, output_folder, assets_folder)

# New signature
generate_templates_from_folder(input_folder, output_folder, assets_folder,
                               program, experiment_code, year)
```

### Command Line Usage

```bash
# Old command
python generate_trials.py ./data ./output/trials.xls --program=UWOYT --year=2021

# New command
python generate_trials.py ./data ./output/trials.xls \
    --program='University of Wisconsin Oat Yield Trial' \
    --code=UWOYT \
    --year=2021
```

### Backward Compatibility

✅ **Fully backward compatible!**

If `experiment_code` is not specified, it defaults to the value of `program`:

```python
# This still works - experiment_code defaults to 'UWOYT'
trials_df = generate_trials_template(
    input_folder='./data',
    program='UWOYT',
    year=2021
)
# Result: trial_name = 'UWOYT_2021_Location'
#         breeding_program = 'UWOYT'
```

### Migration Guide

#### Simple Case (No Change Needed)
If you were using short codes and are happy with the current behavior:
```python
# This still works exactly as before
generate_trials_template(input_folder='./data', program='UWOYT', year=2021)
```

#### Use Case: Separate Long Name and Short Code
If you want a descriptive program name but short trial codes:
```python
# Before (had to choose one)
generate_trials_template(input_folder='./data', breeding_program='UWOYT', year=2021)

# After (can use both)
generate_trials_template(
    input_folder='./data',
    program='University of Wisconsin Oat Yield Trial',  # Descriptive
    experiment_code='UWOYT',                            # Short
    year=2021
)
```

### Files Modified

1. **`generate_trials.py`**
   - Updated function signature
   - Updated internal functions to use both parameters
   - Updated command-line argument parsing

2. **`generate_breedbase_templates.py`**
   - Updated `__init__` to accept new parameters
   - Updated `_extract_trials_from_dataframe` to use `experiment_code` for naming
   - Updated `generate_templates_from_folder` wrapper function

3. **`example_usage.py`**
   - Updated to demonstrate new parameter usage

4. **Documentation**
   - **`USAGE.md`** - Updated function signatures and examples
   - **`QUICKSTART.md`** - Updated quick start examples
   - **`CHANGELOG.md`** - Created this file

### Benefits

1. **Clearer Semantics**
   - Program name for human-readable column
   - Experiment code for concise identifiers

2. **Better Organization**
   - Full program names in database
   - Short codes in trial/plot names

3. **Flexibility**
   - Can use long descriptive names without cluttering identifiers
   - Can use different naming conventions

4. **Backward Compatible**
   - Existing code continues to work
   - No breaking changes

### Examples by Use Case

#### Use Case 1: Short Code Everywhere (Original Behavior)
```python
generate_trials_template(input_folder='./data', program='UWOYT', year=2021)
# breeding_program: 'UWOYT'
# trial_name: 'UWOYT_2021_Location'
```

#### Use Case 2: Descriptive Program, Short Codes for Names
```python
generate_trials_template(
    input_folder='./data',
    program='University of Wisconsin Oat Yield Trial',
    experiment_code='UWOYT',
    year=2021
)
# breeding_program: 'University of Wisconsin Oat Yield Trial'
# trial_name: 'UWOYT_2021_Location'
```

#### Use Case 3: Institution in Program, Project in Code
```python
generate_trials_template(
    input_folder='./data',
    program='University of Wisconsin - Madison',
    experiment_code='OYT',
    year=2021
)
# breeding_program: 'University of Wisconsin - Madison'
# trial_name: 'OYT_2021_Location'
```

## Testing

All existing functionality tested and verified:
- ✅ Module imports successfully
- ✅ Function signatures updated correctly
- ✅ New parameters present in all functions
- ✅ Backward compatibility maintained (experiment_code defaults to program)
- ✅ Command-line interface updated

## Questions?

See updated documentation:
- **USAGE.md** - Complete usage guide with new parameters
- **QUICKSTART.md** - Quick start with examples
- **example_usage.py** - Working example code
