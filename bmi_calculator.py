import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CSV_FILE = "bmi_history.csv"

class AdvancedBMITracker:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Tracker Pro - Health Analytics")
        self.root.geometry("820x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#F1F5F9")

        self.setup_ui()
        self.load_history_table()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0F172A", height=60)
        header.pack(fill="x")
        tk.Label(
            header,
            text="BMI Health Tracker & Trend Analyzer",
            font=("Helvetica", 14, "bold"),
            fg="#FFFFFF",
            bg="#0F172A"
        ).pack(pady=15)

        # Main Layout (Left: Form & Result, Right: History & Graph)
        content_frame = tk.Frame(self.root, bg="#F1F5F9")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        left_frame = tk.Frame(content_frame, bg="#F1F5F9", width=360)
        left_frame.pack(side="left", fill="y", padx=(0, 15))

        right_frame = tk.Frame(content_frame, bg="#F1F5F9", width=420)
        right_frame.pack(side="right", fill="both", expand=True)

        # --- LEFT: INPUT CARD ---
        card = tk.Frame(left_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CBD5E1")
        card.pack(fill="x", ipady=8)

        tk.Label(card, text="Full Name", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(anchor="w", padx=15, pady=(8, 2))
        self.entry_name = tk.Entry(card, font=("Helvetica", 10), highlightthickness=1, highlightbackground="#CBD5E1")
        self.entry_name.pack(fill="x", padx=15, ipady=4)

        # Weight with Unit
        tk.Label(card, text="Weight", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(anchor="w", padx=15, pady=(8, 2))
        w_box = tk.Frame(card, bg="#FFFFFF")
        w_box.pack(fill="x", padx=15)
        self.entry_weight = tk.Entry(w_box, font=("Helvetica", 10), width=18, highlightthickness=1, highlightbackground="#CBD5E1")
        self.entry_weight.pack(side="left", ipady=4)
        self.weight_unit = ttk.Combobox(w_box, values=["kg", "lbs"], width=6, state="readonly")
        self.weight_unit.set("kg")
        self.weight_unit.pack(side="right")

        # Height with Unit
        tk.Label(card, text="Height", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(anchor="w", padx=15, pady=(8, 2))
        h_box = tk.Frame(card, bg="#FFFFFF")
        h_box.pack(fill="x", padx=15)
        self.entry_height = tk.Entry(h_box, font=("Helvetica", 10), width=18, highlightthickness=1, highlightbackground="#CBD5E1")
        self.entry_height.pack(side="left", ipady=4)
        self.height_unit = ttk.Combobox(h_box, values=["meters", "cm", "feet"], width=6, state="readonly")
        self.height_unit.set("meters")
        self.height_unit.pack(side="right")

        # Action Buttons
        btn_calc = tk.Button(
            left_frame,
            text="Calculate & Save",
            command=self.calculate_bmi,
            font=("Helvetica", 10, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )
        btn_calc.pack(fill="x", pady=10, ipady=4)

        # Result Card
        self.result_card = tk.Frame(left_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CBD5E1")
        self.result_card.pack(fill="x", ipady=8)

        self.lbl_bmi_val = tk.Label(self.result_card, text="--", font=("Helvetica", 22, "bold"), bg="#FFFFFF", fg="#64748B")
        self.lbl_bmi_val.pack()

        self.lbl_category = tk.Label(self.result_card, text="Awaiting calculation", font=("Helvetica", 10), bg="#FFFFFF", fg="#64748B")
        self.lbl_category.pack()

        # View Trend Graph Button
        btn_graph = tk.Button(
            left_frame,
            text="📈 Show User Trend Graph",
            command=self.open_trend_window,
            font=("Helvetica", 10),
            bg="#0284C7",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )
        btn_graph.pack(fill="x", pady=10, ipady=4)

        # --- RIGHT: RECORD HISTORY TABLE ---
        table_frame = tk.Frame(right_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CBD5E1")
        table_frame.pack(fill="both", expand=True)

        tk.Label(table_frame, text="Saved Logs (Recent Records)", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#1E293B").pack(anchor="w", padx=10, pady=8)

        columns = ("Time", "Name", "BMI", "Category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Time", text="Date")
        self.tree.heading("Name", text="Name")
        self.tree.heading("BMI", text="BMI")
        self.tree.heading("Category", text="Status")

        self.tree.column("Time", width=85, anchor="center")
        self.tree.column("Name", width=95, anchor="w")
        self.tree.column("BMI", width=55, anchor="center")
        self.tree.column("Category", width=105, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def calculate_bmi(self):
        name = self.entry_name.get().strip()
        w_str = self.entry_weight.get().strip()
        h_str = self.entry_height.get().strip()

        if not name:
            messagebox.showwarning("Input Error", "Please provide a name.")
            return

        try:
            w = float(w_str)
            h = float(h_str)

            if w <= 0 or h <= 0:
                messagebox.showerror("Error", "Weight and height must be positive values.")
                return

            # Convert Weight to kg
            if self.weight_unit.get() == "lbs":
                w = w * 0.453592

            # Convert Height to meters
            if self.height_unit.get() == "cm":
                h = h / 100.0
            elif self.height_unit.get() == "feet":
                h = h * 0.3048

            bmi = round(w / (h ** 2), 2)

            # Categorize
            if bmi < 18.5:
                cat, color = "Underweight", "#3B82F6"
            elif 18.5 <= bmi <= 24.9:
                cat, color = "Normal Weight", "#10B981"
            elif 25.0 <= bmi <= 29.9:
                cat, color = "Overweight", "#F59E0B"
            else:
                cat, color = "Obese", "#EF4444"

            self.lbl_bmi_val.config(text=str(bmi), fg=color)
            self.lbl_category.config(text=f"Status: {cat}", fg=color)

            # Persist and refresh
            self.save_record(name, round(w, 1), round(h, 2), bmi, cat)
            self.load_history_table()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric figures.")

    def save_record(self, name, weight, height, bmi, category):
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Name", "Weight_kg", "Height_m", "BMI", "Category"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), name, weight, height, bmi, category])

    def load_history_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not os.path.isfile(CSV_FILE):
            return

        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 6:
                    self.tree.insert("", 0, values=(row[0].split()[0], row[1], row[4], row[5]))

    def open_trend_window(self):
        target_name = self.entry_name.get().strip()
        if not target_name:
            messagebox.showwarning("Warning", "Enter a user name in the input box to see their trend.")
            return

        dates, bmis = [], []
        if os.path.isfile(CSV_FILE):
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 6 and row[1].lower() == target_name.lower():
                        dates.append(row[0].split()[0])
                        bmis.append(float(row[4]))

        if len(bmis) < 2:
            messagebox.showinfo("Need More Data", f"At least 2 records are required for {target_name} to render a trend graph.")
            return

        # Render Pop-up Graph
        trend_win = tk.Toplevel(self.root)
        trend_win.title(f"BMI Progress - {target_name}")
        trend_win.geometry("520x400")

        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=100)
        ax.plot(dates, bmis, marker='o', color='#2563EB', linewidth=2, label="BMI")
        ax.axhline(y=18.5, color='#3B82F6', linestyle='--', alpha=0.5, label="Underweight (18.5)")
        ax.axhline(y=24.9, color='#10B981', linestyle='--', alpha=0.5, label="Normal Max (24.9)")
        ax.axhline(y=29.9, color='#EF4444', linestyle='--', alpha=0.5, label="Overweight Max (29.9)")

        ax.set_title(f"BMI History for {target_name}", fontsize=11, fontweight="bold")
        ax.set_ylabel("BMI Value")
        ax.tick_params(axis='x', rotation=30)
        ax.legend(loc="upper left", fontsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=trend_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedBMITracker(root)
    root.mainloop()