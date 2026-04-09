import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import db_config

class StockClass:
    def __init__(self, content_area):
        self.content_area = content_area
        self.bg_main = "#F4F6F8" 
        self.bg_card = "#FFFFFF"
        
        # --- Pagination Variables ---
        self.page_size = 50 
        self.current_page = 1
        self.total_pages = 1
        
        # KPI ভেরিয়েবলগুলো
        self.var_total_items = tk.StringVar(value="0")
        self.var_low_stock = tk.StringVar(value="0")
        self.var_out_of_stock = tk.StringVar(value="0")
        self.var_stock_value = tk.StringVar(value="৳ 0.00")
        self.search_var = tk.StringVar()
        
        # বর্তমান ফিল্টার স্ট্যাটাস
        self.current_filter = "All"

        self.build_ui()
        self.load_real_data()

    def build_ui(self):
        main_frame = tk.Frame(self.content_area, bg=self.bg_main)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Top Header ---
        header_frame = tk.Frame(main_frame, bg=self.bg_main)
        header_frame.pack(fill=tk.X, padx=30, pady=(20, 10))
        tk.Label(header_frame, text="Stock Management", font=("Segoe UI", 18, "bold"), bg=self.bg_main, fg="#1F2937").pack(side=tk.LEFT)
        
        # Active Filter Label
        self.lbl_active_filter = tk.Label(header_frame, text="Showing: All Items", font=("Segoe UI", 10, "italic"), bg=self.bg_main, fg="#6B7280")
        self.lbl_active_filter.pack(side=tk.LEFT, padx=20, pady=5)

        # --- KPI Cards Section ---
        kpi_frame = tk.Frame(main_frame, bg=self.bg_main)
        kpi_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        for i in range(4): kpi_frame.columnconfigure(i, weight=1)

        self.create_kpi_card(kpi_frame, 0, "Total Items in Stock", self.var_total_items, "📦", "#E0F2FE", "#0284C7")
        self.create_kpi_card(kpi_frame, 1, "Low Stock Alerts", self.var_low_stock, "⚠️", "#FEF3C7", "#D97706")
        self.create_kpi_card(kpi_frame, 2, "Out of Stock", self.var_out_of_stock, "❌", "#FEE2E2", "#DC2626")
        self.create_kpi_card(kpi_frame, 3, "Total Stock Value", self.var_stock_value, "💰", "#D1FAE5", "#059669")

        # --- Toolbar Section ---
        toolbar_frame = tk.Frame(main_frame, bg=self.bg_main)
        toolbar_frame.pack(fill=tk.X, padx=30, pady=(0, 15))

        search_frame = tk.Frame(toolbar_frame, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        search_frame.pack(side=tk.LEFT)
        tk.Label(search_frame, text="🔍", bg="white", fg="#9CA3AF").pack(side=tk.LEFT, padx=(10, 0))
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10), bg="white", bd=0, width=30, insertbackground="black")
        search_entry.pack(side=tk.LEFT, padx=5, pady=8)
        search_entry.bind("<KeyRelease>", lambda e: self.search_data()) 

        # Filter & Export Buttons 
        tk.Button(toolbar_frame, text="⚙️ Filters", font=("Segoe UI", 10), bg="white", fg="#374151", relief="flat", cursor="hand2", highlightbackground="#E5E7EB", highlightthickness=1, padx=15, pady=6, command=self.show_filter_menu).pack(side=tk.LEFT, padx=10)
        
        tk.Button(toolbar_frame, text="+ Stock Adjustment", font=("Segoe UI", 10, "bold"), bg="#1F2937", fg="white", relief="flat", cursor="hand2", padx=15, pady=6, command=self.open_adjustment_modal).pack(side=tk.RIGHT)
        tk.Button(toolbar_frame, text="📥 Export CSV", font=("Segoe UI", 10), bg="white", fg="#374151", relief="flat", cursor="hand2", highlightbackground="#E5E7EB", highlightthickness=1, padx=15, pady=6, command=self.export_to_csv).pack(side=tk.RIGHT, padx=10)

        # --- Table Section (Professional Look) ---
        table_container = tk.Frame(main_frame, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("default")
        # Row height কমিয়ে ৩২ করা হলো লেখার ডেনসিটি বাড়ানোর জন্য
        style.configure("Modern.Treeview", background="white", foreground="#374151", rowheight=32, fieldbackground="white", borderwidth=0, font=("Segoe UI", 10))
        style.configure("Modern.Treeview.Heading", background="#F9FAFB", foreground="#4B5563", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=8)
        style.map("Modern.Treeview", background=[('selected', '#F3F4F6')], foreground=[('selected', '#111827')])

        scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # ৮টি কলাম ডিক্লেয়ার করা হলো (PID সহ)
        self.inv_tree = ttk.Treeview(table_container, columns=("pid", "product", "sku", "category", "supplier", "stock", "status", "price"), show="headings", style="Modern.Treeview", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.inv_tree.yview)

        # ডিসপ্লেতে শুধু ৭টি কলাম দেখাবে (PID ডাটাবেস আইডির মত ব্যাকএন্ডে থাকবে)
        self.inv_tree["displaycolumns"] = ("product", "sku", "category", "supplier", "stock", "status", "price")

        # Headings
        self.inv_tree.heading("product", text="Product Name", anchor="w")
        self.inv_tree.heading("sku", text="SKU", anchor="w")
        self.inv_tree.heading("category", text="Category", anchor="w")
        self.inv_tree.heading("supplier", text="Supplier", anchor="w")
        self.inv_tree.heading("stock", text="Stock Level", anchor="w")
        self.inv_tree.heading("status", text="Status", anchor="center")
        self.inv_tree.heading("price", text="Cost Price", anchor="w")

        # Professional Column Widths
        self.inv_tree.column("product", width=220, anchor="w")
        self.inv_tree.column("sku", width=100, anchor="w")
        self.inv_tree.column("category", width=120, anchor="w")
        self.inv_tree.column("supplier", width=150, anchor="w")
        self.inv_tree.column("stock", width=100, anchor="w")
        self.inv_tree.column("status", width=110, anchor="center")
        self.inv_tree.column("price", width=110, anchor="w")

        self.inv_tree.pack(fill=tk.BOTH, expand=True)

        self.inv_tree.tag_configure("in_stock", foreground="#059669", font=("Segoe UI", 10, "bold"))  
        self.inv_tree.tag_configure("low_stock", foreground="#D97706", font=("Segoe UI", 10, "bold")) 
        self.inv_tree.tag_configure("out_of_stock", foreground="#DC2626", font=("Segoe UI", 10, "bold")) 

        # --- Pagination Section ---
        pagination_frame = tk.Frame(main_frame, bg=self.bg_main)
        pagination_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        self.btn_prev = tk.Button(pagination_frame, text="⟪ Previous", font=("Segoe UI", 9), bg="white", fg="#374151", relief="flat", cursor="hand2", highlightbackground="#E5E7EB", highlightthickness=1, padx=10, pady=5, command=self.prev_page)
        self.btn_prev.pack(side=tk.LEFT)

        self.lbl_page_info = tk.Label(pagination_frame, text="Page 1 of 1", font=("Segoe UI", 10, "bold"), bg=self.bg_main, fg="#4B5563")
        self.lbl_page_info.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(pagination_frame, text="Next ⟫", font=("Segoe UI", 9), bg="white", fg="#374151", relief="flat", cursor="hand2", highlightbackground="#E5E7EB", highlightthickness=1, padx=10, pady=5, command=self.next_page)
        self.btn_next.pack(side=tk.RIGHT)


    def create_kpi_card(self, parent, col, title, var, icon, icon_bg, icon_fg):
        card = tk.Frame(parent, bg=self.bg_card, highlightbackground="#E5E7EB", highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col==0 else 10, 10 if col!=3 else 0))
        
        top_frame = tk.Frame(card, bg=self.bg_card)
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(top_frame, text=title, font=("Segoe UI", 10, "bold"), fg="#6B7280", bg=self.bg_card).pack(side=tk.LEFT)
        tk.Label(top_frame, text=icon, font=("Segoe UI", 12), bg=icon_bg, fg=icon_fg, width=3, height=1).pack(side=tk.RIGHT)
        tk.Label(card, textvariable=var, font=("Segoe UI", 24, "bold"), fg="#111827", bg=self.bg_card).pack(anchor="w", padx=15, pady=(0, 15))

    # ==========================================
    # 🔍 DATA LOADING & FILTERING LOGIC
    # ==========================================
    def load_real_data(self, search_query=""):
        con = db_config.get_db_connection()
        if not con:
            return

        try:
            cur = con.cursor()
            
            # KPI Data Fetch
            cur.execute("SELECT SUM(stock) FROM products")
            tot_items = cur.fetchone()[0]
            self.var_total_items.set(str(tot_items) if tot_items else "0")

            cur.execute("SELECT COUNT(*) FROM products WHERE stock <= low_stock_alert AND stock > 0")
            low_stk = cur.fetchone()[0]
            self.var_low_stock.set(str(low_stk) if low_stk else "0")

            cur.execute("SELECT COUNT(*) FROM products WHERE stock = 0")
            out_stk = cur.fetchone()[0]
            self.var_out_of_stock.set(str(out_stk) if out_stk else "0")

            cur.execute("SELECT SUM(stock * cost_price) FROM products")
            tot_val = cur.fetchone()[0]
            self.var_stock_value.set(f"৳ {tot_val:,.2f}" if tot_val else "৳ 0.00")

            # Count total filtered items for Pagination
            count_query = "SELECT COUNT(*) FROM products WHERE 1=1"
            params = []
            
            if search_query:
                count_query += " AND (name LIKE %s OR sku LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
                
            if self.current_filter == "Low Stock":
                count_query += " AND stock <= low_stock_alert AND stock > 0"
            elif self.current_filter == "Out of Stock":
                count_query += " AND stock = 0"
            elif self.current_filter == "In Stock":
                count_query += " AND stock > low_stock_alert"

            cur.execute(count_query, tuple(params))
            total_records = cur.fetchone()[0]
            
            self.total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)

            # Table Data Fetch
            self.inv_tree.delete(*self.inv_tree.get_children())
            
            # কুয়েরিতে Supplier যোগ করা হলো
            query = "SELECT pid, name, sku, category, stock, low_stock_alert, cost_price, supplier FROM products WHERE 1=1"
            
            if search_query:
                query += " AND (name LIKE %s OR sku LIKE %s)"
            if self.current_filter == "Low Stock":
                query += " AND stock <= low_stock_alert AND stock > 0"
            elif self.current_filter == "Out of Stock":
                query += " AND stock = 0"
            elif self.current_filter == "In Stock":
                query += " AND stock > low_stock_alert"

            query += " ORDER BY name ASC"
            
            offset = (self.current_page - 1) * self.page_size
            query += f" LIMIT {self.page_size} OFFSET {offset}"
            
            cur.execute(query, tuple(params))
                
            for row in cur.fetchall():
                pid, name, sku, category, stock, alert_level, cost, supplier = row
                
                sku_disp = sku if sku else "N/A"
                cat_disp = category if category else "Uncategorized"
                sup_disp = supplier if supplier else "Unknown"
                cost_disp = f"৳ {cost:,.2f}" if cost else "৳ 0.00"
                stock_qty = stock if stock else 0
                alert = alert_level if alert_level else 5
                
                stock_format = f"{stock_qty} Units"
                
                if stock_qty == 0:
                    status = "Out of Stock"; tag = "out_of_stock"
                elif stock_qty <= alert:
                    status = "Low Stock"; tag = "low_stock"
                else:
                    status = "In Stock"; tag = "in_stock"
                    
                # কলাম সিকোয়েন্স অনুযায়ী ডাটা ইনসার্ট
                self.inv_tree.insert("", tk.END, values=(pid, name, sku_disp, cat_disp, sup_disp, stock_format, status, cost_disp), tags=(tag,))

            self.lbl_page_info.config(text=f"Page {self.current_page} of {self.total_pages}")
            self.btn_prev.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)

        except Exception as e:
            print(f"Error loading stock: {e}")
        finally:
            con.close()

    def search_data(self):
        self.current_page = 1 
        query = self.search_var.get().strip()
        self.load_real_data(query)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_real_data(self.search_var.get().strip())

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_real_data(self.search_var.get().strip())

    # ==========================================
    # ⚙️ FILTER MENU LOGIC
    # ==========================================
    def show_filter_menu(self):
        menu = tk.Menu(self.content_area, tearoff=0, bg="white", fg="#374151", font=("Segoe UI", 10), activebackground="#F3F4F6", activeforeground="#111827")
        menu.add_command(label="📦 All Items", command=lambda: self.apply_filter("All"))
        menu.add_separator()
        menu.add_command(label="✅ In Stock", command=lambda: self.apply_filter("In Stock"))
        menu.add_command(label="⚠️ Low Stock", command=lambda: self.apply_filter("Low Stock"))
        menu.add_command(label="❌ Out of Stock", command=lambda: self.apply_filter("Out of Stock"))
        
        x = self.content_area.winfo_pointerx()
        y = self.content_area.winfo_pointery()
        menu.tk_popup(x, y)

    def apply_filter(self, filter_type):
        self.current_filter = filter_type
        self.lbl_active_filter.config(text=f"Showing: {filter_type}")
        self.current_page = 1 
        self.load_real_data(self.search_var.get().strip())

    # ==========================================
    # 📥 EXPORT TO CSV LOGIC
    # ==========================================
    def export_to_csv(self):
        if not self.inv_tree.get_children():
            messagebox.showwarning("Empty Data", "There is no data to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Stock Report"
        )
        
        if not file_path: return 
            
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # কলাম অনুযায়ী হেডার
                writer.writerow(["Product Name", "SKU", "Category", "Supplier", "Stock Level", "Status", "Cost Price"])
                
                for item in self.inv_tree.get_children():
                    row = self.inv_tree.item(item, 'values')
                    # values = (pid, product, sku, category, supplier, stock, status, price)
                    # তাই row[1] থেকে ডাটা রাইট করা হবে
                    writer.writerow([row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
                    
            messagebox.showinfo("Export Successful", f"Stock report saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")

    # ==========================================
    # 🛠️ STOCK ADJUSTMENT MODAL
    # ==========================================
    def open_adjustment_modal(self):
        selected_row = self.inv_tree.focus()
        if not selected_row:
            messagebox.showwarning("Selection Required", "Please select a product first.")
            return
            
        values = self.inv_tree.item(selected_row, 'values')
        pid = values[0] 
        prod_name = values[1]
        sku = values[2]
        current_stock_str = values[5] # কলাম বদলানোর কারণে এখন ৫ নম্বর ইনডেক্সে স্টক আছে
        current_stock = int(current_stock_str.split(" ")[0]) 

        self.adj_win = tk.Toplevel(self.content_area)
        self.adj_win.title("Adjust Stock Level")
        self.adj_win.geometry("450x400")
        self.adj_win.configure(bg="white")
        self.adj_win.resizable(False, False)
        
        self.adj_win.transient(self.content_area.winfo_toplevel())
        self.adj_win.grab_set() 

        tk.Label(self.adj_win, text="⚙️ Stock Adjustment", font=("Segoe UI", 16, "bold"), bg="white", fg="#1F2937").pack(pady=(20, 10))

        info_frame = tk.Frame(self.adj_win, bg="#F3F4F6", padx=15, pady=10)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(info_frame, text=f"{prod_name} (SKU: {sku})", font=("Segoe UI", 10, "bold"), bg="#F3F4F6", fg="#374151", wraplength=380).pack(anchor="w")
        tk.Label(info_frame, text=f"Current Stock: {current_stock} Units", font=("Segoe UI", 10), bg="#F3F4F6", fg="#059669").pack(anchor="w", pady=(5,0))

        form_frame = tk.Frame(self.adj_win, bg="white")
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10)

        tk.Label(form_frame, text="Adjustment Type *", font=("Segoe UI", 10), bg="white", fg="#374151").grid(row=0, column=0, sticky="w", pady=5)
        var_adj_type = tk.StringVar(value="Add Stock (+)")
        type_combo = ttk.Combobox(form_frame, textvariable=var_adj_type, values=["Add Stock (+)", "Deduct Stock (-)"], state="readonly", font=("Segoe UI", 10), width=25)
        type_combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, text="Quantity *", font=("Segoe UI", 10), bg="white", fg="#374151").grid(row=1, column=0, sticky="w", pady=15)
        var_qty = tk.StringVar()
        qty_entry = tk.Entry(form_frame, textvariable=var_qty, font=("Segoe UI", 11), bg="#F9FAFB", highlightbackground="#E5E7EB", highlightthickness=1, width=27)
        qty_entry.grid(row=1, column=1, padx=10, pady=15, sticky="w")
        
        tk.Label(form_frame, text="Reason (Optional)", font=("Segoe UI", 10), bg="white", fg="#374151").grid(row=2, column=0, sticky="w", pady=5)
        var_reason = tk.StringVar()
        reason_entry = tk.Entry(form_frame, textvariable=var_reason, font=("Segoe UI", 11), bg="#F9FAFB", highlightbackground="#E5E7EB", highlightthickness=1, width=27)
        reason_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        btn_frame = tk.Frame(self.adj_win, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10), bg="#F3F4F6", fg="#374151", relief="flat", cursor="hand2", padx=15, pady=8, command=self.adj_win.destroy).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Save Adjustment", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", relief="flat", cursor="hand2", padx=15, pady=8, 
                  command=lambda: self.save_adjustment(pid, current_stock, var_adj_type.get(), var_qty.get())).pack(side=tk.RIGHT)

    def save_adjustment(self, pid, current_stock, adj_type, qty_str):
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for quantity.", parent=self.adj_win)
            return
            
        qty = int(qty_str)
        
        if "Add" in adj_type:
            new_stock = current_stock + qty
        else:
            new_stock = current_stock - qty
            if new_stock < 0:
                messagebox.showerror("Invalid Adjustment", f"Cannot deduct {qty} units. Only {current_stock} units available.", parent=self.adj_win)
                return

        con = db_config.get_db_connection()
        if con:
            try:
                cur = con.cursor()
                cur.execute("UPDATE products SET stock = %s WHERE pid = %s", (new_stock, pid))
                con.commit()
                
                messagebox.showinfo("Success", f"Stock successfully updated to {new_stock} units.", parent=self.adj_win)
                self.adj_win.destroy()
                self.load_real_data(self.search_var.get().strip()) 
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating stock: {e}", parent=self.adj_win)
            finally:
                con.close()