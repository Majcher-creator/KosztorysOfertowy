# gutter_calculations.py
import math
from typing import Dict, Any, Optional

# Predefined guttering systems with default prices
GUTTER_SYSTEMS = {
    "PVC 75": {
        "name": "PVC 75mm",
        "diameter": 75,
        "material": "PVC",
        "prices": {
            "gutter_mb": 15.0,
            "downpipe_mb": 12.0,
            "gutter_hook": 2.5,
            "gutter_connector": 4.0,
            "downpipe_outlet": 8.0,
            "downpipe_clamp": 3.5,
            "downpipe_elbow": 5.0,
            "end_cap": 3.0,
            "tee": 12.0,
            "corner_inner": 15.0,
            "corner_outer": 15.0,
            "funnel": 10.0
        }
    },
    "PVC 100": {
        "name": "PVC 100mm",
        "diameter": 100,
        "material": "PVC",
        "prices": {
            "gutter_mb": 18.0,
            "downpipe_mb": 15.0,
            "gutter_hook": 3.0,
            "gutter_connector": 5.0,
            "downpipe_outlet": 10.0,
            "downpipe_clamp": 4.0,
            "downpipe_elbow": 6.0,
            "end_cap": 3.5,
            "tee": 15.0,
            "corner_inner": 18.0,
            "corner_outer": 18.0,
            "funnel": 12.0
        }
    },
    "PVC 125": {
        "name": "PVC 125mm",
        "diameter": 125,
        "material": "PVC",
        "prices": {
            "gutter_mb": 22.0,
            "downpipe_mb": 18.0,
            "gutter_hook": 3.5,
            "gutter_connector": 6.0,
            "downpipe_outlet": 12.0,
            "downpipe_clamp": 4.5,
            "downpipe_elbow": 7.0,
            "end_cap": 4.0,
            "tee": 18.0,
            "corner_inner": 22.0,
            "corner_outer": 22.0,
            "funnel": 15.0
        }
    },
    "PVC 150": {
        "name": "PVC 150mm",
        "diameter": 150,
        "material": "PVC",
        "prices": {
            "gutter_mb": 28.0,
            "downpipe_mb": 22.0,
            "gutter_hook": 4.0,
            "gutter_connector": 8.0,
            "downpipe_outlet": 15.0,
            "downpipe_clamp": 5.0,
            "downpipe_elbow": 9.0,
            "end_cap": 5.0,
            "tee": 22.0,
            "corner_inner": 28.0,
            "corner_outer": 28.0,
            "funnel": 18.0
        }
    },
    "Metal": {
        "name": "Metal/Tytan-cynk",
        "diameter": 125,
        "material": "Metal",
        "prices": {
            "gutter_mb": 45.0,
            "downpipe_mb": 35.0,
            "gutter_hook": 5.0,
            "gutter_connector": 12.0,
            "downpipe_outlet": 20.0,
            "downpipe_clamp": 6.0,
            "downpipe_elbow": 15.0,
            "end_cap": 8.0,
            "tee": 30.0,
            "corner_inner": 35.0,
            "corner_outer": 35.0,
            "funnel": 25.0
        }
    },
    "Ocynk": {
        "name": "Ocynk",
        "diameter": 125,
        "material": "Ocynk",
        "prices": {
            "gutter_mb": 35.0,
            "downpipe_mb": 28.0,
            "gutter_hook": 4.0,
            "gutter_connector": 10.0,
            "downpipe_outlet": 15.0,
            "downpipe_clamp": 5.0,
            "downpipe_elbow": 12.0,
            "end_cap": 6.0,
            "tee": 25.0,
            "corner_inner": 30.0,
            "corner_outer": 30.0,
            "funnel": 20.0
        }
    },
    "Kwadrat": {
        "name": "Kwadrat/prostokątny",
        "diameter": 100,
        "material": "PVC",
        "prices": {
            "gutter_mb": 25.0,
            "downpipe_mb": 20.0,
            "gutter_hook": 3.5,
            "gutter_connector": 8.0,
            "downpipe_outlet": 12.0,
            "downpipe_clamp": 5.0,
            "downpipe_elbow": 10.0,
            "end_cap": 5.0,
            "tee": 20.0,
            "corner_inner": 25.0,
            "corner_outer": 25.0,
            "funnel": 15.0
        }
    },
    "Miedź": {
        "name": "Miedź",
        "diameter": 125,
        "material": "Miedź",
        "prices": {
            "gutter_mb": 120.0,
            "downpipe_mb": 95.0,
            "gutter_hook": 12.0,
            "gutter_connector": 25.0,
            "downpipe_outlet": 40.0,
            "downpipe_clamp": 15.0,
            "downpipe_elbow": 35.0,
            "end_cap": 18.0,
            "tee": 65.0,
            "corner_inner": 80.0,
            "corner_outer": 80.0,
            "funnel": 55.0
        }
    }
}

def calculate_guttering(okap_length_m, roof_height_m, num_downpipes=None):
    """
    Oblicza potrzebne orynnowanie, rury spustowe i akcesoria.

    Args:
        okap_length_m (float): Całkowita długość okapu dachu w metrach.
        roof_height_m (float): Wysokość dachu od okapu do ziemi w metrach (długość pojedynczej rury spustowej).
        num_downpipes (int, optional): Liczba rur spustowych. Jeśli None, zostanie oszacowana.

    Returns:
        dict: Słownik z długościami rynien, rur, oraz szacowaną liczbą akcesoriów.
    """
    if okap_length_m < 0 or roof_height_m < 0:
        raise ValueError("Długość okapu i wysokość dachu nie mogą być ujemne.")
    
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

    num_gutter_hooks = math.ceil(total_gutter_length_m / 0.5) if total_gutter_length_m > 0 else 0
    num_gutter_connectors = max(0, math.ceil(total_gutter_length_m / 3.0) - 1)
    num_downpipe_outlets = actual_num_downpipes
    num_downpipe_clamps = math.ceil(total_downpipe_length_m / 2.0) if total_downpipe_length_m > 0 else 0
    num_downpipe_elbows = actual_num_downpipes * 2
    num_end_caps = 2 # Uproszczenie: minimum 2 zaślepki

    return {
        "total_gutter_length_m": total_gutter_length_m,
        "total_downpipe_length_m": total_downpipe_length_m,
        "num_downpipes": actual_num_downpipes,
        "num_gutter_hooks": num_gutter_hooks,
        "num_gutter_connectors": num_gutter_connectors,
        "num_downpipe_outlets": num_downpipe_outlets,
        "num_downpipe_clamps": num_downpipe_clamps,
        "num_downpipe_elbows": num_downpipe_elbows,
        "num_end_caps": num_end_caps
    }

def calculate_guttering_advanced(
    okap_length_m: float,
    roof_height_m: float,
    system: str = "PVC 100",
    num_downpipes: Optional[int] = None,
    manual_accessories: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Zaawansowane obliczenie orynnowania z wyborem systemu i ręcznym wprowadzeniem akcesoriów.
    
    Args:
        okap_length_m: Długość okapu w metrach
        roof_height_m: Wysokość dachu w metrach
        system: Nazwa systemu orynnowania
        num_downpipes: Liczba rur spustowych (opcjonalnie)
        manual_accessories: Słownik z ręcznie wprowadzonymi ilościami akcesoriów:
            {
                "elbows": int,
                "tees": int,
                "corners_inner": int,
                "corners_outer": int,
                "end_caps_left": int,
                "end_caps_right": int,
                "funnels": int
            }
    
    Returns:
        Dict z obliczonymi ilościami i cenami
    """
    if system not in GUTTER_SYSTEMS:
        raise ValueError(f"Nieznany system: {system}")
    
    system_data = GUTTER_SYSTEMS[system]
    prices = system_data["prices"]
    
    # Podstawowe obliczenia
    base_calc = calculate_guttering(okap_length_m, roof_height_m, num_downpipes)
    
    # Akcesoria - używaj ręcznych wartości jeśli podano, w przeciwnym razie automatyczne
    if manual_accessories is None:
        manual_accessories = {}
    
    num_elbows = manual_accessories.get("elbows", base_calc["num_downpipe_elbows"])
    num_tees = manual_accessories.get("tees", 0)
    num_corners_inner = manual_accessories.get("corners_inner", 0)
    num_corners_outer = manual_accessories.get("corners_outer", 0)
    num_end_caps_left = manual_accessories.get("end_caps_left", 0)
    num_end_caps_right = manual_accessories.get("end_caps_right", 0)
    total_end_caps = num_end_caps_left + num_end_caps_right or base_calc["num_end_caps"]
    num_funnels = manual_accessories.get("funnels", 0)
    
    # Oblicz koszty
    items = []
    total_net = 0.0
    
    # Rynny
    if base_calc["total_gutter_length_m"] > 0:
        gutter_cost = base_calc["total_gutter_length_m"] * prices["gutter_mb"]
        items.append({
            "name": f"Rynna {system_data['name']}",
            "quantity": base_calc["total_gutter_length_m"],
            "unit": "mb",
            "price_unit_net": prices["gutter_mb"],
            "total_net": gutter_cost
        })
        total_net += gutter_cost
    
    # Rury spustowe
    if base_calc["total_downpipe_length_m"] > 0:
        downpipe_cost = base_calc["total_downpipe_length_m"] * prices["downpipe_mb"]
        items.append({
            "name": f"Rura spustowa {system_data['name']}",
            "quantity": base_calc["total_downpipe_length_m"],
            "unit": "mb",
            "price_unit_net": prices["downpipe_mb"],
            "total_net": downpipe_cost
        })
        total_net += downpipe_cost
    
    # Akcesoria
    accessories = [
        ("Hak rynnowy", base_calc["num_gutter_hooks"], "szt", prices["gutter_hook"]),
        ("Łącznik rynien", base_calc["num_gutter_connectors"], "szt", prices["gutter_connector"]),
        ("Wpust rynnowy", base_calc["num_downpipe_outlets"], "szt", prices["downpipe_outlet"]),
        ("Objętka rury spustowej", base_calc["num_downpipe_clamps"], "szt", prices["downpipe_clamp"]),
        ("Kolano rury spustowej", num_elbows, "szt", prices["downpipe_elbow"]),
        ("Zaślepka rynny", total_end_caps, "szt", prices["end_cap"]),
    ]
    
    if num_tees > 0:
        accessories.append(("Trójnik", num_tees, "szt", prices["tee"]))
    if num_corners_inner > 0:
        accessories.append(("Narożnik wewnętrzny", num_corners_inner, "szt", prices["corner_inner"]))
    if num_corners_outer > 0:
        accessories.append(("Narożnik zewnętrzny", num_corners_outer, "szt", prices["corner_outer"]))
    if num_funnels > 0:
        accessories.append(("Lejek/wpust", num_funnels, "szt", prices["funnel"]))
    
    for name, qty, unit, price in accessories:
        if qty > 0:
            cost = qty * price
            items.append({
                "name": f"{name} {system_data['name']}",
                "quantity": qty,
                "unit": unit,
                "price_unit_net": price,
                "total_net": cost
            })
            total_net += cost
    
    return {
        "system": system,
        "system_name": system_data["name"],
        "items": items,
        "total_net": total_net,
        "base_calculations": base_calc,
        "manual_accessories": {
            "elbows": num_elbows,
            "tees": num_tees,
            "corners_inner": num_corners_inner,
            "corners_outer": num_corners_outer,
            "end_caps": total_end_caps,
            "funnels": num_funnels
        }
    }

def get_system_names() -> list:
    """Zwraca listę nazw dostępnych systemów orynnowania."""
    return list(GUTTER_SYSTEMS.keys())

def get_system_prices(system: str) -> Dict[str, float]:
    """Zwraca cennik dla danego systemu."""
    if system not in GUTTER_SYSTEMS:
        raise ValueError(f"Nieznany system: {system}")
    return GUTTER_SYSTEMS[system]["prices"].copy()

def update_system_prices(system: str, prices: Dict[str, float]):
    """Aktualizuje ceny dla danego systemu."""
    if system not in GUTTER_SYSTEMS:
        raise ValueError(f"Nieznany system: {system}")
    GUTTER_SYSTEMS[system]["prices"].update(prices)