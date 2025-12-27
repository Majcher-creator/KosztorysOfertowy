# templates_manager.py
"""
Zarządzanie szablonami kosztorysów.
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class TemplatesManager:
    """Klasa do zarządzania szablonami kosztorysów."""
    
    def __init__(self, templates_file: str = None):
        """
        Inicjalizacja menedżera szablonów.
        
        Args:
            templates_file: Ścieżka do pliku z szablonami
        """
        if templates_file is None:
            # Domyślna lokalizacja
            home = os.path.expanduser("~")
            appdir = os.path.join(home, ".roofcalc")
            os.makedirs(appdir, exist_ok=True)
            templates_file = os.path.join(appdir, "templates.json")
        
        self.templates_file = templates_file
        self.templates: List[Dict[str, Any]] = []
        self.load_templates()
    
    def load_templates(self):
        """Wczytuje szablony z pliku."""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    self.templates = json.load(f)
            except Exception as e:
                print(f"Błąd wczytywania szablonów: {e}")
                self.templates = []
        else:
            self.templates = self._get_default_templates()
            self.save_templates()
    
    def save_templates(self):
        """Zapisuje szablony do pliku."""
        try:
            with open(self.templates_file, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Błąd zapisywania szablonów: {e}")
            raise
    
    def _get_default_templates(self) -> List[Dict[str, Any]]:
        """Zwraca predefiniowane szablony przykładowe."""
        return [
            {
                "id": "flat_roof_papa",
                "name": "Dach płaski - papa termozgrzewalna",
                "description": "Standardowy dach płaski z papą",
                "created_at": datetime.now().isoformat(),
                "items": [
                    {
                        "name": "Papa podkładowa",
                        "quantity": 1.0,
                        "unit": "m2",
                        "price_unit_net": 12.5,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Papa nawierzchniowa termozgrzewalna",
                        "quantity": 1.0,
                        "unit": "m2",
                        "price_unit_net": 28.6,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Gruntowanie powierzchni",
                        "quantity": 1.0,
                        "unit": "m2",
                        "price_unit_net": 3.5,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    },
                    {
                        "name": "Układanie papy podkładowej",
                        "quantity": 1.0,
                        "unit": "m2",
                        "price_unit_net": 8.0,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    },
                    {
                        "name": "Układanie papy nawierzchniowej",
                        "quantity": 1.0,
                        "unit": "m2",
                        "price_unit_net": 12.0,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    }
                ]
            },
            {
                "id": "gutter_renovation",
                "name": "Remont orynnowania komplet",
                "description": "Kompleksowy remont systemu orynnowania",
                "created_at": datetime.now().isoformat(),
                "items": [
                    {
                        "name": "Demontaż starego orynnowania",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 5.0,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    },
                    {
                        "name": "Rynna PVC 100mm",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 18.0,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Rura spustowa PVC 100mm",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 15.0,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Montaż orynnowania",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 15.0,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    }
                ]
            },
            {
                "id": "flashing_standard",
                "name": "Obróbki blacharskie standard",
                "description": "Standardowe obróbki blacharskie",
                "created_at": datetime.now().isoformat(),
                "items": [
                    {
                        "name": "Pas nadrynnowy - Blacha powlekana",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 18.0,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Obróbka komina - Blacha powlekana",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 45.0,
                        "vat_rate": 8,
                        "category": "material",
                        "note": ""
                    },
                    {
                        "name": "Montaż obróbek blacharskich",
                        "quantity": 1.0,
                        "unit": "mb",
                        "price_unit_net": 20.0,
                        "vat_rate": 23,
                        "category": "service",
                        "note": ""
                    }
                ]
            }
        ]
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """
        Zwraca listę szablonów (tylko podstawowe info).
        
        Returns:
            Lista słowników z id, name, description
        """
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t.get("description", ""),
                "created_at": t.get("created_at", "")
            }
            for t in self.templates
        ]
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera szablon po ID.
        
        Args:
            template_id: ID szablonu
            
        Returns:
            Słownik z szablonem lub None
        """
        for template in self.templates:
            if template["id"] == template_id:
                return template.copy()
        return None
    
    def add_template(
        self,
        name: str,
        items: List[Dict[str, Any]],
        description: str = ""
    ) -> str:
        """
        Dodaje nowy szablon.
        
        Args:
            name: Nazwa szablonu
            items: Lista pozycji kosztorysowych
            description: Opis szablonu
            
        Returns:
            ID utworzonego szablonu
        """
        # Generuj ID na podstawie nazwy i timestamp
        import re
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Usuń znaki specjalne i zachowaj tylko litery, cyfry i podkreślenia
        safe_name = re.sub(r'[^\w\s-]', '', name.lower())
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        template_id = f"{safe_name}_{timestamp}"
        
        # Sprawdź czy ID już istnieje (mało prawdopodobne, ale zabezpieczenie)
        counter = 1
        original_id = template_id
        while any(t["id"] == template_id for t in self.templates):
            template_id = f"{original_id}_{counter}"
            counter += 1
        
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "items": items
        }
        
        self.templates.append(template)
        self.save_templates()
        
        return template_id
    
    def update_template_name(self, template_id: str, new_name: str):
        """
        Aktualizuje nazwę szablonu.
        
        Args:
            template_id: ID szablonu
            new_name: Nowa nazwa
        """
        for template in self.templates:
            if template["id"] == template_id:
                template["name"] = new_name
                self.save_templates()
                return
        
        raise ValueError(f"Szablon o ID {template_id} nie istnieje")
    
    def delete_template(self, template_id: str):
        """
        Usuwa szablon.
        
        Args:
            template_id: ID szablonu
        """
        self.templates = [t for t in self.templates if t["id"] != template_id]
        self.save_templates()
    
    def load_template_items(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Wczytuje pozycje z szablonu.
        
        Args:
            template_id: ID szablonu
            
        Returns:
            Lista pozycji kosztorysowych
        """
        template = self.get_template(template_id)
        if template is None:
            raise ValueError(f"Szablon o ID {template_id} nie istnieje")
        
        # Zwróć kopię pozycji
        return [item.copy() for item in template["items"]]
