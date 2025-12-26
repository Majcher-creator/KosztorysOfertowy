# gutter_calculations.py
import math

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