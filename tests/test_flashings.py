# tests/test_flashings.py
"""
Testy dla modułu flashing_definitions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from flashing_definitions import (
    FlashingDefinition,
    get_predefined_flashings,
    get_flashing_definition,
    get_material_names,
    get_material_price,
    calculate_flashing_cost
)

class TestFlashingDefinition(unittest.TestCase):
    """Testy dla klasy FlashingDefinition."""
    
    def test_create_flashing(self):
        """Test tworzenia definicji obróbki."""
        flashing = FlashingDefinition(
            name="Test obróbki",
            width_cm=30.0,
            price_per_mb=25.0
        )
        
        self.assertEqual(flashing.name, "Test obróbki")
        self.assertEqual(flashing.width_cm, 30.0)
        self.assertEqual(flashing.price_per_mb, 25.0)
    
    def test_calculate_price_mb(self):
        """Test obliczania ceny za mb."""
        flashing = FlashingDefinition(
            name="Test",
            width_cm=25.0,
            price_per_mb=20.0,
            unit="mb"
        )
        
        price = flashing.calculate_price(10.0)  # 10 metrów
        self.assertEqual(price, 200.0)
    
    def test_calculate_price_m2(self):
        """Test obliczania ceny za m²."""
        flashing = FlashingDefinition(
            name="Test",
            width_cm=50.0,  # 0.5m
            price_per_m2=40.0,
            unit="m2"
        )
        
        price = flashing.calculate_price(10.0)  # 10m długości = 5m² powierzchni
        self.assertEqual(price, 200.0)
    
    def test_calculate_material_needed(self):
        """Test obliczania potrzebnej powierzchni materiału."""
        flashing = FlashingDefinition(
            name="Test",
            width_cm=30.0  # 0.3m
        )
        
        area = flashing.calculate_material_needed(20.0)  # 20m długości
        self.assertEqual(area, 6.0)  # 20m * 0.3m = 6m²
    
    def test_to_dict_from_dict(self):
        """Test konwersji do/z słownika."""
        original = FlashingDefinition(
            name="Test",
            width_cm=25.0,
            price_per_mb=18.0
        )
        
        data = original.to_dict()
        restored = FlashingDefinition.from_dict(data)
        
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.width_cm, restored.width_cm)
        self.assertEqual(original.price_per_mb, restored.price_per_mb)

class TestPredefinedFlashings(unittest.TestCase):
    """Testy dla predefiniowanych obróbek."""
    
    def test_get_predefined_list(self):
        """Test pobierania listy predefiniowanych obróbek."""
        flashings = get_predefined_flashings()
        
        self.assertIn("Pas nadrynnowy", flashings)
        self.assertIn("Obróbka komina", flashings)
        self.assertGreater(len(flashings), 5)
    
    def test_get_flashing_definition(self):
        """Test pobierania definicji obróbki."""
        flashing = get_flashing_definition("Pas nadrynnowy")
        
        self.assertEqual(flashing.name, "Pas nadrynnowy")
        self.assertGreater(flashing.width_cm, 0)
        self.assertGreater(flashing.price_per_mb, 0)
    
    def test_invalid_flashing_name(self):
        """Test dla nieistniejącej obróbki."""
        with self.assertRaises(KeyError):
            get_flashing_definition("Nieistniejąca obróbka")

class TestMaterials(unittest.TestCase):
    """Testy dla materiałów."""
    
    def test_get_material_names(self):
        """Test pobierania listy materiałów."""
        materials = get_material_names()
        
        self.assertIn("Blacha powlekana", materials)
        self.assertIn("Miedź", materials)
        self.assertGreater(len(materials), 3)
    
    def test_get_material_price(self):
        """Test pobierania ceny materiału."""
        price = get_material_price("Blacha powlekana")
        self.assertGreater(price, 0)
        
        copper_price = get_material_price("Miedź")
        self.assertGreater(copper_price, price)  # Miedź droższa od powlekanej
    
    def test_invalid_material_name(self):
        """Test dla nieistniejącego materiału."""
        with self.assertRaises(KeyError):
            get_material_price("Nieistniejący materiał")

class TestFlashingCostCalculation(unittest.TestCase):
    """Testy dla obliczania kosztów obróbek."""
    
    def test_calculate_cost(self):
        """Test obliczania kosztu obróbki."""
        result = calculate_flashing_cost(
            flashing_name="Pas nadrynnowy",
            length_m=15.0,
            material="Blacha powlekana"
        )
        
        self.assertIn("name", result)
        self.assertIn("total_net", result)
        self.assertGreater(result["total_net"], 0)
        self.assertEqual(result["quantity"], 15.0)
    
    def test_custom_width(self):
        """Test z niestandardową szerokością."""
        result = calculate_flashing_cost(
            flashing_name="Pas nadrynnowy",
            length_m=10.0,
            material="Ocynk",
            custom_width_cm=35.0
        )
        
        self.assertEqual(result["width_cm"], 35.0)
    
    def test_custom_price(self):
        """Test z niestandardową ceną."""
        custom_price = 25.0
        result = calculate_flashing_cost(
            flashing_name="Pas nadrynnowy",
            length_m=10.0,
            custom_price_per_mb=custom_price
        )
        
        self.assertEqual(result["price_unit_net"], custom_price)

if __name__ == '__main__':
    unittest.main()
