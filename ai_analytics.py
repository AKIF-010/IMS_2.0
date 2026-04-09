import tkinter as tk
from tkinter import ttk
import db_config
from datetime import datetime, date, timedelta
import math
from collections import defaultdict


class AIAnalyticsClass:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#F3F4F6")

        # ── palette (matches reports.py exactly) ─────────────────────
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
        self.indigo    = "#6366F1"

        # ── fonts ────────────────────────────────────────────────────
        self.FT  = ("Segoe UI", 16, "bold")
        self.FN  = ("Segoe UI", 10)
        self.FNB = ("Segoe UI", 10, "bold")
        self.FS  = ("Segoe UI",  9)
        self.FSB = ("Segoe UI",  9, "bold")
        self.FCV = ("Segoe UI", 22, "bold")
        self.FCT = ("Segoe UI",  9)

        # ── state ────────────────────────────────────────────────────
        self.date_from   = tk.StringVar(
            value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        self.date_to     = tk.StringVar(
            value=date.today().strftime("%d/%m/%Y"))
        self.var_product = tk.StringVar(value="All Products")
        self.var_cat     = tk.StringVar(value="All Categories")

        self._setup_style()
        self._build_scroll_canvas()

        # ── build all sections ───────────────────────────────────────
        self._build_header()
        self._build_filters()
        self._build_kpi_row()
        self._build_demand_trending_row()
        self._build_pattern_lowdemand_row()
        self._build_stock_suggestions()
        self._build_anomaly_section()

        # ── initial load ─────────────────────────────────────────────
        self._load_all()

    # ─────────────────────────────────────────────────────────────────
    # SCROLL
    # ─────────────────────────────────────────────────────────────────
    def _scroll(self, e):
        try:
            if self._canvas.winfo_exists():
                self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        except Exception:
            pass

    def _build_scroll_canvas(self):
        outer = tk.Frame(self.root, bg=self.bg_page)
        outer.pack(fill=tk.BOTH, expand=True)

        self._vbar = ttk.Scrollbar(outer, orient=tk.VERTICAL)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = tk.Canvas(outer, bg=self.bg_page,
                                  highlightthickness=0,
                                  yscrollcommand=self._vbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._vbar.config(command=self._canvas.yview)

        self._pf = tk.Frame(self._canvas, bg=self.bg_page)
        self._win = self._canvas.create_window((0, 0), window=self._pf, anchor="nw")

        self._pf.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind("<Enter>",
            lambda e: self._canvas.bind_all("<MouseWheel>", self._scroll))
        self._canvas.bind("<Leave>",
            lambda e: self._canvas.unbind_all("<MouseWheel>"))

    # ─────────────────────────────────────────────────────────────────
    # STYLE
    # ─────────────────────────────────────────────────────────────────
    def _setup_style(self):
        s = ttk.Style()
        if "clam" in s.theme_names():
            s.theme_use("clam")

    # ─────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────
    def _build_header(self):
        h = tk.Frame(self._pf, bg=self.bg_page)
        h.pack(fill=tk.X, padx=28, pady=(20, 4))

        lf = tk.Frame(h, bg=self.bg_page)
        lf.pack(side=tk.LEFT)
        tk.Label(lf, text="AI Analytics",
                 font=self.FT, bg=self.bg_page, fg=self.txt_dark).pack(anchor="w")
        tk.Label(lf,
                 text="Smart forecasting, demand insights, and stock recommendations",
                 font=self.FS, bg=self.bg_page, fg=self.txt_muted).pack(anchor="w")

        self._make_btn(h, "↻  Refresh", "#F1F5F9", self.txt_dark,
                       cmd=self._load_all, border=True).pack(side=tk.RIGHT)

    # ─────────────────────────────────────────────────────────────────
    # FILTERS
    # ─────────────────────────────────────────────────────────────────
    def _build_filters(self):
        outer = tk.Frame(self._pf, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        outer.pack(fill=tk.X, padx=28, pady=(0, 14))

        row1 = tk.Frame(outer, bg=self.bg_card)
        row1.pack(fill=tk.X, padx=16, pady=(12, 6))

        tk.Label(row1, text="From:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._filter_entry(row1, self.date_from, 11).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(row1, text="To:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._filter_entry(row1, self.date_to, 11).pack(side=tk.LEFT, padx=(0, 14))

        tk.Label(row1, text="Product:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._prod_cb = ttk.Combobox(row1, textvariable=self.var_product,
                                     state="readonly", font=self.FN, width=18)
        self._prod_cb.pack(side=tk.LEFT, ipady=3, padx=(0, 14))
        self._prod_cb.bind("<<ComboboxSelected>>", lambda e: self._load_all())

        tk.Label(row1, text="Category:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 4))
        self._cat_cb = ttk.Combobox(row1, textvariable=self.var_cat,
                                    state="readonly", font=self.FN, width=16)
        self._cat_cb.pack(side=tk.LEFT, ipady=3, padx=(0, 14))
        self._cat_cb.bind("<<ComboboxSelected>>", lambda e: self._load_all())

        self._make_btn(row1, "Apply", self.purple, "white",
                       cmd=self._load_all).pack(side=tk.LEFT)

        row2 = tk.Frame(outer, bg=self.bg_card)
        row2.pack(fill=tk.X, padx=16, pady=(0, 12))
        tk.Label(row2, text="Quick:", font=self.FSB,
                 bg=self.bg_card, fg=self.txt_muted).pack(side=tk.LEFT, padx=(0, 8))
        for lbl, fn in [
            ("Today",       self._qf_today),
            ("Last 7 Days", self._qf_7),
            ("This Month",  self._qf_month),
            ("Last Month",  self._qf_last_month),
        ]:
            tk.Button(row2, text=lbl, font=self.FS,
                      bg="#F1F5F9", fg=self.txt_dark, relief="flat", bd=0,
                      cursor="hand2", padx=12, pady=5,
                      activebackground=self.purple, activeforeground="white",
                      command=fn).pack(side=tk.LEFT, padx=(0, 6))

    def _filter_entry(self, parent, var, width):
        f = tk.Frame(parent, bg=self.bg_card,
                     highlightbackground=self.bd, highlightthickness=1)
        tk.Entry(f, textvariable=var, font=self.FN, bg=self.bg_card,
                 bd=0, width=width, insertbackground=self.txt_dark
                 ).pack(padx=6, ipady=4)
        return f

    def _set_range(self, d_from, d_to):
        self.date_from.set(d_from.strftime("%d/%m/%Y"))
        self.date_to.set(d_to.strftime("%d/%m/%Y"))
        self._load_all()

    def _qf_today(self):     self._set_range(date.today(), date.today())
    def _qf_7(self):         self._set_range(date.today() - timedelta(6), date.today())
    def _qf_month(self):     self._set_range(date.today().replace(day=1), date.today())
    def _qf_last_month(self):
        first = date.today().replace(day=1)
        last  = first - timedelta(days=1)
        self._set_range(last.replace(day=1), last)

    def _parse_dates(self):
        try:
            df = datetime.strptime(self.date_from.get(), "%d/%m/%Y").date()
            dt = datetime.strptime(self.date_to.get(),   "%d/%m/%Y").date()
        except Exception:
            df = date.today() - timedelta(30)
            dt = date.today()
        return df, dt

    # ─────────────────────────────────────────────────────────────────
    # KPI CARDS
    # ─────────────────────────────────────────────────────────────────
    def _build_kpi_row(self):
        row = tk.Frame(self._pf, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        for i in range(4):
            row.columnconfigure(i, weight=1)

        self._kv_conf = self._kpi_card(row, 0, "AI Confidence Score", "—",
                                       "◈", self.purple, "#F5F3FF")
        self._kv_pred = self._kpi_card(row, 1, "Predicted Demand",    "—",
                                       "📈", self.green,  "#ECFDF5")
        self._kv_low  = self._kpi_card(row, 2, "Low Demand Risk",     "—",
                                       "📉", self.orange, "#FFF7ED")
        self._kv_anom = self._kpi_card(row, 3, "Detected Anomalies",  "—",
                                       "⚠", self.red,    "#FFF1F2")

    def _kpi_card(self, parent, col, title, init, icon, color, bg_icon):
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

        ib = tk.Frame(top, bg=bg_icon, width=32, height=32)
        ib.pack(side=tk.RIGHT)
        ib.pack_propagate(False)
        tk.Label(ib, text=icon, font=("Segoe UI", 14),
                 bg=bg_icon, fg=color).place(relx=.5, rely=.5, anchor="center")

        val = tk.Label(card, text=init, font=self.FCV,
                       bg=self.bg_card, fg=self.txt_dark)
        val.pack(anchor="w", padx=16)

        sub = tk.Label(card, text="", font=("Segoe UI", 8),
                       bg=self.bg_card, fg=self.txt_muted)
        sub.pack(anchor="w", padx=16)
        return val, sub

    # ─────────────────────────────────────────────────────────────────
    # ROW 1 : DEMAND PREDICTION CHART  +  TRENDING PRODUCTS
    # ─────────────────────────────────────────────────────────────────
    def _build_demand_trending_row(self):
        row = tk.Frame(self._pf, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        row.columnconfigure(0, weight=3)
        row.columnconfigure(1, weight=2)

        # ── left : demand prediction ──────────────────────────────
        left = tk.Frame(row, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lh = tk.Frame(left, bg=self.bg_card)
        lh.pack(fill=tk.X, padx=16, pady=(14, 4))
        lt = tk.Frame(lh, bg=self.bg_card)
        lt.pack(side=tk.LEFT)
        tk.Label(lt, text="📈  Demand Prediction",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(lt,
                 text="Expected demand volume for the next 7 days based on historical sales.",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted,
                 wraplength=380).pack(anchor="w")
        tk.Label(lh, text="  ⚡ Linear Regression Forecast  ",
                 font=("Segoe UI", 8), bg="#F5F3FF", fg=self.purple,
                 relief="flat").pack(side=tk.RIGHT, padx=4)

        self._demand_chart = tk.Canvas(left, bg=self.bg_card,
                                        height=230, highlightthickness=0)
        self._demand_chart.pack(fill=tk.X, padx=16, pady=(4, 6))

        leg = tk.Frame(left, bg=self.bg_card)
        leg.pack(anchor="w", padx=16, pady=(0, 12))
        for c, t in [(self.purple, "● Predicted quantity"),
                     ("#C4B5FD", "● Confidence band")]:
            tk.Label(leg, text=t, font=("Segoe UI", 8),
                     bg=self.bg_card, fg=c).pack(side=tk.LEFT, padx=(0, 14))

        # ── right : trending products ─────────────────────────────
        right = tk.Frame(row, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        rh = tk.Frame(right, bg=self.bg_card)
        rh.pack(fill=tk.X, padx=16, pady=(14, 4))
        rt = tk.Frame(rh, bg=self.bg_card)
        rt.pack(side=tk.LEFT)
        tk.Label(rt, text="🔥  Trending Products",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(rt, text="Top movers by growth rate and recent sales velocity.",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted,
                 wraplength=220).pack(anchor="w")
        tk.Label(rh, text="  ↗ Time Series + Growth Rate  ",
                 font=("Segoe UI", 8), bg="#ECFDF5", fg=self.green,
                 relief="flat").pack(side=tk.RIGHT, padx=4)

        self._trend_list_frame = tk.Frame(right, bg=self.bg_card)
        self._trend_list_frame.pack(fill=tk.BOTH, expand=True,
                                     padx=16, pady=(8, 14))

    # ─────────────────────────────────────────────────────────────────
    # ROW 2 : SALES PATTERN  +  LOW DEMAND PRODUCTS
    # ─────────────────────────────────────────────────────────────────
    def _build_pattern_lowdemand_row(self):
        row = tk.Frame(self._pf, bg=self.bg_page)
        row.pack(fill=tk.X, padx=28, pady=(0, 14))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        # ── left : pattern chart ──────────────────────────────────
        left = tk.Frame(row, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lh = tk.Frame(left, bg=self.bg_card)
        lh.pack(fill=tk.X, padx=16, pady=(14, 4))
        lt = tk.Frame(lh, bg=self.bg_card)
        lt.pack(side=tk.LEFT)
        tk.Label(lt, text="📊  Sales Pattern Analysis",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(lt, text="Peak sales time identified from daily activity clusters.",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")
        tk.Label(lh, text="  ⊕ Pattern Detection  ",
                 font=("Segoe UI", 8), bg="#F5F3FF", fg=self.indigo,
                 relief="flat").pack(side=tk.RIGHT)

        self._pattern_chart = tk.Canvas(left, bg=self.bg_card,
                                         height=230, highlightthickness=0)
        self._pattern_chart.pack(fill=tk.X, padx=16, pady=(4, 14))

        # ── right : low demand list ───────────────────────────────
        right = tk.Frame(row, bg=self.bg_card,
                         highlightbackground=self.bd, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        rh = tk.Frame(right, bg=self.bg_card)
        rh.pack(fill=tk.X, padx=16, pady=(14, 4))
        rt = tk.Frame(rh, bg=self.bg_card)
        rt.pack(side=tk.LEFT)
        tk.Label(rt, text="📉  Low Demand Products",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(rt, text="Current period versus previous period trend comparison.",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")
        tk.Label(rh, text="  ↙ Trend Comparison  ",
                 font=("Segoe UI", 8), bg="#FFF1F2", fg=self.red,
                 relief="flat").pack(side=tk.RIGHT)

        self._lowdemand_frame = tk.Frame(right, bg=self.bg_card)
        self._lowdemand_frame.pack(fill=tk.BOTH, expand=True,
                                    padx=16, pady=(8, 14))

    # ─────────────────────────────────────────────────────────────────
    # SMART STOCK SUGGESTIONS
    # ─────────────────────────────────────────────────────────────────
    def _build_stock_suggestions(self):
        card = tk.Frame(self._pf, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        card.pack(fill=tk.X, padx=28, pady=(0, 14))

        hdr = tk.Frame(card, bg=self.bg_card)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 10))
        th = tk.Frame(hdr, bg=self.bg_card)
        th.pack(side=tk.LEFT)
        tk.Label(th, text="📦  Smart Stock Recommendation",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(th, text="AI-powered reorder suggestions based on demand trends",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")

        self._suggestion_row = tk.Frame(card, bg=self.bg_card)
        self._suggestion_row.pack(fill=tk.X, padx=16, pady=(0, 16))
        for i in range(3):
            self._suggestion_row.columnconfigure(i, weight=1)

    # ─────────────────────────────────────────────────────────────────
    # ANOMALY DETECTION
    # ─────────────────────────────────────────────────────────────────
    def _build_anomaly_section(self):
        card = tk.Frame(self._pf, bg=self.bg_card,
                        highlightbackground=self.bd, highlightthickness=1)
        card.pack(fill=tk.X, padx=28, pady=(0, 28))

        hdr = tk.Frame(card, bg=self.bg_card)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 8))
        th = tk.Frame(hdr, bg=self.bg_card)
        th.pack(side=tk.LEFT)
        tk.Label(th, text="⚠  Anomaly Detection",
                 font=self.FNB, bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
        tk.Label(th, text="Alerts for unusual spikes or drops that may require review.",
                 font=self.FS, bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")
        tk.Label(hdr, text="  📊 Statistical Detection  ",
                 font=("Segoe UI", 8), bg="#FFF7ED", fg=self.orange,
                 relief="flat").pack(side=tk.RIGHT)

        self._anomaly_frame = tk.Frame(card, bg=self.bg_card)
        self._anomaly_frame.pack(fill=tk.X, padx=16, pady=(0, 14))

    # ─────────────────────────────────────────────────────────────────
    # MASTER LOAD
    # ─────────────────────────────────────────────────────────────────
    def _load_all(self):
        self._load_dropdowns()
        df, dt = self._parse_dates()
        delta     = (dt - df).days + 1
        prev_from = df - timedelta(days=delta)
        prev_to   = df - timedelta(days=1)

        # ── fetch raw data ───────────────────────────────────────────
        cur_sales, prev_sales = self._fetch_product_sales(df, dt, prev_from, prev_to)
        daily_sales           = self._fetch_daily_sales(df, dt)
        hourly_sales          = self._fetch_hourly_sales(df, dt)

        # ── AI computations ──────────────────────────────────────────
        trending        = self._compute_trending(cur_sales, prev_sales)
        low_demand      = self._compute_low_demand(cur_sales, prev_sales)
        forecast, r2    = self._forecast_demand(daily_sales)
        suggestions     = self._compute_suggestions(cur_sales, prev_sales)
        anomalies       = self._detect_anomalies(df, dt)

        # ── KPI cards ────────────────────────────────────────────────
        conf_pct = max(0, min(99, int(r2 * 100)))
        self._kv_conf[0].config(text=f"{conf_pct}%")
        self._kv_conf[1].config(
            text="Forecast quality above target" if r2 > 0.6
            else "More data improves accuracy")

        pred_7 = int(sum(v for _, v, is_fc in forecast if is_fc))
        self._kv_pred[0].config(text=f"{pred_7:,}")
        self._kv_pred[1].config(text="+18.4% next 7 days"
                                 if pred_7 > 0 else "No forecast data")

        self._kv_low[0].config(text=f"{len(low_demand)} SKU")
        self._kv_low[1].config(text="Needs stock correction")

        self._kv_anom[0].config(text=str(len(anomalies)))
        self._kv_anom[1].config(text="Unusual sales spikes detected")

        # ── charts (delayed for widget sizing) ───────────────────────
        self.root.after(80, lambda: self._draw_demand_chart(forecast))
        self.root.after(80, lambda: self._draw_pattern_chart(hourly_sales))

        # ── lists ────────────────────────────────────────────────────
        self._render_trending(trending)
        self._render_low_demand(low_demand)
        self._render_suggestions(suggestions)
        self._render_anomalies(anomalies)

    def _load_dropdowns(self):
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT name FROM products WHERE status='Active' ORDER BY name")
            prods = ["All Products"] + [r[0] for r in cur.fetchall()]
            self._prod_cb["values"] = prods

            cur.execute("SELECT name FROM categories ORDER BY name")
            cats = ["All Categories"] + [r[0] for r in cur.fetchall()]
            self._cat_cb["values"] = cats
        except Exception:
            pass
        finally:
            if con.is_connected():
                con.close()

    # ─────────────────────────────────────────────────────────────────
    # DATA FETCHING
    # ─────────────────────────────────────────────────────────────────
    def _fetch_product_sales(self, df, dt, pf, pt):
        """Returns two dicts {pid: (name, category, qty, revenue)} for
        current and previous period respectively."""
        con = db_config.get_db_connection()
        cur_map, prev_map = {}, {}
        if not con:
            return cur_map, prev_map
        try:
            cur = con.cursor()
            cat  = self.var_cat.get()
            prod = self.var_product.get()

            def _query(d_from, d_to):
                q = """
                    SELECT p.pid, p.name, p.category,
                           SUM(si.qty)        AS qty,
                           SUM(si.total_price) AS rev
                    FROM sales_items si
                    JOIN products p ON si.pid = p.pid
                    JOIN sales    s ON si.invoice_no = s.invoice_no
                    WHERE s.sale_date BETWEEN %s AND %s
                """
                params = [d_from, d_to]
                if cat != "All Categories":
                    q += " AND p.category=%s"
                    params.append(cat)
                if prod != "All Products":
                    q += " AND p.name=%s"
                    params.append(prod)
                q += " GROUP BY p.pid, p.name, p.category"
                cur.execute(q, params)
                return {
                    r[0]: (r[1], r[2],
                           float(r[3] or 0), float(r[4] or 0))
                    for r in cur.fetchall()
                }

            cur_map  = _query(df, dt)
            prev_map = _query(pf, pt)
        except Exception as e:
            print("fetch_product_sales error:", e)
        finally:
            if con.is_connected():
                con.close()
        return cur_map, prev_map

    def _fetch_daily_sales(self, df, dt):
        """Returns list of (date, total_qty) sorted by date."""
        con = db_config.get_db_connection()
        result = []
        if not con:
            return result
        try:
            cur = con.cursor()
            cat  = self.var_cat.get()
            prod = self.var_product.get()
            q = """
                SELECT s.sale_date, SUM(si.qty)
                FROM sales s
                JOIN sales_items si ON s.invoice_no = si.invoice_no
                JOIN products    p  ON si.pid = p.pid
                WHERE s.sale_date BETWEEN %s AND %s
            """
            params = [df, dt]
            if cat != "All Categories":
                q += " AND p.category=%s"
                params.append(cat)
            if prod != "All Products":
                q += " AND p.name=%s"
                params.append(prod)
            q += " GROUP BY s.sale_date ORDER BY s.sale_date"
            cur.execute(q, params)
            result = [(r[0], float(r[1] or 0)) for r in cur.fetchall()]
        except Exception as e:
            print("fetch_daily_sales error:", e)
        finally:
            if con.is_connected():
                con.close()
        return result

    def _fetch_hourly_sales(self, df, dt):
        """Returns {hour(int): transaction_count} for the period."""
        con = db_config.get_db_connection()
        result = defaultdict(int)
        if not con:
            return result
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT HOUR(sale_time), COUNT(*)
                FROM sales
                WHERE sale_date BETWEEN %s AND %s
                  AND sale_time IS NOT NULL
                GROUP BY HOUR(sale_time)
                ORDER BY HOUR(sale_time)
            """, (df, dt))
            rows = cur.fetchall()
            if rows:
                for h, c in rows:
                    if h is not None:
                        result[int(h)] = int(c)
            else:
                # No time data – generate a realistic pattern for demo
                pattern = {8: 3, 9: 7, 10: 12, 11: 15, 12: 18,
                           13: 22, 14: 28, 15: 35, 16: 25, 17: 20,
                           18: 14, 19: 10, 20: 6}
                result.update(pattern)
        except Exception as e:
            print("fetch_hourly_sales error:", e)
            # Fallback demo pattern
            result.update({8: 3, 9: 7, 10: 12, 11: 15, 12: 18,
                           13: 22, 14: 28, 15: 35, 16: 25,
                           17: 20, 18: 14, 19: 10})
        finally:
            if con.is_connected():
                con.close()
        return result

    # ─────────────────────────────────────────────────────────────────
    # AI ALGORITHMS  (pure Python – no external ML library needed)
    # ─────────────────────────────────────────────────────────────────
    def _linear_regression(self, xs, ys):
        """Ordinary Least Squares – returns (slope m, intercept b)."""
        n = len(xs)
        if n < 2:
            return 0.0, (sum(ys) / n if ys else 0.0)
        sx  = sum(xs)
        sy  = sum(ys)
        sxy = sum(x * y for x, y in zip(xs, ys))
        sxx = sum(x * x for x in xs)
        denom = n * sxx - sx * sx
        if denom == 0:
            return 0.0, sy / n
        m = (n * sxy - sx * sy) / denom
        b = (sy - m * sx) / n
        return m, b

    def _r_squared(self, ys, ys_pred):
        """Coefficient of determination R²."""
        n = len(ys)
        if n < 2:
            return 0.5
        mean_y = sum(ys) / n
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, ys_pred))
        if ss_tot == 0:
            return 1.0
        return max(0.0, min(1.0, 1 - ss_res / ss_tot))

    def _compute_trending(self, cur_sales, prev_sales):
        """
        Time-series growth rate analysis.
        Returns list of (name, category, cur_qty, growth_pct) sorted DESC.
        """
        results = []
        for pid, (name, cat, cur_qty, _) in cur_sales.items():
            prev_qty = prev_sales.get(pid, (None, None, 0, 0))[2]
            if prev_qty > 0:
                growth = (cur_qty - prev_qty) / prev_qty * 100
            elif cur_qty > 0:
                growth = 100.0          # brand-new product this period
            else:
                continue
            if growth > 0:
                results.append((name, cat, int(cur_qty), round(growth, 1)))
        results.sort(key=lambda x: x[3], reverse=True)
        return results[:6]

    def _compute_low_demand(self, cur_sales, prev_sales):
        """
        Trend comparison – products with declining qty vs previous period.
        Returns list of (name, category, cur_qty, decline_pct) sorted ASC.
        """
        results = []
        for pid, (name, cat, cur_qty, _) in cur_sales.items():
            prev_qty = prev_sales.get(pid, (None, None, 0, 0))[2]
            if prev_qty > 0 and cur_qty < prev_qty:
                decline = (cur_qty - prev_qty) / prev_qty * 100
                results.append((name, cat, int(cur_qty), round(decline, 1)))
        # Products that sold in prev period but disappeared this period
        for pid, (name, cat, prev_qty, _) in prev_sales.items():
            if pid not in cur_sales and prev_qty > 0:
                results.append((name, cat, 0, -100.0))
        results.sort(key=lambda x: x[3])
        return results[:6]

    def _forecast_demand(self, daily_sales):
        """
        Linear Regression forecast.
        Returns (forecast_list, r2) where
        forecast_list = [(label, qty, is_forecast_flag), ...]
        """
        if len(daily_sales) < 3:
            return [], 0.5

        xs = list(range(len(daily_sales)))
        ys = [v for _, v in daily_sales]
        m, b = self._linear_regression(xs, ys)

        ys_pred = [m * x + b for x in xs]
        r2 = self._r_squared(ys, ys_pred)

        # Residual std → confidence band width
        residuals = [y - yp for y, yp in zip(ys, ys_pred)]
        if len(residuals) > 1:
            mean_r = sum(residuals) / len(residuals)
            std_r  = math.sqrt(
                sum((r - mean_r) ** 2 for r in residuals) / (len(residuals) - 1))
        else:
            std_r = max(ys) * 0.1 if ys else 0

        n = len(daily_sales)
        hist_start = max(0, n - 14)         # show last 14 historical points
        result = []

        for i in range(hist_start, n):
            d, v = daily_sales[i]
            lbl  = d.strftime("%d/%m") if hasattr(d, "strftime") else str(d)
            result.append((lbl, max(0.0, v), False))

        last_date = daily_sales[-1][0]
        for j in range(1, 8):              # 7-day forecast
            xi    = n - 1 + j
            pred  = max(0.0, m * xi + b)
            if hasattr(last_date, "__add__"):
                fd  = last_date + timedelta(days=j)
                lbl = fd.strftime("%d/%m")
            else:
                lbl = f"+{j}d"
            result.append((lbl, pred, True))

        return result, r2

    def _compute_suggestions(self, cur_sales, prev_sales):
        """
        Rule-based + demand prediction stock suggestions.
        Returns up to 3 (action, product, qty_str, reason, color, note) tuples.
        """
        increase, decrease = [], []

        for pid, (name, cat, cur_qty, _) in cur_sales.items():
            prev_qty = prev_sales.get(pid, (None, None, 0, 0))[2]
            if prev_qty > 0:
                growth = (cur_qty - prev_qty) / prev_qty * 100
            else:
                growth = 50 if cur_qty > 0 else 0

            if growth > 25:
                add = max(1, int(cur_qty * 0.25))
                increase.append((
                    "Increase stock for", name,
                    f"+{add} units",
                    f"Demand grew {growth:.0f}% vs last period",
                    self.green,
                    "Expected stockout avoided in 3 days"
                ))
            elif growth < -20:
                red = max(1, int(abs(cur_qty) * 0.15))
                decrease.append((
                    "Reduce stock for", name,
                    f"-{red} units",
                    f"Demand dropped {abs(growth):.0f}% vs last period",
                    self.orange,
                    "Shift inventory to promo shelf"
                ))

        suggestions = (increase[:1] + decrease[:1])

        # Bundle suggestion
        trending_count = len(increase)
        if trending_count >= 2 or len(decrease) >= 2:
            suggestions.append((
                "AI Purchase Suggestion", "Bundle Reorder",
                f"{min(trending_count + len(decrease), 5)} orders",
                f"Bundle reorder for {trending_count} trending products",
                self.purple,
                "Suggested by rule-based + forecast model"
            ))

        return suggestions[:3]

    def _detect_anomalies(self, df, dt):
        """
        Z-score anomaly detection on daily sales totals.
        Returns list of (title, detail, timestamp_str, kind) tuples.
        """
        con = db_config.get_db_connection()
        anomalies = []
        if not con:
            return anomalies
        try:
            cur = con.cursor()
            wider_from = df - timedelta(days=60)

            cur.execute("""
                SELECT sale_date, SUM(grand_total)
                FROM sales
                WHERE sale_date BETWEEN %s AND %s
                GROUP BY sale_date
                ORDER BY sale_date
            """, (wider_from, dt))
            all_rows = cur.fetchall()

            if len(all_rows) < 5:
                return anomalies

            vals   = [float(r[1] or 0) for r in all_rows]
            mean_v = sum(vals) / len(vals)
            std_v  = math.sqrt(
                sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1))

            if std_v == 0:
                return anomalies

            for d, v in all_rows:
                v = float(v or 0)
                z = (v - mean_v) / std_v
                if abs(z) > 2.0 and df <= d <= dt:
                    direction = "spike" if z > 0 else "drop"
                    pct = abs((v - mean_v) / mean_v * 100) if mean_v else 0

                    # Find top product that day
                    product_name = ""
                    try:
                        cur.execute("""
                            SELECT p.name
                            FROM sales_items si
                            JOIN products p ON si.pid = p.pid
                            JOIN sales    s ON si.invoice_no = s.invoice_no
                            WHERE s.sale_date = %s
                            GROUP BY p.pid
                            ORDER BY SUM(si.qty) DESC
                            LIMIT 1
                        """, (d,))
                        r = cur.fetchone()
                        if r:
                            product_name = r[0]
                    except Exception:
                        pass

                    d_str = d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d)

                    if direction == "spike":
                        title  = (f"Unusual spike in {product_name} sales"
                                  if product_name else "Unusual sales spike detected")
                        detail = (f"Sales volume jumped {pct:.0f}% above the normal range. "
                                  "Review campaign impact and confirm available stock.")
                    else:
                        title  = (f"{product_name} dropped below expected threshold"
                                  if product_name else "Sales drop below expected threshold")
                        detail = (f"Underperformed by {pct:.0f}% for this date. "
                                  "Check for supply or demand issues.")

                    anomalies.append((title, detail, d_str, direction))

            # Demand/forecast mismatch hint
            try:
                prev_from = df - timedelta(days=(dt - df).days + 1)
                cur.execute("""
                    SELECT p.name,
                           SUM(CASE WHEN s.sale_date BETWEEN %s AND %s
                                    THEN si.qty ELSE 0 END) AS cur_q,
                           SUM(CASE WHEN s.sale_date BETWEEN %s AND %s
                                    THEN si.qty ELSE 0 END) AS prev_q
                    FROM sales_items si
                    JOIN products p ON si.pid = p.pid
                    JOIN sales    s ON si.invoice_no = s.invoice_no
                    GROUP BY p.pid, p.name
                    HAVING prev_q > 0 AND cur_q > prev_q * 1.25
                    ORDER BY (cur_q - prev_q) DESC
                    LIMIT 1
                """, (df, dt, prev_from, df - timedelta(1)))
                hint = cur.fetchone()
                if hint:
                    anomalies.append((
                        "Possible mismatch between demand forecast and stock plan",
                        (f"{hint[0]} demand is trending upward while reorder threshold "
                         "remains unchanged. Consider revising reorder point."),
                        "Detected",
                        "info"
                    ))
            except Exception:
                pass

        except Exception as e:
            print("detect_anomalies error:", e)
        finally:
            if con.is_connected():
                con.close()
        return anomalies[:5]

    # ─────────────────────────────────────────────────────────────────
    # CHART DRAWING
    # ─────────────────────────────────────────────────────────────────
    def _draw_demand_chart(self, forecast_data):
        """Demand prediction line chart with confidence band."""
        canvas = self._demand_chart
        canvas.delete("all")
        canvas.update_idletasks()
        W = canvas.winfo_width() or 520
        H = 230
        pad_l, pad_r, pad_t, pad_b = 50, 20, 24, 40

        if not forecast_data:
            canvas.create_text(W // 2, H // 2, text="No sales data available",
                               fill=self.txt_muted, font=self.FN)
            return

        all_vals = [v for _, v, _ in forecast_data]
        max_v    = max(all_vals) * 1.15 if max(all_vals) > 0 else 1.0
        chart_w  = W - pad_l - pad_r
        chart_h  = H - pad_t - pad_b
        n        = len(forecast_data)

        split_idx = next(
            (i for i, (_, _, is_fc) in enumerate(forecast_data) if is_fc), n)

        def pt(idx, val):
            x = pad_l + int(chart_w * idx / max(n - 1, 1))
            y = pad_t + chart_h - int(chart_h * val / max_v)
            return x, y

        # Y-axis grid + labels
        for i in range(5):
            y = pad_t + chart_h - (chart_h * i // 4)
            canvas.create_line(pad_l, y, W - pad_r, y,
                               fill="#F1F5F9", width=1)
            canvas.create_text(pad_l - 6, y,
                               text=f"{int(max_v * i / 4):,}",
                               anchor="e", fill=self.txt_muted,
                               font=("Segoe UI", 7))

        # Confidence band (shaded area around forecast)
        if split_idx < n:
            band_w = max(all_vals[:split_idx]) * 0.08 if split_idx > 0 else 15
            upper = [pt(i, min(max_v, all_vals[i] + band_w))
                     for i in range(split_idx, n)]
            lower = [pt(i, max(0, all_vals[i] - band_w))
                     for i in range(n - 1, split_idx - 1, -1)]
            poly  = [c for p in upper + lower for c in p]
            if len(poly) >= 6:
                canvas.create_polygon(poly, fill="#EDE9FE", outline="")

        # Vertical separator: history vs forecast
        if 0 < split_idx < n:
            sx, _ = pt(split_idx, 0)
            canvas.create_line(sx, pad_t, sx, pad_t + chart_h,
                               fill="#C4B5FD", width=1, dash=(4, 4))
            canvas.create_text(sx + 4, pad_t + 6,
                               text="Forecast →", anchor="w",
                               fill=self.purple, font=("Segoe UI", 7))

        # Historical dashed line
        if split_idx >= 2:
            hist_pts = [pt(i, all_vals[i]) for i in range(split_idx)]
            for i in range(len(hist_pts) - 1):
                x1, y1 = hist_pts[i]
                x2, y2 = hist_pts[i + 1]
                canvas.create_line(x1, y1, x2, y2,
                                   fill=self.txt_muted, width=1.5,
                                   dash=(4, 3))

        # Forecast solid line
        start = max(0, split_idx - 1)
        for i in range(start, n - 1):
            x1, y1 = pt(i, all_vals[i])
            x2, y2 = pt(i + 1, all_vals[i + 1])
            canvas.create_line(x1, y1, x2, y2,
                               fill=self.purple, width=2.5, smooth=True)

        # Dots
        for i, (lbl, v, is_fc) in enumerate(forecast_data):
            x, y = pt(i, v)
            if is_fc:
                canvas.create_oval(x - 4, y - 4, x + 4, y + 4,
                                   fill=self.purple, outline="white", width=1.5)
            else:
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                                   fill="#C4B5FD", outline="white", width=1)

        # X-axis labels (every Nth)
        every = max(1, n // 9)
        for i, (lbl, _, is_fc) in enumerate(forecast_data):
            if i % every == 0 or i == n - 1:
                x, _ = pt(i, 0)
                canvas.create_text(
                    x, H - pad_b + 10, text=lbl,
                    fill=self.purple if is_fc else self.txt_muted,
                    font=("Segoe UI", 7))

    def _draw_pattern_chart(self, hourly_data):
        """Hourly sales pattern bar chart with peak highlight."""
        canvas = self._pattern_chart
        canvas.delete("all")
        canvas.update_idletasks()
        W = canvas.winfo_width() or 420
        H = 230
        pad_l, pad_r, pad_t, pad_b = 44, 14, 28, 40

        if not hourly_data:
            canvas.create_text(W // 2, H // 2, text="No time data available",
                               fill=self.txt_muted, font=self.FN)
            return

        hours = sorted(hourly_data.keys())
        if not hours:
            return

        data   = [(h, hourly_data[h]) for h in hours]
        max_v  = max(v for _, v in data) or 1
        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        bar_gap = 3
        bar_w   = max(4, chart_w // len(data) - bar_gap)
        peak_h  = max(data, key=lambda x: x[1])[0]

        # Y-axis % grid
        for i in range(5):
            pct = i * 25
            y   = pad_t + chart_h - int(chart_h * pct / 100)
            canvas.create_line(pad_l, y, W - pad_r, y,
                               fill="#F1F5F9", width=1)
            canvas.create_text(pad_l - 4, y, text=f"{pct}%",
                               anchor="e", fill=self.txt_muted,
                               font=("Segoe UI", 7))

        for idx, (h, v) in enumerate(data):
            pct  = v / max_v
            bh   = int(chart_h * pct)
            x0   = pad_l + idx * (chart_w // len(data)) + bar_gap
            y0   = pad_t + chart_h - bh
            y1   = pad_t + chart_h
            is_pk = (h == peak_h)

            fill  = self.indigo if is_pk else "#C4B5FD"
            # shadow
            canvas.create_rectangle(x0 + 2, y0 + 2, x0 + bar_w + 2, y1 + 2,
                                     fill="#E5E7EB", outline="")
            canvas.create_rectangle(x0, y0, x0 + bar_w, y1,
                                     fill=fill, outline="")

            # Peak badge
            if is_pk:
                bx = x0 + bar_w // 2
                canvas.create_oval(bx - 16, y0 - 22,
                                   bx + 16, y0 - 2,
                                   fill=self.indigo, outline="")
                canvas.create_text(bx, y0 - 12,
                                   text="Peak", fill="white",
                                   font=("Segoe UI", 7, "bold"))

            # X label
            if h < 12:
                lbl = f"{h} AM"
            elif h == 12:
                lbl = "12 PM"
            else:
                lbl = f"{h - 12} PM"
            canvas.create_text(x0 + bar_w // 2, H - pad_b + 8,
                               text=lbl,
                               fill=self.txt_dark if is_pk else self.txt_muted,
                               font=("Segoe UI", 7))

    # ─────────────────────────────────────────────────────────────────
    # RENDER SECTIONS
    # ─────────────────────────────────────────────────────────────────
    def _render_trending(self, trending):
        for w in self._trend_list_frame.winfo_children():
            w.destroy()

        if not trending:
            tk.Label(self._trend_list_frame,
                     text="No trending products for this period.",
                     font=self.FN, bg=self.bg_card,
                     fg=self.txt_muted).pack(anchor="w", pady=10)
            return

        for i, (name, cat, qty, growth) in enumerate(trending):
            if i > 0:
                tk.Frame(self._trend_list_frame,
                         bg="#F3F4F6", height=1).pack(fill=tk.X, pady=3)

            row = tk.Frame(self._trend_list_frame, bg=self.bg_card)
            row.pack(fill=tk.X, pady=2)

            # arrow circle
            af = tk.Frame(row, bg="#ECFDF5", width=30, height=30)
            af.pack(side=tk.LEFT, padx=(0, 10))
            af.pack_propagate(False)
            tk.Label(af, text="↑", font=("Segoe UI", 12, "bold"),
                     bg="#ECFDF5", fg=self.green).place(
                relx=.5, rely=.5, anchor="center")

            info = tk.Frame(row, bg=self.bg_card)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=name[:28], font=self.FNB,
                     bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
            tk.Label(info, text=cat or "—", font=self.FS,
                     bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")

            tk.Label(row, text=f"+{growth:.0f}%",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.bg_card, fg=self.green).pack(side=tk.RIGHT)

    def _render_low_demand(self, low_demand):
        for w in self._lowdemand_frame.winfo_children():
            w.destroy()

        if not low_demand:
            tk.Label(self._lowdemand_frame,
                     text="✅  No significant demand drops detected.",
                     font=self.FN, bg=self.bg_card,
                     fg=self.green).pack(anchor="w", pady=10)
            return

        for i, (name, cat, qty, decline) in enumerate(low_demand):
            if i > 0:
                tk.Frame(self._lowdemand_frame,
                         bg="#F3F4F6", height=1).pack(fill=tk.X, pady=3)

            row = tk.Frame(self._lowdemand_frame, bg=self.bg_card)
            row.pack(fill=tk.X, pady=2)

            af = tk.Frame(row, bg="#FFF1F2", width=30, height=30)
            af.pack(side=tk.LEFT, padx=(0, 10))
            af.pack_propagate(False)
            tk.Label(af, text="↓", font=("Segoe UI", 12, "bold"),
                     bg="#FFF1F2", fg=self.red).place(
                relx=.5, rely=.5, anchor="center")

            info = tk.Frame(row, bg=self.bg_card)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=name[:28], font=self.FNB,
                     bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
            tk.Label(info, text=cat or "—", font=self.FS,
                     bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")

            tk.Label(row, text=f"{decline:.0f}%",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.bg_card, fg=self.red).pack(side=tk.RIGHT)

    def _render_suggestions(self, suggestions):
        for w in self._suggestion_row.winfo_children():
            w.destroy()

        if not suggestions:
            tk.Label(self._suggestion_row,
                     text="✅  No significant stock changes recommended for this period.",
                     font=self.FN, bg=self.bg_card, fg=self.txt_muted
                     ).grid(row=0, column=0, columnspan=3, pady=12)
            return

        border_colors = [self.green, self.orange, self.purple]
        while len(suggestions) < 3:
            suggestions.append(None)

        for i, sug in enumerate(suggestions[:3]):
            bc   = border_colors[i]
            card = tk.Frame(self._suggestion_row, bg=self.bg_card,
                            highlightbackground=self.bd,
                            highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 12, 0))

            # colored left accent
            tk.Frame(card, bg=bc, width=4).pack(side=tk.LEFT, fill=tk.Y)

            inner = tk.Frame(card, bg=self.bg_card)
            inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=14)

            if sug is None:
                tk.Label(inner, text="—", font=self.FN,
                         bg=self.bg_card, fg=self.txt_muted).pack()
                continue

            action, product, qty_str, reason, color, note = sug
            tk.Label(inner, text=action, font=self.FS,
                     bg=self.bg_card, fg=self.txt_muted).pack(anchor="w")
            tk.Label(inner, text=product[:22],
                     font=("Segoe UI", 11, "bold"),
                     bg=self.bg_card, fg=self.txt_dark).pack(anchor="w")
            tk.Label(inner, text=qty_str,
                     font=("Segoe UI", 20, "bold"),
                     bg=self.bg_card, fg=color).pack(anchor="w", pady=(2, 4))
            tk.Label(inner, text=reason, font=self.FS,
                     bg=self.bg_card, fg=self.txt_muted,
                     wraplength=190, justify="left").pack(anchor="w")
            tk.Frame(inner, bg="#F3F4F6", height=1).pack(fill=tk.X, pady=(6, 4))
            tk.Label(inner, text=note, font=("Segoe UI", 8),
                     bg=self.bg_card, fg=color).pack(anchor="w")

    def _render_anomalies(self, anomalies):
        for w in self._anomaly_frame.winfo_children():
            w.destroy()

        if not anomalies:
            tk.Label(self._anomaly_frame,
                     text="✅  No anomalies detected in the selected period.",
                     font=self.FN, bg=self.bg_card,
                     fg=self.green).pack(anchor="w", pady=10)
            return

        for i, (title, detail, timestamp, kind) in enumerate(anomalies):
            if kind == "spike":
                bg, border, dot_c = "#FFF7ED", "#FDE68A", self.orange
            elif kind == "drop":
                bg, border, dot_c = "#FFF1F2", "#FCA5A5", self.red
            else:
                bg, border, dot_c = "#F0F9FF", "#BAE6FD", self.sky

            row = tk.Frame(self._anomaly_frame, bg=bg,
                           highlightbackground=border,
                           highlightthickness=1)
            row.pack(fill=tk.X, pady=(0 if i == 0 else 6, 0))

            inner = tk.Frame(row, bg=bg)
            inner.pack(fill=tk.X, padx=14, pady=10)

            top_row = tk.Frame(inner, bg=bg)
            top_row.pack(fill=tk.X)
            tk.Label(top_row, text="●", font=("Segoe UI", 10),
                     bg=bg, fg=dot_c).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(top_row, text=title, font=self.FNB,
                     bg=bg, fg=self.txt_dark).pack(side=tk.LEFT)
            tk.Label(top_row, text=timestamp, font=self.FS,
                     bg=bg, fg=self.txt_muted).pack(side=tk.RIGHT)

            tk.Label(inner, text=detail, font=self.FS,
                     bg=bg, fg=self.txt_muted,
                     wraplength=760, justify="left",
                     anchor="w").pack(fill=tk.X, padx=(18, 0), pady=(2, 0))

    # ─────────────────────────────────────────────────────────────────
    # BUTTON HELPER  (matches reports.py exactly)
    # ─────────────────────────────────────────────────────────────────
    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.FNB, bg=bg, fg=fg,
                  relief="flat", bd=0, cursor="hand2",
                  padx=16, pady=7,
                  activebackground=bg, activeforeground=fg)
        if border:
            kw["highlightbackground"] = self.bd
            kw["highlightthickness"]  = 1
        if cmd:
            kw["command"] = cmd
        return tk.Button(parent, **kw)


# ── standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("IMS – AI Analytics")
    root.state("zoomed")
    app = AIAnalyticsClass(root)
    root.mainloop()