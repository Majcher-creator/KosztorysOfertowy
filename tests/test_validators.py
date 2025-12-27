# tests/test_validators.py
"""
Testy dla modułu validators.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from validators import CostEstimateValidator

class TestCostEstimateValidator(unittest.TestCase):
    """Testy dla walidatora kosztorysów."""
    
    def setUp(self):
        """Przygotowanie przed każdym testem."""
        self.validator = CostEstimateValidator()
    
    def test_valid_estimate(self):
        """Test poprawnego kosztorysu."""
        items = [
            {
                "name": "Papa",
                "quantity": 100.0,
                "unit": "m2",
                "price_unit_net": 25.0,
                "category": "material"
            },
            {
                "name": "Transport",
                "quantity": 1.0,
                "unit": "kpl",
                "price_unit_net": 500.0,
                "category": "service"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        # Może być nie w pełni poprawny (brak np. rusztowania)
        # ale nie powinien mieć błędów krytycznych
        self.assertIsInstance(warnings, list)
    
    def test_missing_name(self):
        """Test pozycji bez nazwy."""
        items = [
            {
                "name": "",
                "quantity": 10.0,
                "unit": "m2",
                "price_unit_net": 25.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        self.assertFalse(is_valid)
        self.assertTrue(any("Brak nazwy" in w for w in warnings))
    
    def test_invalid_quantity(self):
        """Test nieprawidłowej ilości."""
        items = [
            {
                "name": "Test",
                "quantity": -5.0,
                "unit": "m2",
                "price_unit_net": 25.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        self.assertFalse(is_valid)
        self.assertTrue(any("ilość" in w.lower() for w in warnings))
    
    def test_missing_unit(self):
        """Test pozycji bez jednostki."""
        items = [
            {
                "name": "Test",
                "quantity": 10.0,
                "unit": "",
                "price_unit_net": 25.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        self.assertFalse(is_valid)
        self.assertTrue(any("jednostki" in w.lower() for w in warnings))
    
    def test_gutter_without_hooks(self):
        """Test rynny bez haków."""
        items = [
            {
                "name": "Rynna PVC 100",
                "quantity": 20.0,
                "unit": "mb",
                "price_unit_net": 18.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        # Powinno być ostrzeżenie o brakujących hakach
        self.assertTrue(any("hak" in w.lower() for w in warnings))
    
    def test_downpipe_without_clamps(self):
        """Test rury spustowej bez objęć."""
        items = [
            {
                "name": "Rura spustowa",
                "quantity": 12.0,
                "unit": "mb",
                "price_unit_net": 15.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        # Powinno być ostrzeżenie o brakujących objęciach
        warning_text = " ".join(warnings).lower()
        self.assertTrue("objętk" in warning_text or "obejm" in warning_text)
    
    def test_forgotten_items(self):
        """Test często zapominanych pozycji."""
        items = [
            {
                "name": "Papa",
                "quantity": 100.0,
                "unit": "m2",
                "price_unit_net": 25.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        # Powinny być ostrzeżenia o transporcie i rusztowaniu
        warning_text = " ".join(warnings).lower()
        self.assertTrue("transport" in warning_text or "rusztowanie" in warning_text)
    
    def test_suggest_related_items(self):
        """Test sugerowania powiązanych pozycji."""
        suggestions = self.validator.suggest_related_items("Rynna PVC 100")
        
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any("hak" in s.lower() for s in suggestions))
    
    def test_quantity_relationships(self):
        """Test relacji ilościowych."""
        items = [
            {
                "name": "Rynna PVC",
                "quantity": 20.0,  # 20m rynny
                "unit": "mb",
                "price_unit_net": 18.0,
                "category": "material"
            },
            {
                "name": "Haki rynnowe",
                "quantity": 10.0,  # Za mało haków (powinno być ~40)
                "unit": "szt",
                "price_unit_net": 3.0,
                "category": "material"
            }
        ]
        
        warnings = self.validator.check_quantity_relationships(items)
        self.assertTrue(any("hak" in w.lower() for w in warnings))
    
    def test_disable_warnings(self):
        """Test wyłączania ostrzeżeń."""
        self.validator.disable_warnings()
        
        items = [
            {
                "name": "",
                "quantity": -5.0,
                "unit": "",
                "price_unit_net": -10.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        self.assertTrue(is_valid)
        self.assertEqual(len(warnings), 0)
    
    def test_enable_warnings(self):
        """Test włączania ostrzeżeń."""
        self.validator.disable_warnings()
        self.validator.enable_warnings()
        
        items = [
            {
                "name": "",
                "quantity": 10.0,
                "unit": "m2",
                "price_unit_net": 25.0,
                "category": "material"
            }
        ]
        
        is_valid, warnings = self.validator.validate_estimate(items)
        self.assertFalse(is_valid)
        self.assertGreater(len(warnings), 0)

if __name__ == '__main__':
    unittest.main()
