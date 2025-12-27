# version_control.py
"""
Wersjonowanie i historia zmian kosztorysów.
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque

class VersionControl:
    """Klasa do zarządzania wersjami kosztorysów."""
    
    MAX_VERSIONS = 10  # Maksymalna liczba przechowywanych wersji
    
    def __init__(self, versions_file: str = None):
        """
        Inicjalizacja kontroli wersji.
        
        Args:
            versions_file: Ścieżka do pliku z wersjami
        """
        if versions_file is None:
            # Domyślna lokalizacja
            home = os.path.expanduser("~")
            appdir = os.path.join(home, ".roofcalc")
            os.makedirs(appdir, exist_ok=True)
            versions_file = os.path.join(appdir, "versions.json")
        
        self.versions_file = versions_file
        self.versions: deque = deque(maxlen=self.MAX_VERSIONS)
        self.load_versions()
    
    def load_versions(self):
        """Wczytuje wersje z pliku."""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Zachowaj tylko ostatnie MAX_VERSIONS wersji
                    self.versions = deque(data[-self.MAX_VERSIONS:], maxlen=self.MAX_VERSIONS)
            except Exception as e:
                print(f"Błąd wczytywania wersji: {e}")
                self.versions = deque(maxlen=self.MAX_VERSIONS)
        else:
            self.versions = deque(maxlen=self.MAX_VERSIONS)
    
    def save_versions(self):
        """Zapisuje wersje do pliku."""
        try:
            with open(self.versions_file, "w", encoding="utf-8") as f:
                json.dump(list(self.versions), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Błąd zapisywania wersji: {e}")
            raise
    
    def save_version(
        self,
        items: List[Dict[str, Any]],
        description: str = "Automatyczny zapis",
        invoice_number: str = "",
        client: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Zapisuje nową wersję kosztorysu.
        
        Args:
            items: Lista pozycji kosztorysowych
            description: Opis wersji
            invoice_number: Numer kosztorysu
            client: Nazwa klienta
            metadata: Dodatkowe metadane
            
        Returns:
            ID utworzonej wersji
        """
        timestamp = datetime.now()
        version_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        version = {
            "id": version_id,
            "timestamp": timestamp.isoformat(),
            "description": description,
            "invoice_number": invoice_number,
            "client": client,
            "items_count": len(items),
            "items": [item.copy() for item in items],  # Deep copy
            "metadata": metadata or {}
        }
        
        self.versions.append(version)
        self.save_versions()
        
        return version_id
    
    def get_version_list(self) -> List[Dict[str, Any]]:
        """
        Zwraca listę wersji (tylko podstawowe info).
        
        Returns:
            Lista słowników z podstawowymi informacjami o wersjach
        """
        return [
            {
                "id": v["id"],
                "timestamp": v["timestamp"],
                "description": v["description"],
                "invoice_number": v.get("invoice_number", ""),
                "client": v.get("client", ""),
                "items_count": v.get("items_count", 0)
            }
            for v in self.versions
        ]
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera wersję po ID.
        
        Args:
            version_id: ID wersji
            
        Returns:
            Słownik z wersją lub None
        """
        for version in self.versions:
            if version["id"] == version_id:
                return version.copy()
        return None
    
    def restore_version(self, version_id: str) -> List[Dict[str, Any]]:
        """
        Przywraca wersję kosztorysu.
        
        Args:
            version_id: ID wersji do przywrócenia
            
        Returns:
            Lista pozycji kosztorysowych z wybranej wersji
            
        Raises:
            ValueError: Jeśli wersja nie istnieje
        """
        version = self.get_version(version_id)
        if version is None:
            raise ValueError(f"Wersja o ID {version_id} nie istnieje")
        
        # Zwróć kopię pozycji
        return [item.copy() for item in version["items"]]
    
    def delete_version(self, version_id: str):
        """
        Usuwa wersję.
        
        Args:
            version_id: ID wersji
        """
        self.versions = deque(
            [v for v in self.versions if v["id"] != version_id],
            maxlen=self.MAX_VERSIONS
        )
        self.save_versions()
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Dict[str, Any]:
        """
        Porównuje dwie wersje kosztorysu.
        
        Args:
            version_id1: ID pierwszej wersji
            version_id2: ID drugiej wersji
            
        Returns:
            Słownik z różnicami między wersjami
            
        Raises:
            ValueError: Jeśli któraś z wersji nie istnieje
        """
        v1 = self.get_version(version_id1)
        v2 = self.get_version(version_id2)
        
        if v1 is None:
            raise ValueError(f"Wersja o ID {version_id1} nie istnieje")
        if v2 is None:
            raise ValueError(f"Wersja o ID {version_id2} nie istnieje")
        
        # Porównaj pozycje
        items1 = {self._item_key(item): item for item in v1["items"]}
        items2 = {self._item_key(item): item for item in v2["items"]}
        
        keys1 = set(items1.keys())
        keys2 = set(items2.keys())
        
        # Dodane w wersji 2
        added = []
        for key in keys2 - keys1:
            added.append(items2[key])
        
        # Usunięte z wersji 1
        removed = []
        for key in keys1 - keys2:
            removed.append(items1[key])
        
        # Zmienione
        modified = []
        for key in keys1 & keys2:
            if items1[key] != items2[key]:
                modified.append({
                    "old": items1[key],
                    "new": items2[key]
                })
        
        return {
            "version1": {
                "id": v1["id"],
                "timestamp": v1["timestamp"],
                "description": v1["description"]
            },
            "version2": {
                "id": v2["id"],
                "timestamp": v2["timestamp"],
                "description": v2["description"]
            },
            "added": added,
            "removed": removed,
            "modified": modified,
            "summary": {
                "added_count": len(added),
                "removed_count": len(removed),
                "modified_count": len(modified)
            }
        }
    
    def _item_key(self, item: Dict[str, Any]) -> str:
        """
        Generuje unikalny klucz dla pozycji kosztorysowej.
        
        Args:
            item: Pozycja kosztorysowa
            
        Returns:
            Klucz tekstowy
        """
        return f"{item.get('name', '')}_{item.get('category', '')}"
    
    def auto_save_before_operation(
        self,
        items: List[Dict[str, Any]],
        operation: str,
        **kwargs
    ) -> str:
        """
        Automatycznie zapisuje wersję przed operacją.
        
        Args:
            items: Aktualna lista pozycji
            operation: Nazwa operacji (np. "Czyszczenie", "Ładowanie nowego")
            **kwargs: Dodatkowe parametry (invoice_number, client, itp.)
            
        Returns:
            ID utworzonej wersji
        """
        description = f"Przed: {operation}"
        return self.save_version(
            items=items,
            description=description,
            invoice_number=kwargs.get("invoice_number", ""),
            client=kwargs.get("client", ""),
            metadata={"operation": operation}
        )
    
    def get_recent_versions(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Pobiera najnowsze wersje.
        
        Args:
            count: Liczba wersji do pobrania
            
        Returns:
            Lista najnowszych wersji
        """
        version_list = self.get_version_list()
        return version_list[-count:] if len(version_list) >= count else version_list
    
    def clear_all_versions(self):
        """Usuwa wszystkie wersje."""
        self.versions.clear()
        self.save_versions()
