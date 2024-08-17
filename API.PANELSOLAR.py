import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from datetime import datetime, timedelta
from pysolar.solar import get_altitude, get_azimuth
from pytz import timezone
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Función para obtener la posición solar
def getSolarPosition(latitude, longitude, date):
    az = get_azimuth(latitude, longitude, date)
    el = get_altitude(latitude, longitude, date)
    return np.radians(az), np.radians(el)

# Función para calcular los ángulos de control usando las fórmulas proporcionadas
def calculate_angles(theta, alpha):
    phi = np.arcsin(-np.cos(theta) * np.cos(alpha))  # ϕ
    beta = np.arccos(np.sin(theta) / np.cos(phi))     # β
    return phi, beta

# Función para crear un rectángulo en 3D dado un origen y dos vectores de dirección
def create_rectangle(center, width, height, normal_vector):
    u = np.cross([0, 1, 0], normal_vector)
    v = np.cross(normal_vector, u)
    
    u = u / np.linalg.norm(u) * width / 2
    v = v / np.linalg.norm(v) * height / 2
    
    vertices = [
        center - u - v,
        center + u - v,
        center + u + v,
        center - u + v
    ]
    
    return vertices

# Función para dibujar la trayectoria del sol y la orientación del panel en tiempo real
def plot_solar_tracker(ax, date, end_time, speed):
    latitude, longitude = -0.2105367, -78.491614
    
    panel_center = np.array([0, 0, 0])
    
    def update_plot(current_time):
        if current_time > end_time:
            return
        
        alpha, theta = getSolarPosition(latitude, longitude, current_time)

        # Solo dibujar si hay luz solar (theta > 0)
        if theta > 0:
            phi, beta = calculate_angles(theta, alpha)
            
            sun_vector = np.array([
                np.sin(alpha) * np.cos(theta),
                np.cos(alpha) * np.cos(theta),
                np.sin(theta)
            ])
            
            panel_vector = np.array([
                np.cos(phi) * np.sin(beta),
                -np.sin(phi),
                np.cos(phi)
            ])
            
            ax.quiver(0, 0, 0, sun_vector[0], sun_vector[1], sun_vector[2], color='yellow', alpha=0.6)
            rect_vertices = create_rectangle(panel_center, width=0.5, height=0.3, normal_vector=panel_vector)
            panel = Poly3DCollection([rect_vertices], color='blue', alpha=0.5)
            ax.add_collection3d(panel)
        
        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.set_zlim([-1, 1])
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        ax.legend(['Sun Position', 'Panel Orientation'])
        
        canvas.draw()
        
        # Programar la siguiente actualización
        root.after(speed, update_plot, current_time + timedelta(minutes=60))  # Actualizar cada hora

    # Iniciar la simulación
    update_plot(date)

# Función que se ejecuta al hacer clic en el botón de "Comenzar Simulación"
def start_simulation():
    # Asegurarse de que la fecha seleccionada tenga información de zona horaria
    date_str = date_picker.get()
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    date = timezone("America/Guayaquil").localize(date)  # Convertir a timezone-aware
    
    speed = speed_slider.get()
    
    # Definir el tiempo final basado en la hora ingresada
    end_hour_str = end_hour_picker.get()
    end_time = date.replace(hour=int(end_hour_str.split(':')[0]), minute=int(end_hour_str.split(':')[1]), second=0)
    
    ax.clear()  # Limpiar al inicio de la simulación
    plot_solar_tracker(ax, date, end_time, speed)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Simulador de Seguidor Solar")
root.geometry("800x600")

# Crear los widgets de la interfaz
date_label = tk.Label(root, text="Fecha y Hora de Inicio (YYYY-MM-DD HH:MM:SS):")
date_label.pack()

date_picker = ttk.Entry(root)
date_picker.insert(0, datetime.now(tz=timezone("America/Guayaquil")).strftime("%Y-%m-%d %H:%M:%S"))
date_picker.pack()

end_hour_label = tk.Label(root, text="Hora de Fin (HH:MM):")
end_hour_label.pack()

end_hour_picker = ttk.Entry(root)
end_hour_picker.insert(0, "23:00")
end_hour_picker.pack()

speed_label = tk.Label(root, text="Velocidad de Simulación (ms por hora simulada):")
speed_label.pack()

speed_slider = tk.Scale(root, from_=10, to=1000, orient="horizontal")
speed_slider.set(100)
speed_slider.pack()

start_button = tk.Button(root, text="Comenzar Simulación", command=start_simulation)
start_button.pack()

# Crear la figura de Matplotlib para la gráfica 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Ejecutar la interfaz gráfica
root.mainloop()