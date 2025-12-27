# tests/test_gutters.py
"""
Testy dla modułu gutter_calculations.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from gutter_calculations import (
    calculate_guttering,
    calculate_guttering_advanced,
    get_system_names,
    get_system_prices,
    GUTTER_SYSTEMS
)

class TestGutterCalculations(unittest.TestCase):
    """Testy dla podstawowych obliczeń orynnowania."""
    
    def test_basic_calculation(self):
        """Test podstawowego obliczenia orynnowania."""
        result = calculate_guttering(okap_length_m=20.0, roof_height_m=6.0)
        
        self.assertEqual(result["total_gutter_length_m"], 20.0)
        self.assertEqual(result["num_downpipes"], 2)
        self.assertEqual(result["total_downpipe_length_m"], 12.0)
        self.assertGreater(result["num_gutter_hooks"], 0)
        self.assertGreater(result["num_downpipe_elbows"], 0)
    
    def test_negative_values(self):
        """Test czy funkcja odrzuca ujemne wartości."""
        with self.assertRaises(ValueError):
            calculate_guttering(okap_length_m=-10.0, roof_height_m=6.0)
        
        with self.assertRaises(ValueError):
            calculate_guttering(okap_length_m=10.0, roof_height_m=-6.0)
    
    def test_zero_length(self):
        """Test dla zerowej długości okapu."""
        result = calculate_guttering(okap_length_m=0.0, roof_height_m=6.0)
        
        self.assertEqual(result["total_gutter_length_m"], 0.0)
        self.assertEqual(result["num_downpipes"], 0)
        self.assertEqual(result["num_gutter_hooks"], 0)
    
    def test_manual_downpipes(self):
        """Test z ręcznie określoną liczbą rur spustowych."""
        result = calculate_guttering(okap_length_m=30.0, roof_height_m=6.0, num_downpipes=4)
        
        self.assertEqual(result["num_downpipes"], 4)
        self.assertEqual(result["total_downpipe_length_m"], 24.0)

class TestAdvancedGutterCalculations(unittest.TestCase):
    """Testy dla zaawansowanych obliczeń orynnowania."""
    
    def test_system_calculation(self):
        """Test obliczenia dla konkretnego systemu."""
        result = calculate_guttering_advanced(
            okap_length_m=20.0,
            roof_height_m=6.0,
            system="PVC 100"
        )
        
        self.assertEqual(result["system"], "PVC 100")
        self.assertIn("items", result)
        self.assertGreater(len(result["items"]), 0)
        self.assertGreater(result["total_net"], 0)
    
    def test_manual_accessories(self):
        """Test z ręcznie wprowadzonymi akcesoriami."""
        manual = {
            "elbows": 10,
            "tees": 2,
            "corners_inner": 1,
            "corners_outer": 2
        }
        
        result = calculate_guttering_advanced(
            okap_length_m=20.0,
            roof_height_m=6.0,
            system="PVC 125",
            manual_accessories=manual
        )
        
        self.assertEqual(result["manual_accessories"]["elbows"], 10)
        self.assertEqual(result["manual_accessories"]["tees"], 2)
    
    def test_invalid_system(self):
        """Test dla nieistniejącego systemu."""
        with self.assertRaises(ValueError):
            calculate_guttering_advanced(
                okap_length_m=20.0,
                roof_height_m=6.0,
                system="Nieistniejący System"
            )
    
    def test_all_systems_available(self):
        """Test czy wszystkie systemy są dostępne."""
        systems = get_system_names()
        
        self.assertIn("PVC 100", systems)
        self.assertIn("Metal", systems)
        self.assertIn("Miedź", systems)
        self.assertGreater(len(systems), 5)
    
    def test_system_prices(self):
        """Test pobierania cen systemu."""
        prices = get_system_prices("PVC 100")
        
        self.assertIn("gutter_mb", prices)
        self.assertIn("downpipe_mb", prices)
        self.assertGreater(prices["gutter_mb"], 0)

if __name__ == '__main__':
    unittest.main()
