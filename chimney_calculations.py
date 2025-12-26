# chimney_calculations.py
import math

def calculate_chimney_flashings(width_m, length_m, height_above_roof_m, roof_angle_deg, roof_covering_type, num_chimneys=1):
    """
    Oblicza potrzebne materiały do obróbki komina.
    """
    if any(val < 0 for val in [width_m, length_m, height_above_roof_m, num_chimneys]):
        raise ValueError("Wszystkie wymiary komina i liczba kominów nie mogą być ujemne.")
    if roof_angle_deg < 0 or roof_angle_deg > 90:
        raise ValueError("Kąt nachylenia dachu musi być w zakresie od 0 do 90 stopni.")
    
    # Jeśli wymiary = 0, zwróć 0
    if width_m == 0 or length_m == 0 or height_above_roof_m == 0 or num_chimneys == 0:
        return {
            "total_metal_flashing_surface_m2": 0.0,
            "num_metal_sheets_flashing": 0,
            "total_chimney_cap_surface_m2": 0.0,
            "num_metal_sheets_cap": 0,
            "total_felt_flashing_surface_m2": 0.0,
            "total_clamping_strip_length_m": 0.0,
            "single_chimney_perimeter": 0.0
        }

    perimeter = 2 * (width_m + length_m)
    
    # Uproszczenie: kołnierz dolny
    lower_flashing_developed_width_m = 0.5 
    lower_flashing_length_m = perimeter 
    lower_flashing_surface_m2 = lower_flashing_length_m * lower_flashing_developed_width_m

    # Uproszczenie: Oblachowanie boczne na rąbek
    side_flashing_height_with_overlap = height_above_roof_m + 0.20 
    cladding_surface_m2 = perimeter * side_flashing_height_with_overlap

    # Czapa kominowa
    cap_width_with_overlap = width_m + 2 * 0.05 
    cap_length_with_overlap = length_m + 2 * 0.05 
    chimney_cap_surface_m2 = cap_width_with_overlap * cap_length_with_overlap

    # Papa i listwa dociskowa
    felt_flashing_developed_width_m = 0.5 
    felt_flashing_length_m = perimeter
    felt_flashing_surface_m2 = felt_flashing_length_m * felt_flashing_developed_width_m
    clamping_strip_length_m = perimeter

    # Sumowanie
    total_lower_flashing_surface_m2 = lower_flashing_surface_m2 * num_chimneys
    total_cladding_surface_m2 = cladding_surface_m2 * num_chimneys
    total_chimney_cap_surface_m2 = chimney_cap_surface_m2 * num_chimneys
    total_felt_flashing_surface_m2 = felt_flashing_surface_m2 * num_chimneys
    total_clamping_strip_length_m = clamping_strip_length_m * num_chimneys

    sheet_area = 1.25 * 2.5
    
    total_metal_flashing_surface_m2 = total_lower_flashing_surface_m2 + total_cladding_surface_m2
    num_metal_sheets_flashing = math.ceil(total_metal_flashing_surface_m2 / sheet_area)
    num_metal_sheets_cap = math.ceil(total_chimney_cap_surface_m2 / sheet_area)
    
    if roof_covering_type == "blacha" or roof_covering_type == "dachówka":
        total_felt_flashing_surface_m2 = 0.0
        total_clamping_strip_length_m = 0.0

    return {
        "total_metal_flashing_surface_m2": total_metal_flashing_surface_m2,
        "num_metal_sheets_flashing": num_metal_sheets_flashing,
        "total_chimney_cap_surface_m2": total_chimney_cap_surface_m2,
        "num_metal_sheets_cap": num_metal_sheets_cap,
        "total_felt_flashing_surface_m2": total_felt_flashing_surface_m2,
        "total_clamping_strip_length_m": total_clamping_strip_length_m,
        "single_chimney_perimeter": perimeter
    }

def calculate_chimney_insulation(width_m, length_m, height_above_roof_m, num_chimneys=1):
    """
    Oblicza powierzchnię do ocieplenia komina i siatki z klejem.
    """
    if any(val <= 0 for val in [width_m, length_m, height_above_roof_m, num_chimneys]):
        return {
            "total_insulation_surface_m2": 0.0,
            "total_mesh_surface_m2": 0.0
        }

    single_chimney_side_surface = 2 * (width_m + length_m) * height_above_roof_m
    total_insulation_surface_m2 = single_chimney_side_surface * num_chimneys
    total_mesh_surface_m2 = total_insulation_surface_m2

    return {
        "total_insulation_surface_m2": total_insulation_surface_m2,
        "total_mesh_surface_m2": total_mesh_surface_m2
    }