import tkinter as tk
from tkinter import ttk, messagebox
import db_config

class ProductMenu:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.editing_pid = None 
        
        # Professional Color Theme 
        self.bg_main = "#F3F4F6"      
        self.bg_card = "#FFFFFF"      
        self.text_dark = "#111827"    
        self.text_muted = "#6B7280"   
        self.primary_blue = "#0EA5E9" 
        self.border_color = "#E5E7EB" 
        self.input_bg = "#F9FAFB"     

        self.setup_styles()
        self.create_layout()

    def setup_styles(self):
        style = ttk.Style()
        if 'clam' in style.theme_names(): 
            style.theme_use('clam')
            
        style.configure("Modern.Treeview", background=self.bg_card, fieldbackground=self.bg_card, 
                        foreground=self.text_dark, rowheight=40, borderwidth=0, font=('Arial', 10))
        style.configure("Modern.Treeview.Heading", background=self.input_bg, foreground=self.text_muted, 
                        font=('Arial', 10, 'bold'), borderwidth=0, padding=10)
        style.map("Modern.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', self.primary_blue)])
        
        style.configure("TCombobox", padding=6, font=('Arial', 10))

    def create_layout(self):
        # --- Page Header Removed Here ---

        self.tab_frame = tk.Frame(self.parent, bg=self.bg_main)
        # Added extra top padding (20) since the header is gone
        self.tab_frame.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        tk.Frame(self.parent, bg=self.border_color, height=1).pack(fill=tk.X, padx=30)

        self.content_area = tk.Frame(self.parent, bg=self.bg_main)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        # Initialize Variables
        self.v_name = tk.StringVar(); self.v_cat = tk.StringVar(); self.v_brand = tk.StringVar()
        self.v_supplier = tk.StringVar(); self.v_status = tk.StringVar(value="Active")
        self.v_cost = tk.StringVar(); self.v_sale = tk.StringVar(); self.v_tax = tk.StringVar(value="0")
        self.v_sku = tk.StringVar(); self.v_barcode = tk.StringVar(); self.v_stock = tk.StringVar(value="0"); self.v_low_alert = tk.StringVar(value="5")

        self.create_tab_buttons()
        self.show_all_products()

    def create_tab_buttons(self, active_tab="all"):
        for widget in self.tab_frame.winfo_children(): 
            widget.destroy()

        def make_btn(text, tab_id):
            is_active = (active_tab == tab_id)
            color = self.primary_blue if is_active else self.text_muted
            font = ("Arial", 11, "bold") if is_active else ("Arial", 11)
            btn = tk.Button(self.tab_frame, text=text, font=font, fg=color, bg=self.bg_main, relief="flat", cursor="hand2", command=lambda: self.switch_tab(tab_id))
            btn.pack(side=tk.LEFT, padx=(0, 20))
            if is_active:
                tk.Frame(self.tab_frame, bg=self.primary_blue, height=3).place(in_=btn, relx=0, rely=1, y=-2, relwidth=1)

        make_btn("All Products", "all")
        make_btn("Add / Edit Product", "add")
        make_btn("Categories & Brands", "brands")

    def switch_tab(self, tab_name):
        self.create_tab_buttons(active_tab=tab_name)
        for widget in self.content_area.winfo_children(): 
            widget.destroy()

        if tab_name == "all":
            self.show_all_products()
        elif tab_name == "add":
            if not self.editing_pid: 
                self.clear_form() 
            self.show_add_product()
        elif tab_name == "brands":
            self.show_companies_brands()

    # ================= 1. ALL PRODUCTS TAB =================
    def show_all_products(self):
        card_frame = tk.Frame(self.content_area, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        toolbar = tk.Frame(card_frame, bg=self.bg_card)
        toolbar.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(toolbar, text="💡 Double-click on any row to edit", font=("Arial", 9, "italic"), bg=self.bg_card, fg=self.primary_blue).pack(side=tk.RIGHT, padx=10)

        filter_bg = tk.Frame(toolbar, bg=self.input_bg, highlightbackground=self.border_color, highlightthickness=1)
        filter_bg.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_by_var = tk.StringVar(value="All Columns")
        filter_combo = ttk.Combobox(filter_bg, textvariable=self.search_by_var, values=["All Columns", "Name", "PID", "SKU", "Barcode"], state="readonly", width=12, font=("Arial", 10))
        filter_combo.pack(padx=2, pady=2)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.fetch_products(self.search_var.get()))

        search_bg = tk.Frame(toolbar, bg=self.input_bg, highlightbackground=self.border_color, highlightthickness=1, padx=10, pady=5)
        search_bg.pack(side=tk.LEFT)
        tk.Label(search_bg, text="🔍", bg=self.input_bg, fg=self.text_muted).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.fetch_products(self.search_var.get()))
        
        search_entry = tk.Entry(search_bg, textvariable=self.search_var, font=("Arial", 11), bg=self.input_bg, bd=0, width=35)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.insert(0, "Search products...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, 'end') if search_entry.get() == "Search products..." else None)

        table_frame = tk.Frame(card_frame, bg=self.bg_card)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ("pid", "sku", "barcode", "name", "category", "brand", "supplier", "cost_price", "sale_price", "tax_vat", "stock", "low_stock_alert", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Modern.Treeview", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        headings = [
            ("pid", "PID", 50, "center"), ("sku", "SKU", 100, "w"), ("barcode", "Barcode", 120, "w"),
            ("name", "Product Name", 250, "w"), ("category", "Category", 120, "w"), ("brand", "Brand", 120, "w"),
            ("supplier", "Supplier", 150, "w"), ("cost_price", "Cost (৳)", 80, "e"), ("sale_price", "Price (৳)", 80, "e"),
            ("tax_vat", "Tax (%)", 70, "center"), ("stock", "Stock", 70, "center"), ("low_stock_alert", "Alert Lvl", 80, "center"),
            ("status", "Status", 80, "center")
        ]

        for col, text, width, anchor in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor, stretch=False)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.load_product_for_edit)
        self.fetch_products()

    def fetch_products(self, search_text=""):
        if not hasattr(self, 'tree') or not self.tree.winfo_exists():
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if search_text == "Search products...":
            search_text = ""

        search_by = self.search_by_var.get() if hasattr(self, 'search_by_var') else "All Columns"
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            query = "SELECT pid, sku, barcode, name, category, brand, supplier, cost_price, sale_price, tax_vat, stock, low_stock_alert, status FROM products"
            
            if search_text:
                search_term = f"%{search_text}%"
                if search_by == "All Columns":
                    query += " WHERE name LIKE %s OR sku LIKE %s OR barcode LIKE %s OR pid LIKE %s"
                    cur.execute(query, (search_term, search_term, search_term, search_term))
                elif search_by == "Name":
                    query += " WHERE name LIKE %s"
                    cur.execute(query, (search_term,))
                elif search_by == "PID":
                    query += " WHERE pid LIKE %s"
                    cur.execute(query, (search_term,))
                elif search_by == "SKU":
                    query += " WHERE sku LIKE %s"
                    cur.execute(query, (search_term,))
                elif search_by == "Barcode":
                    query += " WHERE barcode LIKE %s"
                    cur.execute(query, (search_term,))
            else:
                query += " ORDER BY pid DESC"
                cur.execute(query)

            for row in cur.fetchall():
                formatted_row = list(row)
                formatted_row[7] = f"৳ {row[7]:.2f}" if row[7] else "৳ 0.00"
                formatted_row[8] = f"৳ {row[8]:.2f}" if row[8] else "৳ 0.00"
                self.tree.insert("", tk.END, values=formatted_row)
        except Exception as e:
            print(f"Fetch Error: {e}")
        finally:
            if con.is_connected(): con.close()

    # ================= 2. ADD / EDIT PRODUCT TAB =================
    def show_add_product(self):
        footer = tk.Frame(self.content_area, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        btn_frame = tk.Frame(footer, bg=self.bg_card)
        btn_frame.pack(side=tk.RIGHT, padx=30, pady=12)
        
        btn_text = "Update Product" if self.editing_pid else "Save Product"
        btn_color = "#10B981" if self.editing_pid else self.primary_blue
        
        tk.Button(btn_frame, text="Cancel", font=("Arial", 10, "bold"), bg=self.bg_card, fg=self.text_dark, relief="solid", bd=1, cursor="hand2", command=lambda: [self.clear_form(), self.switch_tab("all")], padx=20, pady=6).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text=btn_text, font=("Arial", 10, "bold"), bg=btn_color, fg="white", relief="flat", cursor="hand2", command=self.save_product, padx=20, pady=7).pack(side=tk.LEFT)

        # ADDED: Product Delete button only visible when editing an existing product
        if self.editing_pid:
            tk.Button(btn_frame, text="Delete Product", font=("Arial", 10, "bold"), bg="#EF4444", fg="white", relief="flat", cursor="hand2", command=self.delete_product, padx=20, pady=7).pack(side=tk.LEFT, padx=(10, 0))

        canvas_container = tk.Frame(self.content_area, bg=self.bg_main)
        canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=30, pady=20)

        canvas = tk.Canvas(canvas_container, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=self.bg_main)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda event: canvas.itemconfig(canvas_window, width=event.width))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse scroll bug fix
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception: pass
            
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Load real data from DB
        categories = self.get_list_from_table("categories")
        brands = self.get_list_from_table("brands")

        left_col = tk.Frame(self.scrollable_frame, bg=self.bg_main)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_col = tk.Frame(self.scrollable_frame, bg=self.bg_main)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        gen_card = self.create_card(left_col, "General Information")
        self.create_input(gen_card, "Product Name *", "e.g. Premium Wireless Headphones", self.v_name)
        
        tk.Label(gen_card, text="Description", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(10, 5))
        text_border = tk.Frame(gen_card, bg=self.border_color)
        text_border.pack(fill=tk.X)
        text_inner = tk.Frame(text_border, bg=self.input_bg, padx=1, pady=1)
        text_inner.pack(fill=tk.X, padx=1, pady=1)
        
        if not hasattr(self, 't_desc') or not self.t_desc.winfo_exists():
            self.t_desc = tk.Text(text_inner, font=("Arial", 10), bg=self.input_bg, height=4, bd=0, highlightthickness=0)
        else:
            old_text = self.t_desc.get("1.0", tk.END)
            self.t_desc = tk.Text(text_inner, font=("Arial", 10), bg=self.input_bg, height=4, bd=0, highlightthickness=0)
            self.t_desc.insert("1.0", old_text.strip())
            
        self.t_desc.pack(fill=tk.X, padx=8, pady=5)

        pi_card = self.create_card(left_col, "Pricing & Inventory")
        grid_frame = tk.Frame(pi_card, bg=self.bg_card)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        grid_frame.columnconfigure(0, weight=1, pad=15)
        grid_frame.columnconfigure(1, weight=1)

        self.create_grid_input(grid_frame, "Cost Price (৳)", self.v_cost, 0, 0)
        self.create_grid_input(grid_frame, "SKU (Stock Keeping Unit) *", self.v_sku, 0, 1, "e.g. WH-001")
        self.create_grid_input(grid_frame, "Selling Price (৳) *", self.v_sale, 1, 0)
        self.create_grid_input(grid_frame, "Barcode (ISBN, UPC)", self.v_barcode, 1, 1, "Scan or enter barcode")
        self.create_grid_input(grid_frame, "Tax / VAT (%)", self.v_tax, 2, 0)
        
        stock_f = tk.Frame(grid_frame, bg=self.bg_card)
        stock_f.grid(row=2, column=1, sticky="ew")
        f1 = tk.Frame(stock_f, bg=self.bg_card); f1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        f2 = tk.Frame(stock_f, bg=self.bg_card); f2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        self.create_input(f1, "Initial Stock", "0", self.v_stock)
        self.create_input(f2, "Low Stock Alert", "5", self.v_low_alert)

        org_card = self.create_card(right_col, "Organization")
        org_card.config(width=280)
        
        self.create_dropdown(org_card, "Category *", self.v_cat, categories, state="readonly")
        self.create_dropdown(org_card, "Brand", self.v_brand, brands, state="readonly")
        self.create_dropdown(org_card, "Supplier", self.v_supplier, ["Tech Supplier BD", "Global Imports Ltd."], state="readonly")
        self.create_dropdown(org_card, "Product Status", self.v_status, ["Active", "Inactive"], state="readonly")

    # ================= 3. COMPANIES & BRANDS TAB (Pro Layout) =================
    def show_companies_brands(self):
        self.editing_cat_old = None
        self.editing_brand_old = None
        
        main_frame = tk.Frame(self.content_area, bg=self.bg_main)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 50/50 Layout Columns
        col_left = tk.Frame(main_frame, bg=self.bg_main)
        col_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        col_right = tk.Frame(main_frame, bg=self.bg_main)
        col_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))

        # ----- Left Column: Categories -----
        cat_card = self.create_card(col_left, "📁 Manage Categories")
        
        tk.Label(cat_card, text="💡 Double-click row to edit", font=("Arial", 9, "italic"), bg=self.bg_card, fg=self.text_muted).pack(anchor="e")
        self.new_cat_var = tk.StringVar()
        self.create_input(cat_card, "Category Name", "e.g. Smartphone", self.new_cat_var)
        
        # CATEGORY BUTTONS FRAME (Save, Clear, and Delete all grouped together so they don't get hidden)
        cat_btn_frame = tk.Frame(cat_card, bg=self.bg_card)
        cat_btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_save_cat = tk.Button(cat_btn_frame, text="Save Category", font=("Arial", 9, "bold"), bg=self.primary_blue, fg="white", relief="flat", cursor="hand2", padx=15, pady=6, command=self.save_category)
        self.btn_save_cat.pack(side=tk.LEFT)
        
        tk.Button(cat_btn_frame, text="Clear", font=("Arial", 9, "bold"), bg=self.bg_main, fg=self.text_dark, relief="flat", cursor="hand2", padx=10, pady=6, command=self.clear_cat_form).pack(side=tk.LEFT, padx=10)
        
        # MOVED DELETE BUTTON HERE
        tk.Button(cat_btn_frame, text="🗑️ Delete", font=("Arial", 9, "bold"), bg="#EF4444", fg="white", relief="flat", cursor="hand2", padx=15, pady=6, command=self.delete_category).pack(side=tk.RIGHT)

        # Category Table Area with Scrollbar
        cat_tree_frame = tk.Frame(cat_card, bg=self.bg_card)
        cat_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cat_scroll = ttk.Scrollbar(cat_tree_frame, orient=tk.VERTICAL)
        cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cat_tree = ttk.Treeview(cat_tree_frame, columns=("name",), show="headings", style="Modern.Treeview", height=8, yscrollcommand=cat_scroll.set)
        cat_scroll.config(command=self.cat_tree.yview)
        
        self.cat_tree.heading("name", text="Category List")
        self.cat_tree.column("name", anchor="w")
        self.cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cat_tree.bind("<Double-1>", self.load_category_edit)
        

        # ----- Right Column: Brands -----
        brand_card = self.create_card(col_right, "🏷️ Manage Brands")
        
        tk.Label(brand_card, text="💡 Double-click row to edit", font=("Arial", 9, "italic"), bg=self.bg_card, fg=self.text_muted).pack(anchor="e")
        self.new_brand_var = tk.StringVar()
        self.create_input(brand_card, "Brand Name", "e.g. Samsung", self.new_brand_var)
        
        # BRAND BUTTONS FRAME (Save, Clear, and Delete all grouped together so they don't get hidden)
        brand_btn_frame = tk.Frame(brand_card, bg=self.bg_card)
        brand_btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_save_brand = tk.Button(brand_btn_frame, text="Save Brand", font=("Arial", 9, "bold"), bg=self.primary_blue, fg="white", relief="flat", cursor="hand2", padx=15, pady=6, command=self.save_brand)
        self.btn_save_brand.pack(side=tk.LEFT)
        
        tk.Button(brand_btn_frame, text="Clear", font=("Arial", 9, "bold"), bg=self.bg_main, fg=self.text_dark, relief="flat", cursor="hand2", padx=10, pady=6, command=self.clear_brand_form).pack(side=tk.LEFT, padx=10)
        
        # MOVED DELETE BUTTON HERE
        tk.Button(brand_btn_frame, text="🗑️ Delete", font=("Arial", 9, "bold"), bg="#EF4444", fg="white", relief="flat", cursor="hand2", padx=15, pady=6, command=self.delete_brand).pack(side=tk.RIGHT)

        # Brand Table Area with Scrollbar
        brand_tree_frame = tk.Frame(brand_card, bg=self.bg_card)
        brand_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        brand_scroll = ttk.Scrollbar(brand_tree_frame, orient=tk.VERTICAL)
        brand_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.brand_tree = ttk.Treeview(brand_tree_frame, columns=("name",), show="headings", style="Modern.Treeview", height=8, yscrollcommand=brand_scroll.set)
        brand_scroll.config(command=self.brand_tree.yview)
        
        self.brand_tree.heading("name", text="Brand List")
        self.brand_tree.column("name", anchor="w")
        self.brand_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.brand_tree.bind("<Double-1>", self.load_brand_edit)

        self.load_categories_brands()

    # ================= CATEGORY & BRAND LOGIC =================
    def load_categories_brands(self):
        for item in self.cat_tree.get_children(): self.cat_tree.delete(item)
        for item in self.brand_tree.get_children(): self.brand_tree.delete(item)

        con = db_config.get_db_connection()
        if con:
            try:
                cur = con.cursor()
                cur.execute("SELECT name FROM categories ORDER BY name ASC")
                for row in cur.fetchall(): self.cat_tree.insert("", tk.END, values=(row[0],))
                
                cur.execute("SELECT name FROM brands ORDER BY name ASC")
                for row in cur.fetchall(): self.brand_tree.insert("", tk.END, values=(row[0],))
            except Exception: pass
            finally: con.close()

    # --- Category Logic ---
    def load_category_edit(self, event):
        selected = self.cat_tree.selection()
        if not selected: return
        cat_name = self.cat_tree.item(selected[0], 'values')[0]
        self.editing_cat_old = cat_name
        self.new_cat_var.set(cat_name)
        self.btn_save_cat.config(text="Update Category", bg="#10B981")

    def clear_cat_form(self):
        self.editing_cat_old = None
        self.new_cat_var.set("")
        self.btn_save_cat.config(text="Save Category", bg=self.primary_blue)

    def save_category(self):
        new_cat = self.new_cat_var.get().strip()
        if not new_cat or new_cat == "e.g. Smartphone": 
            return messagebox.showwarning("Warning", "Please enter a valid category name.")
        
        con = db_config.get_db_connection()
        if con:
            try:
                cur = con.cursor()
                if self.editing_cat_old:
                    cur.execute("UPDATE categories SET name=%s WHERE name=%s", (new_cat, self.editing_cat_old))
                else:
                    cur.execute("INSERT INTO categories (name) VALUES (%s)", (new_cat,))
                con.commit()
                self.clear_cat_form()
                self.load_categories_brands()
            except Exception:
                messagebox.showerror("Error", "Category might already exist!")
            finally: con.close()

    def delete_category(self):
        selected = self.cat_tree.selection()
        if not selected: 
            return messagebox.showwarning("Warning", "Select a category to delete.")
        
        cat_name = self.cat_tree.item(selected[0], 'values')[0]
        
        if messagebox.askyesno("Confirm", f"Delete category '{cat_name}'?"):
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("DELETE FROM categories WHERE name=%s", (cat_name,))
                    con.commit()
                    self.load_categories_brands()
                    self.clear_cat_form()
                    messagebox.showinfo("Success", "Category deleted successfully.")
                except Exception as e: 
                    messagebox.showerror("Database Error", f"Could not delete category.\nError: {e}")
                finally: 
                    con.close()

    # --- Brand Logic ---
    def load_brand_edit(self, event):
        selected = self.brand_tree.selection()
        if not selected: return
        brand_name = self.brand_tree.item(selected[0], 'values')[0]
        self.editing_brand_old = brand_name
        self.new_brand_var.set(brand_name)
        self.btn_save_brand.config(text="Update Brand", bg="#10B981")

    def clear_brand_form(self):
        self.editing_brand_old = None
        self.new_brand_var.set("")
        self.btn_save_brand.config(text="Save Brand", bg=self.primary_blue)

    def save_brand(self):
        new_brand = self.new_brand_var.get().strip()
        if not new_brand or new_brand == "e.g. Samsung": 
            return messagebox.showwarning("Warning", "Please enter a valid brand name.")
        
        con = db_config.get_db_connection()
        if con:
            try:
                cur = con.cursor()
                if self.editing_brand_old:
                    cur.execute("UPDATE brands SET name=%s WHERE name=%s", (new_brand, self.editing_brand_old))
                else:
                    cur.execute("INSERT INTO brands (name) VALUES (%s)", (new_brand,))
                con.commit()
                self.clear_brand_form()
                self.load_categories_brands()
            except Exception:
                messagebox.showerror("Error", "Brand might already exist!")
            finally: con.close()

    def delete_brand(self):
        selected = self.brand_tree.selection()
        if not selected: 
            return messagebox.showwarning("Warning", "Select a brand to delete.")
        
        brand_name = self.brand_tree.item(selected[0], 'values')[0]
        
        if messagebox.askyesno("Confirm", f"Delete brand '{brand_name}'?"):
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("DELETE FROM brands WHERE name=%s", (brand_name,))
                    con.commit()
                    self.load_categories_brands()
                    self.clear_brand_form()
                    messagebox.showinfo("Success", "Brand deleted successfully.")
                except Exception as e: 
                    messagebox.showerror("Database Error", f"Could not delete brand.\nError: {e}")
                finally: 
                    con.close()    

    # ================= HELPER FUNCTIONS =================
    def clear_form(self):
        self.editing_pid = None
        self.v_name.set(""); self.v_cat.set(""); self.v_brand.set("")
        self.v_supplier.set(""); self.v_status.set("Active")
        self.v_cost.set(""); self.v_sale.set(""); self.v_tax.set("0")
        self.v_sku.set(""); self.v_barcode.set(""); self.v_stock.set("0"); self.v_low_alert.set("5")
        if hasattr(self, 't_desc') and self.t_desc.winfo_exists():
            self.t_desc.delete("1.0", tk.END)

    def load_product_for_edit(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        
        item_values = self.tree.item(selected_item[0], 'values')
        self.editing_pid = item_values[0]
        
        self.v_sku.set(item_values[1])
        self.v_barcode.set(item_values[2])
        self.v_name.set(item_values[3])
        self.v_cat.set(item_values[4])
        self.v_brand.set(item_values[5])
        self.v_supplier.set(item_values[6])
        
        self.v_cost.set(item_values[7].replace('৳ ', '').replace(',', ''))
        self.v_sale.set(item_values[8].replace('৳ ', '').replace(',', ''))
        self.v_tax.set(item_values[9])
        self.v_stock.set(item_values[10])
        self.v_low_alert.set(item_values[11])
        self.v_status.set(item_values[12])

        con = db_config.get_db_connection()
        if con:
            try:
                cur = con.cursor()
                cur.execute("SELECT description FROM products WHERE pid=%s", (self.editing_pid,))
                desc = cur.fetchone()[0]
                if not hasattr(self, 't_desc') or not self.t_desc.winfo_exists():
                    self.t_desc = tk.Text()
                self.t_desc.delete("1.0", tk.END)
                if desc: self.t_desc.insert("1.0", desc)
            except Exception: pass
            finally: con.close()
            
        self.switch_tab("add")

    def get_list_from_table(self, table_name):
        con = db_config.get_db_connection()
        values = []
        if con:
            try:
                cur = con.cursor()
                cur.execute(f"SELECT name FROM {table_name} ORDER BY name ASC")
                values = [row[0] for row in cur.fetchall()]
            except Exception as e: 
                print(f"Error loading {table_name}: {e}")
            finally: con.close()
        return values

    def create_card(self, parent, title):
        card_border = tk.Frame(parent, bg=self.border_color)
        card_border.pack(fill=tk.X, pady=(0, 20))
        card = tk.Frame(card_border, bg=self.bg_card)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1) 
        
        inner_frame = tk.Frame(card, bg=self.bg_card, padx=25, pady=20)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(inner_frame, text=title, font=("Arial", 12, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 15))
        return inner_frame

    def create_input(self, parent, label, placeholder, var):
        f = tk.Frame(parent, bg=self.bg_card)
        f.pack(fill=tk.X, pady=(0, 15))
        tk.Label(f, text=label, font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 5))
        
        border_frame = tk.Frame(f, bg=self.border_color)
        border_frame.pack(fill=tk.X)
        inner_bg = tk.Frame(border_frame, bg=self.input_bg)
        inner_bg.pack(fill=tk.X, padx=1, pady=1)
        
        ent = tk.Entry(inner_bg, textvariable=var, font=("Arial", 10), bg=self.input_bg, bd=0, highlightthickness=0)
        ent.pack(fill=tk.X, ipady=6, padx=10)
        if placeholder and not var.get(): ent.insert(0, placeholder)
        ent.bind("<FocusIn>", lambda e: ent.delete(0, 'end') if ent.get() == placeholder else None)

    def create_grid_input(self, parent, label, var, r, c, placeholder=None):
        f = tk.Frame(parent, bg=self.bg_card)
        f.grid(row=r, column=c, sticky="ew", pady=(0, 15), padx=(0, 15 if c==0 else 0))
        tk.Label(f, text=label, font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 5))
        
        border_frame = tk.Frame(f, bg=self.border_color)
        border_frame.pack(fill=tk.X)
        inner_bg = tk.Frame(border_frame, bg=self.input_bg)
        inner_bg.pack(fill=tk.X, padx=1, pady=1)
        
        ent = tk.Entry(inner_bg, textvariable=var, font=("Arial", 10), bg=self.input_bg, bd=0, highlightthickness=0)
        ent.pack(fill=tk.X, ipady=6, padx=10)
        if placeholder and not var.get(): ent.insert(0, placeholder)
        ent.bind("<FocusIn>", lambda e: ent.delete(0, 'end') if ent.get() == placeholder else None)

    def create_dropdown(self, parent, label, var, values, state="readonly"):
        f = tk.Frame(parent, bg=self.bg_card)
        f.pack(fill=tk.X, pady=(0, 15))
        tk.Label(f, text=label, font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.text_dark).pack(anchor="w", pady=(0, 5))
        combo = ttk.Combobox(f, textvariable=var, values=values, font=("Arial", 10), state=state)
        combo.pack(fill=tk.X, ipady=3)
    # ================= THE COMPLETED DATABASE SAVE & DELETE LOGIC =================
    def save_product(self):
        name = self.v_name.get().strip()
        desc = self.t_desc.get("1.0", tk.END).strip()
        cat = self.v_cat.get().strip()
        brand = self.v_brand.get().strip()
        supplier = self.v_supplier.get().strip()
        status = self.v_status.get().strip()
        
        cost = self.v_cost.get().strip()
        sale = self.v_sale.get().strip()
        tax = self.v_tax.get().strip()
        sku = self.v_sku.get().strip()
        barcode = self.v_barcode.get().strip()
        stock = self.v_stock.get().strip()
        low_alert = self.v_low_alert.get().strip()

        if not name or name == "e.g. Premium Wireless Headphones": return messagebox.showerror("Validation", "Product Name is required!")
        if not sku or sku == "e.g. WH-001": return messagebox.showerror("Validation", "SKU is required!")
        if not sale: return messagebox.showerror("Validation", "Selling Price is required!")
        if not cat: return messagebox.showerror("Validation", "Category is required!")

        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            
            if self.editing_pid:
                # THIS IS WHERE YOUR CODE CUT OFF! Now completed:
                query = """UPDATE products SET 
                           name=%s, description=%s, category=%s, brand=%s, supplier=%s, status=%s, 
                           cost_price=%s, sale_price=%s, tax_vat=%s, sku=%s, barcode=%s, stock=%s, low_stock_alert=%s 
                           WHERE pid=%s"""
                cur.execute(query, (name, desc, cat, brand, supplier, status, cost, sale, tax, sku, barcode, stock, low_alert, self.editing_pid))
                msg = "Product Updated Successfully!"
            else:
                query = """INSERT INTO products (
                           name, description, category, brand, supplier, status, 
                           cost_price, sale_price, tax_vat, sku, barcode, stock, low_stock_alert) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cur.execute(query, (name, desc, cat, brand, supplier, status, cost, sale, tax, sku, barcode, stock, low_alert))
                msg = "Product Saved Successfully!"
                
            con.commit()
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.switch_tab("all")
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")
        finally:
            con.close()

    # ADDED PRODUCT DELETE FEATURE
    def delete_product(self):
        if not self.editing_pid:
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product? This action cannot be undone.")
        if confirm:
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("DELETE FROM products WHERE pid=%s", (self.editing_pid,))
                    con.commit()
                    messagebox.showinfo("Success", "Product deleted successfully!")
                    self.clear_form()
                    self.switch_tab("all")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete product: {e}")
                finally:
                    con.close()