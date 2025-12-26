"""
cost_calculations.py

Pomocnik do obliczeń kosztorysowych:
- oblicza netto/vat/brutto dla pojedynczych pozycji
- grupuje sumy po stawkach VAT i po kategoriach (material/service)
- dodaje pozycję transportu liczoną jako % od sumy netto (configurable)
- zwraca struktury ułatwiające generowanie raportu / PDF

Użycie:
  from cost_calculations import compute_totals
  res = compute_totals(items, transport_percent=3.0, transport_vat=23)

Format pozycji wejściowej (przykład):
  {
    "name": "Papa wierzchnia",
    "quantity": 120.0,
    "unit": "m2",
    "price_unit_net": 35.0,
    "vat_rate": 23,
    "category": "material",   # lub "service"
    "note": "kolor antracyt"
  }
"""

from typing import List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP, getcontext

# ustawiamy precyzję Decimal wystarczającą do finansów
getcontext().prec = 18

def _round(val: float, places: int = 2) -> float:
    """Zaokrąglenie finansowe (połówkowe do góry) na places miejsc dziesiętnych."""
    d = Decimal(str(val)).quantize(Decimal('1.' + '0'*places), rounding=ROUND_HALF_UP)
    return float(d)

def compute_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Oblicza dla pojedynczej pozycji wartości netto/vat/brutto.

    Wejście (przykład):
      - name (str)
      - quantity (float)
      - unit (str) optional
      - price_unit_net (float)  -- cena netto za jednostkę
      - vat_rate (int) one of [0,8,23] (domyślnie 23)
      - category (str) 'material' or 'service'
      - note (str) optional

    Zwraca słownik uzupełniony o:
      - total_net (float)
      - vat_value (float)
      - total_gross (float)
    """
    qty = float(item.get("quantity", 0.0) or 0.0)
    price_net = float(item.get("price_unit_net", 0.0) or 0.0)
    vat = int(item.get("vat_rate", 23) or 0)

    total_net = qty * price_net
    vat_value = total_net * vat / 100.0
    total_gross = total_net + vat_value

    item_out = dict(item)  # shallow copy
    item_out["total_net"] = _round(total_net, 2)
    item_out["vat_value"] = _round(vat_value, 2)
    item_out["total_gross"] = _round(total_gross, 2)
    # normalize some fields
    item_out["quantity"] = qty
    item_out["price_unit_net"] = _round(price_net, 2)
    item_out["vat_rate"] = vat
    item_out["category"] = (item.get("category") or "material").lower()
    return item_out

def compute_totals(items: List[Dict[str, Any]],
                   transport_percent: float = 3.0,
                   transport_vat: int = 23) -> Dict[str, Any]:
    """
    Przetwarza listę pozycji i zwraca podsumowania.

    Parametry:
      - items: lista pozycji (słowniki, patrz compute_item)
      - transport_percent: ile % z sumy netto doliczyć jako transport (np. 3.0)
      - transport_vat: stawka VAT dla transportu (np. 23)

    Zwraca strukturę:
      {
        "items": [augmented_items],
        "by_vat": { vat_rate: {"net": x, "vat": y, "gross": z}, ...},
        "by_category": { "material": {"net":..., "vat":..., "gross":...}, "service": {...} },
        "transport": { "net": tnet, "vat": tvat, "gross": tgross, "vat_rate": transport_vat, "percent": transport_percent },
        "summary": { "net": ..., "vat": ..., "gross": ... }
      }
    """
    augmented: List[Dict[str, Any]] = []
    by_vat: Dict[int, Dict[str, float]] = {}
    by_cat: Dict[str, Dict[str, float]] = {}
    total_net = 0.0
    total_vat = 0.0
    total_gross = 0.0

    # compute each item and aggregate
    for it in items:
        aug = compute_item(it)
        augmented.append(aug)

        vat_rate = int(aug.get("vat_rate", 0))
        cat = (aug.get("category") or "material").lower()

        if vat_rate not in by_vat:
            by_vat[vat_rate] = {"net": 0.0, "vat": 0.0, "gross": 0.0}
        by_vat[vat_rate]["net"] += aug["total_net"]
        by_vat[vat_rate]["vat"] += aug["vat_value"]
        by_vat[vat_rate]["gross"] += aug["total_gross"]

        if cat not in by_cat:
            by_cat[cat] = {"net": 0.0, "vat": 0.0, "gross": 0.0}
        by_cat[cat]["net"] += aug["total_net"]
        by_cat[cat]["vat"] += aug["vat_value"]
        by_cat[cat]["gross"] += aug["total_gross"]

        total_net += aug["total_net"]
        total_vat += aug["vat_value"]
        total_gross += aug["total_gross"]

    # Transport: procent od sumy netto (wybor użytkownika: procent od ceny netto)
    transport_net = 0.0
    transport_vat_value = 0.0
    transport_gross = 0.0
    try:
        tp = float(transport_percent or 0.0)
        if tp > 0 and total_net > 0:
            transport_net = _round(total_net * (tp / 100.0), 2)
            tv = int(transport_vat or 0)
            transport_vat_value = _round(transport_net * tv / 100.0, 2) if tv else 0.0
            transport_gross = _round(transport_net + transport_vat_value, 2)
    except Exception:
        transport_net = transport_vat_value = transport_gross = 0.0

    # dolicz transport do sum
    total_net = _round(total_net + transport_net, 2)
    total_vat = _round(total_vat + transport_vat_value, 2)
    total_gross = _round(total_gross + transport_gross, 2)

    # włącz transport jako wpis do by_vat oraz by_cat (jako usługa)
    if transport_net:
        tv = int(transport_vat or 0)
        if tv not in by_vat:
            by_vat[tv] = {"net": 0.0, "vat": 0.0, "gross": 0.0}
        by_vat[tv]["net"] += transport_net
        by_vat[tv]["vat"] += transport_vat_value
        by_vat[tv]["gross"] += transport_gross

        svc = "service"
        if svc not in by_cat:
            by_cat[svc] = {"net": 0.0, "vat": 0.0, "gross": 0.0}
        by_cat[svc]["net"] += transport_net
        by_cat[svc]["vat"] += transport_vat_value
        by_cat[svc]["gross"] += transport_gross

    # zaokrąglenie agregatów
    for vat_r, sums in list(by_vat.items()):
        by_vat[vat_r] = {"net": _round(sums["net"], 2), "vat": _round(sums["vat"], 2), "gross": _round(sums["gross"], 2)}
    for cat, sums in list(by_cat.items()):
        by_cat[cat] = {"net": _round(sums["net"], 2), "vat": _round(sums["vat"], 2), "gross": _round(sums["gross"], 2)}

    summary = {"net": _round(total_net, 2), "vat": _round(total_vat, 2), "gross": _round(total_gross, 2)}
    transport = {"net": transport_net, "vat": transport_vat_value, "gross": transport_gross, "vat_rate": int(transport_vat or 0), "percent": float(transport_percent or 0.0)}

    return {
        "items": augmented,
        "by_vat": by_vat,
        "by_category": by_cat,
        "transport": transport,
        "summary": summary
    }

# -- helpery do eksportu CSV (opcjonalne) --
def export_items_to_csv_rows(items: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Przygotowuje listę wierszy (list of strings) do zapisu CSV:
    Nagłówek:
      ["Nazwa", "Ilość", "JM", "Cena netto", "VAT %", "Netto", "VAT", "Brutto", "Kategoria", "Notatka"]
    """
    rows = [["Nazwa", "Ilość", "JM", "Cena netto", "VAT %", "Netto", "VAT", "Brutto", "Kategoria", "Notatka"]]
    for it in items:
        rows.append([
            str(it.get("name", "")),
            f"{it.get('quantity', 0):.3f}",
            str(it.get("unit", "")),
            f"{it.get('price_unit_net', 0.0):.2f}",
            str(it.get("vat_rate", 0)),
            f"{it.get('total_net', 0.0):.2f}",
            f"{it.get('vat_value', 0.0):.2f}",
            f"{it.get('total_gross', 0.0):.2f}",
            str(it.get("category", "")),
            str(it.get("note", ""))
        ])
    return rows

if __name__ == "__main__":
    # prosty testowy przykład
    sample = [
        {"name": "Papa wierzchnia", "quantity": 120.0, "unit": "m2", "price_unit_net": 35.0, "vat_rate": 23, "category": "material"},
        {"name": "Montaż papy", "quantity": 1.0, "unit": "job", "price_unit_net": 4000.0, "vat_rate": 23, "category": "service"},
        {"name": "Śruby i materiały drobne", "quantity": 5.0, "unit": "kg", "price_unit_net": 10.0, "vat_rate": 8, "category": "material"}
    ]
    res = compute_totals(sample, transport_percent=3.0, transport_vat=23)
    import pprint
    pprint.pprint(res)