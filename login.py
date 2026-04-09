import tkinter as tk
from tkinter import messagebox
import db_config

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("IMS - Login")
        self.root.geometry("800x500")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)
        
        # স্ক্রিনের মাঝখানে উইন্ডো ওপেন করার লজিক
        window_width = 800
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # --- Colors ---
        self.brand_color = "#1A252F" # Deep Navy Blue
        self.btn_color = "#16A085"   # Teal Green
        self.text_dark = "#2C3E50"
        self.text_light = "#7F8C8D"

        self.create_layout()

    def create_layout(self):
        # ================= LEFT PANEL (Branding) =================
        left_frame = tk.Frame(self.root, bg=self.brand_color, width=350, height=500)
        left_frame.place(x=0, y=0)

        # লোগো বা টাইটেল
        tk.Label(left_frame, text="💠", font=("Arial", 60), bg=self.brand_color, fg="white").place(x=130, y=120)
        tk.Label(left_frame, text="IMS", font=("Arial", 28, "bold"), bg=self.brand_color, fg="white").place(x=135, y=210)
        tk.Label(left_frame, text="AI-Powered Inventory", font=("Arial", 12), bg=self.brand_color, fg="#BDC3C7").place(x=95, y=260)
        tk.Label(left_frame, text="Manage your business smartly", font=("Arial", 9), bg=self.brand_color, fg="#95A5A6").place(x=90, y=450)


        # ================= RIGHT PANEL (Login Form) =================
        right_frame = tk.Frame(self.root, bg="#FFFFFF", width=450, height=500)
        right_frame.place(x=350, y=0)

        tk.Label(right_frame, text="Welcome Back!", font=("Arial", 22, "bold"), bg="#FFFFFF", fg=self.text_dark).place(x=50, y=60)
        tk.Label(right_frame, text="Please login to your account", font=("Arial", 10), bg="#FFFFFF", fg=self.text_light).place(x=50, y=100)

        # Email Field
        tk.Label(right_frame, text="Email Address", font=("Arial", 10, "bold"), bg="#FFFFFF", fg=self.text_dark).place(x=50, y=160)
        self.email_entry = tk.Entry(right_frame, font=("Arial", 12), bg="#F4F7F6", relief="flat", highlightthickness=1, highlightbackground="#BDC3C7", highlightcolor=self.btn_color)
        self.email_entry.place(x=50, y=190, width=350, height=35)

        # Password Field
        tk.Label(right_frame, text="Password", font=("Arial", 10, "bold"), bg="#FFFFFF", fg=self.text_dark).place(x=50, y=250)
        self.password_entry = tk.Entry(right_frame, font=("Arial", 12), bg="#F4F7F6", relief="flat", show="*", highlightthickness=1, highlightbackground="#BDC3C7", highlightcolor=self.btn_color)
        self.password_entry.place(x=50, y=280, width=350, height=35)

        # Login Button
        login_btn = tk.Button(right_frame, text="LOGIN", font=("Arial", 12, "bold"), bg=self.btn_color, fg="white", activebackground="#1abc9c", activeforeground="white", relief="flat", cursor="hand2", command=self.check_login)
        login_btn.place(x=50, y=360, width=350, height=45)

    def check_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if email == "" or password == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
            return

        try:
            # MySQL ডাটাবেসের সাথে কানেকশন (আপনার পাসওয়ার্ড থাকলে তা দিন)
            con = db_config.get_db_connection()
            cur = con.cursor()
            
            cur.execute("SELECT emp_id, name, role, status FROM users WHERE email=%s AND password=%s", (email, password))
            user = cur.fetchone()

            if user == None:
                messagebox.showerror("Error", "Invalid Email or Password!", parent=self.root)
            else:
                emp_id, name, role, status = user
                
                if status != "Active":
                    messagebox.showerror("Error", "Your account is disabled. Contact Admin.", parent=self.root)
                else:
                    messagebox.showinfo("Success", f"Welcome {name}!\nLogged in as: {role}", parent=self.root)
                    self.log_user_login(con, cur, emp_id)
                    
                    # উইন্ডো বন্ধ করে ড্যাশবোর্ডে যাওয়ার প্রস্তুতি
                    self.root.destroy()
                    self.open_dashboard(name, role)

            con.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {str(e)}", parent=self.root)

    def log_user_login(self, con, cur, emp_id):
        # ইউজার কখন লগইন করেছে তার রেকর্ড রাখা
        try:
            cur.execute("INSERT INTO login_logs (emp_id) VALUES (%s)", (emp_id,))
            con.commit()
        except Exception as e:
            print(f"Failed to log login time: {e}")

    def open_dashboard(self, name, role):
        # এই ফাংশনটি পরবর্তীতে আমাদের মেইন ড্যাশবোর্ড কল করবে
        print(f"Opening Dashboard for {name}. Role: {role}")
        import dashboard
        root = tk.Tk()
        app = dashboard.ModernIMSDashboard(root, name, role)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()