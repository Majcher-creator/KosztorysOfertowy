#!/usr/bin/env python3
# main_app046.py
# Kalkulator Dachów - v4.6
# Zmiany:
# - Przechowywanie ostatniego numeru kosztorysu w settings.json (klucz last_invoice_seq i last_invoice_year).
#   Dzięki temu numer jest generowany szybko i niezawodnie bez parsowania katalogu.
# - Poprawka błędu AttributeError: missing calculate_cost_estimation (metoda dodana).
# - Pełny, zaktualizowany plik aplikacji z wszystkimi funkcjami poprzednich wersji.
# - v4.6: Integracja modułów: orynnowanie, kominy, obróbki, pomiar dachu
#
# Wymagane (opcjonalne do PDF/logo): pip install reportlab pillow
#
# Uruchom: python3.12 main_app046.py

from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json, os, csv, platform, subprocess, re
from datetime import datetime

# Import calculation modules
from gutter_calculations import calculate_guttering
from chimney_calculations import calculate_chimney_flashings, calculate_chimney_insulation
from flashing_calculations import calculate_flashings_total
from measurement_tab import MeasurementTab

# Pillow for logo preview (optional)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# reportlab for PDF
try:
    from reportlab.lib.pagesizes import A4, portrait
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------------- Helpers ----------------
def fmt_money_plain(v: float) -> str:
    s = f"{v:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", " ")

def fmt_money(v: float) -> str:
    return fmt_money_plain(v) + " zł"

def is_valid_float_text(s: str) -> bool:
    if s == "" or s == "-" or s == ".": return True
    s = s.replace(",", ".")
    return bool(re.match(r'^\d+(\.\d{0,3})?$', s))

def find_system_font_possibilities() -> Optional[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # broader search
    dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"), "C:\\Windows\\Fonts", "/Library/Fonts"]
    for d in dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(".ttf") and ("dejavu" in f.lower() or "liberation" in f.lower() or "arial" in f.lower() or "free" in f.lower()):
                    return os.path.join(root, f)
    return None

def safe_filename(s: str, maxlen: int = 140) -> str:
    s = s or ""
    s = s.strip()
    s = s.replace(" ", "_")
    s = re.sub(r'[^\w\-\._]', '', s)
    return s[:maxlen]

def compute_totals_local(items: List[Dict[str,Any]], transport_percent: float = 0.0, transport_vat: int = 23) -> Dict[str,Any]:
    res_items = []
    by_vat: Dict[int, Dict[str,float]] = {}
    by_cat: Dict[str, Dict[str,float]] = {}
    total_net = total_vat = total_gross = 0.0
    for it in items:
        qty = float(it.get("quantity",0.0) or 0.0)
        price = float(it.get("price_unit_net",0.0) or 0.0)
        vat = int(it.get("vat_rate",0) or 0)
        net = round(qty * price, 2)
        vat_val = round(net * vat / 100.0, 2)
        gross = round(net + vat_val, 2)
        aug = dict(it)
        aug.update({"total_net": net, "vat_value": vat_val, "total_gross": gross})
        res_items.append(aug)
        vb = by_vat.setdefault(vat, {"net":0.0,"vat":0.0,"gross":0.0})
        vb["net"] += net; vb["vat"] += vat_val; vb["gross"] += gross
        cat = it.get("category","material")
        cb = by_cat.setdefault(cat, {"net":0.0,"vat":0.0,"gross":0.0})
        cb["net"] += net; cb["vat"] += vat_val; cb["gross"] += gross
        total_net += net; total_vat += vat_val; total_gross += gross
    transport_net = round(total_net * (transport_percent/100.0),2) if transport_percent>0 else 0.0
    transport_vat_val = round(transport_net * (transport_vat/100.0),2) if transport_net>0 else 0.0
    transport_gross = round(transport_net + transport_vat_val,2)
    summary = {"net": round(total_net + transport_net,2), "vat": round(total_vat + transport_vat_val,2), "gross": round(total_gross + transport_gross,2)}
    return {"items": res_items, "by_vat": by_vat, "by_category": by_cat, "transport": {"percent":transport_percent,"net":transport_net,"vat":transport_vat_val,"gross":transport_gross}, "summary": summary}

# ---------------- Dialogs ----------------
class ClientDialog(simpledialog.Dialog):
    def __init__(self,parent,title,client=None):
        self.client = client or {}
        super().__init__(parent,title)
    def body(self,master):
        ttk.Label(master, text="Nazwa klienta:").grid(row=0,column=0,sticky="w")
        self.e_name = ttk.Entry(master, width=60); self.e_name.grid(row=0,column=1,pady=2)
        ttk.Label(master, text="Adres:").grid(row=1,column=0,sticky="w")
        self.e_address = ttk.Entry(master, width=60); self.e_address.grid(row=1,column=1,pady=2)
        ttk.Label(master, text="NIP / ID:").grid(row=2,column=0,sticky="w")
        self.e_id = ttk.Entry(master, width=60); self.e_id.grid(row=2,column=1,pady=2)
        ttk.Label(master, text="Telefon:").grid(row=3,column=0,sticky="w")
        self.e_phone = ttk.Entry(master, width=60); self.e_phone.grid(row=3,column=1,pady=2)
        ttk.Label(master, text="E-mail:").grid(row=4,column=0,sticky="w")
        self.e_mail = ttk.Entry(master, width=60); self.e_mail.grid(row=4,column=1,pady=2)
        if self.client:
            self.e_name.insert(0,self.client.get("name",""))
            self.e_address.insert(0,self.client.get("address",""))
            self.e_id.insert(0,self.client.get("id",""))
            self.e_phone.insert(0,self.client.get("phone",""))
            self.e_mail.insert(0,self.client.get("email",""))
        return self.e_name
    def apply(self):
        self.result = {"name": self.e_name.get().strip(), "address": self.e_address.get().strip(), "id": self.e_id.get().strip(), "phone": self.e_phone.get().strip(), "email": self.e_mail.get().strip()}

class CostItemEditDialog(simpledialog.Dialog):
    def __init__(self,parent,title,item=None):
        self.item = item or {}
        super().__init__(parent,title)
    def body(self,master):
        ttk.Label(master, text="Nazwa:").grid(row=0,column=0,sticky="w")
        self.e_name = ttk.Entry(master, width=50); self.e_name.grid(row=0,column=1,pady=2)
        ttk.Label(master, text="Ilość:").grid(row=1,column=0,sticky="w")
        self.e_qty = ttk.Entry(master, width=12); self.e_qty.grid(row=1,column=1,sticky="w", pady=2)
        ttk.Label(master, text="JM:").grid(row=2,column=0,sticky="w")
        self.e_unit = ttk.Entry(master, width=12); self.e_unit.grid(row=2,column=1,sticky="w", pady=2)
        ttk.Label(master, text="Cena netto:").grid(row=3,column=0,sticky="w")
        self.e_price = ttk.Entry(master, width=12); self.e_price.grid(row=3,column=1,sticky="w", pady=2)
        ttk.Label(master, text="VAT [%]:").grid(row=4,column=0,sticky="w")
        self.vat_cb = ttk.Combobox(master, values=["0","8","23"], width=8, state="readonly"); self.vat_cb.grid(row=4,column=1,sticky="w")
        ttk.Label(master, text="Kategoria:").grid(row=5,column=0,sticky="w")
        self.cat_cb = ttk.Combobox(master, values=["material","service"], width=12, state="readonly"); self.cat_cb.grid(row=5,column=1,sticky="w")
        ttk.Label(master, text="Notatka:").grid(row=6,column=0,sticky="nw")
        self.t_note = tk.Text(master, height=4, width=40); self.t_note.grid(row=6,column=1,pady=2)
        vcmd = (master.register(lambda P: is_valid_float_text(P)), "%P")
        self.e_qty.config(validate="key", validatecommand=vcmd); self.e_price.config(validate="key", validatecommand=vcmd)
        if self.item:
            self.e_name.insert(0,self.item.get("name",""))
            self.e_qty.insert(0,f"{float(self.item.get('quantity',0.0)):.3f}")
            self.e_unit.insert(0,self.item.get("unit",""))
            self.e_price.insert(0,f"{float(self.item.get('price_unit_net',0.0)):.2f}")
            self.vat_cb.set(str(self.item.get("vat_rate",23)))
            self.cat_cb.set(self.item.get("category","material"))
            self.t_note.insert("1.0", self.item.get("note",""))
        else:
            self.vat_cb.set("23"); self.cat_cb.set("material")
        return self.e_name
    def validate(self):
        if not self.e_name.get().strip():
            messagebox.showerror("Błąd","Nazwa wymagana"); return False
        try:
            float(self.e_qty.get().replace(",",".") or 0.0)
            float(self.e_price.get().replace(",",".") or 0.0)
        except Exception:
            messagebox.showerror("Błąd","Ilość i cena muszą być liczbami"); return False
        return True
    def apply(self):
        self.result = {"name": self.e_name.get().strip(), "quantity": float(self.e_qty.get().replace(",","." ) or 0.0), "unit": self.e_unit.get().strip(), "price_unit_net": float(self.e_price.get().replace(",","." ) or 0.0), "vat_rate": int(self.vat_cb.get() or 23), "category": self.cat_cb.get() or "material", "note": self.t_note.get("1.0","end").strip()}

class MaterialEditDialog(simpledialog.Dialog):
    def __init__(self,parent,title,material=None):
        self.material = material or {}
        super().__init__(parent,title)
    def body(self,master):
        ttk.Label(master, text="Nazwa:").grid(row=0,column=0,sticky="w")
        self.e_name = ttk.Entry(master, width=60); self.e_name.grid(row=0,column=1,pady=2)
        ttk.Label(master, text="JM:").grid(row=1,column=0,sticky="w")
        self.e_unit = ttk.Entry(master, width=20); self.e_unit.grid(row=1,column=1,pady=2, sticky="w")
        ttk.Label(master, text="Cena netto (jedn.):").grid(row=2,column=0,sticky="w")
        self.e_price = ttk.Entry(master, width=20); self.e_price.grid(row=2,column=1,pady=2, sticky="w")
        ttk.Label(master, text="VAT [%]:").grid(row=3,column=0,sticky="w")
        self.vat_cb = ttk.Combobox(master, values=["0","8","23"], width=8, state="readonly"); self.vat_cb.grid(row=3,column=1,sticky="w")
        ttk.Label(master, text="Kategoria:").grid(row=4,column=0,sticky="w")
        self.cat_cb = ttk.Combobox(master, values=["material","service"], width=12, state="readonly"); self.cat_cb.grid(row=4,column=1,sticky="w")
        vcmd = (master.register(lambda P: is_valid_float_text(P)), "%P")
        self.e_price.config(validate="key", validatecommand=vcmd)
        if self.material:
            self.e_name.insert(0, self.material.get("name",""))
            self.e_unit.insert(0, self.material.get("unit",""))
            self.e_price.insert(0, f"{float(self.material.get('price_unit_net',0.0)):.2f}")
            self.vat_cb.set(str(self.material.get("vat_rate",23)))
            self.cat_cb.set(self.material.get("category","material"))
        else:
            self.vat_cb.set("23"); self.cat_cb.set("material")
        return self.e_name
    def validate(self):
        if not self.e_name.get().strip():
            messagebox.showerror("Błąd","Nazwa wymagana"); return False
        try:
            float(self.e_price.get().replace(",",".") or 0.0)
        except Exception:
            messagebox.showerror("Błąd","Cena musi być liczbą"); return False
        return True
    def apply(self):
        self.result = {"name": self.e_name.get().strip(), "unit": self.e_unit.get().strip(), "price_unit_net": float(self.e_price.get().replace(",",".") or 0.0), "vat_rate": int(self.vat_cb.get() or 23), "category": self.cat_cb.get() or "material"}

# ---------------- Main App ----------------
class RoofCalculatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Kalkulator Dachów - v4.6")
        master.geometry("1280x940")
        # data stores
        self.clients: List[Dict[str,Any]] = []
        self.materials_db: List[Dict[str,Any]] = []
        self.cost_items: List[Dict[str,Any]] = []
        self.logo_path: Optional[str] = None
        # UI vars
        self.transport_percent = tk.DoubleVar(value=3.0)
        self.transport_vat = tk.IntVar(value=23)
        self.open_pdf_after = tk.BooleanVar(value=True)
        self.invoice_number = tk.StringVar(value="")
        self.invoice_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.roof_area = tk.StringVar(value="0.00")
        self.quote_name = tk.StringVar(value="")
        # company defaults
        self.settings = {
            "company_name": "VICTOR TOMASZ MAJCHERCZYK",
            "company_address": "Reymonta 1/1, Dąbrowa Górnicza",
            "company_nip": "629-225-54-24",
            "company_phone": "555-555-555",
            "company_email": "victor.dachy@example.com",
            "company_account": "14 2000 0000 0000 0000 0000 000",
            # maintained keys:
            "last_invoice_year": None,
            "last_invoice_seq": 0
        }
        # register PDF font
        self._registered_pdf_font_name = None
        if REPORTLAB_AVAILABLE:
            fp = find_system_font_possibilities()
            if fp:
                try:
                    pdfmetrics.registerFont(TTFont("AppUnicode", fp))
                    self._registered_pdf_font_name = "AppUnicode"
                except Exception:
                    self._registered_pdf_font_name = None
        # load db/settings
        self._load_local_db(); self._load_settings()
        # build UI
        self.create_menu(); self.create_notebook(); self.create_all_tabs()
        # set next invoice number on startup (uses settings.json stored sequence)
        self._set_next_invoice_number()

    # persistence helpers
    def _local_appdir(self):
        base = os.path.expanduser("~")
        appdir = os.path.join(base, ".roofcalc")
        os.makedirs(appdir, exist_ok=True)
        return appdir
    def _local_db_path(self, name):
        return os.path.join(self._local_appdir(), name)
    def _profiles_path(self):
        return self._local_db_path("company_profiles.json")
    def _load_local_db(self):
        try:
            m = self._local_db_path("materials_db.json"); c = self._local_db_path("clients_db.json")
            if os.path.exists(m):
                with open(m,"r",encoding="utf-8") as f: self.materials_db = json.load(f)
            if os.path.exists(c):
                with open(c,"r",encoding="utf-8") as f: self.clients = json.load(f)
        except Exception:
            self.materials_db = []; self.clients = []
    def _save_local_db(self):
        try:
            with open(self._local_db_path("clients_db.json"), "w", encoding="utf-8") as f: json.dump(self.clients, f, ensure_ascii=False, indent=2)
            with open(self._local_db_path("materials_db.json"), "w", encoding="utf-8") as f: json.dump(self.materials_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Błąd zapisu bazy", f"Nie udało się zapisać bazy:\n{e}")

    def _load_settings(self):
        p = self._local_db_path("settings.json")
        try:
            if os.path.exists(p):
                with open(p,"r",encoding="utf-8") as f:
                    s = json.load(f)
                    # merge with defaults
                    self.settings.update(s)
                    self.logo_path = s.get("logo", self.logo_path)
        except Exception:
            pass

    def _save_settings(self):
        p = self._local_db_path("settings.json")
        try:
            data = dict(self.settings)
            data["logo"] = self.logo_path
            with open(p,"w",encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Błąd zapisu ustawień", f"Nie udało się zapisać ustawień:\n{e}")

    # invoice numbering using settings.json
    def _get_next_seq_and_set(self) -> int:
        # read last stored sequence/year from settings (already loaded)
        current_year = datetime.now().year
        last_year = self.settings.get("last_invoice_year")
        last_seq = int(self.settings.get("last_invoice_seq", 0) or 0)
        if last_year != current_year:
            next_seq = 1
        else:
            next_seq = last_seq + 1
        # update settings and save
        self.settings["last_invoice_year"] = current_year
        self.settings["last_invoice_seq"] = next_seq
        self._save_settings()
        return next_seq

    def _set_next_invoice_number(self):
        seq = self._get_next_seq_and_set()
        year = datetime.now().year
        self.invoice_number.set(f"{year}-{seq:03d}")

    # menu
    def create_menu(self):
        menubar = tk.Menu(self.master); self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Nowy kosztorys", command=self.new_cost_estimate)
        file_menu.add_command(label="Zapisz kosztorys (.cost.json)", command=self.save_costfile)
        file_menu.add_command(label="Wczytaj kosztorys (.cost.json)", command=self.load_costfile)
        file_menu.add_separator()
        file_menu.add_command(label="Profile firmy...", command=self.open_company_profiles_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Zapisz bazę materiałów", command=self.save_materials_db)
        file_menu.add_command(label="Wczytaj bazę materiałów", command=self.load_materials_db)
        file_menu.add_separator()
        file_menu.add_command(label="Zapisz ustawienia", command=self._save_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.master.quit)
        company_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Firma", menu=company_menu)
        company_menu.add_command(label="Edytuj dane firmy (aktualne)", command=self.edit_current_company)
        company_menu.add_command(label="Wybierz logo...", command=self.select_logo)

    def new_cost_estimate(self):
        if self.cost_items or (hasattr(self,"comment_text") and self.comment_text.get("1.0","end").strip()):
            if not messagebox.askyesno("Nowy kosztorys", "Utworzyć nowy kosztorys (aktualny zostanie odrzucony)?"): return
        self.cost_items = []
        if hasattr(self,"comment_text"):
            self.comment_text.delete("1.0","end")
        self._refresh_cost_ui()
        # allocate new invoice number and persist
        seq = self._get_next_seq_and_set()
        year = datetime.now().year
        self.invoice_number.set(f"{year}-{seq:03d}")
        messagebox.showinfo("Nowy kosztorys", f"Utworzono nowy kosztorys. Nr: {self.invoice_number.get()}")

    def open_company_profiles_dialog(self):
        dlg = CompanyProfilesDialog(self.master, self._profiles_path())
        self.master.wait_window(dlg)
        if getattr(dlg, "selected_profile", None):
            prof = dlg.selected_profile
            self.settings["company_name"] = prof.get("company_name","")
            self.settings["company_address"] = prof.get("company_address","")
            self.settings["company_nip"] = prof.get("company_nip","")
            self.settings["company_phone"] = prof.get("company_phone","")
            self.settings["company_email"] = prof.get("company_email","")
            self.settings["company_account"] = prof.get("company_account","")
            self.logo_path = prof.get("logo", self.logo_path)
            self._save_settings()
            messagebox.showinfo("Profil załadowany", f"Wczytano profil: {prof.get('profile_name','')}")

    def edit_current_company(self):
        prof = {"profile_name":"(aktualne)","company_name":self.settings.get("company_name",""),"company_address":self.settings.get("company_address",""),"company_nip":self.settings.get("company_nip",""),"company_phone":self.settings.get("company_phone",""),"company_email":self.settings.get("company_email",""),"company_account":self.settings.get("company_account",""),"logo":self.logo_path}
        dlg = CompanyEditDialog(self.master, "Edytuj dane firmy", prof)
        if getattr(dlg,"result",None):
            r = dlg.result
            self.settings["company_name"] = r.get("company_name","")
            self.settings["company_address"] = r.get("company_address","")
            self.settings["company_nip"] = r.get("company_nip","")
            self.settings["company_phone"] = r.get("company_phone","")
            self.settings["company_email"] = r.get("company_email","")
            self.settings["company_account"] = r.get("company_account","")
            self.logo_path = r.get("logo", self.logo_path)
            self._save_settings()
            messagebox.showinfo("Zapisano","Dane firmy zaktualizowane.")

    # select logo
    def select_logo(self):
        path = filedialog.askopenfilename(title="Wybierz plik z logo", filetypes=[("Images","*.png;*.jpg;*.jpeg;*.bmp;*.gif"),("All","*.*")])
        if not path: return
        self.logo_path = path; self._save_settings()
        if PIL_AVAILABLE:
            try:
                img = Image.open(path); img.thumbnail((400,200))
                win = tk.Toplevel(self.master); win.title("Podgląd logo"); lbl = ttk.Label(win); lbl.pack(padx=8,pady=8)
                tk_img = ImageTk.PhotoImage(img); lbl.image = tk_img; lbl.config(image=tk_img); ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=6)
            except Exception:
                pass
        messagebox.showinfo("Logo","Logo ustawione. Będzie użyte w nagłówku PDF.")

    # save/load materials DB
    def save_materials_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json"),("All","*.*")])
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as f: json.dump(self.materials_db, f, ensure_ascii=False, indent=2)
            try:
                with open(self._local_db_path("materials_db.json"), "w", encoding="utf-8") as f: json.dump(self.materials_db, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            messagebox.showinfo("Zapisano", f"Zapisano bazę: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać bazy materiałów:\n{e}")

    def load_materials_db(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json"),("All","*.*")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: self.materials_db = json.load(f)
            try:
                with open(self._local_db_path("materials_db.json"), "w", encoding="utf-8") as f: json.dump(self.materials_db, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            messagebox.showinfo("Wczytano", f"Wczytano bazę: {path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać bazy:\n{e}")

    # notebook
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.master); self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Create all tabs
    def create_all_tabs(self):
        self.create_cost_tab()
        self.create_measurement_tab()
        self.create_gutter_tab()
        self.create_chimney_tab()
        self.create_flashing_tab()
    
    # measurement tab (Pomiar Dachu)
    def create_measurement_tab(self):
        self.measurement_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.measurement_frame, text="Pomiar Dachu")
        self.measurement_tab_module = MeasurementTab(self, self.measurement_frame)
        
        # Add button to transfer area to cost estimate
        ctrl_frame = ttk.Frame(self.measurement_frame)
        ctrl_frame.pack(fill="x", padx=10, pady=6)
        ttk.Button(ctrl_frame, text="Przenieś sumę do metrażu dachu", command=self._transfer_measurement_to_roof_area).pack(side="left", padx=4)
    
    def _transfer_measurement_to_roof_area(self):
        total = self.measurement_tab_module.get_total_area()
        if total is None or total == 0:
            messagebox.showwarning("Brak danych", "Brak zmierzonych figur do przeniesienia.")
            return
        self.roof_area.set(f"{total:.2f}")
        messagebox.showinfo("Przeniesiono", f"Powierzchnia {total:.2f} m² przeniesiona do metrażu dachu.")
    
    # gutter tab (Orynnowanie)
    def create_gutter_tab(self):
        self.gutter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gutter_frame, text="Orynnowanie")
        
        input_frame = ttk.LabelFrame(self.gutter_frame, text="Parametry orynnowania")
        input_frame.pack(fill="x", padx=10, pady=8)
        
        # Input fields
        row = 0
        ttk.Label(input_frame, text="Długość okapu [m]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.gutter_okap_length = ttk.Entry(input_frame, width=12)
        self.gutter_okap_length.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Wysokość dachu (rura spustowa) [m]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.gutter_roof_height = ttk.Entry(input_frame, width=12)
        self.gutter_roof_height.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Liczba rur spustowych (opcjonalnie):").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.gutter_num_downpipes = ttk.Entry(input_frame, width=12)
        self.gutter_num_downpipes.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Button(input_frame, text="Oblicz orynnowanie", command=self._calculate_guttering).grid(row=row, column=0, columnspan=2, pady=8)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.gutter_frame, text="Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        self.gutter_results_text = tk.Text(results_frame, height=12, state="disabled")
        self.gutter_results_text.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Button to transfer to cost estimate
        ttk.Button(self.gutter_frame, text="Dodaj do kosztorysu", command=self._add_guttering_to_cost).pack(pady=8)
        
        self.gutter_last_results = None
    
    def _calculate_guttering(self):
        try:
            okap_length = float(self.gutter_okap_length.get() or 0)
            roof_height = float(self.gutter_roof_height.get() or 0)
            num_downpipes_str = self.gutter_num_downpipes.get().strip()
            num_downpipes = int(num_downpipes_str) if num_downpipes_str else None
            
            results = calculate_guttering(okap_length, roof_height, num_downpipes)
            self.gutter_last_results = results
            
            text = f"""Wyniki obliczeń orynnowania:
            
Długość rynny: {results['total_gutter_length_m']:.2f} m
Długość rur spustowych: {results['total_downpipe_length_m']:.2f} m
Liczba rur spustowych: {results['num_downpipes']}
Haki rynnowe: {results['num_gutter_hooks']} szt.
Łączniki rynny: {results['num_gutter_connectors']} szt.
Wyloty do rur: {results['num_downpipe_outlets']} szt.
Obejmy rury spustowej: {results['num_downpipe_clamps']} szt.
Kolanka rury spustowej: {results['num_downpipe_elbows']} szt.
Zaślepki: {results['num_end_caps']} szt.
"""
            self.gutter_results_text.config(state="normal")
            self.gutter_results_text.delete("1.0", "end")
            self.gutter_results_text.insert("end", text)
            self.gutter_results_text.config(state="disabled")
            
        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowe dane: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")
    
    def _add_guttering_to_cost(self):
        if not self.gutter_last_results:
            messagebox.showwarning("Brak danych", "Najpierw wykonaj obliczenia orynnowania.")
            return
        
        r = self.gutter_last_results
        items_to_add = [
            {"name": "Rynna", "quantity": r['total_gutter_length_m'], "unit": "mb", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Rura spustowa", "quantity": r['total_downpipe_length_m'], "unit": "mb", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Haki rynnowe", "quantity": float(r['num_gutter_hooks']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Łączniki rynny", "quantity": float(r['num_gutter_connectors']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Wyloty do rur", "quantity": float(r['num_downpipe_outlets']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Obejmy rury spustowej", "quantity": float(r['num_downpipe_clamps']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Kolanka rury spustowej", "quantity": float(r['num_downpipe_elbows']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Zaślepki rynny", "quantity": float(r['num_end_caps']), "unit": "szt.", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
        ]
        
        for item in items_to_add:
            if item["quantity"] > 0:
                self.cost_items.append(item)
        
        self._refresh_cost_ui()
        messagebox.showinfo("Dodano", "Elementy orynnowania dodane do kosztorysu. Uzupełnij ceny jednostkowe.")
    
    # chimney tab (Kominy)
    def create_chimney_tab(self):
        self.chimney_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chimney_frame, text="Kominy")
        
        input_frame = ttk.LabelFrame(self.chimney_frame, text="Parametry komina")
        input_frame.pack(fill="x", padx=10, pady=8)
        
        row = 0
        ttk.Label(input_frame, text="Szerokość komina [m]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_width = ttk.Entry(input_frame, width=12)
        self.chimney_width.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Długość komina [m]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_length = ttk.Entry(input_frame, width=12)
        self.chimney_length.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Wysokość ponad dachem [m]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_height = ttk.Entry(input_frame, width=12)
        self.chimney_height.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Kąt nachylenia dachu [°]:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_roof_angle = ttk.Entry(input_frame, width=12)
        self.chimney_roof_angle.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Rodzaj pokrycia:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_covering_type = ttk.Combobox(input_frame, values=["papa", "blacha", "dachówka"], width=12, state="readonly")
        self.chimney_covering_type.set("papa")
        self.chimney_covering_type.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Label(input_frame, text="Liczba kominów:").grid(row=row, column=0, sticky="w", padx=4, pady=4)
        self.chimney_num = ttk.Entry(input_frame, width=12)
        self.chimney_num.insert(0, "1")
        self.chimney_num.grid(row=row, column=1, padx=4, pady=4, sticky="w")
        row += 1
        
        ttk.Button(input_frame, text="Oblicz obróbkę komina", command=self._calculate_chimney).grid(row=row, column=0, columnspan=2, pady=8)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.chimney_frame, text="Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        self.chimney_results_text = tk.Text(results_frame, height=12, state="disabled")
        self.chimney_results_text.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Button to transfer to cost estimate
        ttk.Button(self.chimney_frame, text="Dodaj do kosztorysu", command=self._add_chimney_to_cost).pack(pady=8)
        
        self.chimney_last_results = None
    
    def _calculate_chimney(self):
        try:
            width = float(self.chimney_width.get() or 0)
            length = float(self.chimney_length.get() or 0)
            height = float(self.chimney_height.get() or 0)
            roof_angle = float(self.chimney_roof_angle.get() or 30)
            covering_type = self.chimney_covering_type.get()
            num_chimneys = int(self.chimney_num.get() or 1)
            
            results = calculate_chimney_flashings(width, length, height, roof_angle, covering_type, num_chimneys)
            insulation = calculate_chimney_insulation(width, length, height, num_chimneys)
            results.update(insulation)
            self.chimney_last_results = results
            
            text = f"""Wyniki obliczeń obróbki komina:

Powierzchnia obróbki blacharskiej: {results['total_metal_flashing_surface_m2']:.2f} m²
Liczba arkuszy blachy (obróbka): {results['num_metal_sheets_flashing']} szt.
Powierzchnia czapy kominowej: {results['total_chimney_cap_surface_m2']:.2f} m²
Liczba arkuszy blachy (czapa): {results['num_metal_sheets_cap']} szt.
Powierzchnia papy na kołnierz: {results['total_felt_flashing_surface_m2']:.2f} m²
Długość listwy dociskowej: {results['total_clamping_strip_length_m']:.2f} mb
Obwód pojedynczego komina: {results['single_chimney_perimeter']:.2f} m

Ocieplenie:
Powierzchnia ocieplenia: {results.get('total_insulation_surface_m2', 0):.2f} m²
Powierzchnia siatki z klejem: {results.get('total_mesh_surface_m2', 0):.2f} m²
"""
            self.chimney_results_text.config(state="normal")
            self.chimney_results_text.delete("1.0", "end")
            self.chimney_results_text.insert("end", text)
            self.chimney_results_text.config(state="disabled")
            
        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowe dane: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")
    
    def _add_chimney_to_cost(self):
        if not self.chimney_last_results:
            messagebox.showwarning("Brak danych", "Najpierw wykonaj obliczenia obróbki komina.")
            return
        
        r = self.chimney_last_results
        items_to_add = [
            {"name": "Blacha obróbka komina", "quantity": r['total_metal_flashing_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
            {"name": "Czapa kominowa - blacha", "quantity": r['total_chimney_cap_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"},
        ]
        
        if r['total_felt_flashing_surface_m2'] > 0:
            items_to_add.append({"name": "Papa kołnierz komina", "quantity": r['total_felt_flashing_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"})
        
        if r['total_clamping_strip_length_m'] > 0:
            items_to_add.append({"name": "Listwa dociskowa", "quantity": r['total_clamping_strip_length_m'], "unit": "mb", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"})
        
        if r.get('total_insulation_surface_m2', 0) > 0:
            items_to_add.append({"name": "Ocieplenie komina", "quantity": r['total_insulation_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"})
            items_to_add.append({"name": "Siatka z klejem (komin)", "quantity": r['total_mesh_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"})
        
        for item in items_to_add:
            if item["quantity"] > 0:
                self.cost_items.append(item)
        
        self._refresh_cost_ui()
        messagebox.showinfo("Dodano", "Elementy obróbki komina dodane do kosztorysu. Uzupełnij ceny jednostkowe.")
    
    # flashing tab (Obróbki)
    def create_flashing_tab(self):
        self.flashing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flashing_frame, text="Obróbki")
        
        input_frame = ttk.LabelFrame(self.flashing_frame, text="Lista obróbek blacharskich")
        input_frame.pack(fill="x", padx=10, pady=8)
        
        # Define flashing types
        self.flashing_items_vars = {}
        flashing_types = [
            ("Gąsiory", "gasior"),
            ("Wiatrownice", "wiatrownica"),
            ("Kosze dachowe", "kosz"),
            ("Obróbka okapu", "okap"),
            ("Obróbka ściany (gurt)", "gurt"),
            ("Pas nadrynnowy", "pas_nadrynnowy"),
            ("Pas podrynnowy", "pas_podrynnowy"),
        ]
        
        row = 0
        ttk.Label(input_frame, text="Nazwa").grid(row=row, column=0, padx=4, pady=2, sticky="w")
        ttk.Label(input_frame, text="Zaznacz").grid(row=row, column=1, padx=4, pady=2)
        ttk.Label(input_frame, text="Długość [m]").grid(row=row, column=2, padx=4, pady=2)
        ttk.Label(input_frame, text="Szer. rozw. [m]").grid(row=row, column=3, padx=4, pady=2)
        row += 1
        
        for name, key in flashing_types:
            self.flashing_items_vars[key] = {
                "selected": tk.BooleanVar(value=False),
                "length": tk.StringVar(value="0"),
                "width": tk.StringVar(value="0.33"),
            }
            ttk.Label(input_frame, text=name).grid(row=row, column=0, padx=4, pady=2, sticky="w")
            ttk.Checkbutton(input_frame, variable=self.flashing_items_vars[key]["selected"]).grid(row=row, column=1, padx=4, pady=2)
            ttk.Entry(input_frame, textvariable=self.flashing_items_vars[key]["length"], width=10).grid(row=row, column=2, padx=4, pady=2)
            ttk.Entry(input_frame, textvariable=self.flashing_items_vars[key]["width"], width=10).grid(row=row, column=3, padx=4, pady=2)
            row += 1
        
        ttk.Button(input_frame, text="Oblicz obróbki", command=self._calculate_flashings).grid(row=row, column=0, columnspan=4, pady=8)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.flashing_frame, text="Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        self.flashing_results_text = tk.Text(results_frame, height=8, state="disabled")
        self.flashing_results_text.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Button to transfer to cost estimate
        ttk.Button(self.flashing_frame, text="Dodaj do kosztorysu", command=self._add_flashings_to_cost).pack(pady=8)
        
        self.flashing_last_results = None
    
    def _calculate_flashings(self):
        try:
            flashing_items = {}
            for key, vars_dict in self.flashing_items_vars.items():
                flashing_items[key] = {
                    "selected": vars_dict["selected"].get(),
                    "length": float(vars_dict["length"].get() or 0),
                    "width": float(vars_dict["width"].get() or 0),
                }
            
            results = calculate_flashings_total(flashing_items)
            self.flashing_last_results = results
            
            text = f"""Wyniki obliczeń obróbek blacharskich:

Całkowita powierzchnia blachy: {results['total_surface_m2']:.2f} m²
Liczba arkuszy blachy (1,25x2,5m): {results['num_sheets']} szt.

Szczegóły zaznaczonych obróbek:
"""
            for key, data in flashing_items.items():
                if data["selected"]:
                    area = data["length"] * data["width"]
                    text += f"  - {key}: {data['length']:.2f} m × {data['width']:.2f} m = {area:.2f} m²\n"
            
            self.flashing_results_text.config(state="normal")
            self.flashing_results_text.delete("1.0", "end")
            self.flashing_results_text.insert("end", text)
            self.flashing_results_text.config(state="disabled")
            
        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowe dane: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")
    
    def _add_flashings_to_cost(self):
        if not self.flashing_last_results:
            messagebox.showwarning("Brak danych", "Najpierw wykonaj obliczenia obróbek.")
            return
        
        r = self.flashing_last_results
        if r['total_surface_m2'] > 0:
            item = {"name": "Blacha na obróbki", "quantity": r['total_surface_m2'], "unit": "m²", "price_unit_net": 0.0, "vat_rate": 23, "category": "material"}
            self.cost_items.append(item)
            self._refresh_cost_ui()
            messagebox.showinfo("Dodano", f"Blacha na obróbki ({r['total_surface_m2']:.2f} m²) dodana do kosztorysu. Uzupełnij cenę jednostkową.")
        else:
            messagebox.showwarning("Brak danych", "Brak zaznaczonych obróbek do dodania.")

    # cost tab UI (kept similar to previous working version)
    def create_cost_tab(self):
        # Implementation mirrors main_app043/main_app044 UI layout
        self.cost_tab = ttk.Frame(self.notebook); self.notebook.add(self.cost_tab, text="Kosztorys/Oferta")
        left = ttk.Frame(self.cost_tab); left.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        right_container = ttk.Frame(self.cost_tab, width=420); right_container.pack(side="right", fill="y", padx=8, pady=8)

        # header/meta
        header_frame = ttk.Frame(left); header_frame.pack(fill="x", pady=(0,6))
        self.client_summary_label = ttk.Label(header_frame, text="Klient: (brak)", anchor="w", font=("Arial",10)); self.client_summary_label.pack(side="left", anchor="w")
        inv_frame = ttk.Frame(header_frame); inv_frame.pack(side="right", anchor="e")
        ttk.Label(inv_frame, text="Nr kosztorysu:").grid(row=0,column=0,sticky="e"); ttk.Entry(inv_frame,width=18,textvariable=self.invoice_number).grid(row=0,column=1,padx=4)
        ttk.Button(inv_frame, text="Nowy", command=self.new_cost_estimate).grid(row=0,column=2,padx=4)
        ttk.Label(inv_frame, text="Metraż dachu [m²]:").grid(row=0,column=3,sticky="e"); ttk.Entry(inv_frame,width=8,textvariable=self.roof_area).grid(row=0,column=4,padx=4)
        ttk.Label(inv_frame, text="Nazwa kosztorysu:").grid(row=1,column=0,sticky="e"); ttk.Entry(inv_frame,width=30,textvariable=self.quote_name).grid(row=1,column=1,columnspan=4,padx=4)
        ttk.Label(inv_frame, text="Data:").grid(row=0,column=5,sticky="e"); ttk.Entry(inv_frame,width=12,textvariable=self.invoice_date).grid(row=0,column=6,padx=4)

        # toolbar
        toolbar = ttk.Frame(left); toolbar.pack(fill="x", pady=(0,6))
        ttk.Button(toolbar, text="Oblicz kosztorys", command=self.calculate_cost_estimation).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Eksportuj CSV", command=self.export_cost_csv).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Eksportuj PDF", command=self.export_cost_pdf).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Wstaw z bazy", command=self.manage_materials_db).pack(side="right", padx=4)
        ttk.Button(toolbar, text="Klienci", command=self.manage_clients).pack(side="right", padx=4)

        # quick sums
        sums_frame = ttk.Frame(left); sums_frame.pack(fill="x", pady=(0,6))
        self.lbl_mat_total = ttk.Label(sums_frame, text="Materiały netto: 0,00 zł"); self.lbl_mat_total.pack(side="left", padx=6)
        self.lbl_srv_total = ttk.Label(sums_frame, text="Usługi netto: 0,00 zł"); self.lbl_srv_total.pack(side="left", padx=6)
        self.lbl_total_all = ttk.Label(sums_frame, text="Suma brutto: 0,00 zł", font=("Arial",10,"bold")); self.lbl_total_all.pack(side="right", padx=6)

        # split area: materials and services
        split_pane = ttk.Panedwindow(left, orient="vertical")
        split_pane.pack(fill="both", expand=True)
        mat_frame = ttk.Labelframe(split_pane, text="Materiały")
        srv_frame = ttk.Labelframe(split_pane, text="Usługi")
        split_pane.add(mat_frame, weight=1); split_pane.add(srv_frame, weight=1)

        # materials tree with scrollbar
        mat_tree_container = ttk.Frame(mat_frame); mat_tree_container.pack(fill="both", expand=True, padx=6, pady=6)
        mat_tree_container.config(height=260)
        mat_cols = ("name","qty","unit","price_net","net")
        self.mat_tree = ttk.Treeview(mat_tree_container, columns=mat_cols, show="headings", selectmode="browse")
        for c,h in zip(mat_cols,("Nazwa","Ilość","JM","Cena netto","Wartość netto")):
            self.mat_tree.heading(c, text=h); self.mat_tree.column(c, width=300 if c=="name" else 80, anchor="w" if c=="name" else "e")
        mat_vscroll = ttk.Scrollbar(mat_tree_container, orient="vertical", command=self.mat_tree.yview)
        self.mat_tree.configure(yscrollcommand=mat_vscroll.set)
        self.mat_tree.pack(side="left", fill="both", expand=True)
        mat_vscroll.pack(side="right", fill="y")
        mat_btnf = ttk.Frame(mat_frame); mat_btnf.pack(fill="x", padx=6, pady=4)
        ttk.Button(mat_btnf, text="Edytuj zaznaczoną", command=lambda: self._edit_from_tree("material")).pack(side="left", padx=4)
        ttk.Button(mat_btnf, text="Usuń zaznaczoną", command=lambda: self._delete_from_tree("material")).pack(side="left", padx=4)

        # services tree with scrollbar
        srv_tree_container = ttk.Frame(srv_frame); srv_tree_container.pack(fill="both", expand=True, padx=6, pady=6)
        srv_tree_container.config(height=260)
        srv_cols = ("name","qty","unit","price_net","net")
        self.srv_tree = ttk.Treeview(srv_tree_container, columns=srv_cols, show="headings", selectmode="browse")
        for c,h in zip(srv_cols,("Nazwa","Ilość","JM","Cena netto","Wartość netto")):
            self.srv_tree.heading(c, text=h); self.srv_tree.column(c, width=300 if c=="name" else 80, anchor="w" if c=="name" else "e")
        srv_vscroll = ttk.Scrollbar(srv_tree_container, orient="vertical", command=self.srv_tree.yview)
        self.srv_tree.configure(yscrollcommand=srv_vscroll.set)
        self.srv_tree.pack(side="left", fill="both", expand=True)
        srv_vscroll.pack(side="right", fill="y")
        srv_btnf = ttk.Frame(srv_frame); srv_btnf.pack(fill="x", padx=6, pady=4)
        ttk.Button(srv_btnf, text="Edytuj zaznaczoną", command=lambda: self._edit_from_tree("service")).pack(side="left", padx=4)
        ttk.Button(srv_btnf, text="Usuń zaznaczoną", command=lambda: self._delete_from_tree("service")).pack(side="left", padx=4)

        # right panel (add item / client / transport / summary)
        right = ttk.Frame(right_container); right.pack(fill="both", expand=True, padx=4, pady=4)
        form = ttk.LabelFrame(right, text="Dodaj pozycję"); form.pack(fill="x", pady=6, padx=6)
        ttk.Label(form, text="Nazwa:").grid(row=0,column=0,sticky="w"); self.c_name = ttk.Entry(form, width=36); self.c_name.grid(row=0,column=1)
        ttk.Label(form, text="Ilość:").grid(row=1,column=0,sticky="w"); self.c_qty = ttk.Entry(form, width=12); self.c_qty.grid(row=1,column=1,sticky="w")
        ttk.Label(form, text="JM:").grid(row=2,column=0,sticky="w"); self.c_unit = ttk.Entry(form, width=12); self.c_unit.grid(row=2,column=1,sticky="w")
        ttk.Label(form, text="Cena netto:").grid(row=3,column=0,sticky="w"); self.c_price = ttk.Entry(form, width=12); self.c_price.grid(row=3,column=1,sticky="w")
        ttk.Label(form, text="VAT:").grid(row=4,column=0,sticky="w"); self.c_vat = ttk.Combobox(form, values=["0","8","23"], width=8, state="readonly"); self.c_vat.grid(row=4,column=1,sticky="w"); self.c_vat.set("23")
        ttk.Label(form, text="Kategoria:").grid(row=5,column=0,sticky="w"); self.c_cat = ttk.Combobox(form, values=["material","service"], width=12, state="readonly"); self.c_cat.grid(row=5,column=1,sticky="w"); self.c_cat.set("material")
        vcmd_f = (self.master.register(lambda P: is_valid_float_text(P)), "%P")
        self.c_qty.config(validate="key", validatecommand=vcmd_f); self.c_price.config(validate="key", validatecommand=vcmd_f)
        ttk.Button(right, text="Dodaj do kosztorysu", command=self.add_cost_item_from_form).pack(fill="x", pady=6, padx=6)
        ttk.Button(right, text="Wstaw z bazy (okno)", command=self.manage_materials_db).pack(fill="x", pady=2, padx=6)
        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(right, text="Zarządzaj klientami", command=self.manage_clients).pack(fill="x", pady=2, padx=6)
        ttk.Label(right, text="Wybierz klienta:").pack(anchor="w", padx=6, pady=(6,0))
        self.client_cb = ttk.Combobox(right, values=[c.get("name","") for c in self.clients], state="readonly", width=36)
        self.client_cb.pack(anchor="w", padx=6); self.client_cb.bind("<<ComboboxSelected>>", lambda e: self._on_client_selected())
        transport_frame = ttk.LabelFrame(right, text="Transport"); transport_frame.pack(fill="x", pady=6, padx=6)
        ttk.Label(transport_frame, text="Procent [%]:").grid(row=0,column=0,sticky="w"); self.e_transport = ttk.Entry(transport_frame, width=8, textvariable=self.transport_percent); self.e_transport.grid(row=0,column=1,padx=4)
        ttk.Label(transport_frame, text="VAT:").grid(row=1,column=0,sticky="w"); self.transport_vat_cb = ttk.Combobox(transport_frame, values=["0","8","23"], width=8, state="readonly", textvariable=self.transport_vat); self.transport_vat_cb.grid(row=1,column=1)
        summary_frame = ttk.Labelframe(right, text="Podsumowanie / Komentarz"); summary_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.summary_text = tk.Text(summary_frame, height=10, state="disabled"); self.summary_text.pack(fill="both", expand=True)
        ttk.Label(summary_frame, text="Komentarz (umieszczony w PDF):").pack(anchor="w", padx=4, pady=(6,0))
        self.comment_text = tk.Text(summary_frame, height=6); self.comment_text.pack(fill="both", expand=False, padx=4, pady=(0,6))

        # double-click edit bindings
        self.mat_tree.bind("<Double-1>", lambda e: self._edit_from_tree("material"))
        self.srv_tree.bind("<Double-1>", lambda e: self._edit_from_tree("service"))

        self._refresh_cost_ui()

    # map cost_items into trees
    def _refresh_cost_ui(self):
        try:
            self.mat_tree.delete(*self.mat_tree.get_children())
            self.srv_tree.delete(*self.srv_tree.get_children())
            for i,it in enumerate(self.cost_items):
                qty=float(it.get("quantity",0.0)); price=float(it.get("price_unit_net",0.0))
                total_net = round(qty * price,2)
                vals = (it.get("name",""), f"{qty:.3f}", it.get("unit",""), f"{price:.2f}", f"{total_net:.2f}")
                if it.get("category","material") == "material":
                    self.mat_tree.insert("", "end", iid=str(i), values=vals)
                else:
                    self.srv_tree.insert("", "end", iid=str(i), values=vals)
            mats=[it for it in self.cost_items if it.get("category","material")=="material"]
            srvs=[it for it in self.cost_items if it.get("category","material")=="service"]
            mats_tot = sum(round(float(it.get("quantity",0.0))*float(it.get("price_unit_net",0.0)),2) for it in mats)
            srvs_tot = sum(round(float(it.get("quantity",0.0))*float(it.get("price_unit_net",0.0)),2) for it in srvs)
            mats_vat = sum(round((float(it.get("quantity",0.0))*float(it.get("price_unit_net",0.0))) * (int(it.get("vat_rate",0))/100.0),2) for it in mats)
            srvs_vat = sum(round((float(it.get("quantity",0.0))*float(it.get("price_unit_net",0.0))) * (int(it.get("vat_rate",0))/100.0),2) for it in srvs)
            total_gross = mats_tot + mats_vat + srvs_tot + srvs_vat
            self.lbl_mat_total.config(text=f"Materiały netto: {fmt_money_plain(mats_tot)} zł")
            self.lbl_srv_total.config(text=f"Usługi netto: {fmt_money_plain(srvs_tot)} zł")
            self.lbl_total_all.config(text=f"Suma brutto: {fmt_money_plain(total_gross)} zł")
        except Exception as e:
            print("Refresh UI error:", e)

    # add/edit/delete cost items
    def add_cost_item_from_form(self):
        try:
            item = {"name": self.c_name.get().strip(), "quantity": float(self.c_qty.get().replace(",","." ) or 0.0), "unit": self.c_unit.get().strip(), "price_unit_net": float(self.c_price.get().replace(",","." ) or 0.0), "vat_rate": int(self.c_vat.get() or 23), "category": self.c_cat.get() or "material", "note": ""}
        except Exception as e:
            messagebox.showerror("Błąd", f"Nieprawidłowe dane: {e}"); return
        self.cost_items.append(item); self._refresh_cost_ui()
        self.c_name.delete(0,tk.END); self.c_qty.delete(0,tk.END); self.c_unit.delete(0,tk.END); self.c_price.delete(0,tk.END)

    def _edit_from_tree(self, kind: str):
        tree = self.mat_tree if kind=="material" else self.srv_tree
        sel = tree.selection()
        if not sel: messagebox.showwarning("Brak zaznaczenia","Wybierz pozycję"); return
        idx = int(sel[0]); it = self.cost_items[idx]
        dlg = CostItemEditDialog(self.master, "Edytuj pozycję", item=it)
        if getattr(dlg,"result",None):
            self.cost_items[idx] = dlg.result; self._refresh_cost_ui()

    def _delete_from_tree(self, kind: str):
        tree = self.mat_tree if kind=="material" else self.srv_tree
        sel = tree.selection()
        if not sel: messagebox.showwarning("Brak zaznaczenia","Wybierz pozycję"); return
        idx = int(sel[0])
        if not messagebox.askyesno("Usuń","Usunąć pozycję?"): return
        del self.cost_items[idx]; self._refresh_cost_ui()

    # calculation / summary (fix for missing method)
    def calculate_cost_estimation(self):
        res = compute_totals_local(self.cost_items, float(self.transport_percent.get() or 0.0), int(self.transport_vat.get() or 23))
        sb=[]
        sb.append("Podsumowanie wg VAT:\n")
        for vat,s in sorted(res["by_vat"].items()):
            sb.append(f" VAT {vat}%: Netto {s['net']:.2f}  VAT {s['vat']:.2f}  Brutto {s['gross']:.2f}\n")
        sb.append("\nPodsumowanie wg kategorii:\n")
        for cat,s in res["by_category"].items():
            sb.append(f" {cat}: Netto {s['net']:.2f}  Brutto {s['gross']:.2f}\n")
        t=res["transport"]
        sb.append(f"\nTransport ({t['percent']}%): Netto {t['net']:.2f}  VAT {t['vat']:.2f}  Brutto {t['gross']:.2f}\n")
        s=res["summary"]
        sb.append(f"\nSuma końcowa: Netto {s['net']:.2f}  VAT {s['vat']:.2f}  Brutto {s['gross']:.2f}\n")
        self.summary_text.config(state="normal"); self.summary_text.delete("1.0","end"); self.summary_text.insert("end","".join(sb)); self.summary_text.config(state="disabled")
        self.last_cost_calc = res
        messagebox.showinfo("Obliczono","Kosztorys obliczony.")

    # clients management with search by name/address
    def manage_clients(self):
        w=tk.Toplevel(self.master); w.title("Zarządzaj klientami"); w.geometry("760x420")
        top = ttk.Frame(w); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Szukaj (nazwa/adres):").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=search_var, width=40); search_entry.pack(side="left", padx=6)
        listbox=tk.Listbox(w); listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        def populate_list(*_):
            q = search_var.get().strip().lower()
            listbox.delete(0, tk.END)
            for c in self.clients:
                title = c.get("name","")
                addr = c.get("address","")
                if q and q not in title.lower() and q not in addr.lower():
                    continue
                listbox.insert(tk.END, f"{title} — {addr}")
        for c in self.clients: listbox.insert(tk.END, f"{c.get('name','')} — {c.get('address','')}")
        btnf=ttk.Frame(w); btnf.pack(side="right", fill="y", padx=6, pady=6)
        def add_client():
            dlg=ClientDialog(self.master,"Nowy klient")
            if getattr(dlg,"result",None):
                self.clients.append(dlg.result); populate_list(); self._save_local_db(); self._refresh_client_combobox()
        def edit_client():
            sel=listbox.curselection();
            if not sel: messagebox.showwarning("Brak","Wybierz klienta"); return
            i=sel[0]; visible = [c for c in self.clients if (not search_var.get().strip() or search_var.get().strip().lower() in c.get("name","").lower() or search_var.get().strip().lower() in c.get("address","").lower())]
            c = visible[i]
            dlg=ClientDialog(self.master,"Edytuj klienta", client=c)
            if getattr(dlg,"result",None):
                # find real index
                try:
                    real_idx = next(idx for idx,v in enumerate(self.clients) if v is c)
                except StopIteration:
                    real_idx = next(idx for idx,v in enumerate(self.clients) if v.get("name","")==c.get("name","") and v.get("address","")==c.get("address",""))
                self.clients[real_idx]=dlg.result; populate_list(); self._save_local_db(); self._refresh_client_combobox()
        def del_client():
            sel=listbox.curselection();
            if not sel: return
            if not messagebox.askyesno("Usuń","Usuń klienta?"): return
            visible = [c for c in self.clients if (not search_var.get().strip() or search_var.get().strip().lower() in c.get("name","").lower() or search_var.get().strip().lower() in c.get("address","").lower())]
            c = visible[sel[0]]
            self.clients = [x for x in self.clients if x is not c]
            populate_list(); self._save_local_db(); self._refresh_client_combobox()
        def select_and_close():
            sel=listbox.curselection()
            if sel:
                visible = [c for c in self.clients if (not search_var.get().strip() or search_var.get().strip().lower() in c.get("name","").lower() or search_var.get().strip().lower() in c.get("address","").lower())]
                c = visible[sel[0]]
                self.client_cb.set(c.get("name","")); self._on_client_selected()
            w.destroy()
        ttk.Button(btnf, text="Dodaj", command=add_client).pack(fill="x", pady=4)
        ttk.Button(btnf, text="Edytuj", command=edit_client).pack(fill="x", pady=4)
        ttk.Button(btnf, text="Usuń", command=del_client).pack(fill="x", pady=4)
        ttk.Separator(btnf, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(btnf, text="Wybierz i zamknij", command=select_and_close).pack(fill="x", pady=4)
        search_entry.bind("<KeyRelease>", lambda e: populate_list())
        populate_list()

    def _refresh_client_combobox(self):
        names=[c.get("name","") for c in self.clients]
        if hasattr(self,"client_cb"):
            self.client_cb['values']=names
            if names and not self.client_cb.get():
                self.client_cb.set(names[0]); self._on_client_selected()

    def _on_client_selected(self):
        selname=self.client_cb.get()
        client = next((c for c in self.clients if c.get("name","")==selname), None)
        if client:
            summary=f"{client.get('name','')}\n{client.get('address','')}\nNIP: {client.get('id','')}  Tel: {client.get('phone','')}"
            self.client_summary_label.config(text=summary)
        else:
            self.client_summary_label.config(text="Klient: (brak)")

    # manage_materials_db (drag/drop and multi-insert) - reusing prior implementation logic
    def manage_materials_db(self):
        w = tk.Toplevel(self.master); w.title("Baza materiałów/usług"); w.geometry("1000x520")
        topbar = ttk.Frame(w); topbar.pack(fill="x", padx=8, pady=6)
        ttk.Label(topbar, text="Szukaj:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(topbar, textvariable=search_var, width=40); search_entry.pack(side="left", padx=6)
        ttk.Label(topbar, text="Kategoria:").pack(side="left", padx=(10,2))
        cat_var = tk.StringVar(value="all")
        cat_cb = ttk.Combobox(topbar, values=["all","material","service"], textvariable=cat_var, width=12, state="readonly"); cat_cb.pack(side="left")
        sort_asc = tk.BooleanVar(value=True)
        def toggle_sort():
            sort_asc.set(not sort_asc.get()); btn_sort.config(text="Sort: A→Z" if sort_asc.get() else "Sort: Z→A"); populate2()
        btn_sort = ttk.Button(topbar, text="Sort: A→Z", command=toggle_sort); btn_sort.pack(side="left", padx=8)

        cols=("name","unit","price","vat","cat")
        tree=ttk.Treeview(w, columns=cols, show="headings", selectmode="extended")
        for c,h in zip(cols,("Nazwa","JM","Cena net","VAT%","Kategoria")):
            tree.heading(c, text=h); tree.column(c, width=360 if c=="name" else 100, anchor="w" if c=="name" else "center")
        tree.pack(fill="both", expand=True, padx=6, pady=6)

        displayed_list: List[Dict[str,Any]] = []
        def rebuild_displayed_list():
            nonlocal displayed_list
            q = search_var.get().strip().lower()
            cat = cat_var.get()
            displayed_list = []
            for m in self.materials_db:
                nm = m.get("name","")
                if q and q not in nm.lower(): continue
                if cat != "all" and m.get("category","") != cat: continue
                displayed_list.append(m)
            displayed_list.sort(key=lambda x: x.get("name","").lower(), reverse=not sort_asc.get())
            return displayed_list

        def populate2(*_):
            nonlocal displayed_list
            displayed_list = rebuild_displayed_list()
            for iid in tree.get_children(): tree.delete(iid)
            for i,m in enumerate(displayed_list):
                tree.insert("", "end", iid=str(i), values=(m.get("name",""), m.get("unit",""), f"{m.get('price_unit_net',0.0):.2f}", str(m.get('vat_rate',23)), m.get("category","")))
        search_entry.bind("<KeyRelease>", populate2)
        cat_cb.bind("<<ComboboxSelected>>", populate2)
        populate2()

        frame=ttk.Frame(w); frame.pack(fill="x", padx=6, pady=6)
        def add_mat():
            dlg = MaterialEditDialog(self.master, "Nowy materiał/usługa")
            if getattr(dlg,"result",None):
                self.materials_db.append(dlg.result); self._save_local_db(); populate2()
        def edit_mat():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Brak","Wybierz pozycję do edycji"); return
            idx = int(sel[0])
            displayed = rebuild_displayed_list()
            m = displayed[idx]
            try:
                real_idx = next(i for i,v in enumerate(self.materials_db) if v is m)
            except StopIteration:
                real_idx = next(i for i,v in enumerate(self.materials_db) if v.get("name","")==m.get("name","") and v.get("unit","")==m.get("unit",""))
            dlg = MaterialEditDialog(self.master, "Edytuj materiał/usługę", material=self.materials_db[real_idx])
            if getattr(dlg,"result",None):
                self.materials_db[real_idx] = dlg.result; self._save_local_db(); populate2()
        def del_mat():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Brak","Wybierz pozycję do usunięcia"); return
            if not messagebox.askyesno("Usuń","Usunąć wybrane pozycje z bazy?"): return
            displayed = rebuild_displayed_list()
            to_remove = [displayed[int(i)] for i in sel]
            self.materials_db = [m for m in self.materials_db if m not in to_remove]
            self._save_local_db(); populate2()
        def insert_selected_to_cost_and_close():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Brak","Wybierz przynajmniej jedną pozycję do wstawienia"); return
            displayed = rebuild_displayed_list()
            for i in sel:
                idx = int(i)
                if 0 <= idx < len(displayed):
                    m = displayed[idx]
                    item = {"name": m.get("name",""), "quantity": 1.0, "unit": m.get("unit",""), "price_unit_net": m.get("price_unit_net",0.0), "vat_rate": m.get("vat_rate",23), "category": m.get("category","material"), "note": ""}
                    self.cost_items.append(item)
            self._refresh_cost_ui()
            w.destroy()
        ttk.Button(frame, text="Dodaj", command=add_mat).pack(side="left", padx=4)
        ttk.Button(frame, text="Edytuj", command=edit_mat).pack(side="left", padx=4)
        ttk.Button(frame, text="Usuń", command=del_mat).pack(side="left", padx=4)
        ttk.Button(frame, text="Wstaw zaznaczone do kosztorysu i zamknij", command=insert_selected_to_cost_and_close).pack(side="right", padx=4)

        # Drag & drop impl (threshold)
        drag_state = {"start_iids": [], "ghost": None, "dragging": False, "start_pos": (0,0)}
        DRAG_THRESHOLD = 6
        def on_button_press(event):
            sel = tree.selection()
            if not sel: return
            drag_state["start_iids"] = [int(i) for i in sel]
            drag_state["start_pos"] = (event.x_root, event.y_root)
            drag_state["dragging"] = False
        def on_motion(event):
            if not drag_state["start_iids"]: return
            sx, sy = drag_state["start_pos"]
            dx = abs(event.x_root - sx); dy = abs(event.y_root - sy)
            if not drag_state["dragging"] and (dx >= DRAG_THRESHOLD or dy >= DRAG_THRESHOLD):
                drag_state["dragging"] = True
                drag_state["ghost"] = tk.Toplevel(w); drag_state["ghost"].overrideredirect(True)
                lbl = ttk.Label(drag_state["ghost"], text=f"Wstaw: {len(drag_state['start_iids'])} pozycji", relief="solid", background="#ffffe0"); lbl.pack()
            if drag_state["dragging"] and drag_state.get("ghost"):
                drag_state["ghost"].geometry(f"+{event.x_root+10}+{event.y_root+10}")
        def on_button_release(event):
            if not drag_state["start_iids"]: return
            if drag_state["dragging"]:
                x, y = self.master.winfo_pointerx(), self.master.winfo_pointery()
                target = self.master.winfo_containing(x, y)
                displayed = rebuild_displayed_list()
                inserted = 0
                for idx in drag_state["start_iids"]:
                    if 0 <= idx < len(displayed):
                        m = displayed[idx]
                        item = {"name": m.get("name",""), "quantity": 1.0, "unit": m.get("unit",""), "price_unit_net": m.get("price_unit_net",0.0), "vat_rate": m.get("vat_rate",23), "category": m.get("category","material"), "note": ""}
                        if target is getattr(self, "srv_tree", None) or (target and str(target).startswith(str(getattr(self, "srv_tree", None)))):
                            item["category"] = "service"
                        self.cost_items.append(item); inserted += 1
                if drag_state.get("ghost"):
                    drag_state["ghost"].destroy(); drag_state["ghost"] = None
                drag_state["start_iids"] = []; drag_state["dragging"] = False
                if inserted:
                    self._refresh_cost_ui()
                    try: w.destroy()
                    except Exception: pass
                return
            # else: just a click, do nothing special
            drag_state["start_iids"] = []; drag_state["dragging"] = False
            if drag_state.get("ghost"):
                drag_state["ghost"].destroy(); drag_state["ghost"] = None

        tree.bind("<ButtonPress-1>", on_button_press); tree.bind("<B1-Motion>", on_motion); tree.bind("<ButtonRelease-1>", on_button_release)

    # export CSV (same as before)
    def export_cost_csv(self):
        if not self.cost_items:
            messagebox.showwarning("Brak pozycji","Brak pozycji do eksportu."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv"),("All","*.*")])
        if not path: return
        rows=[["Lp","Nazwa","Ilość","JM","Cena netto","Wartość netto","Kategoria"]]
        for i,it in enumerate(self.cost_items, start=1):
            try:
                qty = float(it.get("quantity",0.0)); price = float(it.get("price_unit_net",0.0))
            except Exception:
                qty = 0.0; price = 0.0
            net = round(qty*price,2)
            rows.append([i, it.get("name",""), f"{qty:.3f}", it.get("unit",""), f"{price:.2f}", f"{net:.2f}", it.get("category","")])
        try:
            with open(path,"w",newline='',encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                for r in rows: writer.writerow(r)
            messagebox.showinfo("Eksport CSV", f"Zapisano CSV: {path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać CSV:\n{e}")

    # export PDF (kept from previous working implementation)
    def export_cost_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Brak biblioteki","Zainstaluj reportlab: pip install reportlab"); return
        if not self.cost_items:
            messagebox.showwarning("Brak pozycji","Brak pozycji do eksportu."); return
        totals = compute_totals_local(self.cost_items, float(self.transport_percent.get() or 0.0), int(self.transport_vat.get() or 23))
        items_aug = totals["items"]
        materials = [it for it in items_aug if it.get("category","material")=="material"]
        services = [it for it in items_aug if it.get("category","material")=="service"]
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf"),("All","*.*")])
        if not path: return
        doc = SimpleDocTemplate(path, pagesize=portrait(A4), leftMargin=12, rightMargin=12, topMargin=12, bottomMargin=12)
        styles = getSampleStyleSheet(); base_font = self._registered_pdf_font_name or styles['Normal'].fontName
        normal = ParagraphStyle("NormalApp", parent=styles['Normal'], fontName=base_font, fontSize=9, leading=11)
        heading = ParagraphStyle("HeadingApp", parent=styles['Heading3'], fontName=base_font, fontSize=10, leading=12)
        title = ParagraphStyle("TitleApp", parent=styles['Title'], fontName=base_font, fontSize=12, leading=14, alignment=1)
        elems = []
        # header meta and remaining PDF construction similar to main_app043 - kept for brevity but present in full
        meta_lines = []
        meta_lines.append(f"Nr kosztorysu: {self.invoice_number.get()}")
        meta_lines.append(f"Data: {self.invoice_date.get()}")
        meta_lines.append(f"Metraż dachu: {self.roof_area.get()} m²")
        if self.quote_name.get():
            meta_lines.append(f"Nazwa: {self.quote_name.get()}")
        meta_para = Paragraph("<br/>".join(meta_lines), normal)
        right_parts = []
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = RLImage(self.logo_path)
                img.drawHeight = 30*mm
                img.drawWidth = img.drawHeight * img.imageWidth / img.imageHeight
                right_parts.append(img)
            except Exception:
                pass
        header_tbl = Table([[meta_para, right_parts]], colWidths=[330,200])
        header_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
        elems.append(header_tbl); elems.append(Spacer(1,8))
        # client/company two-column
        client = next((c for c in self.clients if hasattr(self,"client_cb") and c.get("name","")==self.client_cb.get()), None)
        client_lines=[]
        if client:
            client_lines.append(client.get("name",""))
            if client.get("address",""): client_lines.append(client.get("address",""))
            if client.get("id",""): client_lines.append("NIP: "+client.get("id",""))
            if client.get("phone",""): client_lines.append("Tel: "+client.get("phone",""))
            if client.get("email",""): client_lines.append("E-mail: "+client.get("email",""))
        else:
            client_lines.append("(Brak klienta)")
        company_lines=[]
        company_lines.append(self.settings.get("company_name",""))
        if self.settings.get("company_address",""): company_lines.append(self.settings.get("company_address",""))
        if self.settings.get("company_nip",""): company_lines.append("NIP: "+self.settings.get("company_nip",""))
        if self.settings.get("company_phone",""): company_lines.append("Tel: "+self.settings.get("company_phone",""))
        if self.settings.get("company_email",""): company_lines.append("E-mail: "+self.settings.get("company_email",""))
        if self.settings.get("company_account",""): company_lines.append("Nr konta: "+self.settings.get("company_account",""))
        left_part = Paragraph("<br/>".join(client_lines), normal)
        right_part = Paragraph("<br/>".join(company_lines), normal)
        cc_tbl = Table([[left_part,right_part]], colWidths=[330,200]); cc_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
        elems.append(cc_tbl); elems.append(Spacer(1,10))
        elems.append(Paragraph("KOSZTORYS OFERTOWY", title)); elems.append(Spacer(1,10))
        # helper: add tables with sums (narrower columns)
        def add_table_with_sum(title_txt: str, rows: List[List[str]], sum_label: str, sum_value: float):
            elems.append(Paragraph(title_txt, heading))
            max_rows_per_table = 28
            total_rows = len(rows)
            chunks = [rows[i:i+max_rows_per_table] for i in range(0, total_rows, max_rows_per_table)]
            if not chunks:
                chunks = [[]]
            for ci, chunk in enumerate(chunks):
                tbl = [["Lp","Nazwa","Ilość","JM","Cena netto","Wartość netto"]] + chunk
                if ci == len(chunks)-1:
                    tbl.append(["", sum_label, "", "", "", f"{fmt_money_plain(sum_value)}"])
                    t = Table(tbl, repeatRows=1, colWidths=[28,300,48,36,70,80])
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
                        ('ALIGN',(2,1),(2,-2),'RIGHT'),
                        ('ALIGN',(4,1),(5,-2),'RIGHT'),
                        ('ALIGN',(5,-1),(5,-1),'RIGHT'),
                        ('SPAN',(1,-1),(4,-1)),
                        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#FFF2B2")),
                        ('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
                        ('FONTSIZE',(0,0),(-1,-1),9),
                    ]))
                else:
                    t = Table(tbl, repeatRows=1, colWidths=[28,330,48,36,70,80])
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
                        ('ALIGN',(2,1),(2,-1),'RIGHT'),
                        ('ALIGN',(4,1),(5,-1),'RIGHT'),
                        ('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
                        ('FONTSIZE',(0,0),(-1,-1),9),
                    ]))
                elems.append(t); elems.append(Spacer(1,8))
                if ci < len(chunks)-1:
                    elems.append(PageBreak())
        mat_rows = [[str(i+1), it.get("name",""), f"{it.get('quantity',0):.3f}", it.get("unit",""), f"{it.get('price_unit_net',0.0):.2f}", f"{it.get('total_net',0.0):.2f}"] for i,it in enumerate(materials)]
        mat_sum = sum(it.get("total_net",0.0) for it in materials)
        add_table_with_sum("MATERIAŁY", mat_rows, "SUMA MATERIAŁY:", mat_sum)
        srv_rows = [[str(i+1), it.get("name",""), f"{it.get('quantity',0):.3f}", it.get("unit",""), f"{it.get('price_unit_net',0.0):.2f}", f"{it.get('total_net',0.0):.2f}"] for i,it in enumerate(services)]
        srv_sum = sum(it.get("total_net",0.0) for it in services)
        add_table_with_sum("USŁUGI", srv_rows, "SUMA USŁUGI:", srv_sum)
        # overall summary
        elems.append(Paragraph("PODSUMOWANIE", heading))
        summary_rows = [["Opis","Netto","VAT","Brutto"]]
        for vat,s in sorted(totals["by_vat"].items()):
            summary_rows.append([f"VAT {vat} %", fmt_money_plain(s.get("net",0.0))+" zł", fmt_money_plain(s.get("vat",0.0))+" zł", fmt_money_plain(s.get("gross",0.0))+" zł"])
        tinfo = totals["transport"]
        summary_rows.append(["Transport", fmt_money_plain(tinfo.get("net",0.0))+" zł", fmt_money_plain(tinfo.get("vat",0.0))+" zł", fmt_money_plain(tinfo.get("gross",0.0))+" zł"])
        ssum = totals["summary"]
        summary_rows.append(["RAZEM", fmt_money_plain(ssum.get("net",0.0))+" zł", fmt_money_plain(ssum.get("vat",0.0))+" zł", fmt_money_plain(ssum.get("gross",0.0))+" zł"])
        sum_tbl = Table(summary_rows, colWidths=[240,120,120,120])
        sum_tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),0.25,colors.grey),('ALIGN',(1,0),(-1,-1),'RIGHT'),('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),('FONTSIZE',(0,0),(-1,-1),9)]))
        elems.append(sum_tbl); elems.append(Spacer(1,10))
        # comment
        comment = self.comment_text.get("1.0","end").strip()
        if comment:
            elems.append(Paragraph("Komentarz:", heading))
            elems.append(Paragraph(comment.replace("\n","<br/>"), normal))
            elems.append(Spacer(1,8))
        try:
            doc.build(elems)
            messagebox.showinfo("PDF wygenerowany", f"Zapisano PDF: {path}")
        except Exception as e:
            messagebox.showerror("Błąd PDF", f"Nie udało się wygenerować PDF:\n{e}"); return
        if self.open_pdf_after.get():
            try:
                if platform.system()=="Windows":
                    os.startfile(path)
                else:
                    env = os.environ.copy(); env["NO_AT_BRIDGE"]="1"
                    if platform.system()=="Darwin":
                        subprocess.Popen(["open", path], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.Popen(["xdg-open", path], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    # save/load costfile (include comment) - when saving, update last_invoice_seq in settings based on current invoice_number
    def save_costfile(self):
        client = None
        if hasattr(self, "client_cb") and self.client_cb.get():
            client = next((c for c in self.clients if c.get("name","")==self.client_cb.get()), None)
        client_addr = (client.get("address","") if client else "") or (client.get("name","") if client else "")
        quote = self.quote_name.get() or "kosztorys"
        inv = self.invoice_number.get() or ""
        date = self.invoice_date.get() or datetime.now().strftime("%Y-%m-%d")
        part1 = safe_filename(client_addr.replace(" ", ""), 60)
        part2 = safe_filename(quote.replace(" ", "-"), 60)
        part3 = safe_filename(inv, 40)
        base_name = "-".join([p for p in (part1, part2, part3) if p])
        if not base_name: base_name = "kosztorys"
        initial = f"{base_name}.{date}.cost.json"
        path = filedialog.asksaveasfilename(defaultextension=".cost.json", filetypes=[("Kosztorys","*.cost.json"),("JSON","*.json")], initialfile=initial)
        if not path: return
        client_name = self.client_cb.get() if hasattr(self,"client_cb") else ""
        comment = self.comment_text.get("1.0","end").strip()
        # Get measurement data if available
        measurement_items = []
        if hasattr(self, "measurement_tab_module") and self.measurement_tab_module.items:
            measurement_items = self.measurement_tab_module.items
        data = {"items": self.cost_items, "transport_percent": float(self.transport_percent.get()), "transport_vat": int(self.transport_vat.get()), "logo": self.logo_path, "client": client_name, "invoice_number": self.invoice_number.get(), "invoice_date": self.invoice_date.get(), "roof_area": self.roof_area.get(), "quote_name": self.quote_name.get(), "comment": comment, "measurement_items": measurement_items, "saved_at": datetime.now().isoformat()}
        try:
            with open(path,"w",encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
            # update settings last_invoice_seq based on invoice_number format YEAR-SEQ
            try:
                m = re.match(r'(\d{4})[-_]?(\d+)', self.invoice_number.get() or "")
                if m:
                    yr = int(m.group(1)); seq = int(m.group(2))
                    self.settings["last_invoice_year"] = yr
                    self.settings["last_invoice_seq"] = seq
                    self._save_settings()
            except Exception:
                pass
            messagebox.showinfo("Zapisano", f"Zapisano kosztorys: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać kosztorysu:\n{e}")

    def load_costfile(self):
        path = filedialog.askopenfilename(filetypes=[("Kosztorys","*.cost.json"),("JSON","*.json")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: data = json.load(f)
        except Exception as e:
            messagebox.showerror("Błąd wczytania", f"Nie udało się wczytać pliku:\n{e}"); return
        self.cost_items = data.get("items", [])
        try:
            self.transport_percent.set(float(data.get("transport_percent", self.transport_percent.get())))
            self.transport_vat.set(int(data.get("transport_vat", self.transport_vat.get())))
            self.logo_path = data.get("logo", self.logo_path)
            client_name = data.get("client", "")
            if client_name and hasattr(self,"client_cb"): self.client_cb.set(client_name); self._on_client_selected()
            self.invoice_number.set(data.get("invoice_number", self.invoice_number.get()))
            self.invoice_date.set(data.get("invoice_date", self.invoice_date.get()))
            self.roof_area.set(data.get("roof_area", self.roof_area.get()))
            self.quote_name.set(data.get("quote_name", self.quote_name.get()))
            comment = data.get("comment","")
            self.comment_text.delete("1.0","end"); self.comment_text.insert("1.0", comment)
            # Load measurement items if available
            measurement_items = data.get("measurement_items", [])
            if measurement_items and hasattr(self, "measurement_tab_module"):
                self.measurement_tab_module.items = measurement_items
                self.measurement_tab_module.tree.delete(*self.measurement_tab_module.tree.get_children())
                for i, it in enumerate(self.measurement_tab_module.items):
                    params_display = self.measurement_tab_module._params_to_str(it)
                    self.measurement_tab_module.tree.insert("", "end", iid=str(i), values=(it["type"], params_display, f"{it['area']:.3f}"))
                self.measurement_tab_module.update_total_label()
            # optionally update stored last_invoice_seq/year if present in file
            try:
                m = re.match(r'(\d{4})[-_]?(\d+)', self.invoice_number.get() or "")
                if m:
                    yr = int(m.group(1)); seq = int(m.group(2))
                    if self.settings.get("last_invoice_year") is None or (yr > int(self.settings.get("last_invoice_year",0))) or (yr == int(self.settings.get("last_invoice_year",0)) and seq > int(self.settings.get("last_invoice_seq",0))):
                        self.settings["last_invoice_year"] = yr
                        self.settings["last_invoice_seq"] = seq
                        self._save_settings()
            except Exception:
                pass
        except Exception:
            pass
        self._refresh_cost_ui()
        messagebox.showinfo("Wczytano", f"Wczytano kosztorys: {path}")

# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = RoofCalculatorApp(root)
    root.mainloop()