import tkinter as tk
from tkinter import ttk, messagebox
import db_config
import time
from datetime import datetime, date, timedelta
import math


class ModernIMSDashboard:
    def __init__(self, root, name, role):
        self.root = root
        self.root.title(f"IMS Pro  —  {name}  ({role})")
        self.root.geometry("1200x800")
        self.root.configure(bg="#F3F4F6")
        self.root.state("zoomed")

        self.user_name = name
        self.user_role = role

        # ── Unified palette (identical across every page) ─────────────
        self.bg_page      = "#F3F4F6"
        self.bg_card      = "#FFFFFF"
        self.bg_sidebar   = "#1A222C"
        self.text_dark    = "#111827"
        self.text_muted   = "#6B7280"
        self.border_color = "#E5E7EB"
        self.primary_blue = "#2563EB"
        self.green        = "#10B981"
        self.orange       = "#F59E0B"
        self.red          = "#EF4444"
        self.sky          = "#0EA5E9"
        self.purple       = "#8B5CF6"

        # backward-compat aliases kept for handle_menu / other refs
        self.bg_content = self.bg_page
        self.text_main  = self.text_dark

        self.create_sidebar()
        self.create_main_content()
        self.show_home_dashboard()

    # ═══════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════════
    def create_sidebar(self):
        self._c_sidebar     = self.bg_sidebar
        self._c_hover       = "#243040"
        self._c_active_bg   = "#2D3F50"
        self._c_accent      = "#3B82F6"
        self._c_icon_normal = "#64748B"
        self._c_icon_active = "#FFFFFF"
        self._c_text_normal = "#94A3B8"
        self._c_text_active = "#FFFFFF"

        self.active_menu  = "Dashboard"
        self.menu_buttons = {}

        self.sidebar = tk.Frame(self.root, bg=self._c_sidebar, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo
        logo_f = tk.Frame(self.sidebar, bg=self._c_sidebar)
        logo_f.pack(fill=tk.X, padx=18, pady=(22, 18))
        tk.Label(logo_f, text="💠", font=("Segoe UI", 18),
                 bg=self._c_sidebar, fg="white").pack(side=tk.LEFT)
        tk.Label(logo_f, text=" IMS Pro", font=("Segoe UI", 14, "bold"),
                 bg=self._c_sidebar, fg="white").pack(side=tk.LEFT)

        tk.Frame(self.sidebar, bg="#2D3748", height=1).pack(
            fill=tk.X, padx=16, pady=(0, 8))

        ICONS = {
            "Dashboard":    "⊟", "Products":     "◫",
            "Stock":        "≡", "Sales":        "⊞",
            "Purchases":    "⊠", "Suppliers":    "◎",
            "Employees":    "◉", "Reports":      "▤",
            "AI Analytics": "◈", "Users":        "◯",
            "My Report":    "▤",
        }

        if self.user_role == "Admin":
            main_menus   = ["Dashboard", "Products", "Stock", "Sales",
                            "Purchases", "Suppliers", "Employees",
                            "Reports", "AI Analytics"]
            bottom_menus = ["Users"]
        else:
            main_menus   = ["Dashboard", "Sales", "Products", "My Report"]
            bottom_menus = []

        for name in main_menus:
            self._add_menu_item(name, ICONS.get(name, "•"))

        tk.Frame(self.sidebar, bg="#2D3748", height=1).pack(
            fill=tk.X, padx=16, pady=8)

        for name in bottom_menus:
            self._add_menu_item(name, ICONS.get(name, "•"))

        # Logout
        lf = tk.Frame(self.sidebar, bg=self._c_sidebar, cursor="hand2")
        lf.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 18))
        tk.Frame(lf, bg=self._c_sidebar, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(lf, text="→", font=("Segoe UI", 13),
                 bg=self._c_sidebar, fg="#EF4444", width=3).pack(side=tk.LEFT, pady=9)
        tk.Label(lf, text="Logout", font=("Segoe UI", 10),
                 bg=self._c_sidebar, fg="#EF4444", anchor="w").pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        def _lo_in(e):
            for w in lf.winfo_children(): w.config(bg="#2D1515")
            lf.config(bg="#2D1515")
        def _lo_out(e):
            for w in lf.winfo_children(): w.config(bg=self._c_sidebar)
            lf.config(bg=self._c_sidebar)

        for w in [lf] + list(lf.winfo_children()):
            w.bind("<Enter>", _lo_in)
            w.bind("<Leave>", _lo_out)
            w.bind("<Button-1>", lambda e: self.logout())

    def _add_menu_item(self, name, icon):
        is_active = (name == self.active_menu)
        bg   = self._c_active_bg if is_active else self._c_sidebar
        fg_i = self._c_icon_active if is_active else self._c_icon_normal
        fg_t = self._c_text_active if is_active else self._c_text_normal
        acc  = self._c_accent      if is_active else bg

        row = tk.Frame(self.sidebar, bg=bg, cursor="hand2")
        row.pack(fill=tk.X, padx=10, pady=1)

        accent_bar = tk.Frame(row, bg=acc, width=3)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)
        accent_bar.pack_propagate(False)

        icon_lbl = tk.Label(row, text=icon, font=("Segoe UI", 13),
                            bg=bg, fg=fg_i, width=3)
        icon_lbl.pack(side=tk.LEFT, pady=9)

        text_lbl = tk.Label(row, text=name, font=("Segoe UI", 10),
                            bg=bg, fg=fg_t, anchor="w")
        text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.menu_buttons[name] = {
            "row": row, "accent": accent_bar,
            "icon": icon_lbl, "text": text_lbl,
        }

        def _enter(e, n=name):
            if n != self.active_menu:
                for w in [self.menu_buttons[n]["row"],
                          self.menu_buttons[n]["icon"],
                          self.menu_buttons[n]["text"]]:
                    w.config(bg=self._c_hover)
                self.menu_buttons[n]["accent"].config(bg=self._c_hover)

        def _leave(e, n=name):
            if n != self.active_menu:
                for w in [self.menu_buttons[n]["row"],
                          self.menu_buttons[n]["icon"],
                          self.menu_buttons[n]["text"]]:
                    w.config(bg=self._c_sidebar)
                self.menu_buttons[n]["accent"].config(bg=self._c_sidebar)

        def _click(e, n=name):
            self._set_active_menu(n)
            self.handle_menu(n)

        for widget in [row, accent_bar, icon_lbl, text_lbl]:
            widget.bind("<Enter>",    _enter)
            widget.bind("<Leave>",    _leave)
            widget.bind("<Button-1>", _click)

    def _set_active_menu(self, name):
        old = self.active_menu
        if old in self.menu_buttons:
            r = self.menu_buttons[old]
            r["row"].config(bg=self._c_sidebar)
            r["accent"].config(bg=self._c_sidebar)
            r["icon"].config(bg=self._c_sidebar, fg=self._c_icon_normal)
            r["text"].config(bg=self._c_sidebar, fg=self._c_text_normal)
        self.active_menu = name
        if name in self.menu_buttons:
            r = self.menu_buttons[name]
            r["row"].config(bg=self._c_active_bg)
            r["accent"].config(bg=self._c_accent)
            r["icon"].config(bg=self._c_active_bg, fg=self._c_icon_active)
            r["text"].config(bg=self._c_active_bg, fg=self._c_text_active)

    # ═══════════════════════════════════════════════════════════════════
    # MENU HANDLER
    # ═══════════════════════════════════════════════════════════════════
    def handle_menu(self, menu_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if menu_name == "Dashboard":
            self.show_home_dashboard()
        elif menu_name == "Products":
            self.header_title.config(text="Manage Products")
            import product
            product.ProductMenu(self.content_frame)
        elif menu_name == "Stock":
            self.header_title.config(text="Stock Management")
            import stock
            stock.StockClass(self.content_frame)
        elif menu_name == "Sales":
            self.header_title.config(text="Point of Sale (POS)")
            import sales
            sales.SalesClass(self.content_frame)
        elif menu_name == "Purchases":
            self.header_title.config(text="Purchase Management")
            import purchases
            purchases.PurchaseClass(self.content_frame)
        elif menu_name == "Suppliers":
            self.header_title.config(text="Supplier Management")
            import suppliers
            suppliers.SupplierClass(self.content_frame)
        elif menu_name == "Employees":
            self.header_title.config(text="Employee Sales Report")
            import employees
            employees.EmployeeSalesClass(self.content_frame)
        elif menu_name == "Reports":
            self.header_title.config(text="Reports & Analytics")
            import reports
            reports.ReportsClass(self.content_frame)
        elif menu_name == "AI Analytics":
            self.header_title.config(text="AI Analytics")
            import ai_analytics
            ai_analytics.AIAnalyticsClass(self.content_frame)
        elif menu_name == "Users":
            self.header_title.config(text="User Management")
            import users
            users.UsersClass(self.content_frame)
        else:
            self.header_title.config(text=menu_name)
            tk.Label(self.content_frame,
                     text=f"{menu_name} is under development…",
                     font=("Segoe UI", 14), bg=self.bg_page,
                     fg=self.text_muted).pack(pady=120)

    # ═══════════════════════════════════════════════════════════════════
    # MAIN CONTENT AREA  (header + clock + content frame)
    # ═══════════════════════════════════════════════════════════════════
    def create_main_content(self):
        self.header = tk.Frame(self.root, bg=self.bg_card,
                               highlightbackground=self.border_color,
                               highlightthickness=1, height=60)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        self.header_title = tk.Label(
            self.header, text="Dashboard Overview",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_card, fg=self.text_dark)
        self.header_title.pack(side=tk.LEFT, padx=24, pady=15)

        tk.Label(self.header,
                 text=f"🔔  {self.user_name}  ({self.user_role})",
                 font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.text_dark).pack(
            side=tk.RIGHT, padx=24)

        self.lbl_clock = tk.Label(self.header, text="",
                                  font=("Segoe UI", 10, "bold"),
                                  bg=self.bg_card, fg=self.primary_blue)
        self.lbl_clock.pack(side=tk.RIGHT, padx=8)

        # thin separator
        tk.Frame(self.header, bg=self.border_color, width=1).pack(
            side=tk.RIGHT, fill=tk.Y, pady=14)

        self.update_time()

        self.content_frame = tk.Frame(self.root, bg=self.bg_page)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def update_time(self):
        self.lbl_clock.config(
            text=f"📅 {time.strftime('%d %B, %Y')}  |  🕒 {time.strftime('%I:%M:%S %p')}")
        self.lbl_clock.after(1000, self.update_time) 

    # ═══════════════════════════════════════════════════════════════════
    # DASHBOARD HOME
    # ═══════════════════════════════════════════════════════════════════
    def show_home_dashboard(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        self.header_title.config(text="Dashboard Overview")

        # ── Scrollable canvas ───────────────────────────────────────
        outer = tk.Frame(self.content_frame, bg=self.bg_page)
        outer.pack(fill=tk.BOTH, expand=True)

        vbar = ttk.Scrollbar(outer, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._dash_canvas = tk.Canvas(outer, bg=self.bg_page,
                                      highlightthickness=0,
                                      yscrollcommand=vbar.set)
        self._dash_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar.config(command=self._dash_canvas.yview)

        pf = tk.Frame(self._dash_canvas, bg=self.bg_page)
        win = self._dash_canvas.create_window((0, 0), window=pf, anchor="nw")

        pf.bind("<Configure>", lambda e: self._dash_canvas.configure(
            scrollregion=self._dash_canvas.bbox("all")))
        self._dash_canvas.bind("<Configure>",
            lambda e: self._dash_canvas.itemconfig(win, width=e.width))
        self._dash_canvas.bind("<Enter>",
            lambda e: self._dash_canvas.bind_all("<MouseWheel>",
                lambda ev: self._dash_canvas.yview_scroll(
                    int(-1 * (ev.delta / 120)), "units")))
        self._dash_canvas.bind("<Leave>",
            lambda e: self._dash_canvas.unbind_all("<MouseWheel>"))

        # ── Build structure ──────────────────────────────────────────
        self._build_kpi_row(pf)
        self._build_chart_trending_row(pf)
        self._build_lowstock_activities_row(pf)

        # ── Load data after layout is rendered ───────────────────────
        self.root.after(120, self._load_dashboard_data)

    # ─────────────────────────────────────────────────────────────────
    # KPI CARDS
    # ─────────────────────────────────────────────────────────────────
    def _build_kpi_row(self, parent):
        row = tk.Frame(parent, bg=self.bg_page)
        row.pack(fill=tk.X, padx=26, pady=(20, 14))
        for i in range(4):
            row.columnconfigure(i, weight=1)

        self._kv_products = self._make_kpi_card(
            row, 0, "Total Products",   "📦", "#EFF6FF", self.primary_blue)
        self._kv_sales    = self._make_kpi_card(
            row, 1, "Total Sales",      "💰", "#ECFDF5", self.green)
        self._kv_profit   = self._make_kpi_card(
            row, 2, "Total Profit",     "📈", "#F0F9FF", self.sky)
        self._kv_alerts   = self._make_kpi_card(
            row, 3, "Low Stock Alerts", "⚠", "#FFF7ED", self.orange)

    def _make_kpi_card(self, parent, col, title, icon, icon_bg, icon_color):
        card = tk.Frame(parent, bg=self.bg_card,
                        highlightbackground=self.border_color,
                        highlightthickness=1, height=118)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 14, 0))
        card.pack_propagate(False)

        top = tk.Frame(card, bg=self.bg_card)
        top.pack(fill=tk.X, padx=18, pady=(16, 2))

        tk.Label(top, text=title, font=("Segoe UI", 9),
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT)

        icon_f = tk.Frame(top, bg=icon_bg, width=36, height=36)
        icon_f.pack(side=tk.RIGHT)
        icon_f.pack_propagate(False)
        tk.Label(icon_f, text=icon, font=("Segoe UI", 15),
                 bg=icon_bg, fg=icon_color).place(
            relx=.5, rely=.5, anchor="center")

        val_lbl = tk.Label(card, text="—",
                           font=("Segoe UI", 22, "bold"),
                           bg=self.bg_card, fg=self.text_dark)
        val_lbl.pack(anchor="w", padx=18)

        sub_lbl = tk.Label(card, text="Loading…",
                           font=("Segoe UI", 8),
                           bg=self.bg_card, fg=self.text_muted)
        sub_lbl.pack(anchor="w", padx=18, pady=(0, 6))

        return val_lbl, sub_lbl

    # ─────────────────────────────────────────────────────────────────
    # SALES CHART  +  TRENDING PRODUCTS
    # ─────────────────────────────────────────────────────────────────
    def _build_chart_trending_row(self, parent):
        row = tk.Frame(parent, bg=self.bg_page)
        row.pack(fill=tk.X, padx=26, pady=(0, 14))
        row.columnconfigure(0, weight=3)
        row.columnconfigure(1, weight=2)

        # Chart card
        cc = tk.Frame(row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        cc.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ch = tk.Frame(cc, bg=self.bg_card)
        ch.pack(fill=tk.X, padx=20, pady=(16, 6))
        tk.Label(ch, text="Sales Overview",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.bg_card, fg=self.text_dark).pack(side=tk.LEFT)
        tk.Label(ch, text="Last 30 days",
                 font=("Segoe UI", 9),
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT, padx=10)

        self._sales_chart = tk.Canvas(cc, bg=self.bg_card,
                                      height=230, highlightthickness=0)
        self._sales_chart.pack(fill=tk.X, padx=20, pady=(0, 18))

        # Trending card
        tc = tk.Frame(row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        tc.grid(row=0, column=1, sticky="nsew")

        th = tk.Frame(tc, bg=self.bg_card)
        th.pack(fill=tk.X, padx=20, pady=(16, 8))
        tk.Label(th, text="🔥  Trending Products",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.bg_card, fg=self.text_dark).pack(side=tk.LEFT)

        self._trend_frame = tk.Frame(tc, bg=self.bg_card)
        self._trend_frame.pack(fill=tk.BOTH, expand=True,
                               padx=20, pady=(0, 16))

    # ─────────────────────────────────────────────────────────────────
    # LOW STOCK TABLE  +  RECENT ACTIVITIES
    # ─────────────────────────────────────────────────────────────────
    def _build_lowstock_activities_row(self, parent):
        row = tk.Frame(parent, bg=self.bg_page)
        row.pack(fill=tk.X, padx=26, pady=(0, 26))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        # Low stock card
        lc = tk.Frame(row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        lc.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        lh = tk.Frame(lc, bg=self.bg_card)
        lh.pack(fill=tk.X, padx=20, pady=(16, 8))
        tk.Label(lh, text="⚠  Low Stock Products",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.bg_card, fg=self.orange).pack(side=tk.LEFT)

        # Column headers
        thead = tk.Frame(lc, bg="#F8FAFC")
        thead.pack(fill=tk.X, padx=20, pady=(0, 4))
        for txt, anc, w in [
            ("Product Name",  "w",      0),
            ("Remaining Qty", "center", 1),
            ("Status",        "center", 2),
        ]:
            tk.Label(thead, text=txt, font=("Segoe UI", 8, "bold"),
                     bg="#F8FAFC", fg="#475569",
                     anchor=anc, padx=6, pady=6).grid(
                row=0, column=w, sticky="ew")
        thead.columnconfigure(0, weight=3)
        thead.columnconfigure(1, weight=2)
        thead.columnconfigure(2, weight=2)

        self._stock_frame = tk.Frame(lc, bg=self.bg_card)
        self._stock_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

        # Activities card
        ac = tk.Frame(row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        ac.grid(row=0, column=1, sticky="nsew")

        ah = tk.Frame(ac, bg=self.bg_card)
        ah.pack(fill=tk.X, padx=20, pady=(16, 8))
        tk.Label(ah, text="🕐  Recent Activities",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.bg_card, fg=self.text_dark).pack(side=tk.LEFT)

        self._activity_frame = tk.Frame(ac, bg=self.bg_card)
        self._activity_frame.pack(fill=tk.BOTH, expand=True,
                                  padx=20, pady=(0, 16))

    # ═══════════════════════════════════════════════════════════════════
    # DATA LOADING
    # ═══════════════════════════════════════════════════════════════════
    def _load_dashboard_data(self):
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            today           = date.today()
            month_start     = today.replace(day=1)
            prev_month_end  = month_start - timedelta(days=1)
            prev_month_start= prev_month_end.replace(day=1)
            days_30_ago     = today - timedelta(days=29)

            # ── KPI: products ────────────────────────────────────────
            cur.execute("SELECT COUNT(*) FROM products WHERE status='Active'")
            products = cur.fetchone()[0] or 0

            # ── KPI: sales this month vs last month ──────────────────
            cur.execute("SELECT SUM(grand_total) FROM sales WHERE sale_date >= %s",
                        (month_start,))
            sales_this = float(cur.fetchone()[0] or 0)

            cur.execute("SELECT SUM(grand_total) FROM sales "
                        "WHERE sale_date BETWEEN %s AND %s",
                        (prev_month_start, prev_month_end))
            sales_prev = float(cur.fetchone()[0] or 0)

            # ── KPI: profit ───────────────────────────────────────────
            cur.execute("""
                SELECT SUM((si.unit_price - p.cost_price) * si.qty)
                FROM sales_items si
                JOIN products p ON si.pid = p.pid
            """)
            profit = float(cur.fetchone()[0] or 0)

            # ── KPI: low-stock alert count ────────────────────────────
            cur.execute("""
                SELECT COUNT(*) FROM products
                WHERE stock <= low_stock_alert AND status='Active'
            """)
            alerts = cur.fetchone()[0] or 0

            # ── Update KPI labels ────────────────────────────────────
            self._kv_products[0].config(text=f"{products:,}")
            self._kv_products[1].config(text="Active items in inventory")

            self._kv_sales[0].config(text=f"৳ {sales_this:,.0f}")
            if sales_prev > 0:
                pct   = (sales_this - sales_prev) / sales_prev * 100
                arrow = "▲" if pct >= 0 else "▼"
                clr   = self.green if pct >= 0 else self.red
                self._kv_sales[1].config(
                    text=f"{arrow} {abs(pct):.1f}% from last month", fg=clr)
            else:
                self._kv_sales[1].config(text="This month's revenue")

            self._kv_profit[0].config(text=f"৳ {profit:,.0f}")
            self._kv_profit[1].config(text="Overall profit margin")

            self._kv_alerts[0].config(text=str(alerts))
            self._kv_alerts[1].config(
                text="Requires attention immediately" if alerts else "All stock levels healthy",
                fg=self.red if alerts else self.green)

            # ── Chart: daily sales last 30 days ─────────────────────
            cur.execute("""
                SELECT sale_date, SUM(grand_total)
                FROM sales WHERE sale_date >= %s
                GROUP BY sale_date ORDER BY sale_date
            """, (days_30_ago,))
            chart_rows = cur.fetchall()
            chart_data = [
                (r[0].strftime("%d/%m") if hasattr(r[0], "strftime") else str(r[0]),
                 float(r[1] or 0))
                for r in chart_rows
            ]
            self.root.after(80, lambda: self._draw_sales_chart(
                self._sales_chart, chart_data))

            # ── Trending products ─────────────────────────────────────
            cur.execute("""
                SELECT p.name, p.category, SUM(si.qty) AS qty
                FROM sales_items si
                JOIN products p ON si.pid = p.pid
                JOIN sales    s ON si.invoice_no = s.invoice_no
                WHERE s.sale_date >= %s
                GROUP BY p.pid, p.name, p.category
                ORDER BY qty DESC LIMIT 4
            """, (days_30_ago,))
            trending = cur.fetchall()
            self._render_trending(trending)

            # ── Low stock items ───────────────────────────────────────
            cur.execute("""
                SELECT name, stock, low_stock_alert
                FROM products
                WHERE stock <= low_stock_alert AND status='Active'
                ORDER BY stock ASC LIMIT 6
            """)
            low_stock = cur.fetchall()
            self._render_low_stock(low_stock)

            # ── Recent activities (logins + sales) ────────────────────
            cur.execute("""
                SELECT u.name, l.login_time
                FROM login_logs l
                JOIN users u ON l.emp_id = u.emp_id
                ORDER BY l.login_time DESC LIMIT 5
            """)
            logins = cur.fetchall()

            cur.execute("""
                SELECT invoice_no, grand_total, sale_date
                FROM sales ORDER BY invoice_no DESC LIMIT 5
            """)
            recent_sales = cur.fetchall()
            self._render_activities(logins, recent_sales)

        except Exception as e:
            print("Dashboard load error:", e)
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # CHART DRAWING  –  line chart with area fill
    # ═══════════════════════════════════════════════════════════════════
    def _draw_sales_chart(self, canvas, data):
        canvas.delete("all")
        canvas.update_idletasks()
        W = canvas.winfo_width() or 480
        H = 230
        pl, pr, pt, pb = 56, 18, 18, 38

        if not data:
            canvas.create_text(W // 2, H // 2,
                               text="No sales data yet — make some sales!",
                               fill=self.text_muted, font=("Segoe UI", 10))
            return

        vals = [v for _, v in data]
        maxv = max(vals) * 1.1 if max(vals) > 0 else 1
        cw   = W - pl - pr
        ch   = H - pt - pb
        n    = len(data)

        # Y-axis grid + labels
        for i in range(5):
            y   = pt + ch - (ch * i // 4)
            val = maxv * i / 4
            lbl = f"৳{val/1000:.0f}K" if val >= 1000 else f"৳{int(val)}"
            canvas.create_line(pl, y, W - pr, y, fill="#F1F5F9", width=1)
            canvas.create_text(pl - 6, y, text=lbl, anchor="e",
                               fill=self.text_muted, font=("Segoe UI", 7))

        def pt_xy(idx, v):
            x = pl + int(cw * idx / max(n - 1, 1))
            y = pt + ch - int(ch * v / maxv)
            return x, y

        pts = [pt_xy(i, v) for i, (_, v) in enumerate(data)]

        # Filled area under the line
        poly = [pl, pt + ch]
        for x, y in pts:
            poly += [x, y]
        poly += [pts[-1][0], pt + ch]
        canvas.create_polygon(poly, fill="#F1F5F9", outline="")

        # Line
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]; x2, y2 = pts[i + 1]
            canvas.create_line(x1, y1, x2, y2,
                               fill=self.text_dark, width=2.5, smooth=True)

        # Dots + x-labels (every Nth)
        every = max(1, n // 8)
        for i, (lbl, _) in enumerate(data):
            if i % every == 0 or i == n - 1:
                x, y = pts[i]
                canvas.create_oval(x - 4, y - 4, x + 4, y + 4,
                                   fill=self.text_dark, outline="white", width=1.5)
                canvas.create_text(x, H - pb + 10, text=lbl,
                                   fill=self.text_muted, font=("Segoe UI", 7))

    # ═══════════════════════════════════════════════════════════════════
    # RENDER HELPERS
    # ═══════════════════════════════════════════════════════════════════
    def _render_trending(self, trending):
        for w in self._trend_frame.winfo_children():
            w.destroy()

        if not trending:
            tk.Label(self._trend_frame,
                     text="No sales data in the last 30 days.",
                     font=("Segoe UI", 10), bg=self.bg_card,
                     fg=self.text_muted).pack(anchor="w", pady=12)
            return

        colors_bg  = ["#EFF6FF", "#ECFDF5", "#FFF7ED", "#F5F3FF"]
        colors_fg  = [self.primary_blue, self.green, self.orange, self.purple]
        max_qty    = max(r[2] for r in trending) or 1

        for i, (name, cat, qty) in enumerate(trending[:4]):
            bg  = colors_bg[i % 4]
            fg  = colors_fg[i % 4]
            pct = int(qty / max_qty * 100)

            if i > 0:
                tk.Frame(self._trend_frame, bg=self.border_color,
                         height=1).pack(fill=tk.X, pady=5)

            row = tk.Frame(self._trend_frame, bg=self.bg_card)
            row.pack(fill=tk.X, pady=2)

            icon_f = tk.Frame(row, bg=bg, width=38, height=38)
            icon_f.pack(side=tk.LEFT, padx=(0, 12))
            icon_f.pack_propagate(False)
            tk.Label(icon_f, text="📦", font=("Segoe UI", 14),
                     bg=bg, fg=fg).place(relx=.5, rely=.5, anchor="center")

            info = tk.Frame(row, bg=self.bg_card)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=name[:26],
                     font=("Segoe UI", 10, "bold"),
                     bg=self.bg_card, fg=self.text_dark).pack(anchor="w")
            tk.Label(info, text=cat or "Uncategorised",
                     font=("Segoe UI", 9),
                     bg=self.bg_card, fg=self.text_muted).pack(anchor="w")

            badge = tk.Label(row, text=f"↑ +{pct}%",
                             font=("Segoe UI", 9, "bold"),
                             bg="#ECFDF5", fg=self.green, padx=7, pady=2)
            badge.pack(side=tk.RIGHT, padx=4)

    def _render_low_stock(self, items):
        for w in self._stock_frame.winfo_children():
            w.destroy()

        if not items:
            tk.Label(self._stock_frame,
                     text="✅  All stock levels are healthy!",
                     font=("Segoe UI", 10), bg=self.bg_card,
                     fg=self.green).pack(anchor="w", pady=12)
            return

        for i, (name, stock, alert) in enumerate(items):
            is_critical = stock == 0
            s_bg  = self.red    if is_critical else self.orange
            label = "Critical"  if is_critical else "Warning"
            qty   = "Out of stock" if is_critical else f"{stock} units"

            if i > 0:
                tk.Frame(self._stock_frame, bg=self.border_color,
                         height=1).pack(fill=tk.X, pady=2)

            row = tk.Frame(self._stock_frame, bg=self.bg_card)
            row.pack(fill=tk.X, pady=4)
            row.columnconfigure(0, weight=3)
            row.columnconfigure(1, weight=2)
            row.columnconfigure(2, weight=2)

            tk.Label(row, text=name[:28], font=("Segoe UI", 10),
                     bg=self.bg_card, fg=self.text_dark,
                     anchor="w").grid(row=0, column=0, sticky="w")
            tk.Label(row, text=qty, font=("Segoe UI", 10),
                     bg=self.bg_card, fg=self.text_muted,
                     anchor="center").grid(row=0, column=1)
            badge = tk.Label(row, text=f"⊙  {label}",
                             font=("Segoe UI", 8, "bold"),
                             bg=s_bg, fg="white", padx=8, pady=3)
            badge.grid(row=0, column=2, sticky="e")

    def _render_activities(self, logins, recent_sales):
        for w in self._activity_frame.winfo_children():
            w.destroy()

        now = datetime.now()
        activities = []

        for name, login_time in logins:
            if isinstance(login_time, datetime):
                delta = now - login_time
                mins  = int(delta.total_seconds() / 60)
                if mins < 60:
                    ts = f"{mins} mins ago"
                elif mins < 1440:
                    ts = f"{mins // 60} hrs ago"
                else:
                    ts = f"{mins // 1440} days ago"
            else:
                ts = "Recently"
            activities.append((f"System login: {name}", ts, self.text_muted))

        for inv_no, amount, sale_date in recent_sales:
            if isinstance(sale_date, date):
                delta = now.date() - sale_date
                if delta.days == 0:
                    ts = "Today"
                elif delta.days == 1:
                    ts = "Yesterday"
                else:
                    ts = f"{delta.days} days ago"
            else:
                ts = "Recently"
            activities.append((
                f"Sale completed: Order #{inv_no}  (৳{float(amount):,.0f})",
                ts, self.green))

        if not activities:
            tk.Label(self._activity_frame, text="No recent activity.",
                     font=("Segoe UI", 10), bg=self.bg_card,
                     fg=self.text_muted).pack(anchor="w", pady=12)
            return

        for text, ts, dot_clr in activities[:8]:
            row = tk.Frame(self._activity_frame, bg=self.bg_card)
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text="●", font=("Segoe UI", 9),
                     bg=self.bg_card, fg=dot_clr).pack(
                side=tk.LEFT, padx=(0, 10))

            info = tk.Frame(row, bg=self.bg_card)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=text[:48],
                     font=("Segoe UI", 10),
                     bg=self.bg_card, fg=self.text_dark,
                     anchor="w").pack(anchor="w")
            tk.Label(info, text=ts,
                     font=("Segoe UI", 9),
                     bg=self.bg_card, fg=self.text_muted,
                     anchor="w").pack(anchor="w")

    # ═══════════════════════════════════════════════════════════════════
    # LOGOUT
    # ═══════════════════════════════════════════════════════════════════
    def logout(self):
        if messagebox.askyesno("Logout",
                               "Are you sure you want to logout?",
                               parent=self.root):
            self.root.destroy()
            import login
            login_root = tk.Tk()
            login.LoginWindow(login_root)
            login_root.mainloop()


# ── standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ModernIMSDashboard(root, "System Admin", "Admin")
    root.mainloop()