import tkinter as tk
from tkinter import ttk, messagebox
import db_config
from datetime import datetime, date, timedelta
import math

# ── optional CSV / PDF export helpers ────────────────────────────────────────
try:
    import csv, os
    CSV_OK = True
except ImportError:
    CSV_OK = False


class ReportsClass:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#F3F4F6")

        # ── palette ──────────────────────────────────────────────────────
        self.bg_page   = "#F3F4F6"
        self.bg_card   = "#FFFFFF"
        self.bd        = "#E5E7EB"
        self.txt_dark  = "#111827"
        self.txt_muted = "#6B7280"
        self.blue      = "#2563EB"
        self.green     = "#10B981"
        self.orange    = "#F59E0B"
        self.red       = "#EF4444"
        self.purple    = "#8B5CF6"
        self.sky       = "#0EA5E9"

        # ── fonts ────────────────────────────────────────────────────────
        self.FT  = ("Segoe UI", 16, "bold")
        self.FN  = ("Segoe UI", 10)
        self.FNB = ("Segoe UI", 10, "bold")
        self.FS  = ("Segoe UI",  9)
        self.FSB = ("Segoe UI",  9, "bold")
        self.FCV = ("Segoe UI", 22, "bold")
        self.FCT = ("Segoe UI",  9)

        # ── state ────────────────────────────────────────────────────────
        self.date_from = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        self.date_to   = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        self.var_cat   = tk.StringVar(value="All Categories")
        self.var_emp   = tk.StringVar(value="All Employees")
        self.search_rpt= tk.StringVar()
        self._page     = 0
        self._rows_all = []    # full table data for pagination
        self._page_size= 8

        # ── treeview style ───────────────────────────────────────────────
        self._tree_style()

        # ── scrollable master canvas ─────────────────────────────────────
        outer = tk.Frame(self.root, bg=self.bg_page)
        outer.pack(fill=tk.BOTH, expand=True)

        self._vbar = ttk.Scrollbar(outer, orient=tk.VERTICAL)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = tk.Canvas(outer, bg=self.bg_page,
                                 highlightthickness=0,
                                 yscrollcommand=self._vbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._vbar.config(command=self._canvas.yview)

        self._page_frame = tk.Frame(self._canvas, bg=self.bg_page)
        self._win = self._canvas.create_window(
            (0, 0), window=self._page_frame, anchor="nw")

        self._page_frame.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind("<Enter>",
            lambda e: self._canvas.bind_all("<MouseWheel>", self._scroll))
        self._canvas.bind("<Leave>",
            lambda e: self._canvas.unbind_all("<MouseWheel>"))

        # ── build all sections ───────────────────────────────────────────
        self._build_header()
        self._build_filters()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_mid_row()
        self._build_table_section()
        self._build_export_bar()

        # ── initial data load ────────────────────────────────────────────
        self._load_all()

    # ─────────────────────────────────────────────────────────────────────────
    # SCROLL
    # ─────────────────────────────────────────────────────────────────────────
    def _scroll(self, e):
        try:
            if self._canvas.winfo_exists():
                self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # STYLE
    # ─────────────────────────────────────────────────────────────────────────
    def _tree_style(self):
        s = ttk.Style()
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("Rpt.Treeview",
            background="#FFFFFF", fieldbackground="#FFFFFF",
            foreground="#111827", rowheight=36, borderwidth=0,
            font=("Segoe UI", 10))
        s.configure("Rpt.Treeview.Heading",
            background="#F8FAFC", foreground="#475569",
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(10, 8))
        s.map("Rpt.Treeview",
            background=[("selected", "#EFF6FF")],
            foreground=[("selected", "#2563EB")])

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────────────
    def _build_header(self):
        h = tk.Frame(self._page_frame, bg=self.bg_page)
        h.pack(fill=tk.X, padx=28, pady=(20, 4))
        tk.Label(h, text="Reports & Analytics",
                 font=self.FT, bg=self.bg_page, fg=self.txt_dark).pack(side=tk.LEFT)
        self._make_btn(h, "↻ Refresh", "#F1F5F9", self.txt_dark,
                       cmd=self._load_all, border=True).pack(side=tk.RIGHT)

    # ─────────────────────────────────────────────────────────────────────────
    # FILTERS
    # ─────────────────────────────────────────────────────────────────────────
    def _build_filters(self):
        outer = tk.Frame(self._page_frame, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        outer.pack(fill=tk.X, padx=28, pady=(0, 14))

        row1 = tk.Frame(outer, bg=self.bg_card)
        row1.pack(fill=tk.X, padx=16, pady=(12, 6))

        # Date from
        tk.Label(row1, text="From:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._date_from_ent = self._filter_entry(row1, self.date_from, 11)
        self._date_from_ent.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(row1, text="To:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._date_to_ent = self._filter_entry(row1, self.date_to, 11)
        self._date_to_ent.pack(side=tk.LEFT, padx=(0, 14))

        # Category dropdown
        tk.Label(row1, text="Category:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._cat_cb = ttk.Combobox(row1, textvariable=self.var_cat,
                                    state="readonly", font=self.FN, width=16)
        self._cat_cb.pack(side=tk.LEFT, ipady=3, padx=(0, 14))
        self._cat_cb.bind("<<ComboboxSelected>>", lambda e: self._load_all())

        # Employee dropdown
        tk.Label(row1, text="Employee:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._emp_cb = ttk.Combobox(row1, textvariable=self.var_emp,
                                    state="readonly", font=self.FN, width=18)
        self._emp_cb.pack(side=tk.LEFT, ipady=3, padx=(0, 14))
        self._emp_cb.bind("<<ComboboxSelected>>", lambda e: self._load_all())

        # Apply button
        self._make_btn(row1, "Apply Filters", self.blue, "white",
                       cmd=self._load_all).pack(side=tk.LEFT)

        # Quick filters row
        row2 = tk.Frame(outer, bg=self.bg_card)
        row2.pack(fill=tk.X, padx=16, pady=(0, 12))
        tk.Label(row2, text="Quick:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 8))
        for lbl, fn in [
            ("Today",       self._qf_today),
            ("Last 7 Days", self._qf_7),
            ("This Month",  self._qf_month),
            ("Last Month",  self._qf_last_month),
            ("This Year",   self._qf_year),
        ]:
            tk.Button(row2, text=lbl, font=self.FS,
                      bg="#F1F5F9", fg=self.txt_dark, relief="flat", bd=0,
                      cursor="hand2", padx=12, pady=5,
                      activebackground=self.blue, activeforeground="white",
                      command=fn).pack(side=tk.LEFT, padx=(0, 6))

    def _filter_entry(self, parent, var, width):
        f = tk.Frame(parent, bg=self.bg_card,
                     highlightbackground=self.bd, highlightthickness=1)
        tk.Entry(f, textvariable=var, font=self.FN, bg=self.bg_card,
                 bd=0, width=width, insertbackground=self.txt_dark
                 ).pack(padx=6, ipady=4)
        return f

    # quick filter helpers
    def _set_range(self, d_from, d_to):
        self.date_from.set(d_from.strftime("%d/%m/%Y"))
        self.date_to.set(d_to.strftime("%d/%m/%Y"))
        self._load_all()

    def _qf_today(self):      self._set_range(date.today(), date.today())
    def _qf_7(self):          self._set_range(date.today()-timedelta(6), date.today())
    def _qf_month(self):      self._set_range(date.today().replace(day=1), date.today())
    def _qf_last_month(self):
        first = date.today().replace(day=1)
        last  = first - timedelta(days=1)
        self._set_range(last.replace(day=1), last)
    def _qf_year(self):
        self._set_range(date.today().replace(month=1, day=1), date.today())

    def _parse_dates(self):
        try:
            df = datetime.strptime(self.date_from.get(), "%d/%m/%Y").date()
            dt = datetime.strptime(self.date_to.get(),   "%d/%m/%Y").date()
        except Exception:
            df = date.today() - timedelta(30)
            dt = date.today()
        return df, dt

    # ─────────────────────────────────────────────────────────────────────────
    # KPI CARDS
    # ─────────────────────────────────────────────────────────────────────────
    def _build_kpi_row(self):
        row = tk.Frame(self._page_frame, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        for i in range(4):
            row.columnconfigure(i, weight=1)

        self._kv_sales  = self._kpi(row, 0, "Total Sales",         "৳ —",   "💰", self.blue,   "#EFF6FF")
        self._kv_profit = self._kpi(row, 1, "Total Profit",        "৳ —",   "📈", self.green,  "#ECFDF5")
        self._kv_orders = self._kpi(row, 2, "Total Orders",        "—",     "🧾", self.orange, "#FFF7ED")
        self._kv_avg    = self._kpi(row, 3, "Avg Sale Value",      "৳ —",   "⚡", self.red,    "#FFF1F2")

    def _kpi(self, parent, col, title, init, icon, color, bg_icon):
        card = tk.Frame(parent, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1,
                        height=110)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 10, 0))
        card.pack_propagate(False)

        top = tk.Frame(card, bg=self.bg_card)
        top.pack(fill=tk.X, padx=16, pady=(14, 4))
        tk.Label(top, text=title, font=self.FCT,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT)

        icon_f = tk.Frame(top, bg=bg_icon, width=30, height=30)
        icon_f.pack(side=tk.RIGHT); icon_f.pack_propagate(False)
        tk.Label(icon_f, text=icon, font=("Segoe UI", 13),
                 bg=bg_icon, fg=color).place(relx=.5, rely=.5, anchor="center")

        val = tk.Label(card, text=init, font=self.FCV,
                       bg=self.bg_card, fg=self.txt_dark)
        val.pack(anchor="w", padx=16)

        sub = tk.Label(card, text="", font=("Segoe UI", 8),
                       bg=self.bg_card, fg=self.txt_muted)
        sub.pack(anchor="w", padx=16)

        return val, sub

    # ─────────────────────────────────────────────────────────────────────────
    # CHARTS ROW  (hand-drawn on tk.Canvas)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_charts_row(self):
        row = tk.Frame(self._page_frame, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        row.columnconfigure(0, weight=3)
        row.columnconfigure(1, weight=2)

        # Bar chart card
        left = tk.Frame(row, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._chart_hdr(left, "📊  Daily Sales Overview",
                        "Sales amount for the current period")
        self._sales_chart = tk.Canvas(left, bg=self.bg_card, height=200,
                                      highlightthickness=0)
        self._sales_chart.pack(fill=tk.X, padx=16, pady=(0, 16))

        # Line chart card
        right = tk.Frame(row, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        self._chart_hdr(right, "📉  Profit Margin Trend",
                        "Profit growth over the last 30 days")
        self._profit_chart = tk.Canvas(right, bg=self.bg_card, height=200,
                                       highlightthickness=0)
        self._profit_chart.pack(fill=tk.X, padx=16, pady=(0, 16))

    def _chart_hdr(self, parent, title, subtitle):
        f = tk.Frame(parent, bg=self.bg_card)
        f.pack(fill=tk.X, padx=16, pady=(14, 8))
        tk.Label(f, text=title, font=self.FNB,
                 bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(f, text=subtitle, font=self.FS,
                 bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")

    def _draw_bar_chart(self, canvas, data):
        """data = list of (label, value)"""
        canvas.delete("all")
        canvas.update_idletasks()
        W = canvas.winfo_width() or 400
        H = 200
        pad_l, pad_r, pad_t, pad_b = 44, 14, 16, 36

        if not data:
            canvas.create_text(W//2, H//2, text="No data",
                               fill=self.txt_muted, font=self.FN)
            return

        vals   = [v for _, v in data]
        maxv   = max(vals) if max(vals) > 0 else 1
        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        bar_w   = max(4, chart_w // len(data) - 4)

        # grid lines
        for i in range(5):
            y = pad_t + chart_h - (chart_h * i // 4)
            canvas.create_line(pad_l, y, W - pad_r, y,
                               fill="#F1F5F9", width=1)
            lbl = f"৳{int(maxv * i / 4):,}"
            canvas.create_text(pad_l - 4, y, text=lbl,
                               anchor="e", fill=self.txt_muted, font=("Segoe UI", 7))

        # bars
        for idx, (lbl, v) in enumerate(data):
            x0 = pad_l + idx * (chart_w // len(data)) + 2
            bh = int(chart_h * v / maxv) if maxv else 0
            y0 = pad_t + chart_h - bh
            y1 = pad_t + chart_h

            # shadow
            canvas.create_rectangle(x0+2, y0+2, x0+bar_w+2, y1+2,
                                     fill="#CBD5E1", outline="")
            # bar gradient (two rectangles)
            canvas.create_rectangle(x0, y0, x0+bar_w, y1,
                                     fill="#93C5FD", outline="")
            canvas.create_rectangle(x0, y0, x0+bar_w, y0+max(1,bh//2),
                                     fill=self.blue, outline="")
            # x label
            canvas.create_text(x0 + bar_w//2, H - pad_b + 6,
                               text=str(lbl), fill=self.txt_muted,
                               font=("Segoe UI", 7), angle=0)

    def _draw_line_chart(self, canvas, data):
        """data = list of (label, value)"""
        canvas.delete("all")
        canvas.update_idletasks()
        W = canvas.winfo_width() or 340
        H = 200
        pad_l, pad_r, pad_t, pad_b = 44, 14, 16, 36

        if not data:
            canvas.create_text(W//2, H//2, text="No data",
                               fill=self.txt_muted, font=self.FN)
            return

        vals   = [v for _, v in data]
        maxv   = max(vals) if max(vals) > 0 else 1
        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b

        # grid
        for i in range(5):
            y = pad_t + chart_h - (chart_h * i // 4)
            canvas.create_line(pad_l, y, W - pad_r, y,
                               fill="#F1F5F9", width=1)
            canvas.create_text(pad_l - 4, y,
                               text=f"৳{int(maxv * i / 4):,}",
                               anchor="e", fill=self.txt_muted,
                               font=("Segoe UI", 7))

        # compute points
        n = len(data)
        pts = []
        for idx, (_, v) in enumerate(data):
            x = pad_l + int(chart_w * idx / max(n - 1, 1))
            y = pad_t + chart_h - int(chart_h * v / maxv)
            pts.append((x, y))

        # filled area
        poly = [pad_l, pad_t + chart_h]
        for x, y in pts:
            poly += [x, y]
        poly += [pts[-1][0], pad_t + chart_h]
        canvas.create_polygon(poly, fill="#D1FAE5", outline="")

        # line
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]; x2, y2 = pts[i+1]
            canvas.create_line(x1, y1, x2, y2,
                               fill=self.green, width=2, smooth=True)

        # dots
        for x, y in pts:
            canvas.create_oval(x-3, y-3, x+3, y+3,
                               fill=self.green, outline="white", width=1)

        # x labels (every other)
        for idx, (lbl, _) in enumerate(data):
            if idx % max(1, n // 6) == 0:
                x = pad_l + int(chart_w * idx / max(n - 1, 1))
                canvas.create_text(x, H - pad_b + 6, text=str(lbl),
                                   fill=self.txt_muted, font=("Segoe UI", 7))

    # ─────────────────────────────────────────────────────────────────────────
    # MIDDLE ROW  (AI tips + trending | low stock)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_mid_row(self):
        row = tk.Frame(self._page_frame, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        row.columnconfigure(0, weight=3)
        row.columnconfigure(1, weight=2)

        # ── left panel ───────────────────────────────────────────────
        left = tk.Frame(row, bg=self.bg_page)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # AI card
        ai_card = tk.Frame(left, bg="#FEFCE8",
                           highlightbackground="#FDE68A", highlightthickness=1)
        ai_card.pack(fill=tk.X, pady=(0, 12))
        h = tk.Frame(ai_card, bg="#FEFCE8")
        h.pack(fill=tk.X, padx=14, pady=(10, 4))
        tk.Label(h, text="🤖  AI Suggestion Insights",
                 font=self.FNB, bg="#FEFCE8", fg="#92400E").pack(anchor="w")
        self._ai_lbl = tk.Label(ai_card, text="Loading…",
                                font=self.FS, bg="#FEFCE8", fg="#78350F",
                                wraplength=500, justify="left", anchor="w")
        self._ai_lbl.pack(fill=tk.X, padx=14, pady=(0, 12))

        # Trending card
        trend_card = tk.Frame(left, bg=self.bg_card,
                              highlightbackground=self.bd, highlightthickness=1)
        trend_card.pack(fill=tk.BOTH, expand=True)
        hf = tk.Frame(trend_card, bg=self.bg_card)
        hf.pack(fill=tk.X, padx=14, pady=(12, 6))
        tk.Label(hf, text="🔥  Trending Products & Demand",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")

        self._trend_frame = tk.Frame(trend_card, bg=self.bg_card)
        self._trend_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        # ── right panel: low stock ────────────────────────────────────
        right = tk.Frame(row, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        rh = tk.Frame(right, bg=self.bg_card)
        rh.pack(fill=tk.X, padx=14, pady=(12, 6))
        tk.Label(rh, text="⚠️  Low Stock Alerts",
                 font=self.FNB, bg=self.bg_card, fg=self.red).pack(anchor="w")

        self._stock_frame = tk.Frame(right, bg=self.bg_card)
        self._stock_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

    # ─────────────────────────────────────────────────────────────────────────
    # DETAILED TABLE
    # ─────────────────────────────────────────────────────────────────────────
    def _build_table_section(self):
        card = tk.Frame(self._page_frame, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        card.pack(fill=tk.X, padx=28, pady=(0, 14))

        # header row
        hdr = tk.Frame(card, bg=self.bg_card)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 8))
        tk.Label(hdr, text="📋  Detailed Product Performance",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(side=tk.LEFT)

        # search
        sw = tk.Frame(hdr, bg=self.bg_card,
                      highlightbackground=self.bd, highlightthickness=1)
        sw.pack(side=tk.RIGHT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(8, 0))
        se = tk.Entry(sw, textvariable=self.search_rpt,
                      font=self.FN, bg=self.bg_card, bd=0, width=24,
                      insertbackground=self.txt_dark)
        se.pack(side=tk.LEFT, padx=6, ipady=5)
        se.insert(0, "Search products in report…")
        se.bind("<FocusIn>",
            lambda e: se.delete(0, "end")
            if se.get() == "Search products in report…" else None)
        se.bind("<KeyRelease>", lambda e: self._filter_table())

        # treeview
        tw = tk.Frame(card, bg=self.bg_card)
        tw.pack(fill=tk.X, padx=16, pady=(0, 8))
        sb = ttk.Scrollbar(tw, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("name", "category", "qty_sold", "revenue", "profit")
        self._rpt_tree = ttk.Treeview(tw, columns=cols, show="headings",
                                      style="Rpt.Treeview", height=9,
                                      yscrollcommand=sb.set)
        sb.config(command=self._rpt_tree.yview)

        for col, hd, w, anc in [
            ("name",     "Product Name ↕",  260, "w"),
            ("category", "Category",        130, "center"),
            ("qty_sold", "Qty Sold",        100, "center"),
            ("revenue",  "Revenue",         130, "center"),
            ("profit",   "Net Profit",      130, "center"),
        ]:
            self._rpt_tree.heading(col, text=hd,
                command=lambda c=col: self._sort_table(c))
            self._rpt_tree.column(col, width=w, anchor=anc)

        self._rpt_tree.tag_configure("pos",  foreground="#059669")
        self._rpt_tree.tag_configure("neg",  foreground=self.red)
        self._rpt_tree.tag_configure("even", background="#FFFFFF")
        self._rpt_tree.tag_configure("odd",  background="#F9FAFB")
        self._rpt_tree.pack(fill=tk.X)

        # pagination
        pg = tk.Frame(card, bg=self.bg_card)
        pg.pack(fill=tk.X, padx=16, pady=(4, 14))
        self._btn_prev = tk.Button(pg, text="← Prev", font=self.FS,
                                   bg="#F1F5F9", fg=self.txt_dark,
                                   relief="flat", bd=0, cursor="hand2",
                                   padx=10, pady=4, command=self._prev_page)
        self._btn_prev.pack(side=tk.LEFT)
        self._page_lbl = tk.Label(pg, text="Page 1 / 1",
                                  font=self.FNB, bg=self.bg_card,
                                  fg=self.txt_muted)
        self._page_lbl.pack(side=tk.LEFT, expand=True)
        self._btn_next = tk.Button(pg, text="Next →", font=self.FS,
                                   bg="#F1F5F9", fg=self.txt_dark,
                                   relief="flat", bd=0, cursor="hand2",
                                   padx=10, pady=4, command=self._next_page)
        self._btn_next.pack(side=tk.RIGHT)

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT BAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_export_bar(self):
        bar = tk.Frame(self._page_frame, bg=self.bg_card,
                       highlightbackground=self.bd, highlightthickness=1)
        bar.pack(fill=tk.X, padx=28, pady=(0, 24))

        inner = tk.Frame(bar, bg=self.bg_card)
        inner.pack(side=tk.RIGHT, padx=16, pady=10)

        self._make_btn(inner, "🖨  Print Report",  "#F1F5F9", self.txt_dark,
                       cmd=self._print_report, border=True).pack(side=tk.LEFT, padx=(0, 8))
        self._make_btn(inner, "📊  Export Excel",  "#16A34A", "white",
                       cmd=self._export_csv).pack(side=tk.LEFT, padx=(0, 8))
        self._make_btn(inner, "📄  Export PDF",    self.red, "white",
                       cmd=self._export_pdf).pack(side=tk.LEFT)

    # ─────────────────────────────────────────────────────────────────────────
    # DATA LOADING
    # ─────────────────────────────────────────────────────────────────────────
    def _load_all(self):
        self._load_dropdowns()
        self._load_kpis()
        self._load_charts()
        self._load_trending()
        self._load_low_stock()
        self._load_table()
        self._build_ai_tip()

    def _load_dropdowns(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("SELECT name FROM categories ORDER BY name")
            cats = ["All Categories"] + [r[0] for r in cur.fetchall()]
            self._cat_cb["values"] = cats

            cur.execute("SELECT emp_id, name FROM users ORDER BY name")
            emps = ["All Employees"] + [f"{r[1]} (#{r[0]})" for r in cur.fetchall()]
            self._emp_cb["values"] = emps
        except Exception: pass
        finally:
            if con.is_connected(): con.close()

    def _get_emp_id(self):
        v = self.var_emp.get()
        if v == "All Employees": return None
        try: return int(v.split("#")[1].rstrip(")"))
        except Exception: return None

    def _load_kpis(self):
        df, dt = self._parse_dates()
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            eid = self._get_emp_id()
            cat = self.var_cat.get()

            base = ("FROM sales s "
                    "WHERE s.sale_date BETWEEN %s AND %s ")
            params = [df, dt]
            if eid: base += "AND s.emp_id=%s "; params.append(eid)

            # total sales
            cur.execute("SELECT SUM(s.grand_total) " + base, params)
            sales = cur.fetchone()[0] or 0

            # total orders
            cur.execute("SELECT COUNT(*) " + base, params)
            orders = cur.fetchone()[0] or 0

            # total profit: sum((unit_price - cost_price) * qty)
            profit_q = ("SELECT SUM((si.unit_price - p.cost_price) * si.qty) "
                        "FROM sales_items si "
                        "JOIN products p ON si.pid = p.pid "
                        "JOIN sales s ON si.invoice_no = s.invoice_no "
                        "WHERE s.sale_date BETWEEN %s AND %s ")
            pp = [df, dt]
            if cat != "All Categories":
                profit_q += "AND p.category=%s "
                pp.append(cat)
            if eid:
                profit_q += "AND s.emp_id=%s "
                pp.append(eid)
            cur.execute(profit_q, pp)
            profit = cur.fetchone()[0] or 0

            avg = sales / orders if orders else 0

            # compare vs previous same period
            delta = (dt - df).days + 1
            prev_from = df - timedelta(days=delta)
            prev_to   = df - timedelta(days=1)
            cur.execute("SELECT SUM(s.grand_total) FROM sales s "
                        "WHERE s.sale_date BETWEEN %s AND %s", (prev_from, prev_to))
            prev_sales = cur.fetchone()[0] or 0

            def pct_txt(cur_v, prev_v):
                if prev_v == 0: return "No prior data"
                p = (cur_v - prev_v) / prev_v * 100
                arrow = "▲" if p >= 0 else "▼"
                col_hint = "↑" if p >= 0 else "↓"
                return f"{arrow} {abs(p):.1f}% vs prev period"

            self._kv_sales [0].config(text=f"৳ {sales:,.0f}")
            self._kv_sales [1].config(text=pct_txt(sales, prev_sales))
            self._kv_profit[0].config(text=f"৳ {profit:,.0f}")
            self._kv_profit[1].config(text="Gross profit margin")
            self._kv_orders[0].config(text=f"{orders:,}")
            self._kv_orders[1].config(text="Invoices generated")
            self._kv_avg   [0].config(text=f"৳ {avg:,.0f}")
            self._kv_avg   [1].config(text="Per invoice average")

        except Exception as e:
            print("KPI error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_charts(self):
        df, dt = self._parse_dates()
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            eid = self._get_emp_id()

            # Daily sales — group by day
            q = ("SELECT s.sale_date, SUM(s.grand_total) "
                 "FROM sales s WHERE s.sale_date BETWEEN %s AND %s ")
            p = [df, dt]
            if eid: q += "AND s.emp_id=%s "; p.append(eid)
            q += "GROUP BY s.sale_date ORDER BY s.sale_date"
            cur.execute(q, p)
            raw = cur.fetchall()

            days_span = (dt - df).days + 1
            if days_span > 20:
                # group by week label
                from collections import defaultdict
                wk = defaultdict(float)
                for d, v in raw:
                    wd = d.isocalendar()[1] if hasattr(d, 'isocalendar') else 0
                    wk[f"W{wd}"] += float(v)
                sales_data = list(wk.items())
            else:
                sales_data = [(d.strftime("%d/%m") if hasattr(d, 'strftime') else str(d),
                               float(v)) for d, v in raw]

            # Daily profit
            pq = ("SELECT s.sale_date, "
                  "SUM((si.unit_price - p.cost_price) * si.qty) "
                  "FROM sales_items si "
                  "JOIN products p ON si.pid = p.pid "
                  "JOIN sales s ON si.invoice_no = s.invoice_no "
                  "WHERE s.sale_date BETWEEN %s AND %s ")
            pp = [df, dt]
            if eid: pq += "AND s.emp_id=%s "; pp.append(eid)
            pq += "GROUP BY s.sale_date ORDER BY s.sale_date"
            cur.execute(pq, pp)
            praw = cur.fetchall()

            if days_span > 20:
                from collections import defaultdict
                wk2 = defaultdict(float)
                for d, v in praw:
                    wd = d.isocalendar()[1] if hasattr(d, 'isocalendar') else 0
                    wk2[f"W{wd}"] += float(v) if v else 0
                profit_data = list(wk2.items())
            else:
                profit_data = [(d.strftime("%d/%m") if hasattr(d, 'strftime') else str(d),
                                float(v) if v else 0) for d, v in praw]

            # draw after widget has rendered
            self.root.after(50, lambda: self._draw_bar_chart(
                self._sales_chart, sales_data))
            self.root.after(50, lambda: self._draw_line_chart(
                self._profit_chart, profit_data))

        except Exception as e:
            print("Chart error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_trending(self):
        df, dt = self._parse_dates()
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            # top 4 products by qty sold in period
            cur.execute("""
                SELECT p.name, SUM(si.qty) as qty
                FROM sales_items si
                JOIN products p ON si.pid = p.pid
                JOIN sales s ON si.invoice_no = s.invoice_no
                WHERE s.sale_date BETWEEN %s AND %s
                GROUP BY p.pid, p.name
                ORDER BY qty DESC LIMIT 4
            """, (df, dt))
            top = cur.fetchall()

            # bottom 2
            cur.execute("""
                SELECT p.name, SUM(si.qty) as qty
                FROM sales_items si
                JOIN products p ON si.pid = p.pid
                JOIN sales s ON si.invoice_no = s.invoice_no
                WHERE s.sale_date BETWEEN %s AND %s
                GROUP BY p.pid, p.name
                ORDER BY qty ASC LIMIT 2
            """, (df, dt))
            bot = cur.fetchall()

            # rebuild trend frame
            for w in self._trend_frame.winfo_children():
                w.destroy()

            if not top:
                tk.Label(self._trend_frame, text="No sales data in this period.",
                         font=self.FN, bg=self.bg_card,
                         fg=self.txt_muted).pack(anchor="w")
                return

            max_qty = top[0][1] if top else 1
            grid = tk.Frame(self._trend_frame, bg=self.bg_card)
            grid.pack(fill=tk.X)
            for i in range(2): grid.columnconfigure(i, weight=1)

            all_items = [(n, q, True) for n, q in top] + \
                        [(n, q, False) for n, q in bot]

            for idx, (name, qty, is_top) in enumerate(all_items[:4]):
                r, c = divmod(idx, 2)
                pct  = int(qty / max_qty * 100) if max_qty else 0
                bg   = "#ECFDF5" if is_top else "#FFF1F2"
                fg   = self.green if is_top else self.red
                arrow= "↑" if is_top else "↓"
                sign = "+" if is_top else "-"

                cell = tk.Frame(grid, bg=bg,
                                highlightbackground="#E5E7EB",
                                highlightthickness=1)
                cell.grid(row=r, column=c, sticky="nsew",
                          padx=(0 if c == 0 else 6, 0),
                          pady=(0 if r == 0 else 6, 0))

                tf = tk.Frame(cell, bg=bg)
                tf.pack(fill=tk.X, padx=10, pady=8)
                tk.Label(tf, text=name[:22], font=self.FNB,
                         bg=bg, fg=self.txt_dark).pack(side=tk.LEFT)
                tk.Label(tf, text=f"{arrow} {sign}{pct}%",
                         font=("Segoe UI", 10, "bold"),
                         bg=bg, fg=fg).pack(side=tk.RIGHT)
                tk.Label(cell, text=f"{qty} units sold",
                         font=self.FS, bg=bg, fg=self.txt_muted
                         ).pack(anchor="w", padx=10, pady=(0, 8))

        except Exception as e:
            print("Trending error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_low_stock(self):
        for w in self._stock_frame.winfo_children():
            w.destroy()
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT name, stock, low_stock_alert
                FROM products
                WHERE stock <= low_stock_alert AND status='Active'
                ORDER BY stock ASC LIMIT 8
            """)
            rows = cur.fetchall()

            if not rows:
                tk.Label(self._stock_frame, text="✅  All stock levels are healthy!",
                         font=self.FN, bg=self.bg_card,
                         fg=self.green).pack(anchor="w", pady=8)
                return

            for i, (name, stock, alert) in enumerate(rows):
                urgency = stock == 0
                bg = "#FFF1F2" if urgency else "#FFF7ED"
                fg = self.red   if urgency else self.orange
                lbl = "Out of Stock" if urgency else f"Only {stock} left"

                row = tk.Frame(self._stock_frame, bg=bg,
                               highlightbackground="#FCA5A5" if urgency else "#FDE68A",
                               highlightthickness=1)
                row.pack(fill=tk.X, pady=(0 if i == 0 else 4, 0))
                rf = tk.Frame(row, bg=bg)
                rf.pack(fill=tk.X, padx=10, pady=7)
                tk.Label(rf, text=name[:26], font=self.FNB,
                         bg=bg, fg=self.txt_dark).pack(side=tk.LEFT)
                tk.Label(rf, text=lbl, font=("Segoe UI", 9, "bold"),
                         bg=bg, fg=fg).pack(side=tk.RIGHT)

        except Exception as e:
            print("Low stock error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_table(self):
        df, dt = self._parse_dates()
        cat    = self.var_cat.get()
        eid    = self._get_emp_id()
        con    = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            q = """
                SELECT p.name, p.category,
                       SUM(si.qty)                                  AS qty_sold,
                       SUM(si.qty * si.unit_price)                  AS revenue,
                       SUM((si.unit_price - p.cost_price) * si.qty) AS profit
                FROM sales_items si
                JOIN products p ON si.pid = p.pid
                JOIN sales s    ON si.invoice_no = s.invoice_no
                WHERE s.sale_date BETWEEN %s AND %s
            """
            params = [df, dt]
            if cat != "All Categories":
                q += " AND p.category=%s "; params.append(cat)
            if eid:
                q += " AND s.emp_id=%s "; params.append(eid)
            q += " GROUP BY p.pid, p.name, p.category ORDER BY revenue DESC"
            cur.execute(q, params)
            self._rows_all = cur.fetchall()
            self._page = 0
            self._render_table_page()
        except Exception as e:
            print("Table error:", e)
        finally:
            if con.is_connected(): con.close()

    def _build_ai_tip(self):
        df, dt = self._parse_dates()
        con = db_config.get_db_connection()
        if not con: return
        tips = []
        try:
            cur = con.cursor()
            # fast mover
            cur.execute("""
                SELECT p.name, SUM(si.qty) AS q
                FROM sales_items si JOIN products p ON si.pid=p.pid
                JOIN sales s ON si.invoice_no=s.invoice_no
                WHERE s.sale_date BETWEEN %s AND %s
                GROUP BY p.pid ORDER BY q DESC LIMIT 1
            """, (df, dt))
            top = cur.fetchone()
            if top:
                tips.append(f'🔺  {top[0]}  is your best-seller with {top[1]} units sold. Ensure adequate stock.')

            # critical stock
            cur.execute("""
                SELECT name FROM products
                WHERE stock <= low_stock_alert AND status='Active'
                ORDER BY stock ASC LIMIT 2
            """)
            ls = [r[0] for r in cur.fetchall()]
            if ls:
                tips.append(f"⚠️  Low stock detected: {', '.join(ls)}. Consider restocking soon.")

            # category top
            cur.execute("""
                SELECT p.category, SUM(s.grand_total) as rev
                FROM sales s JOIN sales_items si ON s.invoice_no=si.invoice_no
                JOIN products p ON si.pid=p.pid
                WHERE s.sale_date BETWEEN %s AND %s
                GROUP BY p.category ORDER BY rev DESC LIMIT 1
            """, (df, dt))
            tc = cur.fetchone()
            if tc:
                tips.append(f'📦  {tc[0]}  is your top-revenue category (৳{float(tc[1]):,.0f}).')

        except Exception: pass
        finally:
            if con.is_connected(): con.close()

        if tips:
            self._ai_lbl.config(text="  •  ".join(tips))
        else:
            self._ai_lbl.config(text="No significant trends detected for the selected period.")

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _filter_table(self):
        q = self.search_rpt.get().strip().lower()
        if q == "search products in report…": q = ""
        self._rows_all_filtered = [
            r for r in self._rows_all
            if q in r[0].lower() or q in (r[1] or "").lower()
        ] if q else self._rows_all
        self._page = 0
        self._render_table_page(filtered=True)

    def _render_table_page(self, filtered=False):
        data = getattr(self, "_rows_all_filtered", self._rows_all) \
               if filtered else self._rows_all
        self._rows_all_filtered = data

        self._rpt_tree.delete(*self._rpt_tree.get_children())
        total = len(data)
        total_pages = max(1, math.ceil(total / self._page_size))
        start = self._page * self._page_size
        page_data = data[start: start + self._page_size]

        for i, row in enumerate(page_data):
            name, cat, qty, rev, profit = row
            cat    = cat or "—"
            rev    = float(rev)    if rev    else 0
            profit = float(profit) if profit else 0
            p_str  = f"+ ৳ {profit:,.0f}" if profit >= 0 else f"- ৳ {abs(profit):,.0f}"
            tag    = ("pos" if profit >= 0 else "neg",
                      "even" if i % 2 == 0 else "odd")
            self._rpt_tree.insert("", tk.END,
                values=(name, cat, f"{int(qty):,}",
                        f"৳ {rev:,.0f}", p_str),
                tags=tag)

        self._page_lbl.config(text=f"Page {self._page + 1} / {total_pages}")
        self._btn_prev.config(state=tk.NORMAL if self._page > 0 else tk.DISABLED)
        self._btn_next.config(
            state=tk.NORMAL if self._page < total_pages - 1 else tk.DISABLED)

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_table_page()

    def _next_page(self):
        total = len(getattr(self, "_rows_all_filtered", self._rows_all))
        if (self._page + 1) * self._page_size < total:
            self._page += 1
            self._render_table_page()

    def _sort_table(self, col):
        idx = {"name": 0, "category": 1, "qty_sold": 2,
               "revenue": 3, "profit": 4}[col]
        self._rows_all.sort(key=lambda r: r[idx] or 0,
                            reverse=not getattr(self, "_sort_rev", False))
        self._sort_rev = not getattr(self, "_sort_rev", False)
        self._rows_all_filtered = self._rows_all
        self._render_table_page()

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT
    # ─────────────────────────────────────────────────────────────────────────
    def _export_csv(self):
        if not CSV_OK:
            messagebox.showerror("Error", "csv module not available."); return
        from tkinter import filedialog
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Save Excel/CSV Report")
        if not fp: return
        try:
            with open(fp, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Product Name","Category","Qty Sold","Revenue","Net Profit"])
                for row in self._rows_all:
                    n, cat, qty, rev, profit = row
                    w.writerow([n, cat or "—", int(qty or 0),
                                f"{float(rev or 0):.2f}",
                                f"{float(profit or 0):.2f}"])
            messagebox.showinfo("Exported", f"Report saved to:\n{fp}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_pdf(self):
        messagebox.showinfo("Export PDF",
            "PDF export requires the 'reportlab' library.\n"
            "Install via:  pip install reportlab\n\n"
            "For now, use Export Excel and convert via your spreadsheet app.")

    def _print_report(self):
        messagebox.showinfo("Print",
            "Use Export Excel or PDF, then print from the generated file.")

    # ─────────────────────────────────────────────────────────────────────────
    # BUTTON HELPER
    # ─────────────────────────────────────────────────────────────────────────
    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.FNB, bg=bg, fg=fg,
                  relief="flat", bd=0, cursor="hand2",
                  padx=16, pady=7,
                  activebackground=bg, activeforeground=fg)
        if border:
            kw["highlightbackground"] = self.bd
            kw["highlightthickness"]  = 1
        if cmd: kw["command"] = cmd
        return tk.Button(parent, **kw)


# ── standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("IMS – Reports & Analytics")
    root.state("zoomed")
    app = ReportsClass(root)
    root.mainloop()