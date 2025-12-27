# KosztorysOfertowy
Kosztorys ofertowy - dachy

## Opis
Aplikacja do tworzenia kosztorysów ofertowych dla prac dekarskich.

## Funkcje
- **Kosztorys/Oferta** - główna zakładka do zarządzania pozycjami kosztorysowymi
- **Pomiar Dachu** - obliczanie powierzchni dachu z figur geometrycznych (trapezy, trójkąty, prostokąty)
- **Orynnowanie** - kalkulacja elementów systemu rynnowego
- **Kominy** - obliczanie materiałów do obróbki kominów
- **Obróbki** - kalkulacja blachy na obróbki blacharskie

## Wymagania
- Python 3.8+
- tkinter (GUI)
- reportlab (opcjonalnie, do generowania PDF)
- Pillow (opcjonalnie, do podglądu logo)

## Instalacja
```bash
pip install reportlab pillow
```

## Uruchomienie
```bash
python main_app044.py
```

## Struktura plików
- `main_app044.py` - główna aplikacja
- `gutter_calculations.py` - obliczenia orynnowania
- `chimney_calculations.py` - obliczenia obróbki kominów
- `flashing_calculations.py` - obliczenia obróbek blacharskich
- `measurement_tab.py` - moduł pomiaru dachu
- `roof_calculations.py` - obliczenia geometrii dachu
- `felt_calculations.py` - obliczenia pokrycia papowego
- `timber_calculations.py` - obliczenia drewna
- `cost_calculations.py` - pomocnicze obliczenia kosztorysowe
