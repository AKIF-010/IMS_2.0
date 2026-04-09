import tkinter as tk
from tkinter import ttk, messagebox
import db_config
import datetime
import math


class SalesClass:
    def __init__(self, content_area):
        self.root = content_area
        self.root.config(bg="#F3F4F6")

        # ── Unified palette ───────────────────────────────────────────
        self.bg_page      = "#F3F4F6"
        self.bg_card      = "#FFFFFF"
        self.text_dark    = "#111827"
        self.text_muted   = "#6B7280"
        self.border_color = "#E5E7EB"
        self.primary_blue = "#2563EB"
        self.success      = "#10B981"
        self.danger       = "#EF4444"
        self.orange       = "#F59E0B"
        self.input_bg     = "#F9FAFB"

        # ── Font stack ────────────────────────────────────────────────
        self.FT  = ("Segoe UI", 14, "bold")
        self.FN  = ("Segoe UI", 10)
        self.FNB = ("Segoe UI", 10, "bold")
        self.FS  = ("Segoe UI",  9)
        self.FSB = ("Segoe UI",  9, "bold")

        # ── Cart dictionary  {pid: {details + ui refs}} ───────────────
        self.cart_dictionary = {}

        self._setup_style()
        self._build_ui()

    # ═══════════════════════════════════════════════════════════════════
    # STYLE
    # ═══════════════════════════════════════════════════════════════════
    def _setup_style(self):
        s = ttk.Style()
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("Modern.Treeview",
            background=self.bg_card, fieldbackground=self.bg_card,
            foreground=self.text_dark, rowheight=46, borderwidth=0,
            font=self.FN)
        s.configure("Modern.Treeview.Heading",
            background="#F8FAFC", foreground="#475569",
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(12, 10))
        s.map("Modern.Treeview",
            background=[("selected", "#EFF6FF")],
            foreground=[("selected", self.primary_blue)])

    # ═══════════════════════════════════════════════════════════════════
    # BUILD UI
    # ═══════════════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Underline tab bar ─────────────────────────────────────────
        self.tab_frame = tk.Frame(self.root, bg=self.bg_page)
        self.tab_frame.pack(fill=tk.X, padx=30, pady=(20, 0))
        tk.Frame(self.root, bg=self.border_color,
                 height=1).pack(fill=tk.X, padx=30)

        # ── Content frames ─────────────────────────────────────────────
        self.frame_new_sale = tk.Frame(self.root, bg=self.bg_page)
        self.frame_history  = tk.Frame(self.root, bg=self.bg_page)
        self.frame_invoice  = tk.Frame(self.root, bg=self.bg_page)

        # ── Build pages ────────────────────────────────────────────────
        self._build_new_sale_page()
        self._build_history_page()
        self._build_invoice_page()

        # ── Show default tab ───────────────────────────────────────────
        self._show_tab("new_sale")

    # ─────────────────────────────────────────────────────────────────
    # UNDERLINE TAB SWITCHING
    # ─────────────────────────────────────────────────────────────────
    def _render_tabs(self, active):
        for w in self.tab_frame.winfo_children():
            w.destroy()
        for text, tab_id in [
            ("New Sale",      "new_sale"),
            ("Sales History", "history"),
            ("Invoice / Bill","invoice"),
        ]:
            is_active = (active == tab_id)
            btn = tk.Button(
                self.tab_frame, text=text,
                font=("Segoe UI", 11, "bold") if is_active else ("Segoe UI", 11),
                fg=self.primary_blue if is_active else self.text_muted,
                bg=self.bg_page, relief="flat", bd=0, cursor="hand2",
                activebackground=self.bg_page,
                activeforeground=self.primary_blue,
                command=lambda t=tab_id: self._show_tab(t))
            btn.pack(side=tk.LEFT, padx=(0, 24))
            if is_active:
                tk.Frame(self.tab_frame, bg=self.primary_blue,
                         height=3).place(in_=btn, relx=0, rely=1,
                                         y=-2, relwidth=1)

    def _show_tab(self, tab):
        self._render_tabs(tab)
        self.frame_new_sale.pack_forget()
        self.frame_history.pack_forget()
        self.frame_invoice.pack_forget()

        if tab == "new_sale":
            self.frame_new_sale.pack(fill=tk.BOTH, expand=True)
        elif tab == "history":
            self.frame_history.pack(fill=tk.BOTH, expand=True)
            if hasattr(self, "history_table"):
                self.load_history()
        else:
            self.frame_invoice.pack(fill=tk.BOTH, expand=True)

    # ═══════════════════════════════════════════════════════════════════
    # PAGE 1 — NEW SALE (POS)
    # ═══════════════════════════════════════════════════════════════════
    def _build_new_sale_page(self):
        # ── Left: product search panel ────────────────────────────────
        left = tk.Frame(self.frame_new_sale, bg=self.bg_card,
                        highlightbackground=self.border_color, highlightthickness=1)
        left.place(relx=0, rely=0, relwidth=0.60, relheight=1)

        search_row = tk.Frame(left, bg=self.bg_card)
        search_row.pack(fill=tk.X, padx=16, pady=(14, 8))
        tk.Label(search_row, text="Search Product:",
                 font=self.FSB, bg=self.bg_card,
                 fg=self.text_muted).pack(side=tk.LEFT, padx=(0, 8))

        sw = tk.Frame(search_row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        sw.pack(side=tk.LEFT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.text_muted).pack(
            side=tk.LEFT, padx=(8, 0))
        self.search_entry = tk.Entry(sw, font=self.FN, bg=self.bg_card,
                                     bd=0, width=28,
                                     insertbackground=self.text_dark)
        self.search_entry.pack(side=tk.LEFT, padx=6, ipady=6)
        self.search_entry.bind("<KeyRelease>", self.search_products)

        self._make_btn(search_row, "Search", self.success, "white",
                       cmd=self.search_products).pack(side=tk.LEFT, padx=8)

        # Product treeview
        tbl_f = tk.Frame(left, bg=self.bg_card)
        tbl_f.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        scroll_y = ttk.Scrollbar(tbl_f, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.product_table = ttk.Treeview(
            tbl_f,
            columns=("pid", "barcode", "name", "stock", "price", "tax"),
            show="headings", style="Modern.Treeview",
            yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.product_table.yview)

        for col, hd, w, anc in [
            ("pid",     "ID",          50,  "center"),
            ("barcode", "Barcode",     90,  "center"),
            ("name",    "Product Name",180, "w"),
            ("stock",   "Stock",       60,  "center"),
            ("price",   "Price (৳)",   80,  "e"),
            ("tax",     "VAT (%)",     70,  "center"),
        ]:
            self.product_table.heading(col, text=hd)
            self.product_table.column(col, width=w, anchor=anc)

        self.product_table.pack(fill=tk.BOTH, expand=True)
        self.product_table.bind("<Double-1>", self.add_to_cart)

        tk.Label(left, text="💡 Double-click a product to add to cart",
                 font=("Segoe UI", 8, "italic"),
                 bg=self.bg_card, fg=self.text_muted).pack(
            anchor="w", padx=16, pady=(0, 8))

        # ── Right: cart panel ─────────────────────────────────────────
        right = tk.Frame(self.frame_new_sale, bg=self.bg_card,
                         highlightbackground=self.border_color,
                         highlightthickness=1)
        right.place(relx=0.61, rely=0, relwidth=0.39, relheight=1)

        # Cart header
        cart_hdr = tk.Frame(right, bg=self.bg_card)
        cart_hdr.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(14, 6))
        tk.Label(cart_hdr, text="Current Cart",
                 font=self.FNB, bg=self.bg_card,
                 fg=self.text_dark).pack(side=tk.LEFT)
        self.lbl_items_count = tk.Label(cart_hdr, text="(0 Items)",
                                        font=self.FS, bg=self.bg_card,
                                        fg=self.text_muted)
        self.lbl_items_count.pack(side=tk.LEFT, padx=(5, 0))
        tk.Button(cart_hdr, text="🗑️ Clear",
                  font=self.FSB, bg=self.bg_card, fg=self.danger,
                  relief="flat", bd=0, cursor="hand2",
                  command=self.clear_cart).pack(side=tk.RIGHT)

        tk.Frame(right, bg=self.border_color, height=1).pack(fill=tk.X, padx=16)

        # Customer info
        cust_f = tk.Frame(right, bg=self.input_bg,
                          highlightbackground=self.border_color,
                          highlightthickness=1)
        cust_f.pack(side=tk.TOP, fill=tk.X, padx=16, pady=8)

        for row_idx, (lbl, attr) in enumerate([
            ("Customer Name",  "ent_cus_name"),
            ("Phone Number",   "ent_cus_phone"),
        ]):
            tk.Label(cust_f, text=lbl + ":", font=self.FS,
                     bg=self.input_bg, fg=self.text_muted).grid(
                row=row_idx, column=0, sticky="w", padx=(10, 6), pady=4)
            ent = tk.Entry(cust_f, font=self.FN, bg=self.bg_card,
                           highlightbackground=self.border_color,
                           highlightthickness=1, relief="flat", width=22)
            ent.grid(row=row_idx, column=1, padx=(0, 10), pady=4, ipady=4)
            setattr(self, attr, ent)

        # Calculation panel (packed to BOTTOM first so it never disappears)
        calc = tk.Frame(right, bg=self.bg_card)
        calc.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 12))

        for lbl_text, attr in [
            ("Subtotal",       "lbl_subtotal"),
            ("Total Tax (VAT)","lbl_tax"),
        ]:
            r = tk.Frame(calc, bg=self.bg_card)
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=lbl_text, font=self.FN,
                     bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT)
            lbl = tk.Label(r, text="৳ 0.00", font=self.FNB,
                           bg=self.bg_card, fg=self.text_dark)
            lbl.pack(side=tk.RIGHT)
            setattr(self, attr, lbl)

        disc_row = tk.Frame(calc, bg=self.bg_card)
        disc_row.pack(fill=tk.X, pady=2)
        tk.Label(disc_row, text="Discount", font=self.FN,
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT)
        disc_box = tk.Frame(disc_row, bg=self.bg_card,
                            highlightbackground=self.border_color,
                            highlightthickness=1)
        disc_box.pack(side=tk.RIGHT)
        tk.Label(disc_box, text="৳", font=self.FS,
                 bg=self.input_bg, fg=self.text_muted).pack(
            side=tk.LEFT, fill=tk.Y, padx=6)
        self.ent_discount = tk.Entry(disc_box, width=8, font=self.FN,
                                     bd=0, justify=tk.RIGHT,
                                     insertbackground=self.text_dark)
        self.ent_discount.insert(0, "0")
        self.ent_discount.pack(side=tk.LEFT, padx=4, pady=3)
        self.ent_discount.bind("<KeyRelease>", self.update_totals)

        ttk.Separator(calc, orient="horizontal").pack(fill=tk.X, pady=6)

        grand_row = tk.Frame(calc, bg="#EFF6FF")
        grand_row.pack(fill=tk.X, pady=2)
        tk.Label(grand_row, text="Grand Total",
                 font=("Segoe UI", 13, "bold"),
                 bg="#EFF6FF", fg="#1E3A8A").pack(side=tk.LEFT, padx=10, pady=6)
        self.lbl_grand_total = tk.Label(grand_row, text="৳ 0.00",
                                        font=("Segoe UI", 17, "bold"),
                                        bg="#EFF6FF", fg=self.primary_blue)
        self.lbl_grand_total.pack(side=tk.RIGHT, padx=10)

        pay_row = tk.Frame(calc, bg=self.bg_card)
        pay_row.pack(fill=tk.X, pady=5)

        pay_box = tk.Frame(pay_row, bg=self.bg_card)
        pay_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(pay_box, text="Payment Amount", font=self.FS,
                 bg=self.bg_card, fg=self.text_muted).pack(anchor="w")
        p_in = tk.Frame(pay_box, bg=self.bg_card,
                        highlightbackground=self.border_color,
                        highlightthickness=1)
        p_in.pack(fill=tk.X)
        tk.Label(p_in, text="৳", font=self.FS,
                 bg=self.input_bg, fg=self.text_muted).pack(
            side=tk.LEFT, fill=tk.Y, padx=6)
        self.ent_payment = tk.Entry(p_in, font=self.FNB, bd=0,
                                    justify=tk.RIGHT,
                                    insertbackground=self.text_dark)
        self.ent_payment.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)
        self.ent_payment.bind("<KeyRelease>", self.calculate_change)

        chg_box = tk.Frame(pay_row, bg=self.bg_card)
        chg_box.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(chg_box, text="Return Change", font=self.FS,
                 bg=self.bg_card, fg=self.text_muted).pack(anchor="w")
        c_val = tk.Frame(chg_box, bg="#ECFDF5",
                         highlightbackground="#A7F3D0",
                         highlightthickness=1)
        c_val.pack(fill=tk.X)
        self.lbl_change = tk.Label(c_val, text="৳ 0.00",
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#ECFDF5", fg="#047857", pady=5)
        self.lbl_change.pack(fill=tk.X)

        btn_row = tk.Frame(calc, bg=self.bg_card)
        btn_row.pack(fill=tk.X, pady=(6, 0))
        tk.Button(btn_row, text="Clear Cart",
                  font=self.FNB, bg="#FEE2E2", fg="#B91C1C",
                  relief="flat", bd=0, pady=8, cursor="hand2",
                  command=self.clear_cart).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Button(btn_row, text="✓  Confirm Sale",
                  font=self.FNB, bg=self.success, fg="white",
                  relief="flat", bd=0, pady=8, cursor="hand2",
                  command=self.confirm_sale).pack(
            side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

        # Scrollable cart area (packed last — fills remaining space)
        self.cart_canvas = tk.Canvas(right, bg=self.bg_card, bd=0,
                                     highlightthickness=0)
        self.cart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                              padx=16, pady=(0, 8))
        cart_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL,
                                    command=self.cart_canvas.yview)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8))
        self.cart_canvas.config(yscrollcommand=cart_scroll.set)

        self.cart_inner_frame = tk.Frame(self.cart_canvas, bg=self.bg_card)
        self.cart_canvas_win  = self.cart_canvas.create_window(
            (0, 0), window=self.cart_inner_frame, anchor="nw",
            width=self.cart_canvas.winfo_reqwidth())

        self.cart_inner_frame.bind("<Configure>",
            lambda e: self.cart_canvas.configure(
                scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>",
            lambda e: self.cart_canvas.itemconfig(
                self.cart_canvas_win, width=e.width))

        self.fetch_products()

    # ═══════════════════════════════════════════════════════════════════
    # PAGE 2 — SALES HISTORY
    # ═══════════════════════════════════════════════════════════════════
    def _build_history_page(self):
        # Search bar
        top = tk.Frame(self.frame_history, bg=self.bg_card,
                       highlightbackground=self.border_color, highlightthickness=1)
        top.pack(fill=tk.X, padx=30, pady=(16, 0))

        sf = tk.Frame(top, bg=self.bg_card)
        sf.pack(side=tk.LEFT, padx=16, pady=10)
        tk.Label(sf, text="Search Invoice / Customer:",
                 font=self.FSB, bg=self.bg_card,
                 fg=self.text_muted).pack(side=tk.LEFT, padx=(0, 8))

        sw = tk.Frame(sf, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        sw.pack(side=tk.LEFT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.text_muted).pack(
            side=tk.LEFT, padx=(8, 0))
        self.search_history_ent = tk.Entry(
            sw, font=self.FN, bg=self.bg_card, bd=0, width=26,
            insertbackground=self.text_dark)
        self.search_history_ent.pack(side=tk.LEFT, padx=6, ipady=6)
        self.search_history_ent.bind("<KeyRelease>", self.search_history)

        self._make_btn(sf, "Search", self.primary_blue, "white",
                       cmd=self.search_history).pack(side=tk.LEFT, padx=8)
        self._make_btn(sf, "Show All", "#6B7280", "white",
                       cmd=self.load_history).pack(side=tk.LEFT)

        # Master sales table
        mid = tk.Frame(self.frame_history, bg=self.bg_card,
                       highlightbackground=self.border_color, highlightthickness=1)
        mid.pack(fill=tk.BOTH, expand=True, padx=30, pady=(12, 6))

        mid_hdr = tk.Frame(mid, bg=self.bg_card)
        mid_hdr.pack(fill=tk.X, padx=16, pady=(10, 4))
        tk.Label(mid_hdr, text="Sales Records",
                 font=self.FNB, bg=self.bg_card,
                 fg=self.text_dark).pack(side=tk.LEFT)
        tk.Label(mid_hdr, text="Click a row to see items",
                 font=self.FS, bg=self.bg_card,
                 fg=self.text_muted).pack(side=tk.LEFT, padx=12)

        scroll_y = ttk.Scrollbar(mid, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_table = ttk.Treeview(
            mid,
            columns=("inv", "date", "time", "cust", "phone", "total"),
            show="headings", style="Modern.Treeview",
            yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.history_table.yview)

        for col, hd, w, anc in [
            ("inv",   "Invoice No",  90,  "center"),
            ("date",  "Date",        110, "center"),
            ("time",  "Time",        100, "center"),
            ("cust",  "Customer",    200, "w"),
            ("phone", "Phone",       120, "center"),
            ("total", "Grand Total", 130, "e"),
        ]:
            self.history_table.heading(col, text=hd)
            self.history_table.column(col, width=w, anchor=anc)

        self.history_table.tag_configure("row_even", background="#FFFFFF")
        self.history_table.tag_configure("row_odd",  background="#F9FAFB")
        self.history_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.history_table.bind("<ButtonRelease-1>", self.load_history_details)

        # Detail items table
        bot = tk.Frame(self.frame_history, bg=self.bg_card,
                       highlightbackground=self.border_color, highlightthickness=1)
        bot.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 16))

        bot_hdr = tk.Frame(bot, bg=self.bg_card)
        bot_hdr.pack(fill=tk.X, padx=16, pady=(10, 4))
        self.lbl_detail_title = tk.Label(
            bot_hdr, text="Invoice Details",
            font=self.FNB, bg=self.bg_card, fg=self.text_dark)
        self.lbl_detail_title.pack(side=tk.LEFT)

        scroll_d = ttk.Scrollbar(bot, orient=tk.VERTICAL)
        scroll_d.pack(side=tk.RIGHT, fill=tk.Y)

        self.detail_table = ttk.Treeview(
            bot,
            columns=("pid", "name", "qty", "price", "total"),
            show="headings", style="Modern.Treeview",
            yscrollcommand=scroll_d.set)
        scroll_d.config(command=self.detail_table.yview)

        for col, hd, w, anc in [
            ("pid",   "PID",         60,  "center"),
            ("name",  "Product",     260, "w"),
            ("qty",   "Qty",         80,  "center"),
            ("price", "Unit Price",  110, "e"),
            ("total", "Line Total",  110, "e"),
        ]:
            self.detail_table.heading(col, text=hd)
            self.detail_table.column(col, width=w, anchor=anc)

        self.detail_table.tag_configure("row_even", background="#FFFFFF")
        self.detail_table.tag_configure("row_odd",  background="#F9FAFB")
        self.detail_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # ═══════════════════════════════════════════════════════════════════
    # PAGE 3 — INVOICE (placeholder)
    # ═══════════════════════════════════════════════════════════════════
    def _build_invoice_page(self):
        tk.Label(self.frame_invoice, text="Invoice / Bill",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.bg_page, fg=self.text_dark).pack(pady=40)
        tk.Label(self.frame_invoice,
                 text="Select an invoice from Sales History to view the bill.",
                 font=self.FN, bg=self.bg_page, fg=self.text_muted).pack()

    # ═══════════════════════════════════════════════════════════════════
    # PRODUCT DATABASE
    # ═══════════════════════════════════════════════════════════════════
    def fetch_products(self):
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT pid, barcode, name, stock, sale_price, tax_vat
                FROM products WHERE status='Active'
            """)
            rows = cur.fetchall()
            self.product_table.delete(*self.product_table.get_children())
            for row in rows:
                r = list(row)
                r[1] = r[1] or "N/A"
                self.product_table.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    def search_products(self, event=None):
        val = self.search_entry.get().strip()
        if not val:
            self.fetch_products()
            return
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            wc  = f"%{val}%"
            cur.execute("""
                SELECT pid, barcode, name, stock, sale_price, tax_vat
                FROM products
                WHERE status='Active'
                  AND (name LIKE %s OR barcode LIKE %s
                       OR sku LIKE %s OR pid LIKE %s)
            """, (wc, wc, wc, wc))
            rows = cur.fetchall()
            self.product_table.delete(*self.product_table.get_children())
            for row in rows:
                r    = list(row)
                r[1] = r[1] or "N/A"
                self.product_table.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # CART OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    def add_to_cart(self, event=None):
        sel = self.product_table.focus()
        if not sel:
            return
        row_data  = self.product_table.item(sel, "values")
        pid_key   = int(row_data[0])
        name      = row_data[2]
        stock     = int(row_data[3])
        price     = float(row_data[4])
        tax_pct   = float(row_data[5])

        if pid_key in self.cart_dictionary:
            self.qty_change(pid_key, is_increment=True)
            return

        if stock <= 0:
            messagebox.showwarning("Out of Stock", f"{name} is out of stock!")
            return

        item_data = {"name": name, "unit_price": price,
                     "tax_pct": tax_pct, "qty_var": 1, "stock_max": stock}
        card_refs = self._create_cart_card(pid_key, item_data)
        item_data.update(card_refs)
        self.cart_dictionary[pid_key] = item_data
        self.update_totals()

    def qty_change(self, pid_key, is_increment):
        item       = self.cart_dictionary[pid_key]
        current_qty= item["qty_var"]
        if is_increment:
            if current_qty >= item["stock_max"]:
                messagebox.showwarning("Stock Limit",
                    f"Only {item['stock_max']} units available.")
                return
            new_qty = current_qty + 1
        else:
            if current_qty <= 1:
                return
            new_qty = current_qty - 1
        item["qty_var"] = new_qty
        item["lbl_qty_ref"].config(text=str(new_qty))
        item["lbl_line_total_ref"].config(
            text=f"৳ {new_qty * item['unit_price']:,.0f}")
        self.update_totals()

    def remove_cart_item(self, pid_key):
        self.cart_dictionary[pid_key]["card_frame_ref"].destroy()
        del self.cart_dictionary[pid_key]
        self.update_totals()

    def clear_cart(self):
        for pid in list(self.cart_dictionary.keys()):
            self.remove_cart_item(pid)

    def update_totals(self, event=None):
        pre_tax = sum(d["qty_var"] * d["unit_price"]
                      for d in self.cart_dictionary.values())
        vat     = sum(d["qty_var"] * d["unit_price"] * d["tax_pct"] / 100.0
                      for d in self.cart_dictionary.values())
        try:
            discount = float(self.ent_discount.get() or 0)
        except ValueError:
            discount = 0.0
        grand = max(0.0, math.ceil(pre_tax + vat - discount))

        self.lbl_subtotal.config(text=f"৳ {pre_tax:,.2f}")
        self.lbl_tax.config(text=f"৳ {vat:,.2f}")
        self.lbl_grand_total.config(text=f"৳ {grand:,.0f}")
        self.lbl_items_count.config(
            text=f"({len(self.cart_dictionary)} Item"
                 f"{'s' if len(self.cart_dictionary) != 1 else ''})")
        self.calculate_change()

    def calculate_change(self, event=None):
        try:
            pre_tax  = sum(d["qty_var"] * d["unit_price"]
                           for d in self.cart_dictionary.values())
            vat      = sum(d["qty_var"] * d["unit_price"] * d["tax_pct"] / 100.0
                           for d in self.cart_dictionary.values())
            discount = float(self.ent_discount.get() or 0)
            grand    = max(0.0, math.ceil(pre_tax + vat - discount))
            payment  = float(self.ent_payment.get() or 0)
            change   = max(0.0, payment - grand)
            self.lbl_change.config(text=f"৳ {change:,.2f}")
        except ValueError:
            self.lbl_change.config(text="৳ 0.00")

    def _create_cart_card(self, pid_key, item_details):
        card = tk.Frame(self.cart_inner_frame, bg=self.bg_card)
        card.pack(fill=tk.X, anchor="w", pady=(0, 10))

        # Name + unit price
        l1 = tk.Frame(card, bg=self.bg_card)
        l1.pack(fill=tk.X)
        tk.Label(l1, text=item_details["name"],
                 font=self.FNB, bg=self.bg_card,
                 fg=self.text_dark, anchor="w").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(l1, text=f"৳ {item_details['unit_price']:,.0f} / unit",
                 font=self.FS, bg=self.bg_card,
                 fg=self.text_muted).pack(side=tk.RIGHT)

        # Controls
        l2 = tk.Frame(card, bg=self.bg_card)
        l2.pack(fill=tk.X, pady=4)

        qty_outer = tk.Frame(l2, bg="#F3F4F6")
        qty_outer.pack(side=tk.LEFT)
        tk.Button(qty_outer, text="−", font=self.FNB,
                  bg="#F3F4F6", fg=self.text_muted,
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  command=lambda: self.qty_change(pid_key, is_increment=False)
                  ).pack(side=tk.LEFT, pady=2)
        qty_lbl = tk.Label(qty_outer, text="1", font=self.FNB,
                           bg="#F3F4F6", fg=self.text_dark, padx=8)
        qty_lbl.pack(side=tk.LEFT)
        tk.Button(qty_outer, text="+", font=self.FNB,
                  bg="#F3F4F6", fg=self.text_muted,
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  command=lambda: self.qty_change(pid_key, is_increment=True)
                  ).pack(side=tk.LEFT, pady=2)

        tk.Button(l2, text="✕", font=("Segoe UI", 11),
                  bg=self.bg_card, fg=self.danger,
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: self.remove_cart_item(pid_key)
                  ).pack(side=tk.RIGHT)

        line_lbl = tk.Label(l2,
                            text=f"৳ {item_details['unit_price']:,.0f}",
                            font=("Segoe UI", 11, "bold"),
                            bg=self.bg_card, fg=self.text_dark)
        line_lbl.pack(side=tk.RIGHT, padx=8)

        tk.Frame(card, bg=self.border_color, height=1).pack(
            fill=tk.X, pady=(4, 0))

        return {"card_frame_ref":    card,
                "lbl_qty_ref":       qty_lbl,
                "lbl_line_total_ref":line_lbl}

    # ═══════════════════════════════════════════════════════════════════
    # CONFIRM SALE
    # ═══════════════════════════════════════════════════════════════════
    def confirm_sale(self):
        if not self.cart_dictionary:
            messagebox.showerror("Error", "Cart is empty. Add products first.")
            return

        c_name  = self.ent_cus_name.get().strip()
        c_phone = self.ent_cus_phone.get().strip()

        pre_tax = sum(d["qty_var"] * d["unit_price"]
                      for d in self.cart_dictionary.values())
        vat     = sum(d["qty_var"] * d["unit_price"] * d["tax_pct"] / 100.0
                      for d in self.cart_dictionary.values())
        try:
            discount = float(self.ent_discount.get() or 0)
        except ValueError:
            discount = 0.0
        grand = max(0.0, math.ceil(pre_tax + vat - discount))

        try:
            payment = float(self.ent_payment.get() or 0)
        except ValueError:
            payment = 0.0

        if payment < grand:
            messagebox.showwarning("Insufficient Payment",
                "Payment amount is less than the Grand Total.")
            return

        now       = datetime.datetime.now()
        sale_date = now.strftime("%Y-%m-%d")
        sale_time = now.strftime("%H:%M:%S")

        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO sales
                  (emp_id, customer_name, customer_phone,
                   sale_date, sale_time, sub_total,
                   total_discount, total_vat, grand_total)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (c_name, c_phone, sale_date, sale_time,
                  pre_tax, discount, vat, grand))
            inv_no = cur.lastrowid

            for pid, item in self.cart_dictionary.items():
                qty        = item["qty_var"]
                unit_price = item["unit_price"]
                cur.execute("""
                    INSERT INTO sales_items
                      (invoice_no, pid, qty, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (inv_no, pid, qty, unit_price, qty * unit_price))
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE pid = %s",
                    (qty, pid))

            con.commit()
            messagebox.showinfo("Success",
                f"Sale Complete!  Invoice No: #{inv_no}")

            self.clear_cart()
            self.ent_cus_name.delete(0, tk.END)
            self.ent_cus_phone.delete(0, tk.END)
            self.ent_discount.delete(0, tk.END)
            self.ent_discount.insert(0, "0")
            self.ent_payment.delete(0, tk.END)
            self.lbl_change.config(text="৳ 0.00")
            self.fetch_products()

        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to save sale:\n{e}")
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # HISTORY DATABASE
    # ═══════════════════════════════════════════════════════════════════
    def load_history(self):
        self.search_history_ent.delete(0, tk.END)
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT invoice_no, sale_date, sale_time,
                       customer_name, customer_phone, grand_total
                FROM sales ORDER BY invoice_no DESC
            """)
            rows = cur.fetchall()
            self.history_table.delete(*self.history_table.get_children())
            for i, row in enumerate(rows):
                tag = "row_even" if i % 2 == 0 else "row_odd"
                self.history_table.insert("", tk.END, values=row, tags=(tag,))
            self.detail_table.delete(*self.detail_table.get_children())
            self.lbl_detail_title.config(text="Invoice Details")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    def search_history(self, event=None):
        val = self.search_history_ent.get().strip()
        if not val:
            self.load_history()
            return
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            inv_no   = int(val) if val.isdigit() else -1
            wildcard = f"%{val}%"
            cur.execute("""
                SELECT invoice_no, sale_date, sale_time,
                       customer_name, customer_phone, grand_total
                FROM sales
                WHERE invoice_no = %s
                   OR customer_name  LIKE %s
                   OR customer_phone LIKE %s
                ORDER BY invoice_no DESC
            """, (inv_no, wildcard, wildcard))
            rows = cur.fetchall()
            self.history_table.delete(*self.history_table.get_children())
            for i, row in enumerate(rows):
                tag = "row_even" if i % 2 == 0 else "row_odd"
                self.history_table.insert("", tk.END, values=row, tags=(tag,))
            self.detail_table.delete(*self.detail_table.get_children())
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    def load_history_details(self, event=None):
        sel = self.history_table.focus()
        if not sel:
            return
        inv_no = self.history_table.item(sel, "values")[0]
        self.lbl_detail_title.config(
            text=f"Invoice Details  —  Invoice #{inv_no}")
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT s.pid, p.name, s.qty, s.unit_price, s.total_price
                FROM sales_items s
                LEFT JOIN products p ON s.pid = p.pid
                WHERE s.invoice_no = %s
            """, (inv_no,))
            rows = cur.fetchall()
            self.detail_table.delete(*self.detail_table.get_children())
            for i, row in enumerate(rows):
                tag = "row_even" if i % 2 == 0 else "row_odd"
                self.detail_table.insert("", tk.END, values=row, tags=(tag,))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # BUTTON HELPER
    # ═══════════════════════════════════════════════════════════════════
    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.FNB, bg=bg, fg=fg,
                  relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=6,
                  activebackground=bg, activeforeground=fg)
        if border:
            kw["highlightbackground"] = self.border_color
            kw["highlightthickness"]  = 1
        if cmd:
            kw["command"] = cmd
        return tk.Button(parent, **kw)


# ── standalone test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("IMS – Sales / POS")
    root.state("zoomed")
    SalesClass(root)
    root.mainloop()