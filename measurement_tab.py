# measurement_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

import math

class MeasurementTab:
    """
    Moduł obsługujący osobną zakładkę 'Pomiar Dachu' - dodawanie figur (trapez, triangle, rectangle)
    i sumowanie powierzchni. Przechowuje listę elementów i pozwala na eksport sumy.
    """

    def __init__(self, app, parent_frame):
        """
        app: referencja do głównej aplikacji (RoofCalculatorApp) - używana do komunikacji
        parent_frame: frame, do którego dodajemy elementy UI
        """
        self.app = app
        self.parent = parent_frame

        self.items = []  # lista słowników: {"type": "trapez", "params": {...}, "area": float}

        self.build_ui()

    def build_ui(self):
        frm = ttk.LabelFrame(self.parent, text="Lista figur (trapezy / trójkąty / prostokąty)")
        frm.pack(fill="both", expand=False, padx=10, pady=8)

        # Row: typ figury
        ttk.Label(frm, text="Typ figury:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.shape_cb = ttk.Combobox(frm, values=["trapez", "trojkat", "prostokat"], state="readonly", width=12)
        self.shape_cb.set("trapez")
        self.shape_cb.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        self.shape_cb.bind("<<ComboboxSelected>>", lambda e: self.update_param_fields())

        # Parametry (dynamiczne)
        self.params_frame = ttk.Frame(frm)
        self.params_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=4, pady=4)

        # Inicjalne pola dla 'trapez'
        self.param_entries = {}
        self.update_param_fields()

        # Dodaj przycisk dodania
        ttk.Button(frm, text="Dodaj figurę", command=self.add_shape_from_inputs).grid(row=2, column=0, padx=4, pady=6, sticky="w")

        # Lista elementów (Treeview)
        list_frame = ttk.LabelFrame(self.parent, text="Dodane figury")
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("type", "params", "area")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse", height=8)
        self.tree.heading("type", text="Typ")
        self.tree.heading("params", text="Parametry")
        self.tree.heading("area", text="Powierzchnia [m²]")
        self.tree.column("type", width=100)
        self.tree.column("params", width=400)
        self.tree.column("area", width=120, anchor="e")
        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Kontrolki do zarządzania listą i sumą
        ctrl_frame = ttk.Frame(self.parent)
        ctrl_frame.pack(fill="x", padx=10, pady=6)
        ttk.Button(ctrl_frame, text="Usuń zaznaczoną", command=self.remove_selected).pack(side="left", padx=4)
        ttk.Button(ctrl_frame, text="Wyczyść listę", command=self.clear_list).pack(side="left", padx=4)

        self.total_label = ttk.Label(ctrl_frame, text="Suma powierzchni: 0.00 m²", font=("Arial", 10, "bold"))
        self.total_label.pack(side="right", padx=4)

    def update_param_fields(self):
        # Usuń obecne pola
        for child in self.params_frame.winfo_children():
            child.destroy()
        self.param_entries.clear()

        shape = self.shape_cb.get()
        row = 0
        if shape == "trapez":
            # Potrzebujemy: a (podstawa1), b (podstawa2), h (wysokość)
            ttk.Label(self.params_frame, text="a (podstawa1) [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["a"] = ttk.Entry(self.params_frame, width=10); self.param_entries["a"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="b (podstawa2) [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["b"] = ttk.Entry(self.params_frame, width=10); self.param_entries["b"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="h (wysokość) [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["h"] = ttk.Entry(self.params_frame, width=10); self.param_entries["h"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="Opis (opcjonalny):").grid(row=row, column=0, sticky="w"); self.param_entries["desc"] = ttk.Entry(self.params_frame, width=40); self.param_entries["desc"].grid(row=row, column=1, columnspan=2, padx=4, pady=2)
        elif shape == "trojkat":
            # Potrzebujemy: podstawę (b) i wysokość (h) lub trzy boki - przyjmiemy b i h
            ttk.Label(self.params_frame, text="b (podstawa) [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["b"] = ttk.Entry(self.params_frame, width=10); self.param_entries["b"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="h (wysokość) [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["h"] = ttk.Entry(self.params_frame, width=10); self.param_entries["h"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="Opis (opcjonalny):").grid(row=row, column=0, sticky="w"); self.param_entries["desc"] = ttk.Entry(self.params_frame, width=40); self.param_entries["desc"].grid(row=row, column=1, columnspan=2, padx=4, pady=2)
        elif shape == "prostokat":
            ttk.Label(self.params_frame, text="a [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["a"] = ttk.Entry(self.params_frame, width=10); self.param_entries["a"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="b [m]:").grid(row=row, column=0, sticky="w"); self.param_entries["b"] = ttk.Entry(self.params_frame, width=10); self.param_entries["b"].grid(row=row, column=1, padx=4, pady=2); row+=1
            ttk.Label(self.params_frame, text="Opis (opcjonalny):").grid(row=row, column=0, sticky="w"); self.param_entries["desc"] = ttk.Entry(self.params_frame, width=40); self.param_entries["desc"].grid(row=row, column=1, columnspan=2, padx=4, pady=2)

    def add_shape_from_inputs(self):
        shape = self.shape_cb.get()
        try:
            if shape == "trapez":
                a = float(self.param_entries["a"].get())
                b = float(self.param_entries["b"].get())
                h = float(self.param_entries["h"].get())
                if a < 0 or b < 0 or h < 0:
                    raise ValueError("Wymiary muszą być nieujemne.")
                area = 0.5 * (a + b) * h
                desc = self.param_entries.get("desc").get() if self.param_entries.get("desc") else ""
                params_text = f"a={a:.3f}, b={b:.3f}, h={h:.3f}"
                item = {"type": "trapez", "params": {"a": a, "b": b, "h": h, "desc": desc}, "area": area}
            elif shape == "trojkat":
                b = float(self.param_entries["b"].get())
                h = float(self.param_entries["h"].get())
                if b < 0 or h < 0:
                    raise ValueError("Wymiary muszą być nieujemne.")
                area = 0.5 * b * h
                desc = self.param_entries.get("desc").get() if self.param_entries.get("desc") else ""
                params_text = f"b={b:.3f}, h={h:.3f}"
                item = {"type": "trojkat", "params": {"b": b, "h": h, "desc": desc}, "area": area}
            elif shape == "prostokat":
                a = float(self.param_entries["a"].get())
                b = float(self.param_entries["b"].get())
                if a < 0 or b < 0:
                    raise ValueError("Wymiary muszą być nieujemne.")
                area = a * b
                desc = self.param_entries.get("desc").get() if self.param_entries.get("desc") else ""
                params_text = f"a={a:.3f}, b={b:.3f}"
                item = {"type": "prostokat", "params": {"a": a, "b": b, "desc": desc}, "area": area}
            else:
                raise ValueError("Nieznany typ figury.")

            # Dodajemy do listy i Treeview
            self.items.append(item)
            idx = len(self.items) - 1
            desc_text = item["params"].get("desc", "")
            params_display = params_text + (f" ({desc_text})" if desc_text else "")
            self.tree.insert("", "end", iid=str(idx), values=(item["type"], params_display, f"{item['area']:.3f}"))
            self.update_total_label()
        except ValueError as e:
            messagebox.showerror("Błąd danych", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz pozycję do usunięcia.")
            return
        iid = sel[0]
        try:
            idx = int(iid)
            # usuń z listy i tree
            self.items[idx] = None  # zostaw miejsce (prostsze mapowanie), zaktualizujemy tree po usunięciu
            self.tree.delete(iid)
            # przebuduj items i ponumeruj ponownie elementy w drzewie
            new_items = []
            self.tree.delete(*self.tree.get_children())
            for it in self.items:
                if it is not None:
                    new_items.append(it)
            self.items = new_items
            for i, it in enumerate(self.items):
                desc_text = it["params"].get("desc", "")
                params_display = self._params_to_str(it)
                self.tree.insert("", "end", iid=str(i), values=(it["type"], params_display, f"{it['area']:.3f}"))
            self.update_total_label()
        except Exception as e:
            messagebox.showerror("Błąd usuwania", f"Wystąpił błąd: {e}")

    def _params_to_str(self, item):
        t = item["type"]
        p = item["params"]
        if t == "trapez":
            return f"a={p['a']:.3f}, b={p['b']:.3f}, h={p['h']:.3f}" + (f" ({p.get('desc')})" if p.get("desc") else "")
        if t == "trojkat":
            return f"b={p['b']:.3f}, h={p['h']:.3f}" + (f" ({p.get('desc')})" if p.get("desc") else "")
        if t == "prostokat":
            return f"a={p['a']:.3f}, b={p['b']:.3f}" + (f" ({p.get('desc')})" if p.get("desc") else "")
        return ""

    def clear_list(self):
        if not self.items:
            return
        if not messagebox.askyesno("Potwierdź", "Czy na pewno wyczyścić listę figur?"):
            return
        self.items = []
        self.tree.delete(*self.tree.get_children())
        self.update_total_label()

    def update_total_label(self):
        total = sum(it["area"] for it in self.items)
        self.total_label.config(text=f"Suma powierzchni: {total:.3f} m²")

    def get_total_area(self):
        if not self.items:
            return None
        return sum(it["area"] for it in self.items)