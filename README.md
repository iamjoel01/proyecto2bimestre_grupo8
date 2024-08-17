# Informe Proyecto Segundo Bimestre
Un seguidor solar es un sistema de orientación para maximizar la exposición a la luz solar. Esto se consigue cuando el panel solar se orienta perpendicularmente a la luz solar incidente. Cuando el panel no se encuentra perpendicular, la cantidad de energía generada disminuye significativamente.

## Integrantes
* Darlin Anacicha Sanchez
* Elias Cazar Moreira
* Felipe Quirola Sotomayor
* Joel Quilumba Morocho

## Objetivo
El objetivo principal de este proyecto es implementar un programa que permita calcular los ángulos de control para un seguidor solar de 2 grados de libertad, garantizando que el panel solar se mantenga perpendicular a la luz solar incidente. Además, se busca dibujar la trayectoria del sol y del panel solar durante un día específico, permitiendo la interacción con la fecha y la duración de la simulación.

## Planteamiento Matemático

![Planteamiento Matemático](https://github.com/iamjoel01/proyecto2bimestre_grupo8/raw/main/Planetamiento%20Matem%C3%A1tico.jpg)

### Definición del Vector Director de la Posición Solar (S)

El vector director **S** representa la dirección del Sol en un sistema de coordenadas cartesianas y está definido por los ángulos de elevación (θ) y acimut (α). Las componentes del vector director **S** se calculan como:

- **S_x** = cos(θ) * sin(α)
- **S_y** = cos(θ) * cos(α)
- **S_z** = sin(θ)

Por lo tanto, el vector **S** es:

**S** = (cos(θ) * sin(α), cos(θ) * cos(α), sin(θ))

### Igualación de Matrices de Rotación y Despeje de Ángulos Pitch (β) y Roll (φ)

Para calcular los ángulos de control del seguidor solar, igualamos el producto de dos matrices de rotación con el vector solar **S**. La ecuación resultante es:

**R_C_B** * **R_C_A** = **S**

Donde **R_C_B** y **R_C_A** son matrices de rotación y **S** es el vector director del Sol.

De esta igualación, se despejan los ángulos φ (roll) y β (pitch) usando las siguientes fórmulas:

- Para el ángulo φ (roll):

  - -sin(φ) = cos(θ) * cos(α)
  - sin(φ) = -cos(θ) * cos(α)
  - φ = arcsin(-cos(θ) * cos(α))

- Para el ángulo β (pitch):

  - cos(φ) * cos(β) = sin(θ)
  - cos(β) = sin(θ) / cos(φ)
  - β = arccos(sin(θ) / cos(φ))

Estas ecuaciones permiten calcular la orientación del seguidor solar en función de la posición solar en un momento específico.

## Implementación del Código
El código se organiza en funciones para calcular la posición del sol, los ángulos de control y para graficar la trayectoria del sol y del panel solar.

### `getSolarPosition`
Esta función calcula el azimut y la elevación del sol para una posición geográfica y una fecha específicas.

```python
def getSolarPosition(latitude: float = -0.2105367, longitude: float = -78.491614, date: datetime = datetime.now(tz=timezone("America/Guayaquil"))):
    """Calcula el azimut y la elevación para una posición geográfica y fecha."""
    az = get_azimuth(latitude, longitude, date)
    el = get_altitude(latitude, longitude, date)
    return az, el
```
### `calculateControlAngles`
Esta función calcula los ángulos de control pitch y roll a partir de los ángulos de azimut y elevación del sol.

```python
def calculateControlAngles(azimuth, elevation):
    """Calcula los ángulos de control (pitch y roll) en base a la posición solar."""
    # Convertir los ángulos a radianes
    elevation_rad = math.radians(elevation)
    azimuth_rad = math.radians(azimuth)

    # Definir las componentes del vector solar
    S_x = math.cos(elevation_rad) * math.sin(azimuth_rad)
    S_y = math.cos(elevation_rad) * math.cos(azimuth_rad)
    S_z = math.sin(elevation_rad)

    # Calcular roll (φ) y pitch (β) usando las ecuaciones matemáticas
    if S_y != 0:
        roll = math.degrees(math.atan2(S_y, S_x))
    else:
        roll = 0
    
    pitch = math.degrees(math.asin(S_z))

    return pitch, roll
```
### `plotSunAndPanelTrajectory`
Esta función genera un gráfico 3D de la trayectoria del sol y la orientación del panel solar durante un período de tiempo especificado.

```python
def plotSunAndPanelTrajectory(start_date, duration_hours, latitude=-0.2105367, longitude=-78.491614):
    """Dibuja la trayectoria del sol y del panel solar de manera interactiva."""
    # Convertir la fecha a timezone-aware si no lo es
    if start_date.tzinfo is None:
        start_date = timezone("America/Guayaquil").localize(start_date)

    end_date = start_date + timedelta(hours=duration_hours)
    times = [start_date + timedelta(minutes=10*i) for i in range(int((end_date - start_date).total_seconds() / 600))]
    azimuths, elevations, pitches, rolls = [], [], [], []

    for time in times:
        azimuth, elevation = getSolarPosition(latitude, longitude, time)
        pitch, roll = calculateControlAngles(azimuth, elevation)
        azimuths.append(azimuth)
        elevations.append(elevation)
        pitches.append(pitch)
        rolls.append(roll)
    
    # Convertir azimut y elevación a coordenadas 3D
    sun_x = np.cos(np.radians(elevations)) * np.sin(np.radians(azimuths))
    sun_y = np.cos(np.radians(elevations)) * np.cos(np.radians(azimuths))
    sun_z = np.sin(np.radians(elevations))

    # Convertir pitch y roll a coordenadas 3D
    panel_x = np.cos(np.radians(pitches)) * np.sin(np.radians(rolls))
    panel_y = np.cos(np.radians(pitches)) * np.cos(np.radians(rolls))
    panel_z = np.sin(np.radians(pitches))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(sun_x, sun_y, sun_z, label='Trayectoria del Sol', color='orange')
    ax.plot(panel_x, panel_y, panel_z, label='Orientación del Panel', color='blue')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Trayectoria del Sol y Orientación del Panel Solar\n{start_date.date()}')
    ax.legend()
    plt.show()
```
### `interactive_plot`
Esta función proporciona una interfaz interactiva para que el usuario ingrese la fecha y duración de la simulación y visualice el resultado.

```python
def interactive_plot():
    """Crea una interfaz interactiva para ingresar la fecha y duración de la simulación."""
    date_picker = widgets.DatePicker(description='Fecha:', disabled=False)
    time_picker = widgets.FloatSlider(value=6, min=0, max=23, step=1, description='Hora Inicial:')
    duration_picker = widgets.FloatSlider(value=12, min=1, max=24, step=1, description='Duración (h):')

    def update_plot(date, start_hour, duration):
        start_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour)
        # Convertir a timezone-aware
        start_datetime = timezone("America/Guayaquil").localize(start_datetime)
        plotSunAndPanelTrajectory(start_datetime, duration)

    interact = widgets.interactive(update_plot, date=date_picker, start_hour=time_picker, duration=duration_picker)
    display(interact)

if __name__ == "__main__":
    interactive_plot()
```
## Resultados
El programa desarrollado permite visualizar de manera interactiva la trayectoria del sol y la orientación del panel solar a lo largo de un día determinado. Los ángulos de control calculados permiten que el panel solar se mantenga perpendicular a la luz solar, maximizando así la eficiencia del sistema.

Aquí se puede apreciar una fotografía de como queda nuestra interfaz incluído una pequeña simulación.

![Ejecución](https://github.com/iamjoel01/proyecto2bimestre_grupo8/raw/main/Ejecuci%C3%B3n.jpg)

## Conclusión
El seguidor solar desarrollado en este proyecto demuestra cómo el uso de técnicas matemáticas y de programación puede mejorar la eficiencia energética en sistemas solares. La implementación de un modelo interactivo permite explorar de manera dinámica cómo el panel solar sigue la trayectoria del sol, ofreciendo una herramienta educativa y práctica para el estudio de energías renovables.
