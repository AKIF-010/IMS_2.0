import tkinter as tk
from tkinter import ttk, messagebox
import db_config


class PurchaseClass:
    def __init__(self, main_frame):
        self.main_frame = main_frame

        # ── Unified palette (identical to every other page) ───────────
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

        # ── Font stack ─────────────────────────────────────────────────
        self.FT  = ("Segoe UI", 16, "bold")
        self.FN  = ("Segoe UI", 10)
        self.FNB = ("Segoe UI", 10, "bold")
        self.FS  = ("Segoe UI",  9)
        self.FSB = ("Segoe UI",  9, "bold")

        # ── State ──────────────────────────────────────────────────────
        self.cart_items   = {}
        self.supplier_list= []

        self._setup_treeview_style()

        # Tab content frames
        self.frame_new     = tk.Frame(self.main_frame, bg=self.bg_page)
        self.frame_history = tk.Frame(self.main_frame, bg=self.bg_page)

        self._build_tab_bar()
        self._build_new_purchase_page()
        self._build_history_page()
        self._switch_tab("new")

    # ═══════════════════════════════════════════════════════════════════
    # STYLE
    # ═══════════════════════════════════════════════════════════════════
    def _setup_treeview_style(self):
        s = ttk.Style()
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("Modern.Treeview",
            background=self.bg_card, fieldbackground=self.bg_card,
            foreground=self.text_dark, rowheight=46, borderwidth=0,
            font=self.FN if hasattr(self, "FN") else ("Segoe UI", 10))
        s.configure("Modern.Treeview.Heading",
            background="#F8FAFC", foreground="#475569",
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(12, 10))
        s.map("Modern.Treeview",
            background=[("selected", "#EFF6FF")],
            foreground=[("selected", self.primary_blue)])

    # ═══════════════════════════════════════════════════════════════════
    # UNDERLINE TAB BAR  (matches suppliers.py / employees.py)
    # ═══════════════════════════════════════════════════════════════════
    def _build_tab_bar(self):
        self.tab_frame = tk.Frame(self.main_frame, bg=self.bg_page)
        self.tab_frame.pack(fill=tk.X, padx=30, pady=(20, 0))
        tk.Frame(self.main_frame, bg=self.border_color,
                 height=1).pack(fill=tk.X, padx=30)

    def _render_tabs(self, active):
        for w in self.tab_frame.winfo_children():
            w.destroy()

        for text, tab_id in [("New Purchase", "new"),
                              ("Purchase History", "history")]:
            is_active = (active == tab_id)
            btn = tk.Button(
                self.tab_frame, text=text,
                font=("Segoe UI", 11, "bold") if is_active else ("Segoe UI", 11),
                fg=self.primary_blue if is_active else self.text_muted,
                bg=self.bg_page, relief="flat", bd=0, cursor="hand2",
                activebackground=self.bg_page,
                activeforeground=self.primary_blue,
                command=lambda t=tab_id: self._switch_tab(t))
            btn.pack(side=tk.LEFT, padx=(0, 24))
            if is_active:
                tk.Frame(self.tab_frame, bg=self.primary_blue,
                         height=3).place(in_=btn, relx=0, rely=1,
                                         y=-2, relwidth=1)

    def _switch_tab(self, tab):
        self._render_tabs(tab)
        self.frame_new.pack_forget()
        self.frame_history.pack_forget()
        if tab == "new":
            self.frame_new.pack(fill=tk.BOTH, expand=True,
                                padx=30, pady=16)
            self.load_products()
            self._load_suppliers()
        else:
            self.frame_history.pack(fill=tk.BOTH, expand=True,
                                    padx=30, pady=16)
            self._load_purchase_history()

    # ═══════════════════════════════════════════════════════════════════
    # TAB 1 — NEW PURCHASE PAGE
    # ═══════════════════════════════════════════════════════════════════
    def _build_new_purchase_page(self):
        # ── Left: product search & list ────────────────────────────────
        left = tk.Frame(self.frame_new, bg=self.bg_card,
                        highlightbackground=self.border_color, highlightthickness=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Supplier row
        sup_row = tk.Frame(left, bg=self.bg_card)
        sup_row.pack(fill=tk.X, padx=16, pady=(14, 6))
        tk.Label(sup_row, text="Supplier:", font=self.FSB,
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT, padx=(0, 8))
        self.cmb_supplier = ttk.Combobox(sup_row, font=self.FN,
                                         state="readonly", width=28)
        self.cmb_supplier.pack(side=tk.LEFT, ipady=4)
        self.cmb_supplier.set("Select Supplier")

        # Search row
        search_row = tk.Frame(left, bg=self.bg_card)
        search_row.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Search bar (consistent style)
        sw = tk.Frame(search_row, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        sw.pack(side=tk.LEFT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT, padx=(10, 0))
        self.search_entry = tk.Entry(sw, font=self.FN, bg=self.bg_card,
                                     bd=0, width=28,
                                     insertbackground=self.text_dark)
        self.search_entry.pack(side=tk.LEFT, padx=8, ipady=6)
        self.search_entry.insert(0, "Search products…")
        self.search_entry.bind("<FocusIn>",
            lambda e: self.search_entry.delete(0, "end")
            if self.search_entry.get() == "Search products…" else None)
        self.search_entry.bind("<KeyRelease>", self.load_products)

        # Filter dropdown
        tk.Label(search_row, text="Filter:", font=self.FSB,
                 bg=self.bg_card, fg=self.text_muted).pack(
            side=tk.LEFT, padx=(16, 6))
        self.cmb_filter = ttk.Combobox(
            search_row, font=self.FN, state="readonly", width=14,
            values=["All Items", "In Stock", "Low Stock", "Out of Stock"])
        self.cmb_filter.pack(side=tk.LEFT, ipady=4)
        self.cmb_filter.set("All Items")
        self.cmb_filter.bind("<<ComboboxSelected>>", self.load_products)

        # Product table
        tbl_card = tk.Frame(left, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.product_table = ttk.Treeview(
            tbl_card,
            columns=("pid", "name", "stock", "status", "growth", "cost"),
            show="headings", style="Modern.Treeview",
            yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.product_table.yview)

        for col, hd, w, anc in [
            ("pid",    "ID",            50,  "center"),
            ("name",   "Product Name", 220,  "w"),
            ("stock",  "Stock",         80,  "center"),
            ("status", "Status",       110,  "center"),
            ("growth", "Sales Growth ↕",120, "center"),
            ("cost",   "Cost (৳)",      90,  "e"),
        ]:
            # Set basic text and anchor
            self.product_table.heading(col, text=hd)
            self.product_table.column(col, width=w, anchor=anc)
            
            # Only apply command if it's the growth column
            if col == "growth":
                self.product_table.heading(col, command=lambda: self.sort_treeview("growth", False))

        self.product_table.tag_configure("in_stock",    foreground=self.success)
        self.product_table.tag_configure("low_stock",   foreground=self.orange)
        self.product_table.tag_configure("out_of_stock",foreground=self.danger)
        self.product_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Hint
        tk.Label(left, text="💡 Double-click a product to add it to the cart",
                 font=("Segoe UI", 8, "italic"),
                 bg=self.bg_card, fg=self.text_muted).pack(
            anchor="w", padx=16, pady=(0, 8))
        self.product_table.bind("<Double-1>", self._add_to_cart)

        # ── Right: purchase cart ───────────────────────────────────────
        right = tk.Frame(self.frame_new, bg=self.bg_card,
                         highlightbackground=self.border_color,
                         highlightthickness=1, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        # Cart header
        cart_hdr = tk.Frame(right, bg=self.bg_card)
        cart_hdr.pack(fill=tk.X, padx=16, pady=(14, 6))
        self.lbl_cart_count = tk.Label(
            cart_hdr, text="Purchase Cart (0 Items)",
            font=self.FNB, bg=self.bg_card, fg=self.text_dark)
        self.lbl_cart_count.pack(side=tk.LEFT)
        tk.Button(cart_hdr, text="🗑 Clear", font=self.FS,
                  bg=self.bg_card, fg=self.danger, relief="flat", bd=0,
                  cursor="hand2", command=self._clear_cart).pack(side=tk.RIGHT)

        tk.Frame(right, bg=self.border_color, height=1).pack(
            fill=tk.X, padx=16)

        # Scrollable cart items area
        self.cart_canvas = tk.Canvas(right, bg=self.bg_card,
                                     highlightthickness=0)
        cart_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL,
                                    command=self.cart_canvas.yview)
        self.cart_frame = tk.Frame(self.cart_canvas, bg=self.bg_card)
        self.cart_canvas.configure(yscrollcommand=cart_scroll.set)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.cart_window = self.cart_canvas.create_window(
            (0, 0), window=self.cart_frame, anchor="nw")
        self.cart_frame.bind("<Configure>", lambda e:
            self.cart_canvas.configure(
                scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>", lambda e:
            self.cart_canvas.itemconfig(self.cart_window, width=e.width))

        # Checkout panel
        checkout = tk.Frame(right, bg="#F8FAFC",
                            highlightbackground=self.border_color,
                            highlightthickness=1)
        checkout.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_grand_total = tk.Label(
            checkout, text="Grand Total: ৳ 0.00",
            font=("Segoe UI", 13, "bold"),
            bg="#F8FAFC", fg=self.text_dark)
        self.lbl_grand_total.pack(pady=(14, 8))

        self._make_btn(checkout, "Complete Purchase",
                       self.success, "white",
                       cmd=self._complete_purchase).pack(
            fill=tk.X, padx=16, pady=(0, 14))

    # ═══════════════════════════════════════════════════════════════════
    # TAB 2 — PURCHASE HISTORY
    # ═══════════════════════════════════════════════════════════════════
    def _build_history_page(self):
        ctrl = tk.Frame(self.frame_history, bg=self.bg_page)
        ctrl.pack(fill=tk.X, pady=(0, 12))

        title_f = tk.Frame(ctrl, bg=self.bg_page)
        title_f.pack(side=tk.LEFT)
        tk.Label(title_f, text="Purchase History",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.bg_page, fg=self.text_dark).pack(anchor="w")
        tk.Label(title_f, text="Review all product purchases from suppliers.",
                 font=("Segoe UI", 9, "italic"),
                 bg=self.bg_page, fg=self.text_muted).pack(anchor="w")

        self._make_btn(ctrl, "↻ Refresh", "#F1F5F9", self.text_dark,
                       cmd=self._load_purchase_history,
                       border=True).pack(side=tk.RIGHT)

        # Supplier filter
        tk.Label(ctrl, text="Filter by Supplier:", font=self.FN,
                 bg=self.bg_page, fg=self.text_dark).pack(
            side=tk.RIGHT, padx=(10, 10))
        self.supp_filter_var = tk.StringVar(value="All Suppliers")
        self.supp_filter_cb  = ttk.Combobox(ctrl,
            textvariable=self.supp_filter_var,
            state="readonly", font=self.FN, width=22)
        self.supp_filter_cb.pack(side=tk.RIGHT)
        self.supp_filter_cb.bind("<<ComboboxSelected>>",
                                 lambda e: self._load_purchase_history())

        # Table
        tbl_card = tk.Frame(self.frame_history, bg=self.bg_card,
                            highlightbackground=self.border_color,
                            highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("purchase_id", "supp_name", "date",
                "total_items", "total_amount")
        self.purchase_table = ttk.Treeview(
            tbl_card, columns=cols, show="headings",
            style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.purchase_table.yview)

        self.purchase_table.column("purchase_id", width=0, stretch=False)
        self.purchase_table.heading("purchase_id", text="")

        for col, hd, w, anc in [
            ("supp_name",    "Supplier",       280, "w"),
            ("date",         "Purchase Date",  160, "center"),
            ("total_items",  "Total Items",    120, "center"),
            ("total_amount", "Total Amount",   160, "center"),
        ]:
            self.purchase_table.heading(col, text=hd)
            self.purchase_table.column(col, width=w, anchor=anc)

        self.purchase_table.tag_configure("row_even", background="#FFFFFF")
        self.purchase_table.tag_configure("row_odd",  background="#F9FAFB")
        self.purchase_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.purchase_table.bind("<Double-1>", self._open_purchase_items)

    # ═══════════════════════════════════════════════════════════════════
    # DATABASE — PRODUCTS
    # ═══════════════════════════════════════════════════════════════════
    def load_products(self, event=None):
        search_txt    = self.search_entry.get().strip()
        if search_txt == "Search products…":
            search_txt = ""
        filter_status = self.cmb_filter.get()

        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            query = """
                SELECT p.pid, p.name, p.stock, p.cost_price,
                       p.low_stock_alert,
                       COALESCE(SUM(si.qty), 0) AS total_sold
                FROM products p
                LEFT JOIN sales_items si ON p.pid = si.pid
                WHERE p.name LIKE %s
                GROUP BY p.pid, p.name, p.stock,
                         p.cost_price, p.low_stock_alert
            """
            cur.execute(query, (f"%{search_txt}%",))
            rows = cur.fetchall()

            self.product_table.delete(*self.product_table.get_children())
            for row in rows:
                pid, name, stock, cost, low_alert, sold = row
                if stock == 0:
                    status, tag = "Out of Stock", "out_of_stock"
                elif stock <= (low_alert or 5):
                    status, tag = "Low Stock", "low_stock"
                else:
                    status, tag = "In Stock", "in_stock"

                if filter_status == "In Stock"     and status != "In Stock":     continue
                if filter_status == "Low Stock"    and status != "Low Stock":    continue
                if filter_status == "Out of Stock" and status != "Out of Stock": continue

                self.product_table.insert("", tk.END,
                    values=(pid, name, stock, status,
                            f"{int(sold)} units sold",
                            f"৳ {float(cost):,.2f}" if cost else "৳ 0.00"),
                    tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products:\n{e}")
        finally:
            if con.is_connected():
                con.close()

    def _load_suppliers(self):
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("SELECT supp_id, name FROM suppliers ORDER BY name")
            rows = cur.fetchall()
            self.supplier_list = rows
            names = [r[1] for r in rows]
            self.cmb_supplier["values"] = names
            self.supp_filter_cb["values"] = ["All Suppliers"] + names
        except Exception:
            pass
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # CART LOGIC
    # ═══════════════════════════════════════════════════════════════════
    def _add_to_cart(self, event=None):
        sel = self.product_table.focus()
        if not sel:
            return
        vals  = self.product_table.item(sel, "values")
        pid   = int(vals[0])
        name  = vals[1]
        stock = int(vals[2])
        cost_str = vals[5].replace("৳ ", "").replace(",", "")
        try:
            cost = float(cost_str)
        except ValueError:
            cost = 0.0

        if stock <= 0:
            messagebox.showwarning("Out of Stock",
                                   f"{name} is currently out of stock.")
            return

        if pid in self.cart_items:
            self.cart_items[pid]["qty"] += 1
            self.cart_items[pid]["lbl_qty"].config(
                text=str(self.cart_items[pid]["qty"]))
        else:
            self.cart_items[pid] = {"name": name, "qty": 1, "cost": cost}
            self._draw_cart_card(pid)

        self._update_totals()

    def _draw_cart_card(self, pid):
        item = self.cart_items[pid]
        card = tk.Frame(self.cart_frame, bg=self.bg_card)
        card.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Name + cost
        l1 = tk.Frame(card, bg=self.bg_card)
        l1.pack(fill=tk.X)
        tk.Label(l1, text=item["name"][:24],
                 font=self.FNB, bg=self.bg_card, fg=self.text_dark,
                 anchor="w").pack(side=tk.LEFT)
        tk.Label(l1, text=f"৳ {item['cost']:,.2f} / unit",
                 font=self.FS, bg=self.bg_card, fg=self.text_muted).pack(side=tk.RIGHT)

        # Qty controls + remove
        l2 = tk.Frame(card, bg=self.bg_card)
        l2.pack(fill=tk.X, pady=4)

        qty_f = tk.Frame(l2, bg="#F3F4F6")
        qty_f.pack(side=tk.LEFT)
        tk.Button(qty_f, text="−", font=self.FNB, bg="#F3F4F6",
                  fg=self.text_muted, relief="flat", bd=0,
                  padx=8, cursor="hand2",
                  command=lambda p=pid: self._qty_change(p, -1)).pack(side=tk.LEFT)
        lbl_qty = tk.Label(qty_f, text="1", font=self.FNB,
                           bg="#F3F4F6", fg=self.text_dark, padx=8)
        lbl_qty.pack(side=tk.LEFT)
        tk.Button(qty_f, text="+", font=self.FNB, bg="#F3F4F6",
                  fg=self.text_muted, relief="flat", bd=0,
                  padx=8, cursor="hand2",
                  command=lambda p=pid: self._qty_change(p, 1)).pack(side=tk.LEFT)

        item["lbl_qty"]   = lbl_qty
        item["card_frame"]= card

        tk.Button(l2, text="✕", font=("Segoe UI", 11),
                  bg=self.bg_card, fg=self.danger, relief="flat",
                  bd=0, cursor="hand2",
                  command=lambda p=pid: self._remove_item(p)).pack(side=tk.RIGHT)

        line_total = tk.Label(l2, text=f"৳ {item['cost']:,.0f}",
                              font=("Segoe UI", 11, "bold"),
                              bg=self.bg_card, fg=self.text_dark)
        line_total.pack(side=tk.RIGHT, padx=8)
        item["lbl_line"] = line_total

        tk.Frame(card, bg=self.border_color, height=1).pack(
            fill=tk.X, pady=(4, 0))

    def _qty_change(self, pid, delta):
        item = self.cart_items[pid]
        new_qty = item["qty"] + delta
        if new_qty < 1:
            return
        item["qty"] = new_qty
        item["lbl_qty"].config(text=str(new_qty))
        item["lbl_line"].config(text=f"৳ {item['cost'] * new_qty:,.0f}")
        self._update_totals()

    def _remove_item(self, pid):
        self.cart_items[pid]["card_frame"].destroy()
        del self.cart_items[pid]
        self._update_totals()

    def _clear_cart(self):
        for pid in list(self.cart_items.keys()):
            self._remove_item(pid)

    def _update_totals(self):
        total = sum(d["cost"] * d["qty"] for d in self.cart_items.values())
        self.lbl_grand_total.config(text=f"Grand Total: ৳ {total:,.2f}")
        count = len(self.cart_items)
        self.lbl_cart_count.config(text=f"Purchase Cart ({count} Item{'s' if count!=1 else ''})")

    # ═══════════════════════════════════════════════════════════════════
    # COMPLETE PURCHASE
    # ═══════════════════════════════════════════════════════════════════
    def _complete_purchase(self):
        if not self.cart_items:
            messagebox.showerror("Error", "Cart is empty. Add products first.")
            return

        supp_name = self.cmb_supplier.get()
        if supp_name in ("Select Supplier", ""):
            messagebox.showerror("Error", "Please select a supplier first.")
            return

        supp_id = next((r[0] for r in self.supplier_list
                        if r[1] == supp_name), None)
        if not supp_id:
            messagebox.showerror("Error", "Supplier not found.")
            return

        total = sum(d["cost"] * d["qty"] for d in self.cart_items.values())
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")

        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO purchases (supp_id, emp_id, purchase_date, total_amount) "
                "VALUES (%s, NULL, %s, %s)",
                (supp_id, today, total))
            purchase_id = cur.lastrowid

            for pid, item in self.cart_items.items():
                cur.execute(
                    "INSERT INTO purchase_items "
                    "(purchase_id, pid, qty, cost_price, total_price) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (purchase_id, pid, item["qty"], item["cost"],
                     item["cost"] * item["qty"]))
                cur.execute(
                    "UPDATE products SET stock = stock + %s WHERE pid = %s",
                    (item["qty"], pid))

            con.commit()
            messagebox.showinfo("Success",
                f"Purchase #{purchase_id} recorded successfully!")
            self._clear_cart()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # HISTORY DATA
    # ═══════════════════════════════════════════════════════════════════
    def _load_purchase_history(self):
        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            supp_filter = self.supp_filter_var.get()

            query = """
                SELECT p.purchase_id, s.name, p.purchase_date,
                       COUNT(pi.id) AS total_items, p.total_amount
                FROM purchases p
                JOIN suppliers s ON p.supp_id = s.supp_id
                LEFT JOIN purchase_items pi ON p.purchase_id = pi.purchase_id
            """
            params = []
            if supp_filter != "All Suppliers":
                query += " WHERE s.name = %s "
                params.append(supp_filter)
            query += (" GROUP BY p.purchase_id, s.name, "
                      "p.purchase_date, p.total_amount "
                      "ORDER BY p.purchase_date DESC")

            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            self.purchase_table.delete(*self.purchase_table.get_children())
            for i, row in enumerate(rows):
                p_id, s_name, p_date, items, amount = row
                p_date_str = (p_date.strftime("%d %b %Y")
                              if hasattr(p_date, "strftime") else str(p_date))
                amount_str = (f"৳ {float(amount):,.2f}"
                              if amount else "৳ 0.00")
                tag = "row_even" if i % 2 == 0 else "row_odd"
                self.purchase_table.insert("", tk.END,
                    values=(p_id, f"  {s_name}", p_date_str,
                            items, amount_str),
                    tags=(tag,))

            # Populate supplier dropdown
            self.supp_filter_cb["values"] = (
                ["All Suppliers"] + [r[1] for r in rows])
        except Exception as e:
            print("History load error:", e)
        finally:
            if con.is_connected():
                con.close()

    def _open_purchase_items(self, event=None):
        sel = self.purchase_table.selection()
        if not sel:
            return
        vals        = self.purchase_table.item(sel[0], "values")
        purchase_id = vals[0]
        supp_name   = vals[1].strip()
        p_date      = vals[2]
        total       = vals[4]

        win = tk.Toplevel(self.main_frame)
        win.title(f"Order Details — {supp_name}  ({p_date})")
        win.geometry("760x480")
        win.configure(bg=self.bg_card)
        win.resizable(False, False)
        win.transient(self.main_frame)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth()  // 2) - 380
        y = (win.winfo_screenheight() // 2) - 240
        win.geometry(f"+{x}+{y}")

        tk.Label(win, text=f"Order from: {supp_name}",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.bg_card, fg=self.text_dark).pack(
            anchor="w", padx=20, pady=(18, 2))
        tk.Label(win,
                 text=f"Date: {p_date}  |  Total: {total}",
                 font=("Segoe UI", 10),
                 bg=self.bg_card, fg=self.text_muted).pack(anchor="w", padx=20)

        tbl_card = tk.Frame(win, bg=self.bg_card,
                            highlightbackground=self.border_color,
                            highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols  = ("pid", "name", "qty", "cost", "total")
        table = ttk.Treeview(tbl_card, columns=cols, show="headings",
                             style="Modern.Treeview",
                             yscrollcommand=scroll_y.set, height=10)
        scroll_y.config(command=table.yview)

        table.column("pid", width=0, stretch=False)
        table.heading("pid", text="")
        for col, hd, w, anc in [
            ("name",  "Item Name",   320, "w"),
            ("qty",   "Qty",         90,  "center"),
            ("cost",  "Unit Cost",   120, "center"),
            ("total", "Total",       140, "center"),
        ]:
            table.heading(col, text=hd)
            table.column(col, width=w, anchor=anc)

        table.tag_configure("row_even", background="#FFFFFF")
        table.tag_configure("row_odd",  background="#F9FAFB")
        table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        con = db_config.get_db_connection()
        if not con:
            return
        try:
            cur = con.cursor()
            cur.execute("""
                SELECT pr.pid, pr.name, pi.qty, pi.cost_price, pi.total_price
                FROM purchase_items pi
                JOIN products pr ON pi.pid = pr.pid
                WHERE pi.purchase_id = %s
            """, (purchase_id,))
            for i, row in enumerate(cur.fetchall()):
                pid, name, qty, cost, total = row
                tag = "row_even" if i % 2 == 0 else "row_odd"
                table.insert("", tk.END,
                    values=(pid, f"  📦  {name}", qty,
                            f"৳ {float(cost):,.2f}" if cost else "—",
                            f"৳ {float(total):,.2f}" if total else "—"),
                    tags=(tag,))
        except Exception as e:
            print("Modal error:", e)
        finally:
            if con.is_connected():
                con.close()

    # ═══════════════════════════════════════════════════════════════════
    # SORT
    # ═══════════════════════════════════════════════════════════════════
    def sort_treeview(self, col, reverse):
        data = [(self.product_table.set(c, col), c)
                for c in self.product_table.get_children("")]
        if col == "growth":
            try:
                data.sort(key=lambda t: int(t[0].split()[0]), reverse=reverse)
            except Exception:
                data.sort(reverse=reverse)
        else:
            data.sort(reverse=reverse)
        for idx, (_, child) in enumerate(data):
            self.product_table.move(child, "", idx)
        self.product_table.heading(col,
            command=lambda: self.sort_treeview(col, not reverse))

    # ═══════════════════════════════════════════════════════════════════
    # BUTTON HELPER
    # ═══════════════════════════════════════════════════════════════════
    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.FNB, bg=bg, fg=fg,
                  relief="flat", bd=0, cursor="hand2",
                  padx=16, pady=7,
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
    root.title("IMS – Purchase Management")
    root.state("zoomed")
    PurchaseClass(root)
    root.mainloop()