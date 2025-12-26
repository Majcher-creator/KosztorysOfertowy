# flashing_calculations.py
import math

def calculate_flashings_total(flashing_items, standard_sheet_width=1.25, standard_sheet_length=2.50):
    """
    Oblicza całkowitą powierzchnię blachy i liczbę arkuszy potrzebnych na obróbki.

    Args:
        flashing_items (dict): Słownik, gdzie kluczem jest nazwa obróbki, a wartością
                               słownik z danymi: {"selected": bool, "length": float, "width": float}.
        standard_sheet_width (float): Szerokość standardowego arkusza blachy w metrach.
        standard_sheet_length (float): Długość standardowego arkusza blachy w metrach.

    Returns:
        dict: Słownik z całkowitą powierzchnią blachy i liczbą potrzebnych arkuszy.
    """
    total_flashing_surface = 0.0
    standard_sheet_area = standard_sheet_width * standard_sheet_length

    for name, data in flashing_items.items():
        if data["selected"]: 
            length = data["length"]
            width = data["width"]
            
            if length < 0 or width < 0:
                raise ValueError(f"Długość i szerokość obróbki '{name}' nie mogą być ujemne.")

            total_flashing_surface += length * width
    
    num_sheets = math.ceil(total_flashing_surface / standard_sheet_area) if total_flashing_surface > 0 else 0

    return {
        "total_surface_m2": total_flashing_surface,
        "num_sheets": int(num_sheets)
    }