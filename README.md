# KosztorysOfertowy
Kosztorys ofertowy - dachy

## Opis
Aplikacja do tworzenia kosztorysów ofertowych dla prac dekarskich.

## Funkcje

### Zakładka Kosztorys/Oferta
- Zarządzanie pozycjami kosztorysowymi (materiały i usługi)
- **NOWE**: Skróty klawiaturowe:
  - `Delete` - usuwa zaznaczone pozycje (z potwierdzeniem)
  - `Enter` - otwiera dialog edycji
  - `+/-` - zwiększa/zmniejsza ilość o 1
  - `Ctrl+D` - duplikuje pozycję
- **NOWE**: Menu kontekstowe (prawy przycisk myszy) z opcjami edycji, usuwania, duplikacji
- **NOWE**: Wielokrotne zaznaczenie i usuwanie pozycji
- **NOWE**: Przyciski edycji/usuwania w stałym toolbarze (zawsze widoczne)
- Dodawanie pozycji z formularza lub z bazy materiałów
- Obliczanie sum i VAT
- Eksport do CSV i PDF
- Zarządzanie klientami z wyszukiwaniem

### Pomiar Dachu
- Obliczanie powierzchni dachu z figur geometrycznych (trapezy, trójkąty, prostokąty)
- Przenoszenie sumy powierzchni do kosztorysu

### Orynnowanie
- **NOWE**: Wybór systemu orynnowania:
  - PVC (75, 100, 125, 150 mm)
  - Metal/Tytan-cynk
  - Ocynk
  - Kwadrat/prostokątny
  - Miedź
- **NOWE**: Ręczne wprowadzanie ilości elementów:
  - Kolanka, trójniki, narożniki wewnętrzne/zewnętrzne
  - Zaślepki lewe/prawe, lejki/wpusty
- **NOWE**: Zarządzanie cenami systemów
- **NOWE**: Dodawanie jako komplet lub szczegółowo
- Automatyczne obliczenia na podstawie wymiarów dachu

### Kominy
- Obliczanie materiałów do obróbki kominów
- Różne typy pokrycia (papa, blacha, dachówka)
- Automatyczne obliczenia powierzchni

### Obróbki Blacharskie
- **NOWE**: Definiowanie własnych typów obróbek
- **NOWE**: Predefiniowane obróbki (edytowalne):
  - Pas nadrynnowy/podrynnowy
  - Wiatrownica, kosz dachowy
  - Obróbka komina, attyki
  - Gąsior/kalenica, listwa przyścienna
- **NOWE**: Wybór materiału:
  - Blacha powlekana, ocynk, tytan-cynk
  - Miedź, aluminium
- **NOWE**: Kalkulator długości
- **NOWE**: Dodawanie jako pojedyncze pozycje lub komplet
- Obliczenia powierzchni blachy i liczby arkuszy

### Profile Firmy
- Zarządzanie wieloma profilami firmowymi
- Szybkie przełączanie między profilami
- Przechowywanie danych firmowych, logo i konta bankowego

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
python main_app046.py
```

## Struktura plików
- `main_app046.py` - główna aplikacja
- `gutter_calculations.py` - obliczenia orynnowania (z systemami)
- `chimney_calculations.py` - obliczenia obróbki kominów
- `flashing_calculations.py` - obliczenia obróbek blacharskich
- `flashing_definitions.py` - **NOWE** - zarządzanie definicjami obróbek
- `measurement_tab.py` - moduł pomiaru dachu
- `roof_calculations.py` - obliczenia geometrii dachu
- `felt_calculations.py` - obliczenia pokrycia papowego
- `timber_calculations.py` - obliczenia drewna
- `cost_calculations.py` - pomocnicze obliczenia kosztorysowe

## Najnowsze zmiany (v4.6+)
1. **Skróty klawiaturowe i obsługa wielokrotnego zaznaczenia**
   - Szybka edycja i usuwanie z klawiatury
   - Menu kontekstowe na prawym przycisku myszy
   - Możliwość przenoszenia pozycji między materiałami a usługami

2. **Rozbudowa zakładki Orynnowanie**
   - Obsługa różnych systemów z cenami
   - Ręczne wprowadzanie ilości wszystkich elementów
   - Elastyczne dodawanie do kosztorysu

3. **Rozbudowa zakładki Obróbki**
   - Własne definicje obróbek
   - Różne materiały z przelicznikami cen
   - Kalkulator długości

## Planowane funkcje
- System szablonów kosztorysów
- Historia zmian i wersjonowanie
- Grupowanie pozycji
- Kalkulator marży
- Załączniki (zdjęcia, szkice)
