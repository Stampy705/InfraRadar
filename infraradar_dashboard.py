"""
InfraRadar - Contractor Intelligence Hub
A professional-grade desktop dashboard built with customtkinter.
"""
import csv
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from database import InfraRadarDB
import webbrowser
import re
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calculate_market_cap(contracts_list):
    total = 0.0
    pattern = re.compile(r'([\d,\.]+)\s*(lakh\s+crore|crore)', re.IGNORECASE)
    
    for item in contracts_list:
        budget_str = item if isinstance(item, str) else item.get("budget", "")
        if not budget_str or "undisclosed" in budget_str.lower():
            continue
        
        match = pattern.search(budget_str)
        if match:
            number = float(match.group(1).replace(",", ""))
            unit = match.group(2).lower()
            if "lakh crore" in unit:
                number *= 100000
            total += number
    
    return float(total)


C = {
    "bg_root":       "#0D0F12", "bg_panel":      "#12151A", "bg_card":       "#181C23",
    "bg_header":     "#0A0C10", "bg_tree":       "#12151A", "bg_tree_sel":   "#1A3A5C",
    "bg_tree_alt":   "#161920", "bg_input":      "#1E2330", "border":        "#252B38",
    "border_bright": "#2E3A4E", "accent":        "#00A8FF", "accent_dim":    "#0078C0",
    "accent_green":  "#00D68F", "accent_amber":  "#FFB800", "accent_red":    "#FF4D6A",
    "accent_purple": "#A855F7", "fg_primary":    "#E8EDF5", "fg_secondary":  "#8A95A8",
    "fg_muted":      "#4A5568", "fg_header":     "#C5CDD9", "font_mono":     ("Consolas", 11),
    "font_mono_sm":  ("Consolas", 10), "font_ui": ("Segoe UI", 11), "font_ui_sm": ("Segoe UI", 10),
    "font_title":    ("Segoe UI Semibold", 13)
}

db = InfraRadarDB()
CONTRACTS = db.get_all_contracts()

LOCATION_FILTERS = {
    "All India":       lambda c: True,
    "Maharashtra":     lambda c: "Maharashtra" in c["location"],
    "Pune":            lambda c: "Pune" in c["location"],
    "Mumbai":          lambda c: "Mumbai" in c["location"],
    "Nashik":          lambda c: "Nashik" in c["location"],
    "Aurangabad":      lambda c: "Aurangabad" in c["location"],
    "Solapur":         lambda c: "Solapur" in c["location"],
}

STATUS_COLOR = {"Available": C["accent_green"], "Upcoming": C["accent_amber"], "Taken": C["accent_red"]}
STATUS_TAG = {"Available": "status_available", "Upcoming": "status_upcoming", "Taken": "status_taken"}

def apply_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("InfraRadar.Treeview", background=C["bg_tree"], foreground=C["fg_primary"],
                    fieldbackground=C["bg_tree"], bordercolor=C["border"], rowheight=28, font=C["font_ui_sm"])
    style.map("InfraRadar.Treeview", background=[("selected", C["bg_tree_sel"])], foreground=[("selected", "#FFFFFF")])
    style.configure("InfraRadar.Treeview.Heading", background=C["bg_header"], foreground=C["accent"],
                    relief="flat", borderwidth=0, font=("Consolas", 10, "bold"), padding=(6, 6))
    style.configure("InfraRadar.Vertical.TScrollbar", troughcolor=C["bg_panel"], background=C["border_bright"],
                    arrowcolor=C["fg_secondary"], relief="flat", width=10)

class InfraRadarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("InfraRadar — Contractor Intelligence Hub")
        self.geometry("1440x820")
        self.minsize(1100, 640)
        self.configure(fg_color=C["bg_root"])
        apply_treeview_style()

        self._selected_contract = None
        self._filter_var = tk.StringVar(value="All India")

        self._build_header()
        self._build_body()
        self._populate_grid(CONTRACTS)

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=C["bg_header"], corner_radius=0, height=80)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        top_row = ctk.CTkFrame(hdr, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(10, 0))

        title = ctk.CTkLabel(top_row, text="◉ InfraRadar - Master Intelligence", font=C["font_title"], text_color=C["accent"])
        title.pack(side="left")

        self.filter_combo = ctk.CTkComboBox(top_row, values=list(LOCATION_FILTERS.keys()), 
                                           variable=self._filter_var, width=150, height=26, 
                                           command=self._on_filter_change,
                                           fg_color=C["bg_input"], border_color=C["border_bright"])
        self.filter_combo.pack(side="right")

        self.export_btn = ctk.CTkButton(top_row, 
                                       text="Generate Report (Excel)", 
                                       font=C["font_ui_sm"],
                                       width=160, height=26,
                                       fg_color="#1A3A5C",
                                       hover_color=C["accent_dim"],
                                       command=self._export_to_csv)
        self.export_btn.pack(side="right", padx=(0, 10))

        stats_row = ctk.CTkFrame(hdr, fg_color="transparent")
        stats_row.pack(fill="x", padx=14, pady=(5, 5))

        self.total_value_lbl = ctk.CTkLabel(stats_row, text="MARKET VALUE: ₹ 0.0 Cr", 
                                            font=("Consolas", 12, "bold"), text_color=C["accent_green"])
        self.total_value_lbl.pack(side="left", padx=(0, 20))

        self.lead_count_lbl = ctk.CTkLabel(stats_row, text="ACTIVE LEADS: 0", 
                                           font=("Consolas", 12), text_color=C["fg_secondary"])
        self.lead_count_lbl.pack(side="left")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=14)

        left_wrap = ctk.CTkFrame(body, fg_color=C["bg_panel"], corner_radius=8, border_width=1, border_color=C["border"])
        left_wrap.pack(side="left", fill="both", expand=True, padx=(0, 7))

        self._build_market_chart(left_wrap)
        self._build_grid_toolbar(left_wrap)
        self._build_treeview(left_wrap)

        right_wrap = ctk.CTkFrame(body, fg_color=C["bg_card"], corner_radius=8, border_width=1, border_color=C["border"])
        right_wrap.pack(side="right", fill="both", expand=False, padx=(7, 0))

        self._build_detail_pane(right_wrap)

    def _build_grid_toolbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=C["bg_root"], corner_radius=0, height=34)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="CONTRACT REGISTRY", font=("Consolas", 10, "bold"), text_color=C["fg_secondary"]).pack(side="left", padx=12)
        self.count_lbl = ctk.CTkLabel(bar, text="0 records", font=("Consolas", 9), text_color=C["accent"], fg_color=C["bg_input"], corner_radius=4)
        self.count_lbl.pack(side="left", padx=4)

    def _build_treeview(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=C["bg_panel"], corner_radius=0)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=("status", "title", "budget", "deadline"), show="headings", style="InfraRadar.Treeview")
        self.tree.heading("status", text="STATUS", anchor="w")
        self.tree.heading("title", text="PROJECT TITLE", anchor="w")
        self.tree.heading("budget", text="BUDGET", anchor="e")
        self.tree.heading("deadline", text="DEADLINE", anchor="c")

        self.tree.column("status", width=110, stretch=False)
        self.tree.column("title", width=440, stretch=True)
        self.tree.column("budget", width=130, stretch=False, anchor="e")
        self.tree.column("deadline", width=100, stretch=False, anchor="c")

        self.tree.tag_configure("status_available", foreground=C["accent_green"])
        self.tree.tag_configure("status_upcoming", foreground=C["accent_amber"])
        self.tree.tag_configure("status_taken", foreground=C["accent_red"])
        self.tree.tag_configure("alt_row", background=C["bg_tree_alt"])

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview, style="InfraRadar.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def _build_detail_pane(self, parent):
        top_bar = ctk.CTkFrame(parent, fg_color=C["bg_root"], corner_radius=0, height=34)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="DEEP DIVE", font=("Consolas", 10, "bold"), text_color=C["fg_secondary"]).pack(side="left", padx=12)
        self.detail_status_badge = ctk.CTkLabel(top_bar, text="", font=("Consolas", 9), fg_color=C["bg_input"], corner_radius=4)
        self.detail_status_badge.pack(side="left", padx=4)

        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color=C["bg_card"], corner_radius=0)
        scroll_frame.pack(fill="both", expand=True)

        self._field_label(scroll_frame, "PROJECT TITLE", top_pad=18)
        self.detail_title = ctk.CTkLabel(scroll_frame, text="— Select a contract —", font=("Segoe UI Semibold", 14), text_color=C["fg_primary"], anchor="w", wraplength=440)
        self.detail_title.pack(fill="x", padx=18, pady=(2, 12))
        self._divider(scroll_frame)

        self._field_label(scroll_frame, "AUTHORITY / CLIENT")
        self.detail_authority = ctk.CTkLabel(scroll_frame, text="—", font=C["font_ui"], text_color=C["fg_primary"], anchor="w", wraplength=440)
        self.detail_authority.pack(fill="x", padx=18, pady=(2, 10))

        self._field_label(scroll_frame, "LOCATION")
        self.detail_location = ctk.CTkLabel(scroll_frame, text="—", font=C["font_ui"], text_color=C["fg_primary"], anchor="w")
        self.detail_location.pack(fill="x", padx=18, pady=(2, 10))
        self._divider(scroll_frame)

        metrics_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        metrics_row.pack(fill="x", padx=18, pady=(10, 10))

        budget_tile = ctk.CTkFrame(metrics_row, fg_color=C["bg_input"], corner_radius=6)
        budget_tile.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(budget_tile, text="CONTRACT VALUE", font=("Consolas", 8), text_color=C["fg_muted"]).pack(anchor="w", padx=10, pady=(8, 0))
        self.detail_budget = ctk.CTkLabel(budget_tile, text="—", font=("Consolas", 15, "bold"), text_color=C["accent"])
        self.detail_budget.pack(anchor="w", padx=10, pady=(2, 8))

        emd_tile = ctk.CTkFrame(metrics_row, fg_color=C["bg_input"], corner_radius=6)
        emd_tile.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(emd_tile, text="EMD / BID SECURITY", font=("Consolas", 8), text_color=C["fg_muted"]).pack(anchor="w", padx=10, pady=(8, 0))
        self.detail_emd = ctk.CTkLabel(emd_tile, text="—", font=("Consolas", 15, "bold"), text_color=C["accent_amber"])
        self.detail_emd.pack(anchor="w", padx=10, pady=(2, 8))
        self._divider(scroll_frame)

        self._field_label(scroll_frame, "SUBMISSION DEADLINE")
        self.detail_deadline = ctk.CTkLabel(scroll_frame, text="—", font=("Consolas", 12), text_color=C["fg_primary"], anchor="w")
        self.detail_deadline.pack(fill="x", padx=18, pady=(2, 10))
        self._divider(scroll_frame)

        ai_hdr = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        ai_hdr.pack(fill="x", padx=18, pady=(10, 0))
        ctk.CTkLabel(ai_hdr, text=" ◈ AI EXECUTIVE BRIEF ", font=("Consolas", 9, "bold"), text_color=C["accent_purple"], fg_color="#1A1030", corner_radius=4).pack(side="left")

        self.detail_brief_box = ctk.CTkTextbox(scroll_frame, height=130, font=("Segoe UI", 11), fg_color="#10121A", border_color="#2A2050", border_width=1, text_color=C["fg_primary"], wrap="word", state="disabled")
        self.detail_brief_box.pack(fill="x", padx=18, pady=(6, 10))
        self._divider(scroll_frame)

        self.url_button = ctk.CTkButton(scroll_frame, text="Open Tender Portal  ↗", font=("Segoe UI", 11), height=34, fg_color=C["bg_input"], text_color=C["accent"], border_width=1, border_color=C["border_bright"], command=self._open_url, state="disabled")
        self.url_button.pack(fill="x", padx=18, pady=(6, 20))

        self.delete_button = ctk.CTkButton(scroll_frame,
            text          = "Scrap Lead (Delete)",
            font          = ("Segoe UI", 11),
            height        = 34,
            fg_color      = "#2A1010",
            hover_color   = "#4A1010",
            text_color    = "#FF4D6A",
            border_width  = 1,
            border_color  = "#4A2020",
            corner_radius = 6,
            command       = self._on_delete_contract,
            state         = "disabled",
        )
        self.delete_button.pack(fill="x", padx=18, pady=(0, 20))

    def _aggregate_by_city(self, contracts):
        """Reuse calculate_market_cap parsing logic, bucketed per city."""
        known_cities = [
            "Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Navi Mumbai", 
            "Chhatrapati Sambhaji Nagar", "Aurangabad", "Solapur", "Amravati", 
            "Nanded", "Kolhapur", "Akola", "Jalgaon", "Latur", "Dhule", 
            "Ahmednagar", "Ahilyanagar", "Chandrapur", "Parbhani", "Jalna", 
            "Bhusaval", "Satara", "Ratnagiri", "Sangli"
        ]
        
        city_totals  = {city: 0.0 for city in known_cities}
        other_total  = 0.0
        pattern      = re.compile(r'([\d,\.]+)\s*(lakh\s+crore|crore)', re.IGNORECASE)

        for c in contracts:
            budget_str = c.get("budget", "")
            if not budget_str or "undisclosed" in budget_str.lower():
                continue
            match = pattern.search(budget_str)
            if not match:
                continue
            number = float(match.group(1).replace(",", ""))
            if "lakh crore" in match.group(2).lower():
                number *= 100_000
                
            location = c.get("location", "")
            assigned = False
            
            for city in known_cities:
                if city.lower() in location.lower():
                    city_totals[city] += number
                    assigned = True
                    break
            if not assigned:
                other_total += number

        city_totals["Chhatrapati Sambhaji Nagar"] += city_totals.pop("Aurangabad", 0)
        city_totals["Ahilyanagar"] += city_totals.pop("Ahmednagar", 0)

        result = {k: v for k, v in city_totals.items() if v > 0}
        if other_total > 0:
            result["Other"] = other_total
            
        return result

    def _build_market_chart(self, parent):
        """Build the dark-mode Matplotlib bar chart and embed it at the bottom
        of the left panel with fixed height."""
        chart_outer = ctk.CTkFrame(parent, fg_color=C["bg_panel"],
                                   corner_radius=0, height=230)
        chart_outer.pack(side="bottom", fill="x")
        chart_outer.pack_propagate(False)

        hdr = ctk.CTkFrame(chart_outer, fg_color=C["bg_root"],
                           corner_radius=0, height=28)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="MARKET VALUE BY CITY",
                     font=("Consolas", 9, "bold"),
                     text_color=C["fg_secondary"]).pack(side="left", padx=12, pady=4)

        ctk.CTkFrame(chart_outer, fg_color=C["border"],
                     height=1, corner_radius=0).pack(fill="x")

        chart_host = ctk.CTkFrame(chart_outer, fg_color=C["bg_panel"], corner_radius=0)
        chart_host.pack(fill="both", expand=True)

        BG = "#12151A"
        self._chart_fig, self._chart_ax = plt.subplots(figsize=(6, 1.75))
        self._chart_fig.patch.set_facecolor(BG)
        self._chart_ax.set_facecolor(BG)

        self._chart_canvas = FigureCanvasTkAgg(self._chart_fig, master=chart_host)
        self._chart_canvas.get_tk_widget().configure(bg=BG, highlightthickness=0)
        self._chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_market_chart(self, contracts):
        """Redraw the bar chart for the given contracts list."""
        BG       = "#12151A"
        BAR_CLR  = "#00A8FF"
        LABEL_CLR = "#8A95A8"
        GRID_CLR  = "#252B38"

        ax = self._chart_ax
        ax.clear()
        ax.set_facecolor(BG)
        self._chart_fig.patch.set_facecolor(BG)

        city_data = self._aggregate_by_city(contracts)

        if not city_data:
            ax.text(0.5, 0.5, "No Budgetary Data Available",
                    ha="center", va="center",
                    color=LABEL_CLR, fontsize=9,
                    transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            self._chart_canvas.draw()
            return

        cities = list(city_data.keys())
        values = list(city_data.values())

        bars = ax.bar(cities, values, color=BAR_CLR, width=0.52,
                      zorder=3, linewidth=0)

        for bar in bars:
            bar.set_edgecolor("#40C4FF")
            bar.set_linewidth(0.6)

        for bar, val in zip(bars, values):
            label = f"₹{val:,.0f}" if val < 1_000 else f"₹{val/1000:,.1f}K"
            ax.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() * 1.04,
                    label,
                    ha="center", va="bottom",
                    color=LABEL_CLR, fontsize=7,
                    fontfamily="Consolas")

        ax.set_ylabel("Total Value (Cr)", color=LABEL_CLR, fontsize=7.5,
                      labelpad=6, fontfamily="Consolas")
        ax.tick_params(axis="both", colors=LABEL_CLR, labelsize=7.5, length=0)
        ax.tick_params(axis="x", pad=4)

        for label in ax.get_xticklabels():
            label.set_fontfamily("Consolas")
            label.set_rotation(20)
            label.set_ha("right")

        for label in ax.get_yticklabels():
            label.set_fontfamily("Consolas")

        for side, spine in ax.spines.items():
            if side in ("top", "right"):
                spine.set_visible(False)
            else:
                spine.set_edgecolor(GRID_CLR)
                spine.set_linewidth(0.8)

        ax.yaxis.grid(True, color=GRID_CLR, linestyle="--",
                      linewidth=0.5, alpha=0.6, zorder=0)
        ax.set_axisbelow(True)

        max_val = max(values) if values else 1
        ax.set_ylim(0, max_val * 1.35)

        self._chart_fig.tight_layout(pad=0.6)
        self._chart_canvas.draw()

    def _field_label(self, parent, text, top_pad=10):
        """Create a styled field label."""
        ctk.CTkLabel(parent, text=text, font=("Consolas", 9), text_color=C["fg_muted"], anchor="w").pack(fill="x", padx=18, pady=(top_pad, 0))

    def _divider(self, parent):
        """Create a horizontal divider line."""
        ctk.CTkFrame(parent, fg_color=C["border"], height=1, corner_radius=0).pack(fill="x", padx=18, pady=2)

    def _populate_grid(self, contracts):
        """Populate the treeview with contract data and update statistics."""
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for i, c in enumerate(contracts):
            tags = [STATUS_TAG.get(c["status"], "status_available")]
            if i % 2 == 1: tags.append("alt_row")
            self.tree.insert("", "end", iid=str(i), values=(c["status"], c["title"], c["budget"], c["deadline"]), tags=tags)

        total_cr = calculate_market_cap(contracts)
        self.total_value_lbl.configure(text=f"MARKET VALUE: ₹ {total_cr:,.2f} Cr")
        self.lead_count_lbl.configure(text=f"ACTIVE LEADS: {len(contracts)}")
        self.count_lbl.configure(text=f"  {len(contracts)} records  ")

        if hasattr(self, "_chart_canvas"):
            self._update_market_chart(contracts)

    def _on_filter_change(self, choice):
        """Apply location filter and refresh the grid."""
        pred = LOCATION_FILTERS.get(choice, lambda c: True)
        filtered = [c for c in CONTRACTS if pred(c)]
        self._populate_grid(filtered)
        self._clear_detail()

    def _on_row_select(self, event):
        """Handle treeview row selection and populate detail pane."""
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])

        choice = self._filter_var.get()
        pred = LOCATION_FILTERS.get(choice, lambda c: True)
        filtered = [c for c in CONTRACTS if pred(c)]

        if idx >= len(filtered): return
        c = filtered[idx]
        self._selected_contract = c

        self.detail_status_badge.configure(text=f"  {c['status'].upper()}  ", text_color=STATUS_COLOR.get(c["status"], C["fg_secondary"]))
        self.detail_title.configure(text=c["title"])
        self.detail_authority.configure(text=c["authority"])
        self.detail_location.configure(text=c["location"])
        self.detail_budget.configure(text=c["budget"])
        self.detail_emd.configure(text=c["emd"])
        self.detail_deadline.configure(text=c["deadline"])

        self.detail_brief_box.configure(state="normal")
        self.detail_brief_box.delete("0.0", "end")
        self.detail_brief_box.insert("0.0", c.get("ai_brief", "No brief available."))
        self.detail_brief_box.configure(state="disabled")
        self.url_button.configure(state="normal")
        self.delete_button.configure(state="normal")

    def _clear_detail(self):
        """Clear the detail pane and disable interactive elements."""
        self._selected_contract = None
        self.detail_status_badge.configure(text="")
        self.detail_title.configure(text="— Select a contract —")
        for lbl in (self.detail_authority, self.detail_location, self.detail_budget, self.detail_emd, self.detail_deadline):
            lbl.configure(text="—")
        self.detail_brief_box.configure(state="normal")
        self.detail_brief_box.delete("0.0", "end")
        self.detail_brief_box.configure(state="disabled")
        self.url_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    def _open_url(self):
        """Open the tender portal URL in browser."""
        if self._selected_contract and "url" in self._selected_contract:
            webbrowser.open(self._selected_contract["url"])

    def _on_delete_contract(self):
        """Delete selected contract from database and refresh UI."""
        if self._selected_contract:
            c_id = self._selected_contract['id']
            db.delete_contract(c_id)
            
            global CONTRACTS
            CONTRACTS = db.get_all_contracts()
            self._on_filter_change(self._filter_var.get())
            self._clear_detail()
            print(f"🗑️ Record {c_id} moved to scrap pile.")

    def _export_to_csv(self):
        """Export filtered contracts to CSV file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="InfraRadar_Daily_Leads.csv"
        )
        
        if not file_path:
            return

        choice = self._filter_var.get()
        pred = LOCATION_FILTERS.get(choice, lambda c: True)
        filtered_data = [c for c in CONTRACTS if pred(c)]

        if not filtered_data:
            print("⚠️ No data to export.")
            return

        try:
            keys = filtered_data[0].keys()
            with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(filtered_data)
            print(f"📊 Report Exported: {file_path}")
        except Exception as e:
            print(f"❌ Export failed: {e}")


if __name__ == "__main__":
    app = InfraRadarApp()
    app.mainloop()
