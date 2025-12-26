import jinja2
from weasyprint import HTML, CSS
import datetime

# --- 1. Przygotowanie danych (to będziesz chciał dynamicznie zmieniać) ---
# W przyszłości te dane mogą pochodzić z formularza, bazy danych itp.
dane_kosztorysu = {
    "nr_kosztorysu": "112/5/2025",
    "data_wystawienia": datetime.date.today().strftime("%Y-%m-%d"),
    "nazwa_uslugi": "Metraż dachu",
    "metraz": 150,
    "klient": {
        "nazwa": "Jan Kowalski",
        "adres": "ul. Przykładowa 12/3",
        "miasto": "00-001 Warszawa",
        "tel": "500-100-200",
        "nip": "123-456-78-90"
    },
    "materialy": [
        {"nazwa": "Dachówka ceramiczna A", "ilosc": 150, "jm": "m²", "cena_netto": 45.50},
        {"nazwa": "Rynna PVC 100mm", "ilosc": 40, "jm": "mb", "cena_netto": 12.00},
        {"nazwa": "Wkręty farmerskie", "ilosc": 2, "jm": "op.", "cena_netto": 35.00},
    ],
    "robocizna": [
        {"nazwa": "Montaż pokrycia dachowego", "ilosc": 150, "jm": "m²", "cena_netto": 30.00},
        {"nazwa": "Montaż systemu rynnowego", "ilosc": 40, "jm": "mb", "cena_netto": 15.00},
    ],
    "komentarz": "Oferta ważna 30 dni."
}

# --- 2. Obliczenia podsumowań (logika biznesowa) ---
# (To jest uproszczony przykład, dostosuj do swoich potrzeb)
VAT_STAWKA = 0.08 # 8%

# Obliczenia dla materiałów
suma_material_netto = sum(item['ilosc'] * item['cena_netto'] for item in dane_kosztorysu['materialy'])
suma_material_vat = suma_material_netto * VAT_STAWKA
suma_material_brutto = suma_material_netto + suma_material_vat

# Obliczenia dla robocizny
suma_robocizna_netto = sum(item['ilosc'] * item['cena_netto'] for item in dane_kosztorysu['robocizna'])
suma_robocizna_vat = suma_robocizna_netto * VAT_STAWKA
suma_robocizna_brutto = suma_robocizna_netto + suma_robocizna_vat

# (Załóżmy, że transport jest stały lub obliczany inaczej)
transport = 100.00 

# Podsumowanie całości
razem_netto = suma_material_netto + suma_robocizna_netto
razem_brutto = suma_material_brutto + suma_robocizna_brutto + transport # Uwaga: transport może być opodatkowany inaczej!

# Dodajemy obliczone podsumowania do głównych danych
dane_kosztorysu["podsumowanie"] = {
    "material_netto": suma_material_netto,
    "material_vat": suma_material_vat,
    "material_brutto": suma_material_brutto,
    "robocizna_netto": suma_robocizna_netto,
    "robocizna_vat": suma_robocizna_vat,
    "robocizna_brutto": suma_robocizna_brutto,
    "transport": transport,
    "razem_netto": razem_netto,
    "razem_brutto": razem_brutto
}


# --- 3. Proces generowania PDF ---

print("Rozpoczynam generowanie PDF...")

# Załaduj środowisko Jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='.'))
# Załaduj szablon HTML
template = env.get_template('template.html')

# "Renderuj" szablon, wstawiając w niego dane
# To tworzy ostateczny string HTML
html_output = template.render(dane_kosztorysu)

# Wczytaj arkusz stylów CSS
css = CSS(filename='style.css')

# Użyj WeasyPrint do konwersji HTML -> PDF
# 'base_url='.' jest ważne, aby HTML mógł znaleźć plik CSS
html_obj = HTML(string=html_output, base_url='.')
html_obj.write_pdf('kosztorys.pdf', stylesheets=[css])

print(f"✅ Gotowe! Plik 'kosztorys.pdf' został wygenerowany.")
