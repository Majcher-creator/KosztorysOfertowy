# validators.py
"""
Walidacja kosztorysów i ostrzeżenia o brakujących materiałach.
"""
from typing import List, Dict, Any, Tuple

class CostEstimateValidator:
    """Klasa do walidacji kosztorysów i generowania ostrzeżeń."""
    
    def __init__(self):
        self.warnings_enabled = True
        
        # Definicje zależności materiałowych
        self.material_dependencies = {
            "rynna": {
                "keywords": ["rynna", "rynien"],
                "requires": [
                    {"keywords": ["hak", "haki rynnowe"], "name": "Haki rynnowe"}
                ],
                "hooks_per_meter": 2.0  # haki na metr rynny (co 0.5m)
            },
            "rura spustowa": {
                "keywords": ["rura spustowa", "rury spustowe"],
                "requires": [
                    {"keywords": ["objętka", "obejma", "objęcia"], "name": "Objętki/obejmy rury spustowej"}
                ],
                "clamps_per_meter": 0.5  # objętki na metr rury (co 2m)
            },
            "papa": {
                "keywords": ["papa"],
                "requires": [
                    {"keywords": ["klej", "kit", "masa"], "name": "Klej/kit do papy"},
                    {"keywords": ["gruntowanie", "gruntownik"], "name": "Gruntowanie powierzchni"}
                ]
            },
            "blacha": {
                "keywords": ["blacha", "obróbka"],
                "requires": [
                    {"keywords": ["montaż", "układanie"], "name": "Montaż obróbek blacharskich"}
                ]
            }
        }
        
        # Często zapominane pozycje
        self.common_forgotten_items = [
            {
                "name": "Transport materiałów",
                "keywords": ["transport"],
                "category": "service",
                "importance": "high",
                "message": "Czy uwzględniono transport materiałów?"
            },
            {
                "name": "Utylizacja odpadów",
                "keywords": ["utylizacja", "wywóz", "odpady"],
                "category": "service",
                "importance": "medium",
                "message": "Czy uwzględniono utylizację starych materiałów?"
            },
            {
                "name": "Rusztowanie",
                "keywords": ["rusztowanie", "rusztowania", "podnośnik"],
                "category": "service",
                "importance": "high",
                "message": "Czy uwzględniono koszt rusztowania/podnośnika?"
            },
            {
                "name": "Demontaż",
                "keywords": ["demontaż", "rozbórka", "usunięcie"],
                "category": "service",
                "importance": "medium",
                "message": "Czy uwzględniono demontaż starych materiałów?"
            },
            {
                "name": "Obróbki blacharskie",
                "keywords": ["obróbka", "pas", "wiatrownica"],
                "category": "material",
                "importance": "medium",
                "message": "Czy uwzględniono wszystkie niezbędne obróbki blacharskie?"
            }
        ]
    
    def enable_warnings(self):
        """Włącza ostrzeżenia."""
        self.warnings_enabled = True
    
    def disable_warnings(self):
        """Wyłącza ostrzeżenia."""
        self.warnings_enabled = False
    
    def validate_estimate(self, items: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Waliduje kosztorys i zwraca status oraz listę ostrzeżeń.
        
        Args:
            items: Lista pozycji kosztorysowych
            
        Returns:
            Tuple (czy_poprawny, lista_ostrzeżeń)
        """
        if not self.warnings_enabled:
            return True, []
        
        warnings = []
        
        # Sprawdź wymagane pola
        field_warnings = self._validate_required_fields(items)
        warnings.extend(field_warnings)
        
        # Sprawdź powiązane materiały
        dependency_warnings = self._check_material_dependencies(items)
        warnings.extend(dependency_warnings)
        
        # Sprawdź często zapominane pozycje
        forgotten_warnings = self._check_forgotten_items(items)
        warnings.extend(forgotten_warnings)
        
        is_valid = len(warnings) == 0
        return is_valid, warnings
    
    def _validate_required_fields(self, items: List[Dict[str, Any]]) -> List[str]:
        """Sprawdza czy wszystkie pozycje mają wypełnione wymagane pola."""
        warnings = []
        
        for idx, item in enumerate(items, 1):
            if not item.get("name", "").strip():
                warnings.append(f"Pozycja {idx}: Brak nazwy")
            
            try:
                qty = float(item.get("quantity", 0))
                if qty <= 0:
                    warnings.append(f"Pozycja {idx} ({item.get('name', 'bez nazwy')}): Nieprawidłowa ilość")
            except (ValueError, TypeError):
                warnings.append(f"Pozycja {idx} ({item.get('name', 'bez nazwy')}): Nieprawidłowa ilość")
            
            try:
                price = float(item.get("price_unit_net", 0))
                if price < 0:
                    warnings.append(f"Pozycja {idx} ({item.get('name', 'bez nazwy')}): Ujemna cena")
            except (ValueError, TypeError):
                warnings.append(f"Pozycja {idx} ({item.get('name', 'bez nazwy')}): Nieprawidłowa cena")
            
            if not item.get("unit", "").strip():
                warnings.append(f"Pozycja {idx} ({item.get('name', 'bez nazwy')}): Brak jednostki miary")
        
        return warnings
    
    def _check_material_dependencies(self, items: List[Dict[str, Any]]) -> List[str]:
        """Sprawdza czy są wszystkie powiązane materiały."""
        warnings = []
        
        for dep_key, dep_info in self.material_dependencies.items():
            # Sprawdź czy istnieje materiał główny
            main_items = [
                item for item in items
                if any(keyword in item.get("name", "").lower() for keyword in dep_info["keywords"])
            ]
            
            if not main_items:
                continue  # Jeśli nie ma głównego materiału, to nie ma co sprawdzać
            
            # Sprawdź czy istnieją wymagane materiały
            for required in dep_info["requires"]:
                found = any(
                    item for item in items
                    if any(keyword in item.get("name", "").lower() for keyword in required["keywords"])
                )
                
                if not found:
                    main_names = [item.get("name", "") for item in main_items]
                    warnings.append(
                        f"Uwaga: W kosztorysie znajduje się '{main_names[0]}' "
                        f"ale brak powiązanego materiału: {required['name']}"
                    )
        
        return warnings
    
    def _check_forgotten_items(self, items: List[Dict[str, Any]]) -> List[str]:
        """Sprawdza czy nie zapomniano o często pomijanych pozycjach."""
        warnings = []
        
        for forgotten in self.common_forgotten_items:
            # Sprawdź czy pozycja istnieje
            found = any(
                item for item in items
                if any(keyword in item.get("name", "").lower() for keyword in forgotten["keywords"])
            )
            
            if not found and forgotten["importance"] == "high":
                warnings.append(f"⚠️ {forgotten['message']}")
            elif not found and forgotten["importance"] == "medium":
                warnings.append(f"ℹ️ {forgotten['message']}")
        
        return warnings
    
    def get_export_validation_warnings(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        Pobiera ostrzeżenia przed eksportem.
        
        Args:
            items: Lista pozycji kosztorysowych
            
        Returns:
            Lista ostrzeżeń do wyświetlenia przed eksportem
        """
        if not self.warnings_enabled:
            return []
        
        _, all_warnings = self.validate_estimate(items)
        
        # Filtruj tylko ważne ostrzeżenia do wyświetlenia przed eksportem
        export_warnings = [
            w for w in all_warnings
            if "⚠️" in w or "Brak" in w or "Nieprawidłowa" in w
        ]
        
        return export_warnings
    
    def suggest_related_items(self, item_name: str) -> List[str]:
        """
        Sugeruje powiązane pozycje dla danego materiału.
        
        Args:
            item_name: Nazwa materiału
            
        Returns:
            Lista sugerowanych nazw materiałów
        """
        suggestions = []
        item_name_lower = item_name.lower()
        
        for dep_key, dep_info in self.material_dependencies.items():
            if any(keyword in item_name_lower for keyword in dep_info["keywords"]):
                for required in dep_info["requires"]:
                    suggestions.append(required["name"])
        
        return suggestions
    
    def check_quantity_relationships(
        self,
        items: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Sprawdza relacje ilościowe między materiałami.
        
        Args:
            items: Lista pozycji kosztorysowych
            
        Returns:
            Lista ostrzeżeń o nieprawidłowych proporcjach
        """
        warnings = []
        
        # Rynny vs haki
        gutters = [
            item for item in items
            if any(kw in item.get("name", "").lower() for kw in ["rynna", "rynien"])
        ]
        hooks = [
            item for item in items
            if any(kw in item.get("name", "").lower() for kw in ["hak", "haki rynnowe"])
        ]
        
        if gutters and hooks:
            total_gutter_length = sum(float(item.get("quantity", 0)) for item in gutters)
            total_hooks = sum(float(item.get("quantity", 0)) for item in hooks)
            expected_hooks = total_gutter_length * 2.0  # co 0.5m
            
            if total_hooks < expected_hooks * 0.8:  # 20% tolerancja
                warnings.append(
                    f"Uwaga: Mało haków rynnowych. "
                    f"Dla {total_gutter_length:.1f}m rynny zalecane: ~{expected_hooks:.0f} szt, "
                    f"w kosztorysie: {total_hooks:.0f} szt"
                )
        
        # Rury spustowe vs objęcia
        downpipes = [
            item for item in items
            if any(kw in item.get("name", "").lower() for kw in ["rura spustowa", "rury spustowe"])
        ]
        clamps = [
            item for item in items
            if any(kw in item.get("name", "").lower() for kw in ["objętka", "obejma", "objęcia"])
        ]
        
        if downpipes and clamps:
            total_downpipe_length = sum(float(item.get("quantity", 0)) for item in downpipes)
            total_clamps = sum(float(item.get("quantity", 0)) for item in clamps)
            expected_clamps = total_downpipe_length * 0.5  # co 2m
            
            if total_clamps < expected_clamps * 0.8:  # 20% tolerancja
                warnings.append(
                    f"Uwaga: Mało objęć rury spustowej. "
                    f"Dla {total_downpipe_length:.1f}m rury zalecane: ~{expected_clamps:.0f} szt, "
                    f"w kosztorysie: {total_clamps:.0f} szt"
                )
        
        return warnings
