# gutter_calculations.py
import math
import json
import os

# Default gutter systems with pricing
GUTTER_SYSTEMS = {
    "PVC 75": {"diameter": 75, "price_per_meter": 0.0, "description": "PVC 75mm"},
    "PVC 100": {"diameter": 100, "price_per_meter": 0.0, "description": "PVC 100mm"},
    "PVC 125": {"diameter": 125, "price_per_meter": 0.0, "description": "PVC 125mm"},
    "PVC 150": {"diameter": 150, "price_per_meter": 0.0, "description": "PVC 150mm"},
    "Metal/Tytan-cynk": {"diameter": 125, "price_per_meter": 0.0, "description": "Metal/Tytan-cynk"},
    "Ocynk": {"diameter": 125, "price_per_meter": 0.0, "description": "Ocynk"},
    "Kwadrat": {"diameter": 100, "price_per_meter": 0.0, "description": "System kwadratowy"},
    "Miedź": {"diameter": 125, "price_per_meter": 0.0, "description": "Miedź"},
}

def calculate_guttering(okap_length_m, roof_height_m, num_downpipes=None, 
                       manual_quantities=None, system_type="PVC 125"):
    """
    Oblicza potrzebne orynnowanie, rury spustowe i akcesoria.

    Args:
        okap_length_m (float): Całkowita długość okapu dachu w metrach.
        roof_height_m (float): Wysokość dachu od okapu do ziemi w metrach (długość pojedynczej rury spustowej).
        num_downpipes (int, optional): Liczba rur spustowych. Jeśli None, zostanie oszacowana.
        manual_quantities (dict, optional): Ręcznie wprowadzone ilości elementów.
        system_type (str): Typ systemu orynnowania.

    Returns:
        dict: Słownik z długościami rynien, rur, oraz szacowaną liczbą akcesoriów.
    """
    if okap_length_m < 0 or roof_height_m < 0:
        raise ValueError("Długość okapu i wysokość dachu nie mogą być ujemne.")
    
    # Initialize manual quantities if not provided
    if manual_quantities is None:
        manual_quantities = {}
    
    total_gutter_length_m = okap_length_m

    if num_downpipes is None:
        if okap_length_m > 0:
            estimated_downpipes = math.ceil(okap_length_m / 10.0)
            if estimated_downpipes < 1: 
                estimated_downpipes = 1
        else:
            estimated_downpipes = 0
        actual_num_downpipes = estimated_downpipes
    else:
        actual_num_downpipes = num_downpipes
    
    if actual_num_downpipes < 0:
        raise ValueError("Liczba rur spustowych nie może być ujemna.")

    total_downpipe_length_m = actual_num_downpipes * roof_height_m

    # Calculate or use manual quantities
    num_gutter_hooks = manual_quantities.get("hooks", math.ceil(total_gutter_length_m / 0.5) if total_gutter_length_m > 0 else 0)
    num_gutter_connectors = manual_quantities.get("connectors", max(0, math.ceil(total_gutter_length_m / 3.0) - 1))
    num_downpipe_outlets = manual_quantities.get("outlets", actual_num_downpipes)
    num_downpipe_clamps = manual_quantities.get("clamps", math.ceil(total_downpipe_length_m / 2.0) if total_downpipe_length_m > 0 else 0)
    num_downpipe_elbows = manual_quantities.get("elbows", actual_num_downpipes * 2)
    num_end_caps = manual_quantities.get("end_caps", 2)
    
    # Additional manual elements
    num_corners_internal = manual_quantities.get("corners_internal", 0)
    num_corners_external = manual_quantities.get("corners_external", 0)
    num_end_caps_left = manual_quantities.get("end_caps_left", 0)
    num_end_caps_right = manual_quantities.get("end_caps_right", 0)
    num_funnels = manual_quantities.get("funnels", 0)

    return {
        "total_gutter_length_m": total_gutter_length_m,
        "total_downpipe_length_m": total_downpipe_length_m,
        "num_downpipes": actual_num_downpipes,
        "num_gutter_hooks": num_gutter_hooks,
        "num_gutter_connectors": num_gutter_connectors,
        "num_downpipe_outlets": num_downpipe_outlets,
        "num_downpipe_clamps": num_downpipe_clamps,
        "num_downpipe_elbows": num_downpipe_elbows,
        "num_end_caps": num_end_caps,
        "num_corners_internal": num_corners_internal,
        "num_corners_external": num_corners_external,
        "num_end_caps_left": num_end_caps_left,
        "num_end_caps_right": num_end_caps_right,
        "num_funnels": num_funnels,
        "system_type": system_type,
        "system_info": GUTTER_SYSTEMS.get(system_type, GUTTER_SYSTEMS["PVC 125"])
    }

def load_gutter_system_prices(config_path):
    """Load custom gutter system prices from JSON file"""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return GUTTER_SYSTEMS.copy()
    return GUTTER_SYSTEMS.copy()

def save_gutter_system_prices(config_path, systems):
    """Save gutter system prices to JSON file"""
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(systems, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False