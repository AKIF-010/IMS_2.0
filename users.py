import tkinter as tk
from tkinter import ttk, messagebox
import db_config
from datetime import datetime

class UsersClass:
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
        self.role_purple  = "#7C3AED"
        self.success      = "#10B981"
        self.danger       = "#EF4444"
        self.input_bg     = "#F9FAFB"

        # ── Font stack ────────────────────────────────────────────────
        self.F_TITLE  = ("Segoe UI", 18, "bold")
        self.F_SUB    = ("Segoe UI", 10)
        self.F_LABEL  = ("Segoe UI",  9, "bold")
        self.F_NORMAL = ("Segoe UI", 10)
        self.F_BTN    = ("Segoe UI", 10, "bold")
        self.F_TAB    = ("Segoe UI", 10)
        self.F_TAB_A  = ("Segoe UI", 10, "bold")
        self.F_CARD_V = ("Segoe UI", 24, "bold")
        self.F_CARD_T = ("Segoe UI", 11, "bold")
        self.F_HINT   = ("Segoe UI",  9, "italic")

        self.search_var = tk.StringVar()
        
        # User Filters
        self.current_user_role_filter = "All"
        self.current_user_status_filter = "All"

        self._setup_treeview_style()
        self._build_tab_bar()

        # Content frames (one per tab)
        self.frame_users = tk.Frame(self.root, bg=self.bg_page)
        self.frame_logs  = tk.Frame(self.root, bg=self.bg_page)

        self._build_users_tab()
        self._build_logs_tab()
        self._switch_tab("users")

    # ─────────────────────────────────────────────────────────────────
    # STYLES
    # ─────────────────────────────────────────────────────────────────
    def _setup_treeview_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Increased rowheight to 54 to match the spacious web look
        style.configure("Modern.Treeview",
            background=self.bg_card, fieldbackground=self.bg_card,
            foreground=self.text_dark, rowheight=54, borderwidth=0,
            font=("Segoe UI", 10))
        
        # Heading styling
        style.configure("Modern.Treeview.Heading",
            background="#FFFFFF", foreground="#6B7280",
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(0, 15))
            
        style.map("Modern.Treeview",
            background=[("selected", "#F3F4F6")],
            foreground=[("selected", self.text_dark)])

    # ─────────────────────────────────────────────────────────────────
    # TAB BAR
    # ─────────────────────────────────────────────────────────────────
    def _build_tab_bar(self):
        bar = tk.Frame(self.root, bg=self.bg_page)
        bar.pack(fill=tk.X, padx=30, pady=(10, 0))

        self.btn_tab_users = tk.Button(
            bar, text="  Manage Users  ", font=self.F_TAB_A,
            bg=self.primary_blue, fg="white", relief="flat", bd=0,
            cursor="hand2", padx=6, pady=7,
            activebackground=self.primary_blue, activeforeground="white",
            command=lambda: self._switch_tab("users"))
        self.btn_tab_users.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_tab_logs = tk.Button(
            bar, text="  Login Logs  ", font=self.F_TAB,
            bg="#F1F5F9", fg="#64748B", relief="flat", bd=0,
            cursor="hand2", padx=6, pady=7,
            activebackground=self.primary_blue, activeforeground="white",
            command=lambda: self._switch_tab("logs"))
        self.btn_tab_logs.pack(side=tk.LEFT)

        tk.Frame(self.root, bg=self.border_color, height=1).pack(fill=tk.X, padx=30)

    def _switch_tab(self, tab):
        self.frame_users.pack_forget()
        self.frame_logs.pack_forget()
        if tab == "users":
            self.btn_tab_users.config(bg=self.primary_blue, fg="white", font=self.F_TAB_A)
            self.btn_tab_logs.config(bg="#F1F5F9", fg="#64748B", font=self.F_TAB)
            self.frame_users.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._refresh_summary()
            self._load_users()
        else:
            self.btn_tab_logs.config(bg=self.primary_blue, fg="white", font=self.F_TAB_A)
            self.btn_tab_users.config(bg="#F1F5F9", fg="#64748B", font=self.F_TAB)
            self.frame_logs.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)
            self._load_logs()

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 1 : MANAGE USERS ─────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_users_tab(self):
        # ── Summary cards ─────────────────────────────────────────────
        cards_row = tk.Frame(self.frame_users, bg=self.bg_page)
        cards_row.pack(fill=tk.X, pady=(0, 18))
        for i in range(4):
            cards_row.columnconfigure(i, weight=1)

        self._card_total_users  = self._kpi_card(cards_row, 0, "Total Users",        "👥")
        self._card_admins       = self._kpi_card(cards_row, 1, "Active Admins",      "🛡")
        self._card_staff        = self._kpi_card(cards_row, 2, "Active Staff",       "💼")
        self._card_inactive     = self._kpi_card(cards_row, 3, "Inactive Accounts",  "⛔")

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = tk.Frame(self.frame_users, bg=self.bg_page)
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
        se.insert(0, "Search users by name or email…")
        se.bind("<FocusIn>",
                lambda e: se.delete(0, "end") if se.get() == "Search users by name or email…" else None)
        se.bind("<KeyRelease>", self._search_users)

        # Right buttons
        self._make_btn(toolbar, "+ Add New User", self.text_dark, "white",
                       cmd=self._open_add_modal).pack(side=tk.RIGHT)
        
        btn_filter = self._make_btn(toolbar, "⚙ Filter", "#F1F5F9", self.text_dark, border=True)
        btn_filter.pack(side=tk.RIGHT, padx=(0, 8))
        btn_filter.bind("<Button-1>", self._show_user_filter_menu)

        # ── Users table ───────────────────────────────────────────────
        tbl_card = tk.Frame(self.frame_users, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(tbl_card, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Added 'salary' column
        cols = ("emp_id", "name", "role", "email", "contact", "salary", "status", "last_login", "actions")
        self.user_table = ttk.Treeview(tbl_card, columns=cols, show="headings",
                                       style="Modern.Treeview",
                                       yscrollcommand=scroll_y.set,
                                       xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.user_table.yview)
        scroll_x.config(command=self.user_table.xview)

        self.user_table.column("emp_id", width=0, stretch=False)
        self.user_table.heading("emp_id", text="")

        # Adjusted widths and alignments to match the picture (Left aligned Name)
        col_cfg = [
            ("name",       "User",           180, "w"),
            ("role",       "Role",            90, "center"),
            ("email",      "Email Address",  200, "center"),
            ("contact",    "Contact",        110, "center"),
            ("salary",     "Salary",          90, "center"),
            ("status",     "Status",          90, "center"),
            ("last_login", "Last Login",     150, "center"),
            ("actions",    "Actions",         80, "center"),
        ]
        for col, heading, width, anchor in col_cfg:
            self.user_table.heading(col, text=heading)
            self.user_table.column(col, width=width, anchor=anchor)

        # Clean alternating rows
        self.user_table.tag_configure("row_even", background="#FFFFFF")
        self.user_table.tag_configure("row_odd",  background="#F9FAFB")

        self.user_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.user_table.bind("<ButtonRelease-1>", self._on_user_action_click)
        self.user_table.bind("<Double-1>", self._on_user_double_click)

    def _show_user_filter_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, font=self.F_NORMAL, bg=self.bg_card, fg=self.text_dark)
        menu.add_command(label="Show All Users", command=lambda: self._apply_user_filter("All", "All"))
        menu.add_separator()
        menu.add_command(label="Status: Active", command=lambda: self._apply_user_filter("All", "Active"))
        menu.add_command(label="Status: Inactive", command=lambda: self._apply_user_filter("All", "Inactive"))
        menu.add_separator()
        menu.add_command(label="Role: Admin Only", command=lambda: self._apply_user_filter("Admin", "All"))
        menu.add_command(label="Role: Staff Only", command=lambda: self._apply_user_filter("Staff", "All"))

        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        menu.post(x, y)

    def _apply_user_filter(self, role, status):
        self.current_user_role_filter = role
        self.current_user_status_filter = status
        self._load_users()

    # ─────────────────────────────────────────────────────────────────
    # ── TAB 2 : LOGIN LOGS ───────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    def _build_logs_tab(self):
        ctrl = tk.Frame(self.frame_logs, bg=self.bg_page)
        ctrl.pack(fill=tk.X, pady=(0, 12))

        title_f = tk.Frame(ctrl, bg=self.bg_page)
        title_f.pack(side=tk.LEFT)
        tk.Label(title_f, text="Login History",
                 font=("Segoe UI", 14, "bold"), bg=self.bg_page, fg=self.text_dark).pack(anchor="w")
        tk.Label(title_f, text="Review all user sign-ins and session timestamps.",
                 font=self.F_HINT, bg=self.bg_page, fg=self.text_muted).pack(anchor="w")

        self._make_btn(ctrl, "↻ Refresh", "#F1F5F9", self.text_dark,
                       cmd=self._load_logs, border=True).pack(side=tk.RIGHT)

        filter_frame = tk.Frame(ctrl, bg=self.bg_page)
        filter_frame.pack(side=tk.RIGHT, padx=15)
        
        tk.Label(filter_frame, text="Filter:", font=self.F_NORMAL, bg=self.bg_page).pack(side=tk.LEFT, padx=5)
        self.log_filter_var = tk.StringVar(value="All Time")
        self.log_filter_cb = ttk.Combobox(filter_frame, textvariable=self.log_filter_var, 
                                          values=["All Time", "Today", "Last 7 Days"], 
                                          state="readonly", font=self.F_NORMAL, width=15)
        self.log_filter_cb.pack(side=tk.LEFT)
        self.log_filter_cb.bind("<<ComboboxSelected>>", lambda e: self._load_logs())

        tbl_card = tk.Frame(self.frame_logs, bg=self.bg_card,
                            highlightbackground=self.border_color, highlightthickness=1)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(tbl_card, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(tbl_card, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        log_cols = ("log_id", "user", "role", "login_time")
        self.logs_table = ttk.Treeview(tbl_card, columns=log_cols, show="headings",
                                       style="Modern.Treeview",
                                       yscrollcommand=scroll_y.set,
                                       xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.logs_table.yview)
        scroll_x.config(command=self.logs_table.xview)

        self.logs_table.column("log_id", width=0, stretch=False)
        self.logs_table.heading("log_id", text="")

        log_col_cfg = [
            ("user",       "User",       300, "center"),
            ("role",       "Role",       150, "center"),
            ("login_time", "Login Time", 300, "center"),
        ]
        for col, heading, width, anchor in log_col_cfg:
            self.logs_table.heading(col, text=heading)
            self.logs_table.column(col, width=width, anchor=anchor)

        self.logs_table.tag_configure("row_even", background="#FFFFFF")
        self.logs_table.tag_configure("row_odd",  background="#F9FAFB")

        self.logs_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # ─────────────────────────────────────────────────────────────────
    # DATABASE — USERS
    # ─────────────────────────────────────────────────────────────────
    def _refresh_summary(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            self._card_total_users.config(text=str(cur.fetchone()[0]))
            cur.execute("SELECT COUNT(*) FROM users WHERE status='Active' AND role='Admin'")
            self._card_admins.config(text=str(cur.fetchone()[0]))
            cur.execute("SELECT COUNT(*) FROM users WHERE status='Active' AND role!='Admin'")
            self._card_staff.config(text=str(cur.fetchone()[0]))
            cur.execute("SELECT COUNT(*) FROM users WHERE status='Inactive'")
            self._card_inactive.config(text=str(cur.fetchone()[0]))
        except Exception: pass
        finally:
            if con.is_connected(): con.close()

    def _load_users(self, search_text=""):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            
            # Added salary to query
            query = "SELECT emp_id, name, role, email, contact, salary, status FROM users WHERE 1=1 "
            params = []
            
            if search_text and search_text != "Search users by name or email…":
                t = f"%{search_text}%"
                query += "AND (name LIKE %s OR email LIKE %s OR role LIKE %s) "
                params.extend([t, t, t])
                
            if self.current_user_role_filter != "All":
                query += "AND role = %s "
                params.append(self.current_user_role_filter)
                
            if self.current_user_status_filter != "All":
                query += "AND status = %s "
                params.append(self.current_user_status_filter)
                
            query += "ORDER BY emp_id DESC"
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            cur.execute("SELECT emp_id, MAX(login_time) FROM login_logs GROUP BY emp_id")
            login_map = {r[0]: r[1] for r in cur.fetchall()}

            self.user_table.delete(*self.user_table.get_children())
            for i, row in enumerate(rows):
                emp_id, name, role, email, contact, salary, status = row
                
                # Formatting to look as close to the image as possible
                fmt_name    = f"  👤 {name}" 
                contact     = contact or "—"
                fmt_salary  = f"৳ {salary}" if salary else "—"
                fmt_role    = f"[{role}]"
                fmt_status  = f"● {status}"
                
                # Gray pencil, Red trash can spaced out
                actions = " ✎      🗑️" 

                last_login_dt = login_map.get(emp_id)
                if last_login_dt and isinstance(last_login_dt, datetime):
                    today = datetime.now().date()
                    if last_login_dt.date() == today:
                        last_login = f"Today, {last_login_dt.strftime('%I:%M %p')}"
                    else:
                        last_login = last_login_dt.strftime("%d %b %Y, %I:%M %p")
                else:
                    last_login = "Never"

                tag = "row_even" if i % 2 == 0 else "row_odd"

                self.user_table.insert("", tk.END,
                    values=(emp_id, fmt_name, fmt_role, email, contact, fmt_salary,
                            fmt_status, last_login, actions),
                    tags=(tag,))
        except Exception as e:
            print(f"Load users error: {e}")
        finally:
            if con.is_connected(): con.close()

    def _search_users(self, event=None):
        q = self.search_var.get().strip()
        self._load_users(q)

    # ─────────────────────────────────────────────────────────────────
    # DATABASE — LOGS
    # ─────────────────────────────────────────────────────────────────
    def _load_logs(self):
        con = db_config.get_db_connection()
        if not con: return
        try:
            cur = con.cursor()
            filter_val = self.log_filter_var.get()
            
            query = (
                "SELECT l.log_id, u.name, u.role, l.login_time "
                "FROM login_logs l "
                "JOIN users u ON l.emp_id = u.emp_id "
            )
            
            if filter_val == "Today":
                query += "WHERE DATE(l.login_time) = CURDATE() "
            elif filter_val == "Last 7 Days":
                query += "WHERE l.login_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) "
                
            query += "ORDER BY l.login_time DESC"

            cur.execute(query)
            rows = cur.fetchall()

            self.logs_table.delete(*self.logs_table.get_children())
            for i, row in enumerate(rows):
                log_id, name, role, login_time = row
                if isinstance(login_time, datetime):
                    today_d = datetime.now().date()
                    if login_time.date() == today_d:
                        fmt_time = f"Today, {login_time.strftime('%I:%M %p')}"
                    else:
                        fmt_time = login_time.strftime("%d %b %Y, %I:%M %p")
                else:
                    fmt_time = str(login_time)

                tag = "row_even" if i % 2 == 0 else "row_odd"
                
                self.logs_table.insert("", tk.END,
                    values=(log_id, name, f"[{role}]", fmt_time),
                    tags=(tag,))

        except Exception as e:
            print(f"Load logs error: {e}")
        finally:
            if con.is_connected(): con.close()

    # ─────────────────────────────────────────────────────────────────
    # ADD / EDIT USER MODAL
    # ─────────────────────────────────────────────────────────────────
    def _open_add_modal(self, emp_id=None):
        edit_mode = emp_id is not None
        existing = None

        if edit_mode:
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute(
                        "SELECT name, email, role, contact, salary, status "
                        "FROM users WHERE emp_id=%s", (emp_id,))
                    existing = cur.fetchone()
                except Exception: pass
                finally: con.close()
            if not existing:
                messagebox.showerror("Error", "Could not load user data.")
                return

        win = tk.Toplevel(self.root)
        win.title("Edit User" if edit_mode else "Add New User")
        win.geometry("540x620")
        win.configure(bg=self.bg_card)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 270
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 310
        win.geometry(f"+{x}+{y}")

        hdr_color = "#10B981" if edit_mode else self.primary_blue
        hdr = tk.Frame(win, bg=hdr_color)
        hdr.pack(fill=tk.X)
        
        icon = "✏️   Edit User Details" if edit_mode else "👤   Create New User"
        tk.Label(hdr, text=icon, font=("Segoe UI", 14, "bold"),
                 bg=hdr_color, fg="white").pack(anchor="w", padx=28, pady=20)

        form = tk.Frame(win, bg=self.bg_card)
        form.pack(fill=tk.BOTH, expand=True, padx=32, pady=25)

        v_name    = tk.StringVar(value=existing[0] if existing else "")
        v_email   = tk.StringVar(value=existing[1] if existing else "")
        v_role    = tk.StringVar(value=existing[2] if existing else "Staff")
        v_contact = tk.StringVar(value=existing[3] if existing else "")
        v_salary  = tk.StringVar(value=existing[4] if existing else "")
        v_status  = tk.StringVar(value=existing[5] if existing else "Active")
        v_pass    = tk.StringVar()

        def modern_field(parent, label, var, placeholder="", is_dropdown=False, options=None, is_password=False):
            f = tk.Frame(parent, bg=self.bg_card)
            f.pack(fill=tk.X, pady=(0, 16))
            
            tk.Label(f, text=label, font=("Segoe UI", 9, "bold"),
                     bg=self.bg_card, fg="#4B5563").pack(anchor="w", pady=(0, 5))
            
            border = tk.Frame(f, bg=self.border_color)
            border.pack(fill=tk.X)
            inner  = tk.Frame(border, bg=self.input_bg)
            inner.pack(fill=tk.X, padx=1, pady=1)
            
            if is_dropdown:
                w = ttk.Combobox(inner, textvariable=var, values=options,
                                 font=("Segoe UI", 11), state="readonly")
                w.pack(fill=tk.X, ipady=6, padx=10, pady=2)
            else:
                kw = dict(textvariable=var, font=("Segoe UI", 11), bg=self.input_bg,
                          bd=0, highlightthickness=0, insertbackground=self.text_dark)
                if is_password: kw["show"] = "●"
                w = tk.Entry(inner, **kw)
                w.pack(fill=tk.X, ipady=9, padx=12, pady=2)
                if placeholder and not var.get(): w.insert(0, placeholder)
                w.bind("<FocusIn>",
                       lambda e, _w=w, _p=placeholder:
                       _w.delete(0, "end") if _w.get() == _p else None)

        modern_field(form, "FULL NAME *", v_name, "e.g. John Doe")
        modern_field(form, "EMAIL ADDRESS *", v_email, "e.g. john@company.com")

        grid = tk.Frame(form, bg=self.bg_card)
        grid.pack(fill=tk.X)
        grid.columnconfigure(0, weight=1); grid.columnconfigure(1, weight=1)

        left  = tk.Frame(grid, bg=self.bg_card); left.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        right = tk.Frame(grid, bg=self.bg_card); right.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        modern_field(left,  "ROLE *",   v_role,   is_dropdown=True, options=["Admin", "Staff", "Manager"])
        modern_field(right, "STATUS *", v_status, is_dropdown=True, options=["Active", "Inactive"])

        left2  = tk.Frame(grid, bg=self.bg_card); left2.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        right2 = tk.Frame(grid, bg=self.bg_card); right2.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        modern_field(left2,  "CONTACT NUMBER",  v_contact, "01700000000")
        modern_field(right2, "SALARY",   v_salary,  "e.g. 20000")

        pass_lbl = "NEW PASSWORD (leave blank to keep current)" if edit_mode else "PASSWORD *"
        modern_field(form, pass_lbl, v_pass, is_password=True)

        footer = tk.Frame(win, bg="#F9FAFB", highlightbackground=self.border_color, highlightthickness=1)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_row = tk.Frame(footer, bg="#F9FAFB")
        btn_row.pack(side=tk.RIGHT, padx=24, pady=16)

        self._make_btn(btn_row, "  Cancel  ", "#E5E7EB", self.text_dark,
                       cmd=win.destroy).pack(side=tk.LEFT, padx=(0, 10))

        save_lbl   = "  Update User  " if edit_mode else "  Save New User  "
        self._make_btn(btn_row, save_lbl, hdr_color, "white",
                       cmd=lambda: _save()).pack(side=tk.LEFT)

        def _save():
            name    = v_name.get().strip()
            email   = v_email.get().strip()
            role    = v_role.get().strip()
            contact = v_contact.get().strip()
            salary  = v_salary.get().strip()
            status  = v_status.get().strip()
            pwd     = v_pass.get().strip()

            if not name or name == "e.g. John Doe":
                return messagebox.showerror("Validation", "Full Name is required!", parent=win)
            if not email or email == "e.g. john@company.com":
                return messagebox.showerror("Validation", "Email is required!", parent=win)
            if not edit_mode and not pwd:
                return messagebox.showerror("Validation", "Password is required!", parent=win)

            con = db_config.get_db_connection()
            if not con: return
            try:
                cur = con.cursor()
                if edit_mode:
                    if pwd:
                        cur.execute(
                            "UPDATE users SET name=%s,email=%s,role=%s,contact=%s,"
                            "salary=%s,status=%s,password=%s WHERE emp_id=%s",
                            (name, email, role, contact, salary, status, pwd, emp_id))
                    else:
                        cur.execute(
                            "UPDATE users SET name=%s,email=%s,role=%s,contact=%s,"
                            "salary=%s,status=%s WHERE emp_id=%s",
                            (name, email, role, contact, salary, status, emp_id))
                    msg = "User updated successfully!"
                else:
                    cur.execute(
                        "INSERT INTO users (name,email,password,role,contact,salary,status) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (name, email, pwd, role, contact, salary, status))
                    msg = "User added successfully!"
                con.commit()
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self._refresh_summary()
                self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Database error:\n{e}", parent=win)
            finally:
                if con.is_connected(): con.close()

    def _on_user_action_click(self, event):
        region = self.user_table.identify_region(event.x, event.y)
        if region == "cell":
            col = self.user_table.identify_column(event.x)
            if col == '#9':  # Actions is now column 9 because of salary
                item = self.user_table.identify_row(event.y)
                if not item: return
                
                vals = self.user_table.item(item, "values")
                emp_id = vals[0]
                
                bbox = self.user_table.bbox(item, column=col)
                if bbox:
                    x, y, w, h = bbox
                    if event.x < x + (w / 2):
                        self._open_add_modal(emp_id=int(emp_id))
                    else:
                        self._delete_user(int(emp_id))

    def _on_user_double_click(self, event):
        sel = self.user_table.selection()
        if not sel: return
        vals = self.user_table.item(sel[0], "values")
        emp_id = vals[0]
        if emp_id:
            self._open_add_modal(emp_id=int(emp_id))

    def _delete_user(self, emp_id):
        if messagebox.askyesno("Confirm Delete",
                "Are you sure you want to delete this user?\nThis action cannot be undone."):
            con = db_config.get_db_connection()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute("DELETE FROM users WHERE emp_id=%s", (emp_id,))
                    con.commit()
                    messagebox.showinfo("Success", "User deleted successfully.")
                    self._refresh_summary()
                    self._load_users()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete user:\n{e}")
                finally: con.close()

    # ─────────────────────────────────────────────────────────────────
    # REUSABLE UI HELPERS
    # ─────────────────────────────────────────────────────────────────
    def _kpi_card(self, parent, col, title, icon):
        card = tk.Frame(parent, bg=self.bg_card,
                        highlightbackground=self.border_color, highlightthickness=1,
                        height=110)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 10, 0))
        card.pack_propagate(False)

        top = tk.Frame(card, bg=self.bg_card)
        top.pack(fill=tk.X, padx=18, pady=(16, 4))
        
        tk.Label(top, text=title, font=self.F_CARD_T,
                 bg=self.bg_card, fg=self.text_muted).pack(side=tk.LEFT)

        tk.Label(top, text=icon, font=("Segoe UI", 16),
                 bg=self.bg_card, fg="black").pack(side=tk.RIGHT)

        val_lbl = tk.Label(card, text="—", font=self.F_CARD_V,
                           bg=self.bg_card, fg=self.text_dark)
        val_lbl.pack(anchor="w", padx=18)
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
    root.title("IMS - User Management")
    root.state("zoomed")
    app = UsersClass(root)
    root.mainloop()