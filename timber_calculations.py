# timber_calculations.py
import math

def calculate_timber_volume(quantity, length_m, width_cm, height_cm):
    """
    Oblicza objętość drewna dla pojedynczego elementu.

    Args:
        quantity (int): Liczba elementów.
        length_m (float): Długość pojedynczego elementu w metrach.
        width_cm (float): Szerokość przekroju w centymetrach.
        height_cm (float): Wysokość przekroju w centymetrach.

    Returns:
        float: Objętość drewna w metrach sześciennych (m3).
    """
    if quantity < 0 or length_m < 0 or width_cm < 0 or height_cm < 0:
        raise ValueError("Wartości dla ilości, długości i wymiarów przekroju nie mogą być ujemne.")
    
    width_m = width_cm / 100.0
    height_m = height_cm / 100.0
    
    return quantity * length_m * width_m * height_m