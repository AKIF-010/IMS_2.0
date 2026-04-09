import tkinter as tk
from tkinter import ttk, messagebox
import db_config
from datetime import datetime

class SupplierClass:
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
        self.danger       = "#EF4444"
        self.input_bg     = "#F9FAFB"

        # ── Font stack ────────────────────────────────────────────────
        self.F_TITLE  = ("Segoe UI", 18, "bold")
        self.F_SUB    = ("Segoe UI", 10)
        self.F_LABEL  = ("Segoe UI",  9, "bold")
        self.F_NORMAL = ("Segoe UI", 10)
        self.F_BTN    = ("Segoe UI", 10, "bold")
        
        # Updated Card Fonts - Smaller and less bold
        self.F_CARD_V = ("Segoe UI", 20, "bold") 
        self.F_CARD_T = ("Segoe UI", 10)         

        self.search_var = tk.StringVar()

        self._setup_treeview_style()
        
        # Build the empty frames for content
        self.frame_suppliers = tk.Frame(self.root, bg=self.bg_page)
        self.frame_history   = tk.Frame(self.root, bg=self.bg_page)

        # Build tabs and content
        self._build_tab_bar()
        self._build_suppliers_tab()
        self._build_history_tab()
        
        # Load initial tab
        self._switch_tab("suppliers")

    # ─────────────────────────────────────────────────────────────────
    # STYLES
    # ─────────────────────────────────────────────────────────────────
    def _setup_treeview_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Modern.Treeview",
            background=self.bg_card, fieldbackground=self.bg_card,
            foreground=self.text_dark, rowheight=46, borderwidth=0,
            font=self.F_NORMAL)
        style.configure("Modern.Treeview.Heading",
            background="#F8FAFC", foreground="#475569",
            font=self.F_LABEL, borderwidth=0, padding=(12, 10))
        style.map("Modern.Treeview",
            background=[("selected", "#EFF6FF")],
            foreground=[("selected", self.primary_blue)])

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

        make_tab("Manage Suppliers", "suppliers")
        make_tab("Purchase History", "history")

    def _switch_tab(self, tab):
        # Visually update the tabs
        self._render_tabs(tab)
        
        # Hide all frames
        self.frame_suppliers.pack_forget()
        self.frame_history.pack_forget()
        
        # Show selected frame
        if tab == "suppliers":
            self.frame_suppliers.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._refresh_summary()
            self._load_suppliers()
        else:
            self.frame_history.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._load_all_purchases()

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 1 : MANAGE SUPPLIERS ─────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_suppliers_tab(self):
        # ── Summary cards ─────────────────────────────────────────────
        cards_row = tk.Frame(self.frame_suppliers, bg=self.bg_page)
        cards_row.pack(fill=tk.X, pady=(0, 18))
        for i in range(4):
            cards_row.columnconfigure(i, weight=1)

        self._card_total_supp   = self._kpi_card(cards_row, 0, "Total Suppliers",    "👥", "#0EA5E9")
        self._card_active_supp  = self._kpi_card(cards_row, 1, "Active This Month",  "✅",  self.success)
        self._card_total_order  = self._kpi_card(cards_row, 2, "Total Ordered",      "🛒", self.primary_blue)
        self._card_new_supp     = self._kpi_card(cards_row, 3, "New Suppliers",      "➕", "#8B5CF6")

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = tk.Frame(self.frame_suppliers, bg=self.bg_page)
        toolbar.pack(fill=tk.X, pady=(0, 12))

        # Search
        sw = tk.Frame(toolbar, bg=self.bg_card,
                      highlightbackground=self.border_color, highlightthickness=1)
        sw.pack(side=tk.LEFT)
        tk.Label(sw, text="🔍", font=("Segoe UI", 11),
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT, padx=(10, 0))
        se = tk.Entry(sw, textvariable=self.search_var,
                      font=self.F_NORMAL, bg=self.bg_card, bd=0, width=32,
                      insertbackground=self.text_dark)
        se.pack(side=tk.LEFT, padx=8, ipady=7)
        se.insert(0, "Search by name, contact, or address…")
        se.bind("<FocusIn>", lambda e: se.delete(0, "end") if se.get() == "Search by name, contact, or address…" else None)
        se.bind("<KeyRelease>", self._search_suppliers)

        # Right buttons
        self._make_btn(toolbar, "+ Add New Supplier", self.text_dark, "white",
                       cmd=self._open_add_modal).pack(side=tk.RIGHT)
        self._make_btn(toolbar, "⚙ Filter", "#F1F5F9", self.text_dark,
                       border=True).pack(side=tk.RIGHT, padx=(0, 8))

        # ── Supplier table ─────────────────────────────────────────────
        tbl_card = tk.Frame(self.frame_suppliers, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("supp_id", "name", "contact", "address", "total_orders", "last_order", "actions")
        self.supp_table = ttk.Treeview(tbl_card, columns=cols, show="headings",
                                       style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.supp_table.yview)

        # Hidden ID column
        self.supp_table.column("supp_id", width=0, stretch=False)
        self.supp_table.heading("supp_id", text="")

        col_cfg = [
            ("name",         "Supplier Name",  250, "w"),
            ("contact",      "Contact",        150, "center"),
            ("address",      "Address",        300, "w"),
            ("total_orders", "Total Orders",   120, "center"),
            ("last_order",   "Last Order Date", 180, "center"),
            ("actions",      "Actions",         80, "center"),
        ]
        for col, heading, width, anchor in col_cfg:
            self.supp_table.heading(col, text=heading)
            self.supp_table.column(col, width=width, anchor=anchor)

        self.supp_table.tag_configure("row_even", background="#FFFFFF")
        self.supp_table.tag_configure("row_odd",  background="#F9FAFB")
        self.supp_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Click binding for specific supplier history
        self.supp_table.bind("<Double-1>", self._on_supplier_double_click)
        self.supp_table.bind("<ButtonRelease-1>", self._on_supplier_single_click)

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 2 : PURCHASE HISTORY ───────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_history_tab(self):
        ctrl = tk.Frame(self.frame_history, bg=self.bg_page)
        ctrl.pack(fill=tk.X, pady=(0, 12))

        title_f = tk.Frame(ctrl, bg=self.bg_page)
        title_f.pack(side=tk.LEFT)
        tk.Label(title_f, text="Purchase History",
                 font=("Segoe UI", 14, "bold"), bg=self.bg_page, fg=self.text_dark).pack(anchor="w")
        tk.Label(title_f, text="Review all product purchases from suppliers.",
                 font=("Segoe UI", 9, "italic"), bg=self.bg_page, fg=self.text_muted).pack(anchor="w")

        # Refresh Button
        self._make_btn(ctrl, "↻ Refresh", "#F1F5F9", self.text_dark,
                       cmd=self._load_all_purchases, border=True).pack(side=tk.RIGHT)

        # Dropdown Filter
        tk.Label(ctrl, text="Filter by Supplier:", font=self.F_NORMAL, bg=self.bg_page, fg=self.text_dark).pack(side=tk.RIGHT, padx=(10, 15))
        self.supp_filter_var = tk.StringVar(value="All Suppliers")
        self.supp_filter_cb = ttk.Combobox(ctrl, textvariable=self.supp_filter_var, state="readonly", font=self.F_NORMAL, width=25)
        self.supp_filter_cb.pack(side=tk.RIGHT)
        self.supp_filter_cb.bind("<<ComboboxSelected>>", lambda e: self._load_all_purchases())

        # ── Purchase table ───────────────────────────────────────────────
        tbl_card = tk.Frame(self.frame_history, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        purchase_cols = ("purchase_id", "supp_name", "date", "total_items", "total_amount")
        self.purchase_table = ttk.Treeview(tbl_card, columns=purchase_cols, show="headings",
                                           style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.purchase_table.yview)

        # Hidden ID
        self.purchase_table.column("purchase_id", width=0, stretch=False)
        self.purchase_table.heading("purchase_id", text="")

        purchase_col_cfg = [
            ("supp_name",    "Supplier",      300, "w"),
            ("date",         "Purchase Date", 180, "center"),
            ("total_items",  "Total Items",   120, "center"),
            ("total_amount", "Total Amount",  180, "center"),
        ]
        for col, heading, width, anchor in purchase_col_cfg:
            self.purchase_table.heading(col, text=heading)
            self.purchase_table.column(col, width=width, anchor=anchor)

        self.purchase_table.tag_configure("row_even", background="#FFFFFF")
        self.purchase_table.tag_configure("row_odd",  background="#F9FAFB")
        self.purchase_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Double click to view specific items
        self.purchase_table.bind("<Double-1>", self._open_purchase_items_modal)

    # ─────────────────────────────────────────────────────────────────
    # DATABASE & LOGIC
    # ─────────────────────────────────────────────────────────────────
    def _refresh_summary(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM suppliers")
            self._card_total_supp.config(text=str(cur.fetchone()[0]))
            
            # This is simplified. Proper logic requires a JOIN with purchases and date filtering.
            self._card_active_supp.config(text="12")
            
            cur.execute("SELECT SUM(total_amount) FROM purchases")
            total_ordered = cur.fetchone()[0]
            self._card_total_order.config(text=f"৳ {float(total_ordered):,.2f}" if total_ordered else "৳ 0.00")
            
            self._card_new_supp.config(text="3") # Placeholder
        except Exception as e:
            print("Summary Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _load_suppliers(self, search_text=""):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            
            # Complex query to get total orders and last order date per supplier
            query = """
                SELECT s.supp_id, s.name, s.contact, s.address, 
                       COUNT(p.purchase_id) as total_orders, 
                       MAX(p.purchase_date) as last_order
                FROM suppliers s
                LEFT JOIN purchases p ON s.supp_id = p.supp_id
            """
            params = []
            if search_text and search_text != "Search by name, contact, or address…":
                query += " WHERE s.name LIKE %s OR s.contact LIKE %s OR s.address LIKE %s "
                params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            
            query += " GROUP BY s.supp_id, s.name, s.contact, s.address ORDER BY s.name ASC"
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            self.supp_table.delete(*self.supp_table.get_children())
            dropdown_values = ["All Suppliers"]
            
            for i, row in enumerate(rows):
                supp_id, name, contact, address, orders, last_date = row
                contact = contact or "—"
                address = address or "—"
                last_date = last_date.strftime("%d %b %Y") if last_date else "Never"
                actions = "✏️ 🗑️"
                tag = "row_even" if i % 2 == 0 else "row_odd"
                
                self.supp_table.insert("", tk.END,
                    values=(supp_id, f"  👤 {name}", contact, address, orders, last_date, actions),
                    tags=(tag,))
                dropdown_values.append(name)
            
            self.supp_filter_cb['values'] = dropdown_values

        except Exception as e:
            print("Load Suppliers Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _search_suppliers(self, event=None):
        q = self.search_var.get().strip()
        self._load_suppliers(q)

    def _on_supplier_single_click(self, event):
        region = self.supp_table.identify_region(event.x, event.y)
        if region == "cell":
            col = self.supp_table.identify_column(event.x)
            if col == '#7': # 'actions' column
                item = self.supp_table.identify_row(event.y)
                if not item: return
                
                vals = self.supp_table.item(item, "values")
                supp_id = vals[0]
                
                # Split action cell in half
                bbox = self.supp_table.bbox(item, column=col)
                if bbox:
                    x, y, w, h = bbox
                    if event.x < x + (w / 2):
                        # Edit
                        self._open_add_modal(supp_id=int(supp_id))
                    else:
                        # Delete
                        self._delete_supplier(int(supp_id))
    
    def _on_supplier_double_click(self, event):
        sel = self.supp_table.selection()
        if not sel: return
        vals = self.supp_table.item(sel[0], "values")
        supp_name = vals[1].replace("  👤 ", "")
        self.supp_filter_var.set(supp_name)
        self._switch_tab("history")

    def _delete_supplier(self, supp_id):
        if messagebox.askyesno("Confirm Delete",
                "Are you sure you want to delete this supplier?\nIt will also delete all associated purchase records."):
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("DELETE FROM suppliers WHERE supp_id=%s", (supp_id,))
                    con.commit()
                    messagebox.showinfo("Success", "Supplier deleted successfully.")
                    self._refresh_summary()
                    self._load_suppliers()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete supplier:\n{e}")
                finally: con.close()

    # ─────────────────────────────────────────────────────────────────
    # PURCHASE HISTORY & ITEMS
    # ─────────────────────────────────────────────────────────────────
    def _load_all_purchases(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            supp_filter = self.supp_filter_var.get()
            
            # This query requires database schemas for purchases and purchase_items
            query = """
                SELECT p.purchase_id, s.name, p.purchase_date, 
                       COUNT(pi.id) as total_items, p.total_amount
                FROM purchases p
                JOIN suppliers s ON p.supp_id = s.supp_id
                LEFT JOIN purchase_items pi ON p.purchase_id = pi.purchase_id
            """
            params = []
            if supp_filter != "All Suppliers":
                query += " WHERE s.name = %s "
                params.append(supp_filter)
            
            query += " GROUP BY p.purchase_id, s.name, p.purchase_date, p.total_amount ORDER BY p.purchase_date DESC"

            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            self.purchase_table.delete(*self.purchase_table.get_children())
            for i, row in enumerate(rows):
                p_id, s_name, p_date, items, amount = row
                p_date = p_date.strftime("%d %b %Y") if p_date else "—"
                amount_str = f"৳ {float(amount):,.2f}" if amount else "৳ 0.00"
                tag = "row_even" if i % 2 == 0 else "row_odd"
                
                self.purchase_table.insert("", tk.END,
                    values=(p_id, f"  {s_name}", p_date, items, amount_str),
                    tags=(tag,))

        except Exception as e:
            print("Load All Purchases Error:", e)
        finally:
            if con.is_connected(): con.close()

    def _open_purchase_items_modal(self, event):
        sel = self.purchase_table.selection()
        if not sel: return
        vals = self.purchase_table.item(sel[0], "values")
        purchase_id = vals[0]
        supp_name = vals[1].replace("  ", "")
        p_date = vals[2]
        total_amount = vals[4]
        
        # New Modal window for purchase items details
        win = tk.Toplevel(self.root)
        win.title(f"Order Details - {supp_name} ({p_date})")
        win.geometry("800x500")
        win.configure(bg=self.bg_card)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        # Center modal
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 400
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        win.geometry(f"+{x}+{y}")
        
        # Header area
        tk.Label(win, text=f"Order from: {supp_name}", font=("Segoe UI", 12, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", padx=20, pady=(20, 2))
        tk.Label(win, text=f"Date: {p_date} | Order Total: {total_amount}", font=("Segoe UI", 10), bg=self.bg_card, fg=self.text_muted).pack(anchor="w", padx=20)
        
        # Item table card
        tbl_card = tk.Frame(win, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        items_cols = ("pid", "name", "qty", "cost", "total")
        items_table = ttk.Treeview(tbl_card, columns=items_cols, show="headings",
                                   style="Modern.Treeview", yscrollcommand=scroll_y.set, height=1)
        scroll_y.config(command=items_table.yview)

        # Hidden ID
        items_table.column("pid", width=0, stretch=False)
        items_table.heading("pid", text="")

        items_col_cfg = [
            ("name",  "Item Name",  350, "w"),
            ("qty",   "Quantity",   100, "center"),
            ("cost",  "Unit Cost",   120, "center"),
            ("total", "Total Price", 150, "center"),
        ]
        for col, heading, width, anchor in items_col_cfg:
            items_table.heading(col, text=heading)
            items_table.column(col, width=width, anchor=anchor)

        items_table.tag_configure("row_even", background="#FFFFFF")
        items_table.tag_configure("row_odd",  background="#F9FAFB")
        items_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Database fetch logic for specific items from particular purchase
        con = db_config.get_db_connection()
        if not con: win.destroy(); return
        try:
            cur = con.cursor()
            # New query joins purchase_items and products
            query = """
                SELECT pr.pid, pr.name, pi.qty, pi.cost_price, pi.total_price
                FROM purchase_items pi
                JOIN products pr ON pi.pid = pr.pid
                WHERE pi.purchase_id = %s
            """
            cur.execute(query, (purchase_id,))
            item_rows = cur.fetchall()
            for i, row in enumerate(item_rows):
                pid, name, qty, cost, total = row
                cost_str = f"৳ {float(cost):,.2f}" if cost else "—"
                total_str = f"৳ {float(total):,.2f}" if total else "—"
                tag = "row_even" if i % 2 == 0 else "row_odd"
                items_table.insert("", tk.END, values=(pid, f"  📦 {name}", qty, cost_str, total_str), tags=(tag,))
        except Exception as e:
            print("Modal Item Fetch Error:", e)
        finally: con.close()

    # ─────────────────────────────────────────────────────────────────
    # ADD / EDIT MODAL
    # ─────────────────────────────────────────────────────────────────
    def _open_add_modal(self, supp_id=None):
        edit_mode = supp_id is not None
        existing = None

        if edit_mode:
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("SELECT name, contact, address FROM suppliers WHERE supp_id=%s", (supp_id,))
                    existing = cur.fetchone()
                except Exception: pass
                finally: con.close()
            if not existing: messagebox.showerror("Error", "Could not load data."); return

        win = tk.Toplevel(self.root)
        win.title("Edit Supplier" if edit_mode else "Add New Supplier")
        win.geometry("450x420")
        win.configure(bg=self.bg_card)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        # Centre the modal
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 210
        win.geometry(f"+{x}+{y}")

        # Modal Header
        hdr_color = "#F8FAFC"
        hdr = tk.Frame(win, bg=hdr_color, highlightbackground=self.border_color, highlightthickness=1)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Edit Details" if edit_mode else "Create New", font=("Segoe UI", 11, "bold"), bg=hdr_color, fg=self.text_dark).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Form
        form = tk.Frame(win, bg=self.bg_card)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        v_name    = tk.StringVar(value=existing[0] if existing else "")
        v_contact = tk.StringVar(value=existing[1] if existing else "")
        t_address = tk.Text(form, font=self.F_NORMAL, bg=self.input_bg, highlightbackground=self.border_color, highlightthickness=1, height=6, relief="flat")
        if existing and existing[2]: t_address.insert(tk.END, existing[2])

        self._make_field(form, "Supplier Name *", v_name)
        self._make_field(form, "Contact *", v_contact)
        
        f_add = tk.Frame(form, bg=self.bg_card); f_add.pack(fill=tk.X, pady=(0, 10))
        tk.Label(f_add, text="Address", font=self.F_LABEL, bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 4))
        t_address.pack(fill=tk.X)

        # Footer
        footer = tk.Frame(win, bg="#F8FAFC", highlightbackground=self.border_color, highlightthickness=1)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        btn_row = tk.Frame(footer, bg="#F8FAFC")
        btn_row.pack(side=tk.RIGHT, padx=15, pady=10)

        self._make_btn(btn_row, "  Cancel  ", "#E5E7EB", self.text_dark, cmd=win.destroy).pack(side=tk.LEFT, padx=(0, 8))
        self._make_btn(btn_row, " Update Supplier " if edit_mode else " Add Supplier ", self.primary_blue, "white", cmd=lambda: _save()).pack(side=tk.LEFT)

        def _save():
            name = v_name.get().strip()
            contact = v_contact.get().strip()
            address = t_address.get("1.0", tk.END).strip()

            if not name: return messagebox.showerror("Validation", "Name is required!", parent=win)
            if not contact: return messagebox.showerror("Validation", "Contact is required!", parent=win)

            con = db_config.get_db_connection()
            if not con: return
            try:
                cur = con.cursor()
                if edit_mode:
                    cur.execute("UPDATE suppliers SET name=%s, contact=%s, address=%s WHERE supp_id=%s", (name, contact, address, supp_id))
                    msg = "Supplier updated successfully!"
                else:
                    cur.execute("INSERT INTO suppliers (name, contact, address) VALUES (%s, %s, %s)", (name, contact, address))
                    msg = "Supplier added successfully!"
                con.commit()
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self._refresh_summary()
                self._load_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Database error:\n{e}", parent=win)
            finally: con.close()

    # ─────────────────────────────────────────────────────────────────
    # REUSABLE UI HELPERS
    # ─────────────────────────────────────────────────────────────────
    def _kpi_card(self, parent, col, title, icon, icon_color):
        # Adjusted height to 85 (down from 105) for better proportions
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

    def _make_field(self, parent, label, var, is_password=False):
        f = tk.Frame(parent, bg=self.bg_card)
        f.pack(fill=tk.X, pady=(0, 10))
        tk.Label(f, text=label, font=self.F_LABEL, bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 4))
        ent = tk.Entry(f, textvariable=var, font=self.F_NORMAL, bg=self.input_bg, relief="flat", highlightthickness=1, highlightbackground=self.border_color)
        if is_password: ent.config(show="●")
        ent.pack(fill=tk.X, ipady=6)
        return ent

    def _make_btn(self, parent, text, bg, fg, cmd=None, border=False):
        kw = dict(text=text, font=self.F_BTN, bg=bg, fg=fg, relief="flat", bd=0, cursor="hand2", padx=18, pady=7)
        if border: kw["highlightbackground"] = self.border_color; kw["highlightthickness"] = 1
        if cmd: kw["command"] = cmd
        return tk.Button(parent, **kw)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("IMS - Supplier Management")
    root.state("zoomed")
    app = SupplierClass(root)
    root.mainloop()