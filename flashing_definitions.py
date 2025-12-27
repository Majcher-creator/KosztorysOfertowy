# flashing_definitions.py
"""
Module for defining and managing custom flashing types (obróbki blacharskie).
Allows users to create custom flashing definitions with materials and pricing.
"""

import json
import os

# Predefined flashing types with default parameters
PREDEFINED_FLASHINGS = {
    "pas_nadrynnowy": {
        "name": "Pas nadrynnowy",
        "description": "Obróbka nad rynną",
        "default_width_m": 0.33,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "pas_podrynnowy": {
        "name": "Pas podrynnowy",
        "description": "Obróbka pod rynną",
        "default_width_m": 0.25,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "wiatrownica": {
        "name": "Wiatrownica",
        "description": "Obróbka czołowa dachu",
        "default_width_m": 0.33,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "kosz_dachowy": {
        "name": "Kosz dachowy",
        "description": "Obróbka w koszu dachu",
        "default_width_m": 0.66,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "obroba_komina": {
        "name": "Obróbka komina",
        "description": "Obróbka wokół komina",
        "default_width_m": 0.50,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "obroba_attyki": {
        "name": "Obróbka attyki",
        "description": "Obróbka attyki",
        "default_width_m": 0.50,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "gasior_kalenica": {
        "name": "Gąsior/kalenica",
        "description": "Obróbka kalenicy",
        "default_width_m": 0.33,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    },
    "listwa_przyscienna": {
        "name": "Listwa przyścienna",
        "description": "Obróbka przy ścianie",
        "default_width_m": 0.25,
        "material": "blacha_powlekana",
        "price_per_meter": 0.0,
        "unit": "mb"
    }
}

# Available materials
FLASHING_MATERIALS = {
    "blacha_powlekana": {"name": "Blacha powlekana", "price_multiplier": 1.0},
    "ocynk": {"name": "Ocynk", "price_multiplier": 0.8},
    "tytan_cynk": {"name": "Tytan-cynk", "price_multiplier": 2.0},
    "miedz": {"name": "Miedź", "price_multiplier": 5.0},
    "aluminium": {"name": "Aluminium", "price_multiplier": 1.5}
}


class FlashingDefinitionsManager:
    """Manager for custom flashing definitions"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.custom_flashings = {}
        self.load()
    
    def load(self):
        """Load custom flashing definitions from JSON file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.custom_flashings = json.load(f)
            except Exception:
                self.custom_flashings = {}
        else:
            self.custom_flashings = {}
    
    def save(self):
        """Save custom flashing definitions to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.custom_flashings, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_all_flashings(self):
        """Get all flashings (predefined + custom)"""
        all_flashings = dict(PREDEFINED_FLASHINGS)
        all_flashings.update(self.custom_flashings)
        return all_flashings
    
    def add_custom_flashing(self, key, definition):
        """Add or update a custom flashing definition"""
        self.custom_flashings[key] = definition
        self.save()
    
    def delete_custom_flashing(self, key):
        """Delete a custom flashing definition"""
        if key in self.custom_flashings:
            del self.custom_flashings[key]
            self.save()
            return True
        return False
    
    def is_custom(self, key):
        """Check if a flashing is custom (not predefined)"""
        return key not in PREDEFINED_FLASHINGS


def calculate_flashing_cost(length_m, width_m, material="blacha_powlekana", base_price_per_m2=0.0):
    """
    Calculate the cost of a flashing based on dimensions and material.
    
    Args:
        length_m (float): Length in meters
        width_m (float): Development width in meters
        material (str): Material type key
        base_price_per_m2 (float): Base price per square meter
    
    Returns:
        dict: Dictionary with surface area and calculated cost
    """
    surface_m2 = length_m * width_m
    material_info = FLASHING_MATERIALS.get(material, FLASHING_MATERIALS["blacha_powlekana"])
    multiplier = material_info.get("price_multiplier", 1.0)
    total_cost = surface_m2 * base_price_per_m2 * multiplier
    
    return {
        "surface_m2": surface_m2,
        "material": material_info["name"],
        "total_cost": total_cost,
        "unit_price": base_price_per_m2 * multiplier
    }
