# KosztorysOfertowy
Kosztorys ofertowy - dachy / Roofing Cost Estimator

## 🏠 Kalkulator Dachów v4.6

Profesjonalna aplikacja do tworzenia kosztorysów ofertowych dla prac dekarskich.

### ✨ Główne funkcje

- **📋 Kosztorys/Oferta** - Główny moduł do tworzenia kosztorysów z materiałami i usługami
- **📐 Pomiar Dachu** - Kalkulator powierzchni dachu (jednospadowy, dwuspadowy, kopertowy)
- **🌧️ Rynny** - Kalkulator systemu rynnowego (rynny, rury spustowe, akcesoria)
- **🏭 Kominy** - Kalkulator obróbek kominowych i czap
- **🔧 Obróbki** - Kalkulator obróbek blacharskich (wiatrownice, okapnice, pasy nadrynnowe)

### 📄 Eksport

- **PDF** - Profesjonalny kosztorys ofertowy z logo firmy
- **CSV** - Eksport danych do arkusza kalkulacyjnego
- **JSON** - Zapisywanie i wczytywanie kosztorysów

### 🚀 Uruchomienie

```bash
# Wymagania
pip install reportlab pillow

# Uruchomienie aplikacji
python main_app044.py
```

### 📁 Struktura projektu

```
├── main_app044.py        # Główna aplikacja GUI
├── roof_calculations.py  # Obliczenia geometrii dachów
├── gutter_calculations.py # Obliczenia orynnowania
├── chimney_calculations.py # Obliczenia obróbek kominowych
├── flashing_calculations.py # Obliczenia obróbek blacharskich
├── timber_calculations.py # Obliczenia drewna
├── felt_calculations.py  # Obliczenia papy
├── cost_calculations.py  # Logika kosztorysowa
├── measurement_tab.py    # Moduł pomiaru figur
├── template.html         # Szablon HTML dla PDF
├── style.css            # Style CSS dla PDF
├── materialy_uslugi.json # Baza materiałów i usług
└── generuj_pdf.py       # Generator PDF (WeasyPrint)
```

### 🎨 Wygląd aplikacji

Nowoczesny interfejs z kolorystką dopasowaną do branży dekarskiej:
- Pomarańczowe akcenty (kolor dachówki)
- Ikony dla lepszej nawigacji
- Zakładki dla różnych funkcji
- Przejrzyste tabele z podsumowaniami

### 📋 Autor

**VICTOR TOMASZ MAJCHERCZYK**  
Dąbrowa Górnicza  
*TYLKO DACHY TYLKO VICTOR*
