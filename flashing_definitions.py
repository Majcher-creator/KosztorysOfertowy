# flashing_definitions.py
"""
Definicje obróbek blacharskich z parametrami i cenami.
"""
from typing import Dict, Any, List

# Materiały blachy
FLASHING_MATERIALS = {
    "Blacha powlekana": {
        "name": "Blacha powlekana",
        "price_multiplier": 1.0,
        "base_price_per_m2": 35.0
    },
    "Ocynk": {
        "name": "Ocynk",
        "price_multiplier": 0.85,
        "base_price_per_m2": 30.0
    },
    "Tytan-cynk": {
        "name": "Tytan-cynk",
        "price_multiplier": 2.0,
        "base_price_per_m2": 70.0
    },
    "Miedź": {
        "name": "Miedź",
        "price_multiplier": 4.0,
        "base_price_per_m2": 140.0
    },
    "Aluminium": {
        "name": "Aluminium",
        "price_multiplier": 1.5,
        "base_price_per_m2": 52.0
    }
}

# Predefiniowane obróbki blacharskie
PREDEFINED_FLASHINGS = {
    "Pas nadrynnowy": {
        "name": "Pas nadrynnowy",
        "description": "Obróbka nad rynną",
        "typical_width_cm": 25,
        "price_per_mb": 18.0,
        "unit": "mb",
        "category": "standard"
    },
    "Pas podrynnowy": {
        "name": "Pas podrynnowy",
        "description": "Obróbka pod rynną",
        "typical_width_cm": 25,
        "price_per_mb": 18.0,
        "unit": "mb",
        "category": "standard"
    },
    "Wiatrownica": {
        "name": "Wiatrownica",
        "description": "Obróbka ściany szczytowej",
        "typical_width_cm": 30,
        "price_per_mb": 22.0,
        "unit": "mb",
        "category": "standard"
    },
    "Kosz dachowy": {
        "name": "Kosz dachowy",
        "description": "Obróbka w koszu/narożu dachu",
        "typical_width_cm": 40,
        "price_per_mb": 35.0,
        "unit": "mb",
        "category": "standard"
    },
    "Obróbka komina": {
        "name": "Obróbka komina",
        "description": "Kompletna obróbka komina",
        "typical_width_cm": 35,
        "price_per_mb": 45.0,
        "unit": "mb",
        "category": "complex"
    },
    "Obróbka attyki": {
        "name": "Obróbka attyki",
        "description": "Obróbka górnej części attyki/murłaty",
        "typical_width_cm": 40,
        "price_per_mb": 40.0,
        "unit": "mb",
        "category": "standard"
    },
    "Gąsior/kalenica": {
        "name": "Gąsior/kalenica",
        "description": "Obróbka kalenicy dachu",
        "typical_width_cm": 35,
        "price_per_mb": 30.0,
        "unit": "mb",
        "category": "standard"
    },
    "Listwa przyścienna": {
        "name": "Listwa przyścienna",
        "description": "Obróbka przy ścianie",
        "typical_width_cm": 25,
        "price_per_mb": 20.0,
        "unit": "mb",
        "category": "standard"
    }
}

class FlashingDefinition:
    """Klasa reprezentująca definicję obróbki blacharskiej."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        width_cm: float = 25.0,
        material: str = "Blacha powlekana",
        price_per_mb: float = 0.0,
        price_per_m2: float = 0.0,
        unit: str = "mb",
        category: str = "custom"
    ):
        self.name = name
        self.description = description
        self.width_cm = width_cm
        self.material = material
        self.price_per_mb = price_per_mb
        self.price_per_m2 = price_per_m2
        self.unit = unit
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje definicję do słownika."""
        return {
            "name": self.name,
            "description": self.description,
            "width_cm": self.width_cm,
            "material": self.material,
            "price_per_mb": self.price_per_mb,
            "price_per_m2": self.price_per_m2,
            "unit": self.unit,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlashingDefinition':
        """Tworzy definicję ze słownika z walidacją."""
        # Walidacja danych wejściowych
        width_cm = float(data.get("width_cm", 25.0))
        if width_cm <= 0:
            raise ValueError(f"Szerokość musi być dodatnia, otrzymano: {width_cm}")
        
        price_per_mb = float(data.get("price_per_mb", 0.0))
        if price_per_mb < 0:
            raise ValueError(f"Cena nie może być ujemna, otrzymano: {price_per_mb}")
        
        price_per_m2 = float(data.get("price_per_m2", 0.0))
        if price_per_m2 < 0:
            raise ValueError(f"Cena nie może być ujemna, otrzymano: {price_per_m2}")
        
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            width_cm=width_cm,
            material=data.get("material", "Blacha powlekana"),
            price_per_mb=price_per_mb,
            price_per_m2=price_per_m2,
            unit=data.get("unit", "mb"),
            category=data.get("category", "custom")
        )
    
    def calculate_price(self, length_m: float) -> float:
        """
        Oblicza cenę dla danej długości obróbki.
        
        Args:
            length_m: Długość obróbki w metrach
            
        Returns:
            Całkowita cena netto
        """
        if self.unit == "mb":
            return length_m * self.price_per_mb
        elif self.unit == "m2":
            area_m2 = length_m * (self.width_cm / 100.0)
            return area_m2 * self.price_per_m2
        else:
            return 0.0
    
    def calculate_material_needed(self, length_m: float) -> float:
        """
        Oblicza potrzebną powierzchnię materiału w m².
        
        Args:
            length_m: Długość obróbki w metrach
            
        Returns:
            Powierzchnia w m²
        """
        return length_m * (self.width_cm / 100.0)

def get_predefined_flashings() -> List[str]:
    """Zwraca listę nazw predefiniowanych obróbek."""
    return list(PREDEFINED_FLASHINGS.keys())

def get_flashing_definition(name: str) -> FlashingDefinition:
    """
    Zwraca definicję obróbki na podstawie nazwy.
    
    Args:
        name: Nazwa obróbki
        
    Returns:
        FlashingDefinition
        
    Raises:
        KeyError: Jeśli obróbka nie istnieje
    """
    if name not in PREDEFINED_FLASHINGS:
        raise KeyError(f"Nieznana obróbka: {name}")
    
    data = PREDEFINED_FLASHINGS[name]
    return FlashingDefinition(
        name=data["name"],
        description=data["description"],
        width_cm=data["typical_width_cm"],
        price_per_mb=data["price_per_mb"],
        unit=data["unit"],
        category=data["category"]
    )

def get_material_names() -> List[str]:
    """Zwraca listę nazw dostępnych materiałów."""
    return list(FLASHING_MATERIALS.keys())

def get_material_price(material: str) -> float:
    """
    Zwraca cenę bazową materiału za m².
    
    Args:
        material: Nazwa materiału
        
    Returns:
        Cena za m²
        
    Raises:
        KeyError: Jeśli materiał nie istnieje
    """
    if material not in FLASHING_MATERIALS:
        raise KeyError(f"Nieznany materiał: {material}")
    
    return FLASHING_MATERIALS[material]["base_price_per_m2"]

def calculate_flashing_cost(
    flashing_name: str,
    length_m: float,
    material: str = "Blacha powlekana",
    custom_width_cm: float = None,
    custom_price_per_mb: float = None
) -> Dict[str, Any]:
    """
    Oblicza koszt obróbki blacharskiej.
    
    Args:
        flashing_name: Nazwa obróbki
        length_m: Długość w metrach
        material: Rodzaj materiału
        custom_width_cm: Niestandardowa szerokość (opcjonalnie)
        custom_price_per_mb: Niestandardowa cena za mb (opcjonalnie)
        
    Returns:
        Słownik z danymi obróbki i kosztem
    """
    flashing = get_flashing_definition(flashing_name)
    
    if custom_width_cm is not None:
        flashing.width_cm = custom_width_cm
    
    if custom_price_per_mb is not None:
        flashing.price_per_mb = custom_price_per_mb
    
    flashing.material = material
    
    # Oblicz koszt
    total_cost = flashing.calculate_price(length_m)
    material_area = flashing.calculate_material_needed(length_m)
    
    return {
        "name": f"{flashing.name} - {material}",
        "quantity": length_m,
        "unit": flashing.unit,
        "price_unit_net": flashing.price_per_mb if flashing.unit == "mb" else flashing.price_per_m2,
        "total_net": total_cost,
        "material": material,
        "width_cm": flashing.width_cm,
        "material_area_m2": material_area,
        "description": flashing.description
    }
