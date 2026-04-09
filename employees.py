import tkinter as tk
from tkinter import ttk, messagebox
import db_config
from datetime import datetime

class EmployeeSalesClass:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#F3F4F6")

        # ── Colour palette ────────────────────────────────────────────
        self.bg_page      = "#F3F4F6"
        self.bg_card      = "#FFFFFF"
        self.text_dark    = "#111827"
        self.text_muted   = "#6B7280"
        self.border_color = "#E5E7EB"
        self.primary_blue = "#2563EB"
        self.success      = "#10B981"
        self.input_bg     = "#F9FAFB"

        # ── Font stack ────────────────────────────────────────────────
        self.F_TITLE  = ("Segoe UI", 18, "bold")
        self.F_NORMAL = ("Segoe UI", 10)
        self.F_BTN    = ("Segoe UI", 10, "bold")
        
        # Updated Card Fonts - Smaller and less bold
        self.F_CARD_V = ("Segoe UI", 20, "bold") 
        self.F_CARD_T = ("Segoe UI", 10) 

        # Variables
        self.search_var = tk.StringVar()
        self.selected_emp_var = tk.StringVar()
        self.emp_dict = {} # To store { "Name - ID" : emp_id } for the dropdown

        self._setup_treeview_style()
        
        # Content frames (built before tabs so _switch_tab can use them)
        self.frame_performance = tk.Frame(self.root, bg=self.bg_page)
        self.frame_history     = tk.Frame(self.root, bg=self.bg_page)

        self._build_tab_bar()
        self._build_performance_tab()
        self._build_history_tab()
        
        self._switch_tab("performance")
        self._populate_employee_dropdown()

    # ─────────────────────────────────────────────────────────────────
    # STYLES
    # ─────────────────────────────────────────────────────────────────
    def _setup_treeview_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Modern.Treeview",
            background=self.bg_card, fieldbackground=self.bg_card,
            foreground=self.text_dark, rowheight=54, borderwidth=0,
            font=("Segoe UI", 10))
        
        style.configure("Modern.Treeview.Heading",
            background="#FFFFFF", foreground="#6B7280",
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(0, 15))
            
        style.map("Modern.Treeview",
            background=[("selected", "#F3F4F6")],
            foreground=[("selected", self.text_dark)])

    # ─────────────────────────────────────────────────────────────────
    # NEW TAB BAR LOGIC
    # ─────────────────────────────────────────────────────────────────
    def _build_tab_bar(self):
        # Create container for tabs
        self.tab_frame = tk.Frame(self.root, bg=self.bg_page)
        self.tab_frame.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        # Bottom separator line for the tab row
        tk.Frame(self.root, bg=self.border_color, height=1).pack(fill=tk.X, padx=30)

    def _render_tabs(self, active_tab):
        # Clear old tabs
        for widget in self.tab_frame.winfo_children():
            widget.destroy()
            
        def make_tab(text, tab_id):
            is_active = (active_tab == tab_id)
            color = self.primary_blue if is_active else self.text_muted
            font = ("Segoe UI", 11, "bold") if is_active else ("Segoe UI", 11)
            
            btn = tk.Button(self.tab_frame, text=text, font=font, fg=color, bg=self.bg_page,
                            relief="flat", bd=0, cursor="hand2", 
                            activebackground=self.bg_page, activeforeground=self.primary_blue,
                            command=lambda: self._switch_tab(tab_id))
            btn.pack(side=tk.LEFT, padx=(0, 24))
            
            # The sleek blue indicator line
            if is_active:
                tk.Frame(self.tab_frame, bg=self.primary_blue, height=3).place(in_=btn, relx=0, rely=1, y=-2, relwidth=1)

        make_tab("Sales Performance", "performance")
        make_tab("Individual History", "history")

    def _switch_tab(self, tab):
        # Visually update the tabs
        self._render_tabs(tab)
        
        # Hide all frames
        self.frame_performance.pack_forget()
        self.frame_history.pack_forget()
        
        # Show selected frame
        if tab == "performance":
            self.frame_performance.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._load_performance()
            self._refresh_summary()
        else:
            self.frame_history.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._populate_employee_dropdown()

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 1 : PERFORMANCE OVERVIEW ─────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_performance_tab(self):
        # ── Summary cards ─────────────────────────────────────────────
        cards_row = tk.Frame(self.frame_performance, bg=self.bg_page)
        cards_row.pack(fill=tk.X, pady=(0, 18))
        for i in range(3):
            cards_row.columnconfigure(i, weight=1)

        self._card_total_revenue = self._kpi_card(cards_row, 0, "Total Revenue (All)", "💰", "#0EA5E9")
        self._card_total_sales   = self._kpi_card(cards_row, 1, "Total Invoices",      "📄", self.primary_blue)
        self._card_top_seller    = self._kpi_card(cards_row, 2, "Top Seller",          "🏆", self.success)

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = tk.Frame(self.frame_performance, bg=self.bg_page)
        toolbar.pack(fill=tk.X, pady=(0, 12))

        sw = tk.Frame(toolbar, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        sw.pack(side=tk.LEFT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 11),
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT, padx=(10, 0))
        se = tk.Entry(sw, textvariable=self.search_var,
                      font=self.F_NORMAL, bg=self.bg_card, bd=0, width=32,
                      insertbackground=self.text_dark)
        se.pack(side=tk.LEFT, padx=8, ipady=7)
        se.insert(0, "Search employee...")
        se.bind("<FocusIn>", lambda e: se.delete(0, "end") if se.get() == "Search employee..." else None)
        se.bind("<KeyRelease>", lambda e: self._load_performance())

        self._make_btn(toolbar, "↻ Refresh", "#F1F5F9", self.text_dark,
                       cmd=self._load_performance, border=True).pack(side=tk.RIGHT)

        # ── Table ───────────────────────────────────────────────
        tbl_card = tk.Frame(self.frame_performance, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("emp_id", "name", "role", "total_invoices", "total_revenue")
        self.perf_table = ttk.Treeview(tbl_card, columns=cols, show="headings",
                                       style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.perf_table.yview)

        col_cfg = [
            ("emp_id",         "Emp ID",          80, "center"),
            ("name",           "Employee Name",  250, "w"),
            ("role",           "Role",           120, "center"),
            ("total_invoices", "Total Sales",    150, "center"),
            ("total_revenue",  "Total Revenue",  200, "center"),
        ]
        for col, heading, width, anchor in col_cfg:
            self.perf_table.heading(col, text=heading)
            self.perf_table.column(col, width=width, anchor=anchor)

        self.perf_table.tag_configure("row_even", background="#FFFFFF")
        self.perf_table.tag_configure("row_odd",  background="#F9FAFB")
        self.perf_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 2 : INDIVIDUAL HISTORY ───────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_history_tab(self):
        ctrl = tk.Frame(self.frame_history, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(0, 16), ipady=10)

        tk.Label(ctrl, text="Select Employee:", font=self.F_NORMAL, bg=self.bg_card, fg=self.text_dark).pack(side=tk.LEFT, padx=(20, 10))
        
        self.emp_combo = ttk.Combobox(ctrl, textvariable=self.selected_emp_var, state="readonly", font=self.F_NORMAL, width=35)
        self.emp_combo.pack(side=tk.LEFT)
        self.emp_combo.bind("<<ComboboxSelected>>", lambda e: self._load_employee_history())

        self._make_btn(ctrl, "View Details", self.primary_blue, "white", cmd=self._load_employee_history).pack(side=tk.LEFT, padx=10)

        # ── Table ───────────────────────────────────────────────
        tbl_card = tk.Frame(self.frame_history, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("invoice", "date", "customer", "subtotal", "discount", "grandtotal")
        self.hist_table = ttk.Treeview(tbl_card, columns=cols, show="headings",
                                       style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.hist_table.yview)

        col_cfg = [
            ("invoice",    "Invoice No.",   100, "center"),
            ("date",       "Date & Time",   180, "center"),
            ("customer",   "Customer Name",  200, "w"),
            ("subtotal",   "Sub Total",      120, "center"),
            ("discount",   "Discount",       100, "center"),
            ("grandtotal", "Grand Total",    150, "center"),
        ]
        for col, heading, width, anchor in col_cfg:
            self.hist_table.heading(col, text=heading)
            self.hist_table.column(col, width=width, anchor=anchor)

        self.hist_table.tag_configure("row_even", background="#FFFFFF")
        self.hist_table.tag_configure("row_odd",  background="#F9FAFB")
        self.hist_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # ─────────────────────────────────────────────────────────────────
    # DATABASE & LOGIC
    # ─────────────────────────────────────────────────────────────────
    def _refresh_summary(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            # Total Revenue
            cur.execute("SELECT SUM(grand_total) FROM sales")
            rev = cur.fetchone()[0]
            self._card_total_revenue.config(text=f"৳ {float(rev):,.2f}" if rev else "৳ 0.00")

            # Total Sales Count
            cur.execute("SELECT COUNT(invoice_no) FROM sales")
            self._card_total_sales.config(text=str(cur.fetchone()[0]))

            # Top Seller
            cur.execute("""
                SELECT u.name, SUM(s.grand_total) as total 
                FROM sales s 
                JOIN users u ON s.emp_id = u.emp_id 
                GROUP BY s.emp_id 
                ORDER BY total DESC LIMIT 1
            """)
            top = cur.fetchone()
            self._card_top_seller.config(text=top[0] if top else "N/A")
        except Exception as e:
            print("Summary Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_performance(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            q = self.search_var.get().strip()
            
            query = """
                SELECT u.emp_id, u.name, u.role, 
                       COUNT(s.invoice_no) as total_invoices, 
                       SUM(s.grand_total) as total_revenue
                FROM users u
                LEFT JOIN sales s ON u.emp_id = s.emp_id
            """
            params = []
            if q and q != "Search employee...":
                query += " WHERE u.name LIKE %s OR u.emp_id LIKE %s "
                params.extend([f"%{q}%", f"%{q}%"])
            
            query += " GROUP BY u.emp_id, u.name, u.role ORDER BY total_revenue DESC"
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            self.perf_table.delete(*self.perf_table.get_children())
            for i, row in enumerate(rows):
                emp_id, name, role, inv_count, rev = row
                rev_str = f"৳ {float(rev):,.2f}" if rev else "৳ 0.00"
                tag = "row_even" if i % 2 == 0 else "row_odd"
                
                self.perf_table.insert("", tk.END,
                    values=(emp_id, f"  👤 {name}", f"[{role}]", inv_count, rev_str),
                    tags=(tag,))
        except Exception as e:
            print("Performance Load Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _populate_employee_dropdown(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("SELECT emp_id, name FROM users ORDER BY name ASC")
            rows = cur.fetchall()
            self.emp_dict.clear()
            options = []
            for r in rows:
                label = f"{r[1]} (ID: {r[0]})"
                self.emp_dict[label] = r[0]
                options.append(label)
            
            self.emp_combo['values'] = options
            if options:
                self.emp_combo.current(0)
        except Exception as e:
            print("Dropdown Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_employee_history(self):
        selection = self.selected_emp_var.get()
        if not selection or selection not in self.emp_dict:
            return
            
        emp_id = self.emp_dict[selection]
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT invoice_no, sale_date, sale_time, customer_name, sub_total, total_discount, grand_total
                FROM sales 
                WHERE emp_id = %s 
                ORDER BY sale_date DESC, sale_time DESC
            """, (emp_id,))
            rows = cur.fetchall()

            self.hist_table.delete(*self.hist_table.get_children())
            for i, row in enumerate(rows):
                inv, s_date, s_time, cust, sub, disc, grand = row
                
                # Format Date & Time properly
                dt_str = f"{s_date} {s_time}" if s_date else "—"
                cust = cust if cust else "Walk-in Customer"
                
                tag = "row_even" if i % 2 == 0 else "row_odd"
                
                self.hist_table.insert("", tk.END,
                    values=(inv, dt_str, f"  {cust}", 
                            f"৳ {float(sub):,.2f}", 
                            f"৳ {float(disc):,.2f}", 
                            f"৳ {float(grand):,.2f}"),
                    tags=(tag,))
        except Exception as e:
            print("History Load Error:", e)
        finally:
            if con.is_connected(): con.close()

    # ─────────────────────────────────────────────────────────────────
    # REUSABLE UI HELPERS
    # ─────────────────────────────────────────────────────────────────
    def _kpi_card(self, parent, col, title, icon, icon_color):
        # Adjusted height to 85 (down from 110) for better proportions
        card = tk.Frame(parent, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, height=85)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0))
        card.pack_propagate(False)

        top = tk.Frame(card, bg=self.bg_card)
        top.pack(fill=tk.X, padx=16, pady=(10, 2)) # Adjusted top padding to fit smaller height
        tk.Label(top, text=title, font=self.F_CARD_T, bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT)
        tk.Label(top, text=icon, font=("Segoe UI", 14), bg=self.bg_card, fg=icon_color).pack(side=tk.RIGHT)

        val_lbl = tk.Label(card, text="—", font=self.F_CARD_V, bg=self.bg_card, fg=self.text_dark)
        val_lbl.pack(anchor="w", padx=16)
        return val_lbl

    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.F_BTN, bg=bg, fg=fg,
                  relief="flat", bd=0, cursor="hand2",
                  padx=18, pady=7,
                  activebackground=bg, activeforeground=fg)
        if border:
            kw["highlightbackground"] = self.border_color
            kw["highlightthickness"]  = 1
        if cmd: kw["command"] = cmd
        return tk.Button(parent, **kw)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("IMS - Employee Sales Performance")
    root.state("zoomed")
    app = EmployeeSalesClass(root)
    root.mainloop()