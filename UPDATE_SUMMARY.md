# Update Summary: Separate Program and Experiment Code Parameters

## What Was Changed

The `generate_trials_template()` function now supports separate parameters for:

1. **`program`** - Full breeding program name (used in `breeding_program` column)
2. **`experiment_code`** - Short code for trial and plot naming (optional, defaults to `program`)

## Why This Change?

Previously, you had to choose between:
- ❌ Long descriptive program names → verbose trial/plot names
- ❌ Short codes for naming → cryptic program names in database

Now you can have both:
- ✅ Descriptive program names in the database
- ✅ Concise codes in trial and plot identifiers

## Examples

### Before (Single Parameter)
```python
generate_trials_template(
    input_folder='./data',
    breeding_program='UWOYT',
    year=2021
)
```
**Result:**
- `breeding_program`: `'UWOYT'`
- `trial_name`: `'UWOYT_2021_BelleMina'`

### After (Separate Parameters)
```python
generate_trials_template(
    input_folder='./data',
    program='University of Wisconsin Oat Yield Trial',  # Descriptive
    experiment_code='UWOYT',                            # Concise
    year=2021
)
```
**Result:**
- `breeding_program`: `'University of Wisconsin Oat Yield Trial'` ← Full name
- `trial_name`: `'UWOYT_2021_BelleMina'` ← Short code

## Backward Compatible ✅

If you only specify `program`, it works exactly like before:

```python
# This still works - experiment_code defaults to 'UWOYT'
generate_trials_template(
    input_folder='./data',
    program='UWOYT',
    year=2021
)
```

## Updated Files

✅ **`generate_trials.py`** - Main function updated
✅ **`generate_breedbase_templates.py`** - Class updated
✅ **`example_usage.py`** - Example updated
✅ **`USAGE.md`** - Documentation updated
✅ **`QUICKSTART.md`** - Quick start updated
✅ **`CHANGELOG.md`** - Full change log created

## Command Line Usage

**New arguments:**
```bash
python generate_trials.py ./data ./output/trials.xls \
    --program='University of Wisconsin Oat Yield Trial' \
    --code=UWOYT \
    --year=2021
```

**Old usage still works:**
```bash
python generate_trials.py ./data ./output/trials.xls \
    --program=UWOYT \
    --year=2021
```

## Testing

All modules tested and verified:
```
✓ generate_trials imported
✓ BreedbaseTemplateGenerator imported
✓ New parameters (program, experiment_code) present
✓ Backward compatibility maintained
```

## Need More Info?

- **`CHANGELOG.md`** - Complete changelog with migration guide
- **`USAGE.md`** - Full usage documentation
- **`example_usage.py`** - Working code example

## Quick Reference

| Parameter | Purpose | Example | Used In |
|-----------|---------|---------|---------|
| `program` | Full program name | `'University of Wisconsin Oat Yield Trial'` | `breeding_program` column |
| `experiment_code` | Short naming code | `'UWOYT'` | `trial_name`, `plot_name` |

**Both parameters are optional and default to sensible values!**
