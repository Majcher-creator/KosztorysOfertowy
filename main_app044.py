#!/usr/bin/env python3
# main_app046.py
# Kalkulator Dachów - v4.6
# Zmiany:
# - Ulepszony UI z nowoczesnym stylem i lepszymi kolorami
# - Dodano zakładki do obliczeń dachowych (pomiar, rynny, kominy, obróbki, drewno)
# - Ulepszony eksport PDF z profesjonalnym wyglądem
# - Lepsza walidacja danych wejściowych i UX
# - Przechowywanie ostatniego numeru kosztorysu w settings.json
#
# Wymagane (opcjonalne do PDF/logo): pip install reportlab pillow
#
# Uruchom: python3.12 main_app046.py

from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json, os, csv, platform, subprocess, re, math
from datetime import datetime

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

# Import calculation modules
try:
    from roof_calculations import calculate_single_slope_roof, calculate_gable_roof, calculate_hip_roof
    from gutter_calculations import calculate_guttering
    from chimney_calculations import calculate_chimney_flashings, calculate_chimney_insulation
    from flashing_calculations import calculate_flashings_total
    from timber_calculations import calculate_timber_volume
    from felt_calculations import calculate_felt_roof
    CALC_MODULES_AVAILABLE = True
except ImportError:
    CALC_MODULES_AVAILABLE = False

# ---------------- Color Theme ----------------
# Modern color palette for roofing application
COLORS = {
    'primary': '#2C3E50',        # Dark blue-gray for headers
    'secondary': '#34495E',      # Lighter blue-gray
    'accent': '#E67E22',         # Orange accent (roof tiles color)
    'accent_dark': '#D35400',    # Darker orange
    'success': '#27AE60',        # Green for success
    'warning': '#F39C12',        # Yellow for warnings
    'danger': '#E74C3C',         # Red for errors
    'bg_light': '#ECF0F1',       # Light gray background
    'bg_white': '#FFFFFF',       # White
    'text_dark': '#2C3E50',      # Dark text
    'text_light': '#7F8C8D',     # Light gray text
    'border': '#BDC3C7',         # Border color
    'table_header': '#FCD5B4',   # Table header (warm orange)
    'table_alt': '#FFF9F2',      # Alternate row color
}

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

def apply_modern_style(root):
    """Apply modern styling to ttk widgets."""
    style = ttk.Style(root)
    style.theme_use('clam')  # Use clam theme as base
    
    # Configure general styles
    style.configure('TFrame', background=COLORS['bg_light'])
    style.configure('TLabel', background=COLORS['bg_light'], foreground=COLORS['text_dark'], font=('Segoe UI', 10))
    style.configure('TLabelframe', background=COLORS['bg_light'], foreground=COLORS['text_dark'])
    style.configure('TLabelframe.Label', background=COLORS['bg_light'], foreground=COLORS['primary'], font=('Segoe UI', 11, 'bold'))
    
    # Configure buttons
    style.configure('TButton', 
                    background=COLORS['primary'], 
                    foreground=COLORS['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('TButton', 
              background=[('active', COLORS['secondary']), ('pressed', COLORS['accent_dark'])])
    
    # Accent button style
    style.configure('Accent.TButton', 
                    background=COLORS['accent'],
                    foreground=COLORS['bg_white'],
                    padding=(12, 6),
                    font=('Segoe UI', 10, 'bold'))
    style.map('Accent.TButton', 
              background=[('active', COLORS['accent_dark'])])
    
    # Success button style
    style.configure('Success.TButton', 
                    background=COLORS['success'],
                    foreground=COLORS['bg_white'],
                    padding=(10, 5),
                    font=('Segoe UI', 10))
    style.map('Success.TButton', 
              background=[('active', '#229954')])
    
    # Configure entries
    style.configure('TEntry', 
                    fieldbackground=COLORS['bg_white'],
                    borderwidth=2,
                    relief='flat')
    
    # Configure comboboxes
    style.configure('TCombobox', 
                    fieldbackground=COLORS['bg_white'],
                    background=COLORS['bg_white'])
    
    # Configure notebooks/tabs
    style.configure('TNotebook', background=COLORS['bg_light'])
    style.configure('TNotebook.Tab', 
                    background=COLORS['bg_light'],
                    foreground=COLORS['text_dark'],
                    padding=(15, 8),
                    font=('Segoe UI', 10))
    style.map('TNotebook.Tab',
              background=[('selected', COLORS['accent']), ('active', COLORS['secondary'])],
              foreground=[('selected', COLORS['bg_white']), ('active', COLORS['bg_white'])])
    
    # Configure Treeview
    style.configure('Treeview',
                    background=COLORS['bg_white'],
                    foreground=COLORS['text_dark'],
                    fieldbackground=COLORS['bg_white'],
                    rowheight=28,
                    font=('Segoe UI', 10))
    style.configure('Treeview.Heading',
                    background=COLORS['table_header'],
                    foreground=COLORS['text_dark'],
                    font=('Segoe UI', 10, 'bold'))
    style.map('Treeview',
              background=[('selected', COLORS['accent'])],
              foreground=[('selected', COLORS['bg_white'])])
    
    # Configure Panedwindow
    style.configure('TPanedwindow', background=COLORS['bg_light'])
    
    # Configure Separator
    style.configure('TSeparator', background=COLORS['border'])
    
    return style

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
        master.title("🏠 Kalkulator Dachów - v4.6")
        master.geometry("1400x980")
        master.configure(bg=COLORS['bg_light'])
        
        # Apply modern styling
        self.style = apply_modern_style(master)
        
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
        self.validity_days = tk.IntVar(value=30)
        
        # Roof measurement variables
        self.roof_type = tk.StringVar(value="dwuspadowy")
        self.roof_length = tk.DoubleVar(value=10.0)
        self.roof_width = tk.DoubleVar(value=8.0)
        self.roof_angle = tk.DoubleVar(value=30.0)
        self.is_real_dimensions = tk.BooleanVar(value=False)
        
        # company defaults
        self.settings = {
            "company_name": "VICTOR TOMASZ MAJCHERCZYK",
            "company_address": "Reymonta 1/1, Dąbrowa Górnicza 41-300",
            "company_nip": "625-227-54-24",
            "company_phone": "(32)262-34-21, 505-438-585",
            "company_email": "dachy_daw@gmail.com",
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
        self.create_header_bar()
        self.create_menu()
        self.create_notebook()
        self.create_cost_tab()
        self.create_measurement_tab()
        self.create_gutter_tab()
        self.create_chimney_tab()
        self.create_flashing_tab()
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

    # header bar with company info and quick actions
    def create_header_bar(self):
        header = tk.Frame(self.master, bg=COLORS['primary'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Left side - logo area and title
        left = tk.Frame(header, bg=COLORS['primary'])
        left.pack(side='left', padx=15, pady=8)
        
        title_lbl = tk.Label(left, text="🏠 KALKULATOR DACHÓW", 
                            font=('Segoe UI', 16, 'bold'),
                            fg=COLORS['bg_white'], bg=COLORS['primary'])
        title_lbl.pack(side='left')
        
        subtitle = tk.Label(left, text="v4.6 - Kosztorys Ofertowy",
                           font=('Segoe UI', 10),
                           fg=COLORS['border'], bg=COLORS['primary'])
        subtitle.pack(side='left', padx=15)
        
        # Right side - quick info
        right = tk.Frame(header, bg=COLORS['primary'])
        right.pack(side='right', padx=15, pady=8)
        
        self.company_header_label = tk.Label(right, 
            text=f"📋 {self.settings.get('company_name', '')}",
            font=('Segoe UI', 10),
            fg=COLORS['bg_white'], bg=COLORS['primary'])
        self.company_header_label.pack(side='right')

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
        # Main container with notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=(5, 10))

    # cost tab UI with improved styling
    def create_cost_tab(self):
        self.cost_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cost_tab, text="📋 Kosztorys/Oferta")
        
        left = ttk.Frame(self.cost_tab)
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        right_container = ttk.Frame(self.cost_tab, width=440)
        right_container.pack(side="right", fill="y", padx=8, pady=8)

        # header/meta with improved layout
        header_frame = ttk.LabelFrame(left, text="📄 Informacje o kosztorysie")
        header_frame.pack(fill="x", pady=(0,8))
        
        # Client info row
        client_row = ttk.Frame(header_frame)
        client_row.pack(fill="x", padx=8, pady=4)
        self.client_summary_label = ttk.Label(client_row, text="👤 Klient: (brak)", anchor="w", font=("Segoe UI", 10, "bold"))
        self.client_summary_label.pack(side="left", anchor="w")
        
        # Invoice details row
        inv_frame = ttk.Frame(header_frame)
        inv_frame.pack(fill="x", padx=8, pady=4)
        
        ttk.Label(inv_frame, text="Nr kosztorysu:").grid(row=0,column=0,sticky="e", padx=2)
        ttk.Entry(inv_frame,width=18,textvariable=self.invoice_number).grid(row=0,column=1,padx=4)
        ttk.Button(inv_frame, text="🆕 Nowy", command=self.new_cost_estimate, style='Accent.TButton').grid(row=0,column=2,padx=4)
        
        ttk.Label(inv_frame, text="Metraż dachu [m²]:").grid(row=0,column=3,sticky="e", padx=2)
        ttk.Entry(inv_frame,width=10,textvariable=self.roof_area).grid(row=0,column=4,padx=4)
        
        ttk.Label(inv_frame, text="Data:").grid(row=0,column=5,sticky="e", padx=2)
        ttk.Entry(inv_frame,width=12,textvariable=self.invoice_date).grid(row=0,column=6,padx=4)
        
        ttk.Label(inv_frame, text="Nazwa kosztorysu:").grid(row=1,column=0,sticky="e", padx=2, pady=4)
        ttk.Entry(inv_frame,width=50,textvariable=self.quote_name).grid(row=1,column=1,columnspan=4,padx=4, pady=4, sticky="w")
        
        ttk.Label(inv_frame, text="Ważność (dni):").grid(row=1,column=5,sticky="e", padx=2)
        ttk.Entry(inv_frame,width=6,textvariable=self.validity_days).grid(row=1,column=6,padx=4)

        # toolbar with styled buttons
        toolbar = ttk.LabelFrame(left, text="⚡ Akcje")
        toolbar.pack(fill="x", pady=(0,8))
        
        toolbar_inner = ttk.Frame(toolbar)
        toolbar_inner.pack(fill="x", padx=8, pady=6)
        
        ttk.Button(toolbar_inner, text="📊 Oblicz kosztorys", command=self.calculate_cost_estimation, style='Accent.TButton').pack(side="left", padx=4)
        ttk.Button(toolbar_inner, text="📄 Eksportuj CSV", command=self.export_cost_csv).pack(side="left", padx=4)
        ttk.Button(toolbar_inner, text="📑 Eksportuj PDF", command=self.export_cost_pdf, style='Success.TButton').pack(side="left", padx=4)
        ttk.Button(toolbar_inner, text="📦 Wstaw z bazy", command=self.manage_materials_db).pack(side="right", padx=4)
        ttk.Button(toolbar_inner, text="👥 Klienci", command=self.manage_clients).pack(side="right", padx=4)

        # quick sums with styled labels
        sums_frame = ttk.LabelFrame(left, text="💰 Podsumowanie")
        sums_frame.pack(fill="x", pady=(0,8))
        
        sums_inner = ttk.Frame(sums_frame)
        sums_inner.pack(fill="x", padx=8, pady=6)
        
        self.lbl_mat_total = ttk.Label(sums_inner, text="🧱 Materiały netto: 0,00 zł", font=("Segoe UI", 10))
        self.lbl_mat_total.pack(side="left", padx=12)
        self.lbl_srv_total = ttk.Label(sums_inner, text="🔧 Usługi netto: 0,00 zł", font=("Segoe UI", 10))
        self.lbl_srv_total.pack(side="left", padx=12)
        self.lbl_total_all = ttk.Label(sums_inner, text="💵 Suma brutto: 0,00 zł", font=("Segoe UI", 11, "bold"))
        self.lbl_total_all.pack(side="right", padx=12)

        # split area: materials and services
        split_pane = ttk.Panedwindow(left, orient="vertical")
        split_pane.pack(fill="both", expand=True)
        mat_frame = ttk.Labelframe(split_pane, text="🧱 Materiały")
        srv_frame = ttk.Labelframe(split_pane, text="🔧 Usługi")
        split_pane.add(mat_frame, weight=1)
        split_pane.add(srv_frame, weight=1)

        # materials tree with scrollbar
        mat_tree_container = ttk.Frame(mat_frame)
        mat_tree_container.pack(fill="both", expand=True, padx=6, pady=6)
        mat_cols = ("name","qty","unit","price_net","net")
        self.mat_tree = ttk.Treeview(mat_tree_container, columns=mat_cols, show="headings", selectmode="browse")
        for c,h in zip(mat_cols,("Nazwa","Ilość","JM","Cena netto","Wartość netto")):
            self.mat_tree.heading(c, text=h)
            self.mat_tree.column(c, width=320 if c=="name" else 90, anchor="w" if c=="name" else "e")
        mat_vscroll = ttk.Scrollbar(mat_tree_container, orient="vertical", command=self.mat_tree.yview)
        self.mat_tree.configure(yscrollcommand=mat_vscroll.set)
        self.mat_tree.pack(side="left", fill="both", expand=True)
        mat_vscroll.pack(side="right", fill="y")
        
        mat_btnf = ttk.Frame(mat_frame)
        mat_btnf.pack(fill="x", padx=6, pady=4)
        ttk.Button(mat_btnf, text="✏️ Edytuj", command=lambda: self._edit_from_tree("material")).pack(side="left", padx=4)
        ttk.Button(mat_btnf, text="🗑️ Usuń", command=lambda: self._delete_from_tree("material")).pack(side="left", padx=4)

        # services tree with scrollbar
        srv_tree_container = ttk.Frame(srv_frame)
        srv_tree_container.pack(fill="both", expand=True, padx=6, pady=6)
        srv_cols = ("name","qty","unit","price_net","net")
        self.srv_tree = ttk.Treeview(srv_tree_container, columns=srv_cols, show="headings", selectmode="browse")
        for c,h in zip(srv_cols,("Nazwa","Ilość","JM","Cena netto","Wartość netto")):
            self.srv_tree.heading(c, text=h)
            self.srv_tree.column(c, width=320 if c=="name" else 90, anchor="w" if c=="name" else "e")
        srv_vscroll = ttk.Scrollbar(srv_tree_container, orient="vertical", command=self.srv_tree.yview)
        self.srv_tree.configure(yscrollcommand=srv_vscroll.set)
        self.srv_tree.pack(side="left", fill="both", expand=True)
        srv_vscroll.pack(side="right", fill="y")
        
        srv_btnf = ttk.Frame(srv_frame)
        srv_btnf.pack(fill="x", padx=6, pady=4)
        ttk.Button(srv_btnf, text="✏️ Edytuj", command=lambda: self._edit_from_tree("service")).pack(side="left", padx=4)
        ttk.Button(srv_btnf, text="🗑️ Usuń", command=lambda: self._delete_from_tree("service")).pack(side="left", padx=4)

        # right panel (add item / client / transport / summary)
        right = ttk.Frame(right_container)
        right.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Add item form with icons
        form = ttk.LabelFrame(right, text="➕ Dodaj pozycję")
        form.pack(fill="x", pady=6, padx=6)
        
        ttk.Label(form, text="Nazwa:").grid(row=0,column=0,sticky="w", padx=4, pady=2)
        self.c_name = ttk.Entry(form, width=36)
        self.c_name.grid(row=0,column=1, pady=2)
        
        ttk.Label(form, text="Ilość:").grid(row=1,column=0,sticky="w", padx=4, pady=2)
        self.c_qty = ttk.Entry(form, width=12)
        self.c_qty.grid(row=1,column=1,sticky="w", pady=2)
        
        ttk.Label(form, text="JM:").grid(row=2,column=0,sticky="w", padx=4, pady=2)
        self.c_unit = ttk.Entry(form, width=12)
        self.c_unit.grid(row=2,column=1,sticky="w", pady=2)
        
        ttk.Label(form, text="Cena netto:").grid(row=3,column=0,sticky="w", padx=4, pady=2)
        self.c_price = ttk.Entry(form, width=12)
        self.c_price.grid(row=3,column=1,sticky="w", pady=2)
        
        ttk.Label(form, text="VAT:").grid(row=4,column=0,sticky="w", padx=4, pady=2)
        self.c_vat = ttk.Combobox(form, values=["0","8","23"], width=8, state="readonly")
        self.c_vat.grid(row=4,column=1,sticky="w", pady=2)
        self.c_vat.set("23")
        
        ttk.Label(form, text="Kategoria:").grid(row=5,column=0,sticky="w", padx=4, pady=2)
        self.c_cat = ttk.Combobox(form, values=["material","service"], width=12, state="readonly")
        self.c_cat.grid(row=5,column=1,sticky="w", pady=2)
        self.c_cat.set("material")
        
        vcmd_f = (self.master.register(lambda P: is_valid_float_text(P)), "%P")
        self.c_qty.config(validate="key", validatecommand=vcmd_f)
        self.c_price.config(validate="key", validatecommand=vcmd_f)
        
        ttk.Button(right, text="➕ Dodaj do kosztorysu", command=self.add_cost_item_from_form, style='Accent.TButton').pack(fill="x", pady=6, padx=6)
        ttk.Button(right, text="📦 Wstaw z bazy (okno)", command=self.manage_materials_db).pack(fill="x", pady=2, padx=6)
        
        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=8)
        
        # Client section
        client_section = ttk.LabelFrame(right, text="👥 Klient")
        client_section.pack(fill="x", pady=4, padx=6)
        
        ttk.Button(client_section, text="Zarządzaj klientami", command=self.manage_clients).pack(fill="x", pady=4, padx=8)
        ttk.Label(client_section, text="Wybierz klienta:").pack(anchor="w", padx=8, pady=(4,0))
        self.client_cb = ttk.Combobox(client_section, values=[c.get("name","") for c in self.clients], state="readonly", width=36)
        self.client_cb.pack(anchor="w", padx=8, pady=(0,8))
        self.client_cb.bind("<<ComboboxSelected>>", lambda e: self._on_client_selected())
        
        # Transport section
        transport_frame = ttk.LabelFrame(right, text="🚚 Transport")
        transport_frame.pack(fill="x", pady=4, padx=6)
        
        ttk.Label(transport_frame, text="Procent [%]:").grid(row=0,column=0,sticky="w", padx=8, pady=4)
        self.e_transport = ttk.Entry(transport_frame, width=8, textvariable=self.transport_percent)
        self.e_transport.grid(row=0,column=1,padx=4, pady=4)
        
        ttk.Label(transport_frame, text="VAT:").grid(row=0,column=2,sticky="w", padx=8, pady=4)
        self.transport_vat_cb = ttk.Combobox(transport_frame, values=["0","8","23"], width=8, state="readonly", textvariable=self.transport_vat)
        self.transport_vat_cb.grid(row=0,column=3, padx=4, pady=4)
        
        # Summary/Comment section
        summary_frame = ttk.Labelframe(right, text="📝 Podsumowanie / Komentarz")
        summary_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        self.summary_text = tk.Text(summary_frame, height=8, state="disabled", bg=COLORS['bg_white'], font=("Segoe UI", 9))
        self.summary_text.pack(fill="both", expand=True, padx=4, pady=4)
        
        ttk.Label(summary_frame, text="Komentarz (umieszczony w PDF):").pack(anchor="w", padx=4, pady=(6,0))
        self.comment_text = tk.Text(summary_frame, height=5, bg=COLORS['bg_white'], font=("Segoe UI", 9))
        self.comment_text.pack(fill="both", expand=False, padx=4, pady=(0,6))

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
            self.lbl_mat_total.config(text=f"🧱 Materiały netto: {fmt_money_plain(mats_tot)} zł")
            self.lbl_srv_total.config(text=f"🔧 Usługi netto: {fmt_money_plain(srvs_tot)} zł")
            self.lbl_total_all.config(text=f"💵 Suma brutto: {fmt_money_plain(total_gross)} zł")
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
        doc = SimpleDocTemplate(path, pagesize=portrait(A4), leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
        styles = getSampleStyleSheet(); base_font = self._registered_pdf_font_name or styles['Normal'].fontName
        normal = ParagraphStyle("NormalApp", parent=styles['Normal'], fontName=base_font, fontSize=9, leading=12)
        normal_bold = ParagraphStyle("NormalBoldApp", parent=normal, fontName=base_font, fontSize=9, leading=12, textColor=colors.HexColor("#2C3E50"))
        heading = ParagraphStyle("HeadingApp", parent=styles['Heading3'], fontName=base_font, fontSize=11, leading=14, textColor=colors.HexColor("#E67E22"))
        title = ParagraphStyle("TitleApp", parent=styles['Title'], fontName=base_font, fontSize=16, leading=18, alignment=1, textColor=colors.HexColor("#2C3E50"))
        subtitle = ParagraphStyle("SubtitleApp", parent=styles['Normal'], fontName=base_font, fontSize=10, leading=12, alignment=1, textColor=colors.HexColor("#7F8C8D"))
        elems = []
        
        # Header with logo and document info
        meta_lines = []
        meta_lines.append(f"<b>Nr kosztorysu:</b> {self.invoice_number.get()}")
        meta_lines.append(f"<b>Data wystawienia:</b> {self.invoice_date.get()}")
        meta_lines.append(f"<b>Metraż dachu:</b> {self.roof_area.get()} m²")
        meta_lines.append(f"<b>Ważność oferty:</b> {self.validity_days.get()} dni")
        if self.quote_name.get():
            meta_lines.append(f"<b>Nazwa:</b> {self.quote_name.get()}")
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
        header_tbl = Table([[meta_para, right_parts]], colWidths=[320,210])
        header_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
        elems.append(header_tbl)
        elems.append(Spacer(1,12))
        
        # Title
        elems.append(Paragraph("KOSZTORYS OFERTOWY", title))
        elems.append(Spacer(1,8))
        
        # client/company two-column with styled headers
        client = next((c for c in self.clients if hasattr(self,"client_cb") and c.get("name","")==self.client_cb.get()), None)
        client_lines=["<b>KLIENT:</b>"]
        if client:
            client_lines.append(f"<b>{client.get('name','')}</b>")
            if client.get("address",""): client_lines.append(client.get("address",""))
            if client.get("id",""): client_lines.append("NIP: "+client.get("id",""))
            if client.get("phone",""): client_lines.append("Tel: "+client.get("phone",""))
            if client.get("email",""): client_lines.append("E-mail: "+client.get("email",""))
        else:
            client_lines.append("(Brak danych klienta)")
            
        company_lines=["<b>WYKONAWCA:</b>"]
        company_lines.append(f"<b>{self.settings.get('company_name','')}</b>")
        if self.settings.get("company_address",""): company_lines.append(self.settings.get("company_address",""))
        if self.settings.get("company_nip",""): company_lines.append("NIP: "+self.settings.get("company_nip",""))
        if self.settings.get("company_phone",""): company_lines.append("Tel: "+self.settings.get("company_phone",""))
        if self.settings.get("company_email",""): company_lines.append("E-mail: "+self.settings.get("company_email",""))
        if self.settings.get("company_account",""): company_lines.append("Nr konta: "+self.settings.get("company_account",""))
        
        left_part = Paragraph("<br/>".join(client_lines), normal)
        right_part = Paragraph("<br/>".join(company_lines), normal)
        cc_tbl = Table([[left_part,right_part]], colWidths=[270,270])
        cc_tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('BOX',(0,0),(0,0),0.5,colors.HexColor("#BDC3C7")),
            ('BOX',(1,0),(1,0),0.5,colors.HexColor("#BDC3C7")),
            ('PADDING',(0,0),(-1,-1),8),
        ]))
        elems.append(cc_tbl)
        elems.append(Spacer(1,15))
        
        # helper: add tables with sums (narrower columns) - improved styling
        def add_table_with_sum(title_txt: str, rows: List[List[str]], sum_label: str, sum_value: float):
            elems.append(Paragraph(title_txt, heading))
            elems.append(Spacer(1,4))
            max_rows_per_table = 28
            total_rows = len(rows)
            chunks = [rows[i:i+max_rows_per_table] for i in range(0, total_rows, max_rows_per_table)]
            if not chunks:
                chunks = [[]]
            for ci, chunk in enumerate(chunks):
                tbl = [["Lp","Nazwa","Ilość","JM","Cena netto","Wartość netto"]] + chunk
                if ci == len(chunks)-1:
                    tbl.append(["", sum_label, "", "", "", f"{fmt_money_plain(sum_value)} zł"])
                    t = Table(tbl, repeatRows=1, colWidths=[25,280,50,35,75,75])
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#FCD5B4")),
                        ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor("#2C3E50")),
                        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#BDC3C7")),
                        ('ALIGN',(0,0),(0,-1),'CENTER'),
                        ('ALIGN',(2,1),(2,-2),'RIGHT'),
                        ('ALIGN',(4,1),(5,-2),'RIGHT'),
                        ('ALIGN',(5,-1),(5,-1),'RIGHT'),
                        ('SPAN',(1,-1),(4,-1)),
                        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#E8F6F3")),
                        ('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
                        ('FONTSIZE',(0,0),(-1,-1),9),
                        ('FONTNAME',(0,-1),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
                        ('BOTTOMPADDING',(0,0),(-1,-1),6),
                        ('TOPPADDING',(0,0),(-1,-1),6),
                    ]))
                else:
                    t = Table(tbl, repeatRows=1, colWidths=[25,280,50,35,75,75])
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#FCD5B4")),
                        ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor("#2C3E50")),
                        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#BDC3C7")),
                        ('ALIGN',(0,0),(0,-1),'CENTER'),
                        ('ALIGN',(2,1),(2,-1),'RIGHT'),
                        ('ALIGN',(4,1),(5,-1),'RIGHT'),
                        ('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
                        ('FONTSIZE',(0,0),(-1,-1),9),
                        ('BOTTOMPADDING',(0,0),(-1,-1),6),
                        ('TOPPADDING',(0,0),(-1,-1),6),
                    ]))
                elems.append(t); elems.append(Spacer(1,10))
                if ci < len(chunks)-1:
                    elems.append(PageBreak())
        mat_rows = [[str(i+1), it.get("name",""), f"{it.get('quantity',0):.3f}", it.get("unit",""), f"{it.get('price_unit_net',0.0):.2f}", f"{it.get('total_net',0.0):.2f}"] for i,it in enumerate(materials)]
        mat_sum = sum(it.get("total_net",0.0) for it in materials)
        add_table_with_sum("MATERIAŁY", mat_rows, "SUMA MATERIAŁY:", mat_sum)
        srv_rows = [[str(i+1), it.get("name",""), f"{it.get('quantity',0):.3f}", it.get("unit",""), f"{it.get('price_unit_net',0.0):.2f}", f"{it.get('total_net',0.0):.2f}"] for i,it in enumerate(services)]
        srv_sum = sum(it.get("total_net",0.0) for it in services)
        add_table_with_sum("ROBOCIZNA / USŁUGI", srv_rows, "SUMA USŁUGI:", srv_sum)
        
        # overall summary with improved styling
        elems.append(Paragraph("PODSUMOWANIE", heading))
        elems.append(Spacer(1,4))
        summary_rows = [["Opis","Netto","VAT","Brutto"]]
        for vat,s in sorted(totals["by_vat"].items()):
            summary_rows.append([f"VAT {vat} %", fmt_money_plain(s.get("net",0.0))+" zł", fmt_money_plain(s.get("vat",0.0))+" zł", fmt_money_plain(s.get("gross",0.0))+" zł"])
        tinfo = totals["transport"]
        summary_rows.append([f"Transport ({tinfo.get('percent',0)}%)", fmt_money_plain(tinfo.get("net",0.0))+" zł", fmt_money_plain(tinfo.get("vat",0.0))+" zł", fmt_money_plain(tinfo.get("gross",0.0))+" zł"])
        ssum = totals["summary"]
        summary_rows.append(["RAZEM DO ZAPŁATY", fmt_money_plain(ssum.get("net",0.0))+" zł", fmt_money_plain(ssum.get("vat",0.0))+" zł", fmt_money_plain(ssum.get("gross",0.0))+" zł"])
        sum_tbl = Table(summary_rows, colWidths=[180,120,100,120])
        sum_tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#FCD5B4")),
            ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor("#2C3E50")),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#BDC3C7")),
            ('ALIGN',(1,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#27AE60")),
            ('TEXTCOLOR',(0,-1),(-1,-1),colors.white),
            ('FONTNAME',(0,-1),(-1,-1), self._registered_pdf_font_name or styles['Normal'].fontName),
            ('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('TOPPADDING',(0,0),(-1,-1),8),
        ]))
        elems.append(sum_tbl)
        elems.append(Spacer(1,15))
        
        # comment section
        comment = self.comment_text.get("1.0","end").strip()
        if comment:
            elems.append(Paragraph("Komentarz:", heading))
            elems.append(Spacer(1,4))
            elems.append(Paragraph(comment.replace("\n","<br/>"), normal))
            elems.append(Spacer(1,10))
        
        # Footnotes/disclaimers
        footnote_style = ParagraphStyle("FootnoteApp", parent=normal, fontSize=8, leading=10, textColor=colors.HexColor("#7F8C8D"))
        footnotes = [
            "* Transport pionowy, Praca sprzętu, Materiały pomocnicze i Koszty zakupu = 3% od Wartości (min 100 zł)",
            "** Cena bez utylizacji odpadów",
            "*** Ceny materiałów mogą ulec zmianie w zależności od sytuacji rynkowej"
        ]
        for fn in footnotes:
            elems.append(Paragraph(fn, footnote_style))
        elems.append(Spacer(1,15))
        
        # Footer with company slogan
        footer_style = ParagraphStyle("FooterApp", parent=normal, fontSize=12, leading=14, alignment=1, textColor=colors.HexColor("#E67E22"))
        elems.append(Paragraph("<b>TYLKO DACHY TYLKO VICTOR</b>", footer_style))
        
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
        data = {"items": self.cost_items, "transport_percent": float(self.transport_percent.get()), "transport_vat": int(self.transport_vat.get()), "logo": self.logo_path, "client": client_name, "invoice_number": self.invoice_number.get(), "invoice_date": self.invoice_date.get(), "roof_area": self.roof_area.get(), "quote_name": self.quote_name.get(), "comment": comment, "saved_at": datetime.now().isoformat()}
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

    # ==================== NEW TABS ====================
    
    def create_measurement_tab(self):
        """Create roof measurement/calculation tab"""
        self.measurement_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.measurement_tab, text="📐 Pomiar Dachu")
        
        # Left panel - roof configuration
        left = ttk.Frame(self.measurement_tab)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Right panel - results
        right = ttk.Frame(self.measurement_tab, width=400)
        right.pack(side="right", fill="y", padx=10, pady=10)
        
        # Roof type selection
        type_frame = ttk.LabelFrame(left, text="🏠 Typ dachu")
        type_frame.pack(fill="x", pady=(0,10))
        
        types_inner = ttk.Frame(type_frame)
        types_inner.pack(padx=10, pady=10)
        
        ttk.Radiobutton(types_inner, text="Jednospadowy", variable=self.roof_type, value="jednospadowy").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(types_inner, text="Dwuspadowy", variable=self.roof_type, value="dwuspadowy").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(types_inner, text="Kopertowy", variable=self.roof_type, value="kopertowy").grid(row=0, column=2, padx=10)
        
        # Dimensions input
        dim_frame = ttk.LabelFrame(left, text="📏 Wymiary")
        dim_frame.pack(fill="x", pady=(0,10))
        
        dim_inner = ttk.Frame(dim_frame)
        dim_inner.pack(padx=10, pady=10)
        
        ttk.Label(dim_inner, text="Długość budynku [m]:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(dim_inner, textvariable=self.roof_length, width=12).grid(row=0, column=1, padx=8, pady=4)
        
        ttk.Label(dim_inner, text="Szerokość budynku [m]:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(dim_inner, textvariable=self.roof_width, width=12).grid(row=1, column=1, padx=8, pady=4)
        
        ttk.Label(dim_inner, text="Kąt nachylenia [°]:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(dim_inner, textvariable=self.roof_angle, width=12).grid(row=2, column=1, padx=8, pady=4)
        
        ttk.Checkbutton(dim_inner, text="Podaję wymiary rzeczywiste (nie rzut)", variable=self.is_real_dimensions).grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        
        # Calculate button
        ttk.Button(left, text="📊 Oblicz wymiary dachu", command=self.calculate_roof, style='Accent.TButton').pack(pady=10)
        
        # Results display
        results_frame = ttk.LabelFrame(right, text="📋 Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.roof_results_text = tk.Text(results_frame, height=20, state="disabled", bg=COLORS['bg_white'], font=("Segoe UI", 10))
        self.roof_results_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Button to transfer area to cost estimate
        ttk.Button(right, text="➡️ Przenieś metraż do kosztorysu", command=self.transfer_roof_area, style='Success.TButton').pack(pady=10, fill="x", padx=10)
    
    def calculate_roof(self):
        """Calculate roof dimensions based on inputs"""
        try:
            roof_type = self.roof_type.get()
            length = self.roof_length.get()
            width = self.roof_width.get()
            angle = self.roof_angle.get()
            is_real = self.is_real_dimensions.get()
            
            if roof_type == "jednospadowy":
                results = calculate_single_slope_roof(length, width, angle, is_real) if CALC_MODULES_AVAILABLE else self._calc_single_slope(length, width, angle, is_real)
            elif roof_type == "dwuspadowy":
                results = calculate_gable_roof(length, width, angle, is_real) if CALC_MODULES_AVAILABLE else self._calc_gable_roof(length, width, angle, is_real)
            elif roof_type == "kopertowy":
                results = calculate_hip_roof(length, width, angle, is_real) if CALC_MODULES_AVAILABLE else self._calc_hip_roof(length, width, angle)
            else:
                results = {"powierzchnia_dachu": 0.0}
            
            # Display results
            output = []
            output.append(f"🏠 Typ dachu: {roof_type}")
            output.append(f"📏 Wymiary: {length} x {width} m")
            output.append(f"📐 Kąt nachylenia: {angle}°")
            output.append("")
            output.append("=" * 40)
            output.append("")
            output.append(f"📊 POWIERZCHNIA DACHU: {results.get('powierzchnia_dachu', 0.0):.2f} m²")
            output.append("")
            output.append(f"🔺 Długość okapu: {results.get('dlugosc_okapu', 0.0):.2f} m")
            output.append(f"🔺 Długość gąsiorów: {results.get('dlugosc_gasiorow', 0.0):.2f} m")
            output.append(f"🔺 Długość wiatrownic: {results.get('dlugosc_wiatrownic', 0.0):.2f} m")
            output.append(f"🔺 Długość koszy: {results.get('dlugosc_koszy', 0.0):.2f} m")
            output.append(f"🔺 Długość krokwi skośnej: {results.get('slant_rafter_length', 0.0):.2f} m")
            
            self.roof_results_text.config(state="normal")
            self.roof_results_text.delete("1.0", "end")
            self.roof_results_text.insert("1.0", "\n".join(output))
            self.roof_results_text.config(state="disabled")
            
            # Store for transfer
            self._last_roof_calc = results
            
        except Exception as e:
            messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd: {e}")
    
    def _calc_single_slope(self, dl, szer, angle, is_real):
        """Fallback calculation for single slope roof"""
        if is_real:
            return {"powierzchnia_dachu": dl * szer, "dlugosc_okapu": dl, "dlugosc_gasiorow": 0.0, "dlugosc_wiatrownic": 2*szer, "dlugosc_koszy": 0.0, "slant_rafter_length": szer}
        # Protect against division by zero for angles near 90 degrees
        if angle and angle < 89.5:  # Practical limit for roof angles
            cos_val = math.cos(math.radians(angle))
            slant_szer = szer / cos_val if cos_val > 0.01 else szer * 100  # Cap at practical maximum
        else:
            slant_szer = szer
        return {"powierzchnia_dachu": dl * slant_szer, "dlugosc_okapu": dl, "dlugosc_gasiorow": 0.0, "dlugosc_wiatrownic": 2*slant_szer, "dlugosc_koszy": 0.0, "slant_rafter_length": slant_szer}
    
    def _calc_gable_roof(self, dl, szer, angle, is_real):
        """Fallback calculation for gable roof"""
        if is_real:
            return {"powierzchnia_dachu": 2 * dl * szer, "dlugosc_okapu": 2*dl, "dlugosc_gasiorow": dl, "dlugosc_wiatrownic": 4*szer, "dlugosc_koszy": 0.0, "slant_rafter_length": szer}
        half_szer = szer / 2
        # Protect against division by zero for angles near 90 degrees
        if angle and angle < 89.5:  # Practical limit for roof angles
            cos_val = math.cos(math.radians(angle))
            slant_krokiew = half_szer / cos_val if cos_val > 0.01 else half_szer * 100
        else:
            slant_krokiew = half_szer
        return {"powierzchnia_dachu": 2 * dl * slant_krokiew, "dlugosc_okapu": 2*dl, "dlugosc_gasiorow": dl, "dlugosc_wiatrownic": 4*slant_krokiew, "dlugosc_koszy": 0.0, "slant_rafter_length": slant_krokiew}
    
    def _calc_hip_roof(self, dl, szer, angle):
        """Fallback calculation for hip roof"""
        # Protect against division by zero for angles near 90 degrees
        if angle and angle < 89.5:  # Practical limit for roof angles
            cos_val = math.cos(math.radians(angle))
            slant = (szer/2) / cos_val if cos_val > 0.01 else (szer/2) * 100
        else:
            slant = szer/2
        area_triangles = 2 * (0.5 * szer * slant)
        kalenica = max(0, dl - szer)
        area_trapezoids = 2 * (0.5 * (kalenica + dl) * slant)
        return {"powierzchnia_dachu": area_triangles + area_trapezoids, "dlugosc_okapu": 2*(dl+szer), "dlugosc_gasiorow": 4*slant + kalenica, "dlugosc_wiatrownic": 0.0, "dlugosc_koszy": 0.0, "slant_rafter_length": slant}
    
    def transfer_roof_area(self):
        """Transfer calculated roof area to the cost estimate tab"""
        if hasattr(self, '_last_roof_calc') and self._last_roof_calc:
            area = self._last_roof_calc.get('powierzchnia_dachu', 0.0)
            self.roof_area.set(f"{area:.2f}")
            messagebox.showinfo("Przeniesiono", f"Metraż dachu {area:.2f} m² przeniesiony do kosztorysu.")
            self.notebook.select(self.cost_tab)
        else:
            messagebox.showwarning("Brak danych", "Najpierw oblicz wymiary dachu.")
    
    def create_gutter_tab(self):
        """Create gutter calculation tab"""
        self.gutter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gutter_tab, text="🌧️ Rynny")
        
        # Main container
        main = ttk.Frame(self.gutter_tab)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input section
        input_frame = ttk.LabelFrame(main, text="📏 Parametry orynnowania")
        input_frame.pack(fill="x", pady=(0,10))
        
        input_inner = ttk.Frame(input_frame)
        input_inner.pack(padx=10, pady=10)
        
        self.gutter_okap_length = tk.DoubleVar(value=20.0)
        self.gutter_roof_height = tk.DoubleVar(value=5.0)
        self.gutter_num_downpipes = tk.IntVar(value=0)
        
        ttk.Label(input_inner, text="Długość okapu [m]:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.gutter_okap_length, width=12).grid(row=0, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Wysokość dachu (rury spustowej) [m]:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.gutter_roof_height, width=12).grid(row=1, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Liczba rur spustowych (0=auto):").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.gutter_num_downpipes, width=12).grid(row=2, column=1, padx=8, pady=4)
        
        ttk.Button(main, text="📊 Oblicz orynnowanie", command=self.calculate_gutters, style='Accent.TButton').pack(pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main, text="📋 Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True)
        
        self.gutter_results_text = tk.Text(results_frame, height=15, state="disabled", bg=COLORS['bg_white'], font=("Segoe UI", 10))
        self.gutter_results_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        ttk.Button(main, text="➕ Dodaj pozycje do kosztorysu", command=self.add_gutter_items, style='Success.TButton').pack(pady=10)
    
    def calculate_gutters(self):
        """Calculate guttering requirements"""
        try:
            okap = self.gutter_okap_length.get()
            height = self.gutter_roof_height.get()
            num_dp = self.gutter_num_downpipes.get() if self.gutter_num_downpipes.get() > 0 else None
            
            if CALC_MODULES_AVAILABLE:
                results = calculate_guttering(okap, height, num_dp)
            else:
                # Fallback calculation
                num_downpipes = num_dp if num_dp else max(1, math.ceil(okap / 10.0))
                results = {
                    "total_gutter_length_m": okap,
                    "total_downpipe_length_m": num_downpipes * height,
                    "num_downpipes": num_downpipes,
                    "num_gutter_hooks": math.ceil(okap / 0.5) if okap > 0 else 0,
                    "num_gutter_connectors": max(0, math.ceil(okap / 3.0) - 1),
                    "num_downpipe_outlets": num_downpipes,
                    "num_downpipe_clamps": math.ceil(num_downpipes * height / 2.0) if height > 0 else 0,
                    "num_downpipe_elbows": num_downpipes * 2,
                    "num_end_caps": 2
                }
            
            output = []
            output.append("🌧️ KALKULATOR ORYNNOWANIA")
            output.append("=" * 40)
            output.append("")
            output.append(f"📏 Długość rynny: {results['total_gutter_length_m']:.2f} m")
            output.append(f"📏 Długość rur spustowych: {results['total_downpipe_length_m']:.2f} m")
            output.append(f"🔢 Liczba rur spustowych: {results['num_downpipes']}")
            output.append("")
            output.append("📦 Akcesoria:")
            output.append(f"   • Haki rynnowe: {results['num_gutter_hooks']} szt.")
            output.append(f"   • Łączniki rynien: {results['num_gutter_connectors']} szt.")
            output.append(f"   • Wyloty do rur: {results['num_downpipe_outlets']} szt.")
            output.append(f"   • Obejmy rurowe: {results['num_downpipe_clamps']} szt.")
            output.append(f"   • Kolanka: {results['num_downpipe_elbows']} szt.")
            output.append(f"   • Zaślepki: {results['num_end_caps']} szt.")
            
            self.gutter_results_text.config(state="normal")
            self.gutter_results_text.delete("1.0", "end")
            self.gutter_results_text.insert("1.0", "\n".join(output))
            self.gutter_results_text.config(state="disabled")
            
            self._last_gutter_calc = results
            
        except Exception as e:
            messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd: {e}")
    
    def add_gutter_items(self):
        """Add gutter items to cost estimate"""
        if not hasattr(self, '_last_gutter_calc') or not self._last_gutter_calc:
            messagebox.showwarning("Brak danych", "Najpierw oblicz orynnowanie.")
            return
        
        r = self._last_gutter_calc
        items = [
            {"name": "Rynna", "quantity": r['total_gutter_length_m'], "unit": "mb", "price_unit_net": 25.0, "vat_rate": 8, "category": "material"},
            {"name": "Rura spustowa", "quantity": r['total_downpipe_length_m'], "unit": "mb", "price_unit_net": 28.0, "vat_rate": 8, "category": "material"},
            {"name": "Haki rynnowe", "quantity": r['num_gutter_hooks'], "unit": "szt.", "price_unit_net": 8.0, "vat_rate": 8, "category": "material"},
            {"name": "Łączniki rynien", "quantity": r['num_gutter_connectors'], "unit": "szt.", "price_unit_net": 12.0, "vat_rate": 8, "category": "material"},
            {"name": "Montaż orynnowania", "quantity": r['total_gutter_length_m'], "unit": "mb", "price_unit_net": 15.0, "vat_rate": 8, "category": "service"},
        ]
        
        for item in items:
            item["note"] = ""
            self.cost_items.append(item)
        
        self._refresh_cost_ui()
        messagebox.showinfo("Dodano", f"Dodano {len(items)} pozycji orynnowania do kosztorysu.")
        self.notebook.select(self.cost_tab)
    
    def create_chimney_tab(self):
        """Create chimney calculation tab"""
        self.chimney_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chimney_tab, text="🏭 Kominy")
        
        main = ttk.Frame(self.chimney_tab)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        input_frame = ttk.LabelFrame(main, text="📏 Parametry komina")
        input_frame.pack(fill="x", pady=(0,10))
        
        input_inner = ttk.Frame(input_frame)
        input_inner.pack(padx=10, pady=10)
        
        self.chimney_width = tk.DoubleVar(value=0.5)
        self.chimney_length = tk.DoubleVar(value=0.5)
        self.chimney_height = tk.DoubleVar(value=1.0)
        self.chimney_num = tk.IntVar(value=1)
        self.chimney_covering = tk.StringVar(value="papa")
        
        ttk.Label(input_inner, text="Szerokość komina [m]:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.chimney_width, width=12).grid(row=0, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Długość komina [m]:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.chimney_length, width=12).grid(row=1, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Wysokość nad dachem [m]:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.chimney_height, width=12).grid(row=2, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Liczba kominów:").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(input_inner, textvariable=self.chimney_num, width=12).grid(row=3, column=1, padx=8, pady=4)
        
        ttk.Label(input_inner, text="Typ pokrycia:").grid(row=4, column=0, sticky="w", pady=4)
        covering_cb = ttk.Combobox(input_inner, textvariable=self.chimney_covering, values=["papa", "blacha", "dachówka"], width=12, state="readonly")
        covering_cb.grid(row=4, column=1, padx=8, pady=4)
        
        ttk.Button(main, text="📊 Oblicz obróbki kominowe", command=self.calculate_chimneys, style='Accent.TButton').pack(pady=10)
        
        results_frame = ttk.LabelFrame(main, text="📋 Wyniki obliczeń")
        results_frame.pack(fill="both", expand=True)
        
        self.chimney_results_text = tk.Text(results_frame, height=12, state="disabled", bg=COLORS['bg_white'], font=("Segoe UI", 10))
        self.chimney_results_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        ttk.Button(main, text="➕ Dodaj pozycje do kosztorysu", command=self.add_chimney_items, style='Success.TButton').pack(pady=10)
    
    def calculate_chimneys(self):
        """Calculate chimney flashing requirements"""
        try:
            w = self.chimney_width.get()
            l = self.chimney_length.get()
            h = self.chimney_height.get()
            num = self.chimney_num.get()
            covering = self.chimney_covering.get()
            
            if CALC_MODULES_AVAILABLE:
                results = calculate_chimney_flashings(w, l, h, self.roof_angle.get(), covering, num)
            else:
                perimeter = 2 * (w + l)
                flashing_surface = perimeter * 0.5 + perimeter * (h + 0.2)
                cap_surface = (w + 0.1) * (l + 0.1)
                results = {
                    "total_metal_flashing_surface_m2": flashing_surface * num,
                    "num_metal_sheets_flashing": math.ceil(flashing_surface * num / (1.25 * 2.5)),
                    "total_chimney_cap_surface_m2": cap_surface * num,
                    "num_metal_sheets_cap": math.ceil(cap_surface * num / (1.25 * 2.5)),
                    "total_felt_flashing_surface_m2": perimeter * 0.5 * num if covering == "papa" else 0,
                    "total_clamping_strip_length_m": perimeter * num if covering == "papa" else 0,
                    "single_chimney_perimeter": perimeter
                }
            
            output = []
            output.append("🏭 KALKULATOR OBRÓBEK KOMINOWYCH")
            output.append("=" * 40)
            output.append("")
            output.append(f"📏 Obwód komina: {results['single_chimney_perimeter']:.2f} m")
            output.append(f"📐 Powierzchnia obróbek blaszanych: {results['total_metal_flashing_surface_m2']:.2f} m²")
            output.append(f"📦 Arkusze blachy na obróbki: {results['num_metal_sheets_flashing']} szt.")
            output.append(f"📐 Powierzchnia czapy: {results['total_chimney_cap_surface_m2']:.2f} m²")
            output.append(f"📦 Arkusze blachy na czapę: {results['num_metal_sheets_cap']} szt.")
            if results['total_felt_flashing_surface_m2'] > 0:
                output.append(f"📐 Papa na obróbki: {results['total_felt_flashing_surface_m2']:.2f} m²")
                output.append(f"📏 Listwa dociskowa: {results['total_clamping_strip_length_m']:.2f} m")
            
            self.chimney_results_text.config(state="normal")
            self.chimney_results_text.delete("1.0", "end")
            self.chimney_results_text.insert("1.0", "\n".join(output))
            self.chimney_results_text.config(state="disabled")
            
            self._last_chimney_calc = results
            
        except Exception as e:
            messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd: {e}")
    
    def add_chimney_items(self):
        """Add chimney items to cost estimate"""
        if not hasattr(self, '_last_chimney_calc') or not self._last_chimney_calc:
            messagebox.showwarning("Brak danych", "Najpierw oblicz obróbki kominowe.")
            return
        
        r = self._last_chimney_calc
        items = [
            {"name": "Blacha na obróbki kominowe", "quantity": r['num_metal_sheets_flashing'], "unit": "ark.", "price_unit_net": 98.0, "vat_rate": 8, "category": "material"},
            {"name": "Blacha na czapę kominową", "quantity": r['num_metal_sheets_cap'], "unit": "ark.", "price_unit_net": 98.0, "vat_rate": 8, "category": "material"},
            {"name": "Montaż obróbek kominowych", "quantity": self.chimney_num.get(), "unit": "szt.", "price_unit_net": 350.0, "vat_rate": 8, "category": "service"},
        ]
        
        if r['total_felt_flashing_surface_m2'] > 0:
            items.append({"name": "Papa na obróbki kominowe", "quantity": r['total_felt_flashing_surface_m2'], "unit": "m²", "price_unit_net": 28.6, "vat_rate": 8, "category": "material"})
            items.append({"name": "Listwa dociskowa", "quantity": r['total_clamping_strip_length_m'], "unit": "mb", "price_unit_net": 15.0, "vat_rate": 8, "category": "material"})
        
        for item in items:
            item["note"] = ""
            self.cost_items.append(item)
        
        self._refresh_cost_ui()
        messagebox.showinfo("Dodano", f"Dodano {len(items)} pozycji kominowych do kosztorysu.")
        self.notebook.select(self.cost_tab)
    
    def create_flashing_tab(self):
        """Create flashing/trim calculation tab"""
        self.flashing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.flashing_tab, text="🔧 Obróbki")
        
        main = ttk.Frame(self.flashing_tab)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Description
        desc_label = ttk.Label(main, text="Oblicz ilość blachy potrzebnej na obróbki blacharskie (wiatrownice, okapnice, pasy nadrynnowe itp.)", font=("Segoe UI", 10))
        desc_label.pack(pady=(0,10))
        
        # Flashing items list
        input_frame = ttk.LabelFrame(main, text="📋 Obróbki blacharskie")
        input_frame.pack(fill="both", expand=True, pady=(0,10))
        
        # Create a list of common flashing types
        self.flashing_items = {}
        flashing_types = [
            ("Wiatrownica", 0.0, 0.35),
            ("Okapnica", 0.0, 0.25),
            ("Pas nadrynnowy", 0.0, 0.20),
            ("Gąsior", 0.0, 0.40),
            ("Pas przyścienny", 0.0, 0.30),
            ("Kosz", 0.0, 0.50),
        ]
        
        cols = ("name", "length", "width", "area")
        self.flashing_tree = ttk.Treeview(input_frame, columns=cols, show="headings", height=8)
        for c,h in zip(cols, ("Nazwa obróbki", "Długość [m]", "Szer. rozwinięcia [m]", "Powierzchnia [m²]")):
            self.flashing_tree.heading(c, text=h)
            self.flashing_tree.column(c, width=180 if c=="name" else 120, anchor="center" if c!="name" else "w")
        self.flashing_tree.pack(fill="both", expand=True, padx=8, pady=8)
        
        for name, length, width in flashing_types:
            self.flashing_tree.insert("", "end", values=(name, f"{length:.2f}", f"{width:.2f}", f"{length*width:.2f}"))
        
        # Edit controls
        edit_frame = ttk.Frame(main)
        edit_frame.pack(fill="x", pady=5)
        
        ttk.Label(edit_frame, text="Długość:").pack(side="left", padx=4)
        self.flashing_length_entry = ttk.Entry(edit_frame, width=10)
        self.flashing_length_entry.pack(side="left", padx=4)
        
        ttk.Button(edit_frame, text="Aktualizuj zaznaczone", command=self.update_flashing_length).pack(side="left", padx=10)
        
        # Results
        result_frame = ttk.Frame(main)
        result_frame.pack(fill="x", pady=10)
        
        self.flashing_total_label = ttk.Label(result_frame, text="Suma powierzchni: 0.00 m² | Arkusze blachy (1.25x2.5m): 0 szt.", font=("Segoe UI", 11, "bold"))
        self.flashing_total_label.pack(side="left")
        
        ttk.Button(main, text="➕ Dodaj pozycje do kosztorysu", command=self.add_flashing_items, style='Success.TButton').pack(pady=10)
    
    def update_flashing_length(self):
        """Update the length of selected flashing item"""
        sel = self.flashing_tree.selection()
        if not sel:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz pozycję do aktualizacji.")
            return
        
        try:
            length = float(self.flashing_length_entry.get().replace(",", "."))
            for item_id in sel:
                values = self.flashing_tree.item(item_id)['values']
                name = values[0]
                width = float(values[2])
                area = length * width
                self.flashing_tree.item(item_id, values=(name, f"{length:.2f}", f"{width:.2f}", f"{area:.2f}"))
            
            self._update_flashing_totals()
        except ValueError:
            messagebox.showerror("Błąd", "Podaj prawidłową wartość długości.")
    
    def _update_flashing_totals(self):
        """Update flashing totals display"""
        total_area = 0.0
        for item_id in self.flashing_tree.get_children():
            values = self.flashing_tree.item(item_id)['values']
            total_area += float(values[3])
        
        sheet_area = 1.25 * 2.5
        num_sheets = math.ceil(total_area / sheet_area) if total_area > 0 else 0
        self.flashing_total_label.config(text=f"Suma powierzchni: {total_area:.2f} m² | Arkusze blachy (1.25x2.5m): {num_sheets} szt.")
    
    def add_flashing_items(self):
        """Add flashing items to cost estimate"""
        items_added = 0
        for item_id in self.flashing_tree.get_children():
            values = self.flashing_tree.item(item_id)['values']
            length = float(values[1])
            if length > 0:
                item = {
                    "name": f"Obróbka - {values[0]}", 
                    "quantity": length, 
                    "unit": "mb", 
                    "price_unit_net": 35.0, 
                    "vat_rate": 8, 
                    "category": "material",
                    "note": f"Szerokość rozwinięcia: {values[2]} m"
                }
                self.cost_items.append(item)
                items_added += 1
        
        if items_added > 0:
            self._refresh_cost_ui()
            messagebox.showinfo("Dodano", f"Dodano {items_added} pozycji obróbek do kosztorysu.")
            self.notebook.select(self.cost_tab)
        else:
            messagebox.showwarning("Brak pozycji", "Nie ma pozycji z długością większą niż 0 do dodania.")

# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = RoofCalculatorApp(root)
    root.mainloop()