# felt_calculations.py
import math

def calculate_felt_roof(roof_surface_m2, roof_type, is_tear_off,
                       is_decking=False, is_osb_on_battens=False, is_concrete=False,
                       chimney_felt_surface_m2=0.0,
                       firewall_length_m=0.0, firewall_height_m=0.0, firewall_thickness_m=0.0):
    """
    Oblicza potrzebne materiały dla pokrycia papowego.
    """
    if roof_surface_m2 < 0:
        raise ValueError("Powierzchnia dachu nie może być ujemna.")
    
    if roof_surface_m2 == 0 and chimney_felt_surface_m2 == 0 and firewall_length_m == 0:
         return {
            "total_top_felt_m2": 0.0,
            "total_underlay_felt_m2": 0.0,
            "decking_m2": 0.0,
            "osb_m2": 0.0,
            "concrete_topping_m3": 0.0, # Zmieniono na m3
            "primer_liters": 0.0,
            "firewall_osb_m2": 0.0,
            "firewall_felt_m2": 0.0
        }

    # 1. Współczynnik zużycia papy
    if roof_type in ["jednospadowy", "dwuspadowy"]:
        felt_waste_factor = 1.15
    else: # kopertowy, niestandardowy
        felt_waste_factor = 1.18

    # 2. Papa wierzchniego krycia
    total_top_felt_m2 = roof_surface_m2 * felt_waste_factor

    # 3. Papa podkładowa
    total_underlay_felt_m2 = 0.0
    if not is_concrete:
        total_underlay_felt_m2 = roof_surface_m2 * felt_waste_factor

    # 4. Materiały podłoża
    decking_m2 = 0.0
    osb_m2 = 0.0
    concrete_topping_m3 = 0.0 # Objętość w m3
    primer_liters = 0.0

    if is_tear_off:
        if is_decking:
            decking_m2 = roof_surface_m2 * 0.30 # 30% wymiana
        elif is_concrete:
            primer_liters = roof_surface_m2 * 0.2 # Gruntowanie
            # 20% powierzchni x 3cm (0.03m) grubości wylewki
            concrete_topping_m3 = (roof_surface_m2 * 0.20) * 0.03 
    else: # Nowy dach
        if is_decking:
            decking_m2 = roof_surface_m2 * 1.0 # Pełne deskowanie
        elif is_osb_on_battens:
            osb_m2 = roof_surface_m2 * 1.0 # Pełna płyta OSB
        elif is_concrete:
            primer_liters = roof_surface_m2 * 0.2 # Gruntowanie

    # 5. Ogniomury / Gzymsy
    firewall_osb_m2 = 0.0
    firewall_felt_m2 = 0.0
    
    if firewall_length_m > 0 and firewall_height_m > 0 and firewall_thickness_m > 0:
        # Powierzchnia OSB (2 boki)
        firewall_osb_m2 = firewall_length_m * firewall_height_m * 2
        
        # Papa (2 boki + góra + zakład na dach)
        felt_developed_width_for_firewall = (2 * firewall_height_m) + firewall_thickness_m + 0.15
        firewall_felt_m2 = firewall_length_m * felt_developed_width_for_firewall

    # 6. Sumowanie papy (dach + kominy + ogniomury)
    total_top_felt_m2 += chimney_felt_surface_m2 + firewall_felt_m2
    if total_underlay_felt_m2 > 0:
        total_underlay_felt_m2 += chimney_felt_surface_m2 + firewall_felt_m2

    return {
        "total_top_felt_m2": total_top_felt_m2,
        "total_underlay_felt_m2": total_underlay_felt_m2,
        "decking_m2": decking_m2,
        "osb_m2": osb_m2,
        "concrete_topping_m3": concrete_topping_m3,
        "primer_liters": primer_liters,
        "firewall_osb_m2": firewall_osb_m2,
        "firewall_felt_m2": firewall_felt_m2
    }