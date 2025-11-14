import threading
import queue
import time
import serial
from serial.tools import list_ports
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import json
import os
import datetime


class PanelSolarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoreo de Limpieza - Panel Solar")
        self.root.geometry("700x420")
        self.root.config(bg="#1e2a38")

        # Estado de serial/lecturas
        self.serial_port = None
        self.ser = None
        self.read_thread = None
        self.read_queue = queue.Queue()
        self.alive = threading.Event()

        # Buffer de lecturas para suavizar
        self.buffer = []
        self.buffer_size = 6

        # Valor calibrado que representa panel limpio (lux)
        self.clean_lux = None
        self.config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")

        # Registro CSV
        self.logging = False
        self.csv_fp = None
        self.csv_path = None

        # Estilos
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e2a38")
        style.configure("TLabel", background="#1e2a38", foreground="white", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("green.Horizontal.TProgressbar", troughcolor="#34495e", background="#27ae60", thickness=24)
        style.configure("yellow.Horizontal.TProgressbar", troughcolor="#34495e", background="#f1c40f", thickness=24)
        style.configure("red.Horizontal.TProgressbar", troughcolor="#34495e", background="#e74c3c", thickness=24)

        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        title = tk.Label(main_frame, text="Sistema de Monitoreo de Limpieza de Paneles Solares",
                         font=("Segoe UI", 14, "bold"), bg="#1e2a38", fg="white")
        title.pack(pady=6)

        # Status
        self.status_label = tk.Label(main_frame, text="Estado: Desconectado", fg="red", bg="#1e2a38",
                                     font=("Segoe UI", 11, "bold"))
        self.status_label.pack(pady=4)

        # Puerto / baud
        conn_frame = ttk.Frame(main_frame)
        conn_frame.pack(pady=6)
        ttk.Label(conn_frame, text="Puerto:").grid(row=0, column=0, padx=6)
        self.port_cb = ttk.Combobox(conn_frame, values=self._list_serial_ports(), width=18)
        self.port_cb.grid(row=0, column=1)
        ttk.Label(conn_frame, text="Baud:").grid(row=0, column=2, padx=6)
        self.baud_cb = ttk.Combobox(conn_frame, values=["9600", "115200"], width=10)
        self.baud_cb.set("115200")
        self.baud_cb.grid(row=0, column=3)
        self.refresh_btn = ttk.Button(conn_frame, text="Actualizar puertos", command=self._refresh_ports)
        self.refresh_btn.grid(row=0, column=4, padx=8)

        # Lecturas
        self.radiation_label = ttk.Label(main_frame, text="Radiación actual: -- lux")
        self.radiation_label.pack(pady=6)

        self.calibration_label = ttk.Label(main_frame, text="Calibración: -- (no guardada)")
        self.calibration_label.pack(pady=2)

        ttk.Label(main_frame, text="Porcentaje de suciedad (0% = limpio, 100% = muy sucio):").pack(pady=4)
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=560,
                                        style="green.Horizontal.TProgressbar")
        self.progress.pack(pady=6)
        self.percent_label = ttk.Label(main_frame, text="0%")
        self.percent_label.pack(pady=2)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=12)
        self.connect_btn = ttk.Button(button_frame, text="Conectar", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=0, padx=6)
        self.calibrate_btn = ttk.Button(button_frame, text="Calibrar (establecer limpio)", command=self.calibrate)
        self.calibrate_btn.grid(row=0, column=1, padx=6)
        self.log_btn = ttk.Button(button_frame, text="Iniciar registro CSV", command=self.toggle_logging)
        self.log_btn.grid(row=0, column=2, padx=6)
        self.exit_btn = ttk.Button(button_frame, text="Salir", command=self.on_exit)
        self.exit_btn.grid(row=0, column=3, padx=6)

        # Información de ayuda
        self.info_label = ttk.Label(main_frame, text="Formato serie aceptado: 'LUX:123.4' o '123.4'", font=("Segoe UI", 9))
        self.info_label.pack(pady=6)

        # Polling de queue
        self.root.after(200, self._poll_queue)

        # Cargar configuración (calibración) si existe
        self._load_config()

    def _list_serial_ports(self):
        ports = [p.device for p in list_ports.comports()]
        return ports

    def _refresh_ports(self):
        self.port_cb['values'] = self._list_serial_ports()

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self._disconnect_serial()
        else:
            self._connect_serial()

    def _connect_serial(self):
        port = self.port_cb.get()
        try:
            baud = int(self.baud_cb.get())
        except Exception:
            baud = 115200

        if not port:
            messagebox.showwarning("Puerto no seleccionado", "Selecciona el puerto serie donde está el ESP32.")
            return

        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            messagebox.showerror("Error al abrir puerto", str(e))
            return

        self.status_label.config(text=f"Estado: Conectado ({port} @ {baud})", fg="#27ae60")
        self.connect_btn.config(text="Desconectar")
        self.alive.set()
        self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.read_thread.start()

    def _disconnect_serial(self):
        self.alive.clear()
        try:
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
        except Exception:
            pass
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

        self.ser = None
        self.status_label.config(text="Estado: Desconectado", fg="red")
        self.connect_btn.config(text="Conectar")

    def _reader_loop(self):
        # Lee líneas del puerto serie y las manda a la queue
        while self.alive.is_set() and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors='ignore').strip()
                if line:
                    self.read_queue.put(line)
            except Exception:
                # en caso de error, rompe el loop
                break
            time.sleep(0.01)

    def _poll_queue(self):
        # Procesa líneas entrantes
        processed = False
        while not self.read_queue.empty():
            line = self.read_queue.get()
            self._process_serial_line(line)
            processed = True

        # Actualiza UI si hubo lectura
        if processed:
            self._update_ui()

        self.root.after(200, self._poll_queue)

    def _process_serial_line(self, line: str):
        # Soporta formatos: 'LUX:123.45' o '123.45'
        try:
            if ':' in line:
                key, val = line.split(':', 1)
                if key.strip().upper() == 'LUX':
                    lux = float(val.strip())
                else:
                    # intentar extraer número
                    lux = float(val.strip())
            else:
                lux = float(line.strip())
        except Exception:
            # No se pudo parsear, ignorar
            return

        # Añadir al buffer
        self.buffer.append(lux)
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

    def _get_smoothed_lux(self):
        if not self.buffer:
            return None
        return sum(self.buffer) / len(self.buffer)

    def _compute_dirt_percent(self, lux):
        # Si no hay calibración, no se puede computar correctamente
        if self.clean_lux is None or self.clean_lux <= 0:
            return 0

        # Si la lectura es mayor o igual al valor calibrado, asumimos limpio (0%)
        if lux >= self.clean_lux:
            return 0

        # Porcentaje de suciedad = cuánto se ha reducido la luz respecto al limpio
        diff = max(0.0, self.clean_lux - lux)
        pct = (diff / self.clean_lux) * 100.0
        pct = min(100.0, max(0.0, pct))
        return pct

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    val = data.get('clean_lux')
                    if isinstance(val, (int, float)):
                        self.clean_lux = float(val)
                        self.calibration_label.config(text=f"Calibración: {self.clean_lux:.1f} lux")
        except Exception:
            # No bloquear la app si algo falla en lectura
            pass

    def _save_config(self):
        try:
            data = {'clean_lux': None}
            if self.clean_lux is not None:
                data['clean_lux'] = float(self.clean_lux)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def toggle_logging(self):
        # Inicia o detiene el registro CSV
        if not self.logging:
            # Pedir archivo para guardar
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')],
                                                title='Guardar registro CSV')
            if not path:
                return
            try:
                fp = open(path, 'w', encoding='utf-8', newline='')
                fp.write('timestamp,lux,dirt_pct\n')
                fp.flush()
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo abrir el archivo:\n{e}')
                return
            self.csv_fp = fp
            self.csv_path = path
            self.logging = True
            self.log_btn.config(text='Detener registro CSV')
            messagebox.showinfo('Registro CSV', f'Registro iniciado:\n{path}')
        else:
            # Detener
            try:
                if self.csv_fp:
                    self.csv_fp.close()
            except Exception:
                pass
            self.csv_fp = None
            self.csv_path = None
            self.logging = False
            self.log_btn.config(text='Iniciar registro CSV')
            messagebox.showinfo('Registro CSV', 'Registro detenido y guardado.')

    def _update_ui(self):
        lux = self._get_smoothed_lux()
        if lux is None:
            return

        self.radiation_label.config(text=f"Radiación actual: {lux:.1f} lux")

        dirt_pct = self._compute_dirt_percent(lux)
        self.progress['value'] = dirt_pct
        self.percent_label.config(text=f"{dirt_pct:.1f}%")

        # Cambiar color según nivel
        if dirt_pct < 30:
            self.progress.configure(style="green.Horizontal.TProgressbar")
        elif dirt_pct < 70:
            self.progress.configure(style="yellow.Horizontal.TProgressbar")
        else:
            self.progress.configure(style="red.Horizontal.TProgressbar")

        # Escribir en CSV si está activo
        if self.logging and self.csv_fp:
            try:
                ts = datetime.datetime.now().isoformat()
                line = f"{ts},{lux:.3f},{dirt_pct:.3f}\n"
                self.csv_fp.write(line)
                self.csv_fp.flush()
            except Exception:
                # si falla el registro, detener logging para evitar spam
                try:
                    self.csv_fp.close()
                except Exception:
                    pass
                self.csv_fp = None
                self.logging = False
                self.log_btn.config(text='Iniciar registro CSV')

    def calibrate(self):
        # Establece el valor actual (promedio) como panel limpio
        lux = self._get_smoothed_lux()
        if lux is None:
            messagebox.showwarning("Calibración", "No hay lecturas disponibles para calibrar.")
            return
        self.clean_lux = lux
        self.calibration_label.config(text=f"Calibración: {self.clean_lux:.1f} lux")
        self._save_config()
        messagebox.showinfo("Calibración", f"Valor de panel limpio establecido: {lux:.1f} lux (guardado)")

    def on_exit(self):
        # Asegurar cerrar todo correctamente
        try:
            if self.logging and self.csv_fp:
                self.csv_fp.close()
        except Exception:
            pass
        self._save_config()
        self._disconnect_serial()
        self.root.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = PanelSolarApp(root)
    root.mainloop()
