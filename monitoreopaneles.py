import tkinter as tk
from tkinter import ttk, messagebox
import random

class PanelSolarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoreo de Limpieza - Panel Solar")
        self.root.geometry("600x400")
        self.root.config(bg="#1e2a38")

        
        self.connected = False

        
        style = ttk.Style()
        style.configure("TFrame", background="#1e2a38")
        style.configure("TLabel", background="#1e2a38", foreground="white", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Horizontal.TProgressbar", troughcolor="#34495e", background="#27ae60", thickness=20)

       
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

       
        title = tk.Label(main_frame, text="Sistema de Monitoreo de Limpieza de Paneles Solares",
                         font=("Segoe UI", 14, "bold"), bg="#1e2a38", fg="white")
        title.pack(pady=10)

        
        self.status_label = tk.Label(main_frame, text="Estado: Desconectado", fg="red", bg="#1e2a38", font=("Segoe UI", 11, "bold"))
        self.status_label.pack(pady=5)

        
        self.radiation_label = ttk.Label(main_frame, text="Radiación actual: -- lux")
        self.radiation_label.pack(pady=5)

        
        ttk.Label(main_frame, text="Porcentaje de suciedad:").pack(pady=5)
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=400)
        self.progress.pack(pady=5)
        self.percent_label = ttk.Label(main_frame, text="0%")
        self.percent_label.pack(pady=5)

        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)

        self.connect_btn = ttk.Button(button_frame, text="Conectar ESP32", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=0, padx=5)

        self.simulate_btn = ttk.Button(button_frame, text="Simular Datos", command=self.simulate_data)
        self.simulate_btn.grid(row=0, column=1, padx=5)

        self.exit_btn = ttk.Button(button_frame, text="Salir", command=self.root.quit)
        self.exit_btn.grid(row=0, column=2, padx=5)

    def toggle_connection(self):
        """Simula conexión/desconexión con el ESP32."""
        self.connected = not self.connected
        if self.connected:
            self.status_label.config(text="Estado: Conectado", fg="#27ae60")
            self.connect_btn.config(text="Desconectar ESP32")
        else:
            self.status_label.config(text="Estado: Desconectado", fg="red")
            self.connect_btn.config(text="Conectar ESP32")

    def simulate_data(self):
        """Simula valores del sensor de luz y porcentaje de limpieza."""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Conecta el ESP32 primero.")
            return

        radiation = random.randint(200, 1200)
        clean_percent = random.randint(0, 100)

        self.radiation_label.config(text=f"Radiación actual: {radiation} lux")
        self.progress["value"] = clean_percent
        self.percent_label.config(text=f"{clean_percent}%")

      
        if clean_percent > 75:
            self.progress.configure(style="green.Horizontal.TProgressbar")
        elif clean_percent > 40:
            self.progress.configure(style="yellow.Horizontal.TProgressbar")
        else:
            self.progress.configure(style="red.Horizontal.TProgressbar")



def create_custom_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("green.Horizontal.TProgressbar", background="#27ae60")
    style.configure("yellow.Horizontal.TProgressbar", background="#f1c40f")
    style.configure("red.Horizontal.TProgressbar", background="#e74c3c")

if __name__ == "__main__":
    root = tk.Tk()
    create_custom_styles()
    app = PanelSolarApp(root)
    root.mainloop()
