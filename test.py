import tkinter as tk
from tkinter import ttk, messagebox

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IMS Pro - AI-Powered Inventory System")
        self.geometry("1200x800")
        self.configure(bg="#F4F7F6")
        
        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style(self)
        # Use 'clam' theme as a base for better styling in Tkinter
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        # Global Styles
        style.configure('TFrame', background='#F4F7F6')
        style.configure('Card.TFrame', background='white', borderwidth=1, relief='solid', bordercolor='#E2E8F0')
        
        # Sidebar Styles
        style.configure('Sidebar.TFrame', background='#1A252F')
        style.configure('Sidebar.TLabel', background='#1A252F', foreground='white', font=('Helvetica', 16, 'bold'))
        style.configure('SidebarBtn.TButton', background='#1A252F', foreground='#cbd5e1', 
                        font=('Helvetica', 11), borderwidth=0, anchor='w', padding=10)
        style.map('SidebarBtn.TButton', 
                  background=[('active', '#2C3E50'), ('pressed', '#3498DB')],
                  foreground=[('active', 'white')])
        
        # Headers & Text
        style.configure('H1.TLabel', background='#F4F7F6', foreground='#1A252F', font=('Helvetica', 20, 'bold'))
        style.configure('H2.TLabel', background='white', foreground='#1A252F', font=('Helvetica', 14, 'bold'))
        style.configure('CardValue.TLabel', background='white', foreground='#1A252F', font=('Helvetica', 24, 'bold'))
        style.configure('CardTitle.TLabel', background='white', foreground='#64748B', font=('Helvetica', 10))

    def create_layout(self):
        # Configure grid for main window
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar = ttk.Frame(self, style='Sidebar.TFrame', width=220)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Sidebar Title
        ttk.Label(self.sidebar, text="📦 IMS Pro", style='Sidebar.TLabel').pack(pady=20, padx=20, anchor='w')

        # Navigation Buttons
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Sales / POS", self.show_pos),
            ("Suppliers", None),
            ("Employees", None),
            ("Reports", None),
            ("AI Analytics", None),
            ("Settings", None)
        ]

        for text, command in nav_items:
            btn = ttk.Button(self.sidebar, text=f"  {text}", style='SidebarBtn.TButton', command=command)
            btn.pack(fill='x', padx=10, pady=2)

        # Main Content Area
        self.main_content = ttk.Frame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.columnconfigure(0, weight=1)
        self.main_content.rowconfigure(1, weight=1)

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # ---------------------------------------------------------
    # 1. Dashboard View
    # ---------------------------------------------------------
    def show_dashboard(self):
        self.clear_main_content()
        ttk.Label(self.main_content, text="Dashboard Overview", style='H1.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 20))

        content_frame = ttk.Frame(self.main_content)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure((0, 1, 2, 3), weight=1)

        # Top Row: Summary Cards
        self.create_stat_card(content_frame, "Total Products", "1,245", 0, 0)
        self.create_stat_card(content_frame, "Total Sales", "৳ 45,230", 0, 1)
        self.create_stat_card(content_frame, "Total Profit", "৳ 12,400", 0, 2)
        self.create_stat_card(content_frame, "Low Stock Alerts", "14", 0, 3)

        # Middle Row: Chart & Trending
        mid_frame = ttk.Frame(content_frame)
        mid_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=20)
        mid_frame.columnconfigure(0, weight=2)
        mid_frame.columnconfigure(1, weight=1)

        # Chart Placeholder
        chart_card = ttk.Frame(mid_frame, style='Card.TFrame')
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(chart_card, text="📊 Sales Overview", style='H2.TLabel').pack(anchor='w', padx=15, pady=15)
        canvas = tk.Canvas(chart_card, bg='white', height=200, highlightthickness=0)
        canvas.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        canvas.create_line(10, 150, 100, 100, 200, 180, 300, 50, 400, 90, 500, 30, fill="#3498DB", width=3)

        # Trending List
        trend_card = ttk.Frame(mid_frame, style='Card.TFrame')
        trend_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(trend_card, text="🔥 Trending Products", style='H2.TLabel').pack(anchor='w', padx=15, pady=15)
        trends = ["Rice ↑ +120%", "Oil ↑ +85%", "Sugar ↑ +64%", "Flour ↑ +42%"]
        for t in trends:
            ttk.Label(trend_card, text=t, background='white', foreground='#16A085', font=('Helvetica', 11)).pack(anchor='w', padx=15, pady=5)

        # Bottom Row: Low Stock & Activities
        bot_frame = ttk.Frame(content_frame)
        bot_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")
        bot_frame.columnconfigure((0, 1), weight=1)

        # Low Stock Table
        stock_card = ttk.Frame(bot_frame, style='Card.TFrame')
        stock_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(stock_card, text="⚠ Low Stock Products", style='H2.TLabel').pack(anchor='w', padx=15, pady=15)
        cols = ("Product", "Remaining")
        tree = ttk.Treeview(stock_card, columns=cols, show='headings', height=4)
        tree.heading("Product", text="Product Name")
        tree.heading("Remaining", text="Quantity")
        tree.insert("", "end", values=("Miniket Rice 50kg", "2 Bags"))
        tree.insert("", "end", values=("Rupchanda Oil 5L", "5 Btls"))
        tree.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Activities List
        act_card = ttk.Frame(bot_frame, style='Card.TFrame')
        act_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(act_card, text="🕒 Recent Activities", style='H2.TLabel').pack(anchor='w', padx=15, pady=15)
        activities = ["10m ago: Sale completed (৳ 450)", "1h ago: New product added", "3h ago: Low stock alert triggered"]
        for a in activities:
            ttk.Label(act_card, text=a, background='white', font=('Helvetica', 10)).pack(anchor='w', padx=15, pady=5)

    def create_stat_card(self, parent, title, value, row, col):
        card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        ttk.Label(card, text=title, style='CardTitle.TLabel').pack(anchor='w')
        ttk.Label(card, text=value, style='CardValue.TLabel').pack(anchor='w', pady=(5, 0))

    # ---------------------------------------------------------
    # 2. Product Management (Tabbed)
    # ---------------------------------------------------------
    def show_products(self):
        self.clear_main_content()
        ttk.Label(self.main_content, text="Product Management", style='H1.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 20))

        # Setup Notebook (Tabs)
        notebook = ttk.Notebook(self.main_content)
        notebook.grid(row=1, column=0, sticky="nsew")

        # Tab 1: All Products
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="  All Products  ")
        
        # Toolbar
        toolbar = ttk.Frame(tab1)
        toolbar.pack(fill='x', pady=15, padx=15)
        ttk.Entry(toolbar, width=40).pack(side='left')
        ttk.Button(toolbar, text="🔍 Search").pack(side='left', padx=5)
        ttk.Button(toolbar, text="⚙ Filter").pack(side='right')

        # Treeview (Data Table)
        columns = ("id", "name", "brand", "stock", "price", "actions")
        tree = ttk.Treeview(tab1, columns=columns, show='headings')
        tree.heading("id", text="ID")
        tree.heading("name", text="Product Name")
        tree.heading("brand", text="Brand/Company")
        tree.heading("stock", text="Current Stock")
        tree.heading("price", text="Price (৳)")
        tree.heading("actions", text="Actions")
        
        tree.column("id", width=50)
        tree.column("stock", width=100, anchor='center')
        tree.column("price", width=100, anchor='e')
        tree.column("actions", width=100, anchor='center')

        # Dummy Data
        mock_data = [
            ("P001", "Basmati Rice 25kg", "Pran", "45", "1650.00", "Edit/Del"),
            ("P002", "Soyabean Oil 5L", "Rupchanda", "12", "820.00", "Edit/Del"),
            ("P003", "Lentils 1kg", "Teer", "120", "110.00", "Edit/Del")
        ]
        for item in mock_data:
            tree.insert("", "end", values=item)

        tree.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Tab 2 & 3 Placeholders
        tab2 = ttk.Frame(notebook)
        ttk.Label(tab2, text="Form to Add New Product").pack(pady=50)
        notebook.add(tab2, text="  Add New Product  ")

        tab3 = ttk.Frame(notebook)
        ttk.Label(tab3, text="List of Companies and Brands").pack(pady=50)
        notebook.add(tab3, text="  Companies & Brands  ")

    # ---------------------------------------------------------
    # 3. Sales / POS Interface
    # ---------------------------------------------------------
    def show_pos(self):
        self.clear_main_content()
        ttk.Label(self.main_content, text="Point of Sale", style='H1.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 10))

        pos_frame = ttk.Frame(self.main_content)
        pos_frame.grid(row=1, column=0, sticky="nsew")
        pos_frame.columnconfigure(0, weight=3) # 60% Left
        pos_frame.columnconfigure(1, weight=2) # 40% Right
        pos_frame.rowconfigure(0, weight=1)

        # Left Side (Products Grid)
        left_frame = ttk.Frame(pos_frame, style='Card.TFrame')
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # POS Search
        ttk.Entry(left_frame, width=50, font=('Helvetica', 14)).pack(pady=15, padx=15, fill='x')
        
        # Product Grid (using Canvas/Frame for scrolling)
        grid_frame = ttk.Frame(left_frame)
        grid_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        products = [("Rice 5kg", "৳ 350"), ("Oil 1L", "৳ 165"), ("Sugar 1kg", "৳ 130"), 
                    ("Salt 1kg", "৳ 40"), ("Flour 2kg", "৳ 120"), ("Tea 500g", "৳ 200")]
        
        for i, (name, price) in enumerate(products):
            r, c = divmod(i, 3)
            p_card = ttk.Frame(grid_frame, style='Card.TFrame', padding=10)
            p_card.grid(row=r, column=c, padx=5, pady=5, sticky='nsew')
            ttk.Label(p_card, text="[IMG]", background='white', foreground='#cbd5e1').pack()
            ttk.Label(p_card, text=name, background='white', font=('Helvetica', 10, 'bold')).pack(pady=5)
            ttk.Label(p_card, text=price, background='white', foreground='#16A085').pack()

        # Right Side (Cart & Billing)
        right_frame = ttk.Frame(pos_frame, style='Card.TFrame')
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        ttk.Label(right_frame, text="🛒 Current Cart", style='H2.TLabel').pack(anchor='w', padx=15, pady=15)
        
        # Cart Listbox
        cart_list = tk.Listbox(right_frame, font=('Helvetica', 11), height=10, borderwidth=0)
        cart_list.pack(fill='both', expand=True, padx=15)
        cart_list.insert(tk.END, "1x Rice 5kg          ৳ 350.00")
        cart_list.insert(tk.END, "2x Oil 1L               ৳ 330.00")

        # Billing Details
        billing_frame = ttk.Frame(right_frame, style='Card.TFrame', padding=15)
        billing_frame.pack(fill='x', side='bottom')
        
        ttk.Label(billing_frame, text="Subtotal: ৳ 680.00", background='white', font=('Helvetica', 11)).pack(anchor='e', pady=2)
        ttk.Label(billing_frame, text="Discount: ৳ 0.00", background='white', font=('Helvetica', 11)).pack(anchor='e', pady=2)
        ttk.Label(billing_frame, text="Tax (5%): ৳ 34.00", background='white', font=('Helvetica', 11)).pack(anchor='e', pady=2)
        ttk.Label(billing_frame, text="Total: ৳ 714.00", background='white', font=('Helvetica', 16, 'bold')).pack(anchor='e', pady=10)

        # Buttons
        btn_frame = ttk.Frame(billing_frame, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=(10, 0))
        btn_frame.columnconfigure((0, 1), weight=1)
        
        ttk.Button(btn_frame, text="Print Receipt").grid(row=0, column=0, sticky='ew', padx=2)
        
        # Tkinter lacks simple button coloring without custom styles, but logic remains
        invoice_btn = ttk.Button(btn_frame, text="Generate Invoice")
        invoice_btn.grid(row=0, column=1, sticky='ew', padx=2)

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()