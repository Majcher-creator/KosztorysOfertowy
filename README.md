# KosztorysOfertowy
Kalkulator Dachów - Kosztorys ofertowy dla usług dekarskich

## Wersja 5.0

Profesjonalna aplikacja do tworzenia kosztorysów ofertowych dla prac dekarskich.

### Nowe funkcje w v5.0

#### ⌨️ Skróty klawiaturowe
- **Delete** - usuń zaznaczoną pozycję (z potwierdzeniem)
- **Enter** - edytuj zaznaczoną pozycję
- **+** lub **-** - zwiększ/zmniejsz ilość o 1
- **Ctrl+D** - duplikuj zaznaczoną pozycję

#### 🖱️ Menu kontekstowe (PPM)
Kliknięcie prawym przyciskiem myszy na pozycji wyświetla menu z opcjami:
- ✏️ Edytuj
- 🗑️ Usuń
- 📋 Duplikuj
- ➕ Zwiększ ilość (+1)
- ➖ Zmniejsz ilość (-1)
- 🔧/🧱 Przenieś między materiałami/usługami

#### 📊 Eksport do Excel
Profesjonalny eksport XLSX z:
- Osobnymi arkuszami: Materiały, Usługi, Podsumowanie
- Formatowaniem walutowym
- Kolorowaniem nagłówków i sum

#### 📋 Menedżer szablonów
- Zapisywanie aktualnego kosztorysu jako szablon
- Szybkie ładowanie szablonów
- Zarządzanie listą szablonów

#### ✓ Walidacja kosztorysu
Sprawdzanie poprawności kosztorysu z ostrzeżeniami o:
- Brakujących powiązanych pozycjach (np. rynny bez haków)
- Potencjalnie zapomnianych elementach (transport, utylizacja)

### Instalacja

```bash
pip install -r requirements.txt
```

### Uruchomienie

```bash
python3 main_app044.py
```

### Wymagania
- Python 3.8+
- reportlab (PDF)
- Pillow (obrazy/logo)
- openpyxl (Excel)
