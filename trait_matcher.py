"""
Trait Matching and Ontology Lookup Utilities

Matches trait names from input data to standardized ontology terms with IDs.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


class TraitMatcher:
    """Match trait names to ontology terms"""

    def __init__(self, assets_folder: str = None):
        """
        Initialize trait matcher

        Args:
            assets_folder: Path to assets folder with ontologies
        """
        if assets_folder is None:
            assets_folder = Path(__file__).parent / 'assets'
        else:
            assets_folder = Path(assets_folder)

        self.assets_folder = assets_folder
        self.ontologies = self._load_ontologies()
        self.abbreviations = self._load_abbreviations()

        # Build reverse lookup indices
        self._build_lookup_indices()

    def _load_ontologies(self) -> Dict[str, Dict]:
        """Load all ontology files"""
        ontologies = {}
        ontology_dir = self.assets_folder / 'trait-ontologies'

        for species_file in ['oat.txt', 'barley.txt', 'wheat.txt']:
            species = species_file.replace('.txt', '')
            file_path = ontology_dir / species_file

            if file_path.exists():
                ontologies[species] = self._parse_obo_file(file_path)

        return ontologies

    def _parse_obo_file(self, file_path: Path) -> Dict:
        """Parse OBO format ontology file"""
        ontology = {
            'traits': {},      # trait_id -> trait_data
            'by_name': {},     # lowercase name -> trait_id
            'by_synonym': {},  # lowercase synonym -> trait_id
        }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into term blocks
        term_blocks = re.split(r'\n\[Term\]', content)

        for block in term_blocks[1:]:  # Skip header
            term = self._parse_term_block(block)
            if term and 'id' in term:
                term_id = term['id']
                ontology['traits'][term_id] = term

                # Index by name
                if 'name' in term:
                    name_key = term['name'].lower().strip()
                    ontology['by_name'][name_key] = term_id

                # Index by synonyms
                if 'synonyms' in term:
                    for syn in term['synonyms']:
                        syn_key = syn.lower().strip()
                        ontology['by_synonym'][syn_key] = term_id

        return ontology

    def _parse_term_block(self, block: str) -> Dict:
        """Parse a single term block from OBO file"""
        term = {}
        synonyms = []

        for line in block.split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if key == 'id':
                term['id'] = value
            elif key == 'name':
                term['name'] = value
            elif key == 'def':
                # Extract definition from quoted text
                match = re.search(r'"([^"]+)"', value)
                if match:
                    term['def'] = match.group(1)
            elif key == 'synonym':
                # Extract synonym from quoted text
                match = re.search(r'"([^"]+)"', value)
                if match:
                    synonyms.append(match.group(1))

        if synonyms:
            term['synonyms'] = synonyms

        return term

    def _load_abbreviations(self) -> pd.DataFrame:
        """Load trait abbreviations mapping"""
        abbr_file = self.assets_folder / 'trait_abbreviations.xlsx'

        if abbr_file.exists():
            try:
                df = pd.read_excel(abbr_file)
                return df
            except:
                pass

        return pd.DataFrame()

    def _build_lookup_indices(self):
        """Build additional lookup indices for faster matching"""
        self.all_trait_names = {}  # species -> list of (name, id)
        self.all_trait_keywords = {}  # species -> keyword -> list of ids

        for species, ontology in self.ontologies.items():
            names = []
            keywords = {}

            for term_id, term_data in ontology['traits'].items():
                if 'name' in term_data:
                    name = term_data['name']
                    names.append((name.lower(), term_id))

                    # Extract keywords
                    words = re.findall(r'\w+', name.lower())
                    for word in words:
                        if len(word) > 2:  # Skip very short words
                            if word not in keywords:
                                keywords[word] = []
                            keywords[word].append(term_id)

                # Also process synonyms
                if 'synonyms' in term_data:
                    for syn in term_data['synonyms']:
                        words = re.findall(r'\w+', syn.lower())
                        for word in words:
                            if len(word) > 2:
                                if word not in keywords:
                                    keywords[word] = []
                                keywords[word].append(term_id)

            self.all_trait_names[species] = names
            self.all_trait_keywords[species] = keywords

    def match_trait(self, trait_name: str, unit: str = None, species: str = 'oat') -> Optional[Dict]:
        """
        Match a trait name (and optionally unit) to an ontology term

        Args:
            trait_name: Trait name from input data
            unit: Optional unit string
            species: Species ('oat', 'barley', 'wheat')

        Returns:
            Dict with ontology_id, full_name, description, unit or None
        """
        if species not in self.ontologies:
            # Try default to oat
            species = 'oat'
            if species not in self.ontologies:
                return None

        ontology = self.ontologies[species]
        trait_clean = trait_name.lower().strip()

        # 1. Try exact match by name
        if trait_clean in ontology['by_name']:
            term_id = ontology['by_name'][trait_clean]
            return self._format_match_result(term_id, ontology, unit)

        # 2. Try exact match by synonym
        if trait_clean in ontology['by_synonym']:
            term_id = ontology['by_synonym'][trait_clean]
            return self._format_match_result(term_id, ontology, unit)

        # 3. Try abbreviation expansion
        if not self.abbreviations.empty:
            abbr_row = self.abbreviations[
                self.abbreviations.iloc[:, 0].str.lower() == trait_clean
            ]
            if not abbr_row.empty and len(abbr_row.columns) > 1:
                full_name = abbr_row.iloc[0, 1]
                full_name_clean = str(full_name).lower().strip()

                if full_name_clean in ontology['by_name']:
                    term_id = ontology['by_name'][full_name_clean]
                    return self._format_match_result(term_id, ontology, unit)

        # 4. Try fuzzy matching
        best_match = self._fuzzy_match(trait_clean, species)
        if best_match:
            return self._format_match_result(best_match, ontology, unit)

        # 5. Try keyword matching
        keyword_match = self._keyword_match(trait_clean, species)
        if keyword_match:
            return self._format_match_result(keyword_match, ontology, unit)

        return None

    def _format_match_result(self, term_id: str, ontology: Dict, unit: str = None) -> Dict:
        """Format matched term as result dictionary"""
        term = ontology['traits'].get(term_id)
        if not term:
            return None

        # Determine unit if not provided
        if not unit:
            unit = self._infer_unit_from_term(term)

        result = {
            'ontology_id': term_id,
            'full_name': term.get('name', ''),
            'description': f"{term.get('name', '')} - {unit}" if unit else term.get('name', ''),
            'unit': unit
        }

        return result

    def _infer_unit_from_term(self, term: Dict) -> str:
        """Infer unit from term name or definition"""
        name = term.get('name', '').lower()
        definition = term.get('def', '').lower()
        text = name + ' ' + definition

        # Look for unit indicators
        if 'g/m' in text or 'g/m2' in text or 'g/m²' in text:
            return 'g/m2'
        elif 'g/l' in text:
            return 'g/L'
        elif 'cm' in text or 'centimeter' in text:
            return 'cm'
        elif 'julian' in text or 'day of year' in text:
            return 'Julian day'
        elif 'percent' in text or '%' in name:
            return '%'
        elif 'rating' in text or '0-9' in text or '1-5' in text or '1-9' in text:
            if '0-9' in text:
                return '0-9 rating'
            elif '1-5' in text:
                return '1-5 rating'
            elif '1-9' in text:
                return '1-9 rating'
            return 'rating'
        elif 'gram' in text and 'kilogram' not in text:
            return 'g'

        return ''

    def _fuzzy_match(self, trait_name: str, species: str, threshold: float = 0.8) -> Optional[str]:
        """Fuzzy match trait name to ontology terms"""
        if species not in self.all_trait_names:
            return None

        best_score = 0
        best_match = None

        for name, term_id in self.all_trait_names[species]:
            score = SequenceMatcher(None, trait_name, name).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = term_id

        return best_match

    def _keyword_match(self, trait_name: str, species: str) -> Optional[str]:
        """Match based on shared keywords"""
        if species not in self.all_trait_keywords:
            return None

        # Extract keywords from trait name
        words = re.findall(r'\w+', trait_name.lower())
        words = [w for w in words if len(w) > 2]

        if not words:
            return None

        # Find terms that share keywords
        candidates = {}  # term_id -> keyword count
        keywords_dict = self.all_trait_keywords[species]

        for word in words:
            if word in keywords_dict:
                for term_id in keywords_dict[word]:
                    candidates[term_id] = candidates.get(term_id, 0) + 1

        # Return term with most keyword matches
        if candidates:
            best_match = max(candidates.items(), key=lambda x: x[1])
            # Require at least 2 matching keywords or 1 if trait name is short
            if best_match[1] >= 2 or (len(words) <= 2 and best_match[1] >= 1):
                return best_match[0]

        return None

    def get_ontology_column_header(self, trait_name: str, unit: str = None,
                                   species: str = 'oat') -> str:
        """
        Get Breedbase-formatted column header for a trait

        Format: "{trait_name} - {description}|{ONTOLOGY_ID}"

        Args:
            trait_name: Trait name from input
            unit: Optional unit
            species: Species name

        Returns:
            Formatted column header string
        """
        match = self.match_trait(trait_name, unit, species)

        if match:
            return f"{match['description']}|{match['ontology_id']}"
        else:
            # Fallback: return original name with unit if no match
            if unit:
                return f"{trait_name} - {unit}"
            return trait_name

    def batch_match_traits(self, trait_list: List[Tuple[str, str]], species: str = 'oat') -> Dict[str, Dict]:
        """
        Match multiple traits at once

        Args:
            trait_list: List of (trait_name, unit) tuples
            species: Species name

        Returns:
            Dict mapping original trait names to match results
        """
        results = {}

        for trait_name, unit in trait_list:
            match = self.match_trait(trait_name, unit, species)
            results[trait_name] = match

        return results
