# Sistema de Monitoreo de Limpieza de Paneles Solares

Este proyecto incluye un cliente Python que se conecta a un ESP32 que transmite lecturas del sensor de luz BH1750. El objetivo es medir la radiación (lux) y mostrar un porcentaje estimado de suciedad del panel: cuanto más alto sea el porcentaje, más sucio está el panel.

Archivos incluidos
- `monitoreopaneles.py`: Aplicación GUI en Tkinter que se conecta por puerto serie al ESP32, lee valores LUX y muestra una barra de suciedad (verde/amarillo/rojo). Incluye calibración persistente y registro CSV.
- `esp32_bh1750.ino`: Ejemplo de sketch Arduino/ESP32 que lee el BH1750 y envía por Serial en formato `LUX:<valor>` cada segundo.
- `requirements.txt`: Dependencias Python (pyserial).

Requisitos
- Python 3.8+
- Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Uso (PC)
1. Conecta el ESP32 por USB y carga `esp32_bh1750.ino` (usa el Library Manager para instalar la librería `BH1750`).
2. Ejecuta `monitoreopaneles.py`:

```powershell
python monitoreopaneles.py
```

3. En la GUI selecciona el puerto COM donde está el ESP32 (puedes pulsar "Actualizar puertos"), selecciona el baud (115200 por defecto) y pulsa "Conectar".
4. Cuando veas lecturas en "Radiación actual" puedes pulsar "Calibrar (establecer limpio)" estando el panel limpio (p. ej. después de limpieza), para que el programa calcule el % de suciedad relativo a ese valor limpio.

Formato serie
- Debe enviarse por Serial líneas de texto con el valor de lux. Formatos aceptados:
  - `LUX:123.45`  (recomendado)
  - `123.45`

Notas y recomendaciones
- La estimación de suciedad es relativa: el programa compara la lectura actual con el valor calibrado para panel limpio. Si no calibras, la barra se mostrará como 0%.
- Si el panel está orientado diferente o la iluminación cambia (nubes), la lectura variará; calibra en un momento con buena iluminación y panel limpio.

Nuevas funciones añadidas
- Calibración persistente: cuando calibras (botón "Calibrar"), el valor de lux del panel limpio se guarda en `config.json` y se recarga al iniciar la aplicación.
- Registro CSV: puedes iniciar/detener un registro CSV desde el botón "Iniciar registro CSV". El archivo guardará líneas con: timestamp,lux,dirt_pct.

Soporte
Si necesitas adaptar la interfaz (por ejemplo un umbral automático, guardado de calibraciones adicionales o envío a la nube), indícame qué prefieres y lo incorporo.
# Sistema de Monitoreo de Limpieza de Paneles Solares

Este proyecto incluye un cliente Python que se conecta a un ESP32 que transmite lecturas del sensor de luz BH1750. El objetivo es medir la radiación (lux) y mostrar un porcentaje estimado de suciedad del panel: cuanto más alto sea el porcentaje, más sucio está el panel.

Archivos incluidos
- `monitoreopaneles.py`: Aplicación GUI en Tkinter que se conecta por puerto serie al ESP32, lee valores LUX y muestra una barra de suciedad (verde/amarillo/rojo).
- `esp32_bh1750.ino`: Ejemplo de sketch Arduino/ESP32 que lee el BH1750 y envía por Serial en formato `LUX:<valor>` cada segundo.
- `requirements.txt`: Dependencias Python (pyserial).

Requisitos
- Python 3.8+
- Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Uso (PC)
1. Conecta el ESP32 por USB y carga `esp32_bh1750.ino` (usa el Library Manager para instalar la librería `BH1750`).
2. Ejecuta `monitoreopaneles.py`:

```powershell
python monitoreopaneles.py
```

3. En la GUI selecciona el puerto COM donde está el ESP32 (puedes pulsar "Actualizar puertos"), selecciona el baud (115200 por defecto) y pulsa "Conectar".
4. Cuando veas lecturas en "Radiación actual" puedes pulsar "Calibrar (establecer limpio)" estando el panel limpio (p. ej. después de limpieza), para que el programa calcule el % de suciedad relativo a ese valor limpio.

Formato serie
- Debe enviarse por Serial líneas de texto con el valor de lux. Formatos aceptados:
  - `LUX:123.45`  (recomendado)
  - `123.45`

Notas y recomendaciones
- La estimación de suciedad es relativa: el programa compara la lectura actual con el valor calibrado para panel limpio. Si no calibras, la barra se mostrará como 0%.
- Si el panel está orientado diferente o la iluminación cambia (nubes), la lectura variará; calibra en un momento con buena iluminación y panel limpio.
- Si necesitas enviar también temperatura, humedad o más datos, adapta el sketch y `monitoreopaneles.py` para parsear otros prefijos (ej: `TMP:`, `HUM:`).

Soporte
Si necesitas adaptar la interfaz (por ejemplo un umbral automático, guardado de calibraciones o envío a la nube), indícame qué prefieres y lo incorporo.
