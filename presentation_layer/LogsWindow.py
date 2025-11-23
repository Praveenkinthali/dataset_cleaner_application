# presentation_layer/LogsWindow.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class LogsWindow(tk.Frame):
    def __init__(self, master):
        self.light_bg = getattr(master, 'light_bg', '#f8f9fa')
        self.primary_color = getattr(master, 'primary_color', '#2c3e50')
        self.accent_color = getattr(master, 'accent_color', '#3498db')
        self.success_color = getattr(master, 'success_color', '#27ae60')
        self.danger_color = getattr(master, 'danger_color', '#e74c3c')
        
        super().__init__(master, bg=self.light_bg)
        self.master = master

        # Main container
        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with Back Button
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 10))
        
        btn_back = tk.Button(
            header_frame, text="← Back",
            bg="#95a5a6", fg="white",
            command=lambda: master.show_frame(master.MainMenu),
            padx=15, font=("Arial", 10)
        )
        btn_back.pack(side="left", padx=(0, 20))

        title_frame = tk.Frame(header_frame, bg=self.light_bg)
        title_frame.pack(side="left", expand=True)
        
        tk.Label(
            title_frame, text="Transformation Logs",
            font=("Arial", 20, "bold"), fg=self.primary_color, bg=self.light_bg
        ).pack()
        
        tk.Label(
            title_frame, text="Track all data transformations and feature engineering operations",
            font=("Arial", 10), fg="#7f8c8d", bg=self.light_bg
        ).pack()

        # Logs Display Area
        logs_frame = tk.LabelFrame(main_container, text="Transformation History", 
                                  font=("Arial", 12, "bold"), bg=self.light_bg)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        log_container = tk.Frame(logs_frame, bg=self.light_bg)
        log_container.pack(fill="both", expand=True, padx=7, pady=7)
        
        self.log_area = tk.Text(
            log_container, height=20, font=("Consolas", 10),
            bg="#f8f9fa", wrap="word", padx=10, pady=10
        )
        
        v_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.log_area.yview)
        h_scroll = ttk.Scrollbar(log_container, orient="horizontal", command=self.log_area.xview)
        self.log_area.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.log_area.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        # Control buttons
        controls = tk.Frame(main_container, bg=self.light_bg)
        controls.pack(fill="x", pady=10)
        
        tk.Button(controls, text="🔄 Refresh", command=self.refresh_log,
                  bg=self.accent_color, fg="white", width=12).pack(side="left", padx=5)
        tk.Button(controls, text="💾 Export Log", command=self.export_log,
                  bg=self.success_color, fg="white", width=12).pack(side="left", padx=5)
        tk.Button(controls, text="🗑️ Clear Log", command=self.clear_log,
                  bg=self.danger_color, fg="white", width=12).pack(side="left", padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(main_container, textvariable=self.status_var,
                               relief="sunken", anchor="w", bg="#ecf0f1")
        status_label.pack(fill="x", side="bottom", pady=(5, 0))

        # Auto-load
        self.refresh_log()

    def refresh_log(self):
        """Display logs from logging service"""
        try:
            self.log_area.delete("1.0", tk.END)
            
            # UPDATED: Use logging_service from master
            result = self.master.logging_service.get_logs(self.master.dataset_id)
            
            if result["success"] and result["logs"]:
                logs = result["logs"]
                
                self.log_area.insert("1.0", "=" * 80 + "\n")
                self.log_area.insert(tk.END, "TRANSFORMATION LOGS\n")
                self.log_area.insert(tk.END, "=" * 80 + "\n\n")
                
                for log in logs:
                    self.log_area.insert(tk.END, f"🕒 {log['timestamp']}\n")
                    self.log_area.insert(tk.END, f"🧩 Operation: {log['operation_type']}\n")
                    self.log_area.insert(tk.END, f"📝 Description: {log['description']}\n")
                    self.log_area.insert(tk.END, "-" * 80 + "\n\n")
                
                self.status_var.set(f"Loaded {len(logs)} logs successfully.")
            else:
                self.show_no_logs_message()

        except Exception as e:
            self.log_area.insert("1.0", f"Error loading logs: {str(e)}")
            self.status_var.set("Error loading logs")

    def show_no_logs_message(self):
        msg = (
            "No transformation logs available yet.\n\n"
            "Logs will appear here after you perform operations in:\n"
            "• Data Cleaning window\n"
            "• Feature Engineering window\n"
            "• Other transformation tools"
        )
        self.log_area.insert("1.0", msg)
        self.status_var.set("No logs available")

    def export_log(self):
        """Export logs to file"""
        content = self.log_area.get("1.0", tk.END).strip()
        if not content or "No transformation logs" in content:
            messagebox.showinfo("Export", "No logs available to export.")
            return
        
        try:
            fname = filedialog.asksaveasfilename(
                defaultextension=".txt",
                title="Export Transformation Logs",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if fname:
                # UPDATED: Use logging_service export method
                result = self.master.logging_service.export_logs(fname, self.master.dataset_id)
                
                if result["success"]:
                    messagebox.showinfo("Export Successful", result["message"])
                    self.status_var.set(f"Logs exported to {fname}")
                else:
                    messagebox.showerror("Export Error", result["message"])
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")

    def clear_log(self):
        """Clear local logs"""
        if not messagebox.askyesno(
            "Clear Logs",
            "Are you sure you want to clear *local* logs?\nDatabase logs will remain intact."
        ):
            return
        
        try:
            # UPDATED: Use logging_service to clear logs
            result = self.master.logging_service.clear_local_logs()
            
            if result["success"]:
                self.refresh_log()
                self.status_var.set("Cleared local logs.")
                messagebox.showinfo("Success", "Local logs cleared successfully!")
            else:
                messagebox.showerror("Error", result["message"])
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear logs: {str(e)}")

    def on_show(self):
        """Called when window is shown"""
        self.refresh_log()