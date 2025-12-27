# KosztorysOfertowy - Kalkulator Dachów v5.0

Profesjonalna aplikacja do tworzenia kosztorysów ofertowych dla prac dekarskich.

## ✨ Główne funkcje

### 📋 Kosztorys/Oferta
- Główny moduł do tworzenia kosztorysów z materiałami i usługami
- Nowoczesny interfejs z kolorystką dopasowaną do branży dekarskiej
- Ikony dla lepszej nawigacji

### 📐 Zakładki kalkulatorów
- **Pomiar Dachu** - Kalkulator powierzchni dachu (jednospadowy, dwuspadowy, kopertowy)
- **Rynny** - Kalkulator systemu rynnowego (rynny, rury spustowe, akcesoria)
- **Kominy** - Kalkulator obróbek kominowych i czap
- **Obróbki** - Kalkulator obróbek blacharskich (wiatrownice, okapnice, pasy nadrynnowe)

## Nowe funkcje w wersji 5.0

### 🎯 Skróty klawiaturowe
- **Delete** - Usuwa zaznaczoną pozycję
- **Enter** - Otwiera edycję zaznaczonej pozycji
- **+** lub **-** - Zwiększa/zmniejsza ilość o 1
- **Ctrl+D** - Duplikuje zaznaczoną pozycję

### 🖱️ Menu kontekstowe (prawy przycisk myszy)
- Edytuj
- Usuń
- Duplikuj
- Zmień ilość (+1/-1)
- Przenieś do usług/materiałów

### 📊 Eksport do Excel
- Profesjonalne formatowanie (pogrubione nagłówki, obramowanie)
- Osobne arkusze dla: Materiałów, Usług, Podsumowania
- Kolorowanie wierszy (materiały szare, usługi niebieskie)
- Formatowanie walutowe i numeryczne

### 🔧 Nowe moduły backend
- **gutter_calculations.py** - Zaawansowane obliczenia orynnowania (8 systemów: PVC 75/100/125/150, Metal, Ocynk, Kwadrat, Miedź)
- **flashing_definitions.py** - Definicje obróbek blacharskich (8 typów, 5 materiałów)
- **templates_manager.py** - Zarządzanie szablonami kosztorysów
- **version_control.py** - Wersjonowanie i historia zmian
- **validators.py** - Walidacja i ostrzeżenia

### 🎨 Ulepszony interfejs (UI)
- Pomarańczowe akcenty (kolor dachówki)
- Nowoczesny styl CSS dla eksportu PDF
- Przejrzyste tabele z podsumowaniami

## 📄 Eksport

- **PDF** - Profesjonalny kosztorys ofertowy z logo firmy
- **Excel** - Eksport z formatowaniem do .xlsx
- **CSV** - Eksport danych do arkusza kalkulacyjnego
- **JSON** - Zapisywanie i wczytywanie kosztorysów

## Instalacja

### Wymagania
- Python 3.8 lub nowszy
- pip (menedżer pakietów Python)

### Instalacja zależności
```bash
pip install -r requirements.txt
```

Zależności:
- `reportlab>=3.6.0` - Generowanie PDF
- `Pillow>=9.0.0` - Obsługa obrazów/logo
- `openpyxl>=3.0.0` - Eksport do Excel

## 🚀 Uruchomienie

```bash
python main_app044.py
```

## Testy

Projekt zawiera kompleksowy zestaw testów jednostkowych:

```bash
# Uruchom wszystkie testy
python -m unittest discover tests/

# Uruchom konkretny test
python tests/test_gutters.py
python tests/test_flashings.py
python tests/test_validators.py
```

**Statystyki testów:**
- Łącznie: 34 testy
- Testy orynnowania: 9
- Testy obróbek: 14
- Testy walidacji: 11
- Status: ✅ Wszystkie przechodzą

## 📁 Struktura projektu

```
KosztorysOfertowy/
├── main_app044.py              # Główna aplikacja GUI
├── gutter_calculations.py      # Obliczenia orynnowania
├── flashing_definitions.py     # Definicje obróbek
├── templates_manager.py        # Szablony kosztorysów
├── version_control.py          # Wersjonowanie
├── validators.py               # Walidacja
├── cost_calculations.py        # Obliczenia kosztów
├── timber_calculations.py      # Obliczenia więźby
├── roof_calculations.py        # Obliczenia pokryć
├── chimney_calculations.py     # Obliczenia kominów
├── felt_calculations.py        # Obliczenia papa
├── flashing_calculations.py    # Obliczenia obróbek
├── measurement_tab.py          # Moduł pomiaru figur
├── generuj_pdf.py              # Generator PDF
├── template.html               # Szablon HTML dla PDF
├── style.css                   # Style CSS dla PDF
├── materialy_uslugi.json       # Baza materiałów i usług
├── requirements.txt            # Zależności
├── .gitignore                  # Git ignore
└── tests/                      # Testy jednostkowe
    ├── test_gutters.py
    ├── test_flashings.py
    └── test_validators.py
```

## Dane użytkownika

Aplikacja przechowuje dane w katalogu `~/.roofcalc/`:
- `clients_db.json` - Baza klientów
- `materials_db.json` - Baza materiałów
- `settings.json` - Ustawienia aplikacji
- `templates.json` - Szablony kosztorysów
- `versions.json` - Historia wersji

## Wsparcie i rozwój

Projekt jest aktywnie rozwijany. Nowe funkcje w planach:
- Interfejs UI dla nowych modułów (orynnowanie, obróbki, szablony)
- Grupowanie pozycji w kosztorysie
- Kalkulator marży
- Załączniki (zdjęcia, szkice)
- Podgląd PDF przed zapisem
- Import cenników z Excel/CSV

## 📋 Autor

**VICTOR TOMASZ MAJCHERCZYK**  
Dąbrowa Górnicza  
*TYLKO DACHY TYLKO VICTOR*
