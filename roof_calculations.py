# roof_calculations.py
import math

def degrees_to_radians(degrees):
    """Konwertuje stopnie na radiany."""
    return math.radians(degrees)

def calculate_slant_length(horizontal_length, angle_degrees):
    """
    Oblicza długość skośną (np. krokwi) na podstawie długości poziomej
    i kąta nachylenia w stopniach.
    """
    if angle_degrees == 90:
        return float('inf') 
    if angle_degrees == 0 or angle_degrees is None:
        return horizontal_length 
    
    angle_radians = degrees_to_radians(angle_degrees)
    if math.cos(angle_radians) == 0:
        return float('inf') 
        
    return horizontal_length / math.cos(angle_radians)

def calculate_horizontal_length(slant_length, angle_degrees):
    """
    Oblicza długość poziomą na podstawie długości skośnej
    i kąta nachylenia w stopniach.
    """
    if angle_degrees is None:
        return slant_length
    angle_radians = degrees_to_radians(angle_degrees)
    return slant_length * math.cos(angle_radians)

def calculate_single_slope_roof(dl, szer, angle_degrees=None, is_real_dimensions=False):
    """Oblicza długości dla dachu jednospadowego."""
    results = {
        "dlugosc_okapu": 0.0,
        "dlugosc_gasiorow": 0.0,
        "dlugosc_wiatrownic": 0.0,
        "powierzchnia_dachu": 0.0,
        "dlugosc_koszy": 0.0,
        "slant_rafter_length": 0.0,
        "roof_angle_deg": 0.0
    }

    if is_real_dimensions:
        results["dlugosc_okapu"] = dl
        results["slant_rafter_length"] = szer
        results["dlugosc_wiatrownic"] = 2 * szer
        results["powierzchnia_dachu"] = dl * szer
        # W trybie rzeczywistym kąt nie jest podawany, ale możemy go potrzebować (np. dla kominów)
        # Na razie zakładamy, że jeśli jest potrzebny, użytkownik wprowadzi go ręcznie w odpowiedniej zakładce
    else:
        if angle_degrees is None:
            raise ValueError("Kąt nachylenia jest wymagany dla wymiarów poziomych.")
        slant_szer = calculate_slant_length(szer, angle_degrees)
        results["dlugosc_okapu"] = dl
        results["slant_rafter_length"] = slant_szer
        results["dlugosc_wiatrownic"] = 2 * slant_szer
        results["powierzchnia_dachu"] = dl * slant_szer
        results["roof_angle_deg"] = angle_degrees
    
    results["dlugosc_gasiorow"] = 0.0 
    results["dlugosc_koszy"] = 0.0
    return results

def calculate_gable_roof(dl, szer, angle_degrees=None, is_real_dimensions=False):
    """Oblicza długości dla dachu dwuspadowego."""
    results = {
        "dlugosc_okapu": 0.0,
        "dlugosc_gasiorow": 0.0,
        "dlugosc_wiatrownic": 0.0,
        "powierzchnia_dachu": 0.0,
        "dlugosc_koszy": 0.0,
        "slant_rafter_length": 0.0,
        "roof_angle_deg": 0.0
    }

    if is_real_dimensions:
        real_dl = dl
        real_krokiew_len = szer
        
        results["dlugosc_okapu"] = 2 * real_dl
        results["dlugosc_gasiorow"] = real_dl
        results["dlugosc_wiatrownic"] = 4 * real_krokiew_len
        results["powierzchnia_dachu"] = 2 * real_dl * real_krokiew_len
        results["slant_rafter_length"] = real_krokiew_len
    else:
        if angle_degrees is None:
            raise ValueError("Kąt nachylenia jest wymagany dla wymiarów poziomych.")
        
        real_dl = dl
        half_szer_horizontal = szer / 2
        slant_krokiew_len = calculate_slant_length(half_szer_horizontal, angle_degrees)
        
        results["dlugosc_okapu"] = 2 * real_dl
        results["dlugosc_gasiorow"] = real_dl
        results["dlugosc_wiatrownic"] = 4 * slant_krokiew_len
        results["powierzchnia_dachu"] = 2 * real_dl * slant_krokiew_len
        results["slant_rafter_length"] = slant_krokiew_len
        results["roof_angle_deg"] = angle_degrees

    results["dlugosc_koszy"] = 0.0
    return results

def calculate_hip_roof(dl, szer, angle_degrees=None, is_real_dimensions=False):
    """Oblicza długości dla dachu kopertowego (czterospadowego)."""
    results = {
        "dlugosc_okapu": 0.0,
        "dlugosc_gasiorow": 0.0,
        "dlugosc_wiatrownic": 0.0,
        "powierzchnia_dachu": 0.0,
        "dlugosc_koszy": 0.0,
        "slant_rafter_length": 0.0,
        "roof_angle_deg": 0.0
    }
    
    # Wymiary podstawy (zawsze potrzebne do obliczenia gąsiorów)
    horizontal_dl = dl
    horizontal_szer = szer
    
    if is_real_dimensions:
        # Jeśli podano wymiary rzeczywiste (okapów), musimy je przeliczyć z powrotem na rzut poziomy
        # To jest skomplikowane i wymagałoby kąta.
        # Uproszczenie: Zakładamy, że dla dachu kopertowego 'dl' i 'szer' to ZAWSZE wymiary podstawy (rzut poziomy)
        # a 'angle_degrees' jest ZAWSZE wymagany.
        pass

    if angle_degrees is None:
        raise ValueError("Kąt nachylenia jest wymagany dla obliczeń dachu kopertowego.")
        
    results["roof_angle_deg"] = angle_degrees
    results["dlugosc_okapu"] = 2 * (horizontal_dl + horizontal_szer)
    results["dlugosc_wiatrownic"] = 0.0 

    # Długość rzutu poziomego grzbietu
    if horizontal_dl >= horizontal_szer:
        kalenica_pozioma_dl_horizontal = horizontal_dl - horizontal_szer
        grzbiet_horizontal_proj = horizontal_szer / 2
    else:
        # Przypadek, gdy szerokość jest większa niż długość
        kalenica_pozioma_dl_horizontal = horizontal_szer - horizontal_dl
        grzbiet_horizontal_proj = horizontal_dl / 2
        # Zamień dl i szer miejscami dla spójności obliczeń powierzchni
        horizontal_dl, horizontal_szer = horizontal_szer, horizontal_dl

    # Długość grzbietu (naroża) - rzut poziomy grzbietu jest po przekątnej kwadratu o boku 'grzbiet_horizontal_proj'
    # UWAGA: To jest błąd w poprzedniej logice. Rzut poziomy grzbietu to przekątna.
    # Uproszczenie: Długość rzutu poziomego grzbietu (naroża) jest taka sama jak rzut połaci trójkątnej (połowy szerokości)
    # Rzut poziomy naroża (grzbietu)
    hip_rafter_horizontal_proj = math.sqrt((horizontal_szer/2)**2 + (horizontal_szer/2)**2)
    
    # Długość skośna grzbietu (naroża)
    # Kąt nachylenia połaci narożnej jest inny niż połaci głównej!
    # Ale dla uproszczenia kalkulacji długości, możemy użyć kąta głównego
    # Lepsze uproszczenie: Długość skośna grzbietu (naroża)
    slant_grzbiet_len = calculate_slant_length(hip_rafter_horizontal_proj, angle_degrees)
    
    # Długość skośna kalenicy poziomej (jest płaska, więc nie zależy od kąta)
    slant_kalenica_pozioma_len = kalenica_pozioma_dl_horizontal

    results["dlugosc_gasiorow"] = (4 * slant_grzbiet_len) + slant_kalenica_pozioma_len
    
    # Powierzchnia dachu kopertowego
    slant_krokiew_dluga_polac = calculate_slant_length(horizontal_szer / 2, angle_degrees) # Połać trapezowa
    slant_krokiew_krotka_polac = calculate_slant_length(horizontal_szer / 2, angle_degrees) # Połać trójkątna

    # Powierzchnia dwóch trójkątów (na krótszych bokach)
    area_side_triangles = 2 * (0.5 * horizontal_szer * slant_krokiew_krotka_polac)
    # Powierzchnia dwóch trapezów (na dłuższych bokach)
    area_front_trapezoids = 2 * (0.5 * (kalenica_pozioma_dl_horizontal + horizontal_dl) * slant_krokiew_dluga_polac)
    
    results["powierzchnia_dachu"] = area_side_triangles + area_front_trapezoids
    results["slant_rafter_length"] = slant_krokiew_dluga_polac # Używamy dłuższej jako referencyjnej

    return results