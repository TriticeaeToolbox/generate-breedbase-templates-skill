"""
Unit Conversion Utilities for Breedbase Templates

Handles conversion between various measurement units commonly found in breeding trials.
"""

import pandas as pd
from datetime import datetime
from typing import Any, Optional


class UnitConverter:
    """Unit conversion utilities for breeding trial data"""

    # Conversion factors
    CONVERSIONS = {
        # Yield conversions
        ('bu/a', 'g/m2'): 3.586715,  # Oats bushels/acre to g/m²
        ('kg/ha', 'g/m2'): 0.1,      # kg/ha to g/m²

        # Test weight conversions
        ('lb/bu', 'g/l'): 12.871981,  # lb/bu to g/L

        # Height conversions
        ('in', 'cm'): 2.54,           # inches to cm
        ('inch', 'cm'): 2.54,
        ('inches', 'cm'): 2.54,

        # Weight conversions
        ('lb', 'g'): 453.592,         # pounds to grams
        ('oz', 'g'): 28.3495,         # ounces to grams
        ('kg', 'g'): 1000,            # kilograms to grams
    }

    @staticmethod
    def normalize_unit(unit: str) -> str:
        """Normalize unit string for comparison"""
        if pd.isna(unit):
            return ''

        unit = str(unit).lower().strip()

        # Remove extra characters
        unit = unit.replace('.', '').replace(' ', '').replace('/', '')

        # Common normalizations
        replacements = {
            'bua': 'bu/a',
            'bu_a': 'bu/a',
            'buacre': 'bu/a',
            'kgha': 'kg/ha',
            'kg_ha': 'kg/ha',
            'gm2': 'g/m2',
            'g_m2': 'g/m2',
            'lbbu': 'lb/bu',
            'lb_bu': 'lb/bu',
            'gl': 'g/l',
            'g_l': 'g/l',
        }

        for old, new in replacements.items():
            unit = unit.replace(old, new)

        return unit

    @staticmethod
    def convert_value(value: Any, from_unit: str, to_unit: str) -> Optional[float]:
        """
        Convert a value from one unit to another

        Args:
            value: The value to convert
            from_unit: Source unit (e.g., 'bu/A', 'lb/bu', 'inches')
            to_unit: Target unit (e.g., 'g/m2', 'g/L', 'cm')

        Returns:
            Converted value, or original value if no conversion found
        """
        if pd.isna(value):
            return None

        try:
            value_float = float(value)
        except (ValueError, TypeError):
            return None

        from_unit_norm = UnitConverter.normalize_unit(from_unit)
        to_unit_norm = UnitConverter.normalize_unit(to_unit)

        # Check if conversion is needed
        if from_unit_norm == to_unit_norm:
            return value_float

        # Look up conversion factor
        conversion_key = (from_unit_norm, to_unit_norm)
        if conversion_key in UnitConverter.CONVERSIONS:
            factor = UnitConverter.CONVERSIONS[conversion_key]
            return value_float * factor

        # Try reverse conversion
        reverse_key = (to_unit_norm, from_unit_norm)
        if reverse_key in UnitConverter.CONVERSIONS:
            factor = UnitConverter.CONVERSIONS[reverse_key]
            return value_float / factor

        # No conversion found
        return value_float

    @staticmethod
    def date_to_julian(date_value: Any) -> Optional[int]:
        """
        Convert date to Julian day (1-365/366)

        Args:
            date_value: Date value (datetime, string, or numeric)

        Returns:
            Julian day (1-365/366) or None
        """
        if pd.isna(date_value):
            return None

        # Already a datetime
        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.timetuple().tm_yday

        # Try parsing string
        if isinstance(date_value, str):
            date_value = date_value.strip()

            # Handle common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
                       '%Y/%m/%d', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y']:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.timetuple().tm_yday
                except ValueError:
                    continue

            # Try pandas
            try:
                dt = pd.to_datetime(date_value)
                return dt.timetuple().tm_yday
            except:
                pass

        # If numeric, assume it's already Julian day
        try:
            julian = int(float(date_value))
            if 1 <= julian <= 366:
                return julian
        except:
            pass

        return None

    @staticmethod
    def detect_unit_from_column_name(column_name: str) -> Optional[str]:
        """
        Try to detect unit from column name

        Args:
            column_name: Column name (e.g., 'Yield (bu/A)', 'Height_inches')

        Returns:
            Detected unit string or None
        """
        col = str(column_name).lower()

        # Look for units in parentheses
        import re
        paren_match = re.search(r'\(([^)]+)\)', col)
        if paren_match:
            return paren_match.group(1).strip()

        # Look for common unit patterns
        unit_patterns = {
            r'bu[/_\s]*a': 'bu/A',
            r'kg[/_\s]*ha': 'kg/ha',
            r'g[/_\s]*m2': 'g/m2',
            r'lb[/_\s]*bu': 'lb/bu',
            r'g[/_\s]*l': 'g/L',
            r'inch(?:es)?': 'inches',
            r'\bcm\b': 'cm',
            r'julian': 'Julian day',
            r'percent|%': '%',
            r'rating': 'rating',
        }

        for pattern, unit in unit_patterns.items():
            if re.search(pattern, col):
                return unit

        return None

    @staticmethod
    def infer_trait_unit(trait_name: str, value_sample: Any = None) -> str:
        """
        Infer the most likely unit for a trait based on its name and sample values

        Args:
            trait_name: Name of the trait
            value_sample: Optional sample value to help infer units

        Returns:
            Most likely unit string
        """
        trait_lower = str(trait_name).lower()

        # Yield
        if 'yield' in trait_lower or 'yld' in trait_lower or 'grnyie' in trait_lower:
            if value_sample and isinstance(value_sample, (int, float)):
                if value_sample > 1000:
                    return 'kg/ha'
                elif value_sample > 100:
                    return 'bu/A'
                else:
                    return 'g/m2'
            return 'g/m2'

        # Test weight
        if 'test' in trait_lower and 'weight' in trait_lower or 'tw' == trait_lower:
            return 'g/L'

        # Height
        if 'height' in trait_lower or 'ht' in trait_lower:
            if value_sample and isinstance(value_sample, (int, float)):
                if value_sample < 100:
                    return 'inches'
                else:
                    return 'cm'
            return 'cm'

        # Heading date
        if 'heading' in trait_lower or 'hd' in trait_lower or 'anthesis' in trait_lower:
            return 'Julian day'

        # Lodging
        if 'lodg' in trait_lower:
            return '0-9 rating'

        # Disease severity
        if 'severity' in trait_lower or 'rust' in trait_lower or 'disease' in trait_lower:
            if '%' in trait_lower or 'percent' in trait_lower:
                return '%'
            return '0-9 rating'

        # Protein, oil, etc.
        if any(kw in trait_lower for kw in ['protein', 'oil', 'fat', 'fiber', 'beta', 'groat']):
            return '%'

        # Weight measurements
        if 'weight' in trait_lower and 'kernel' in trait_lower:
            return 'g'

        # Default
        return ''


def convert_trait_column(values: pd.Series, from_unit: str, to_unit: str) -> pd.Series:
    """
    Convert an entire column of trait values

    Args:
        values: Series of values to convert
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        Series of converted values
    """
    converter = UnitConverter()
    return values.apply(lambda x: converter.convert_value(x, from_unit, to_unit))


def convert_date_column(values: pd.Series) -> pd.Series:
    """
    Convert an entire column of dates to Julian days

    Args:
        values: Series of date values

    Returns:
        Series of Julian days
    """
    converter = UnitConverter()
    return values.apply(lambda x: converter.date_to_julian(x))
