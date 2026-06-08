# Sistema de Detección de Señales de Tránsito en Tiempo Real con YOLOv8

¡Bienvenido al proyecto! Este sistema utiliza **YOLOv8s** para detectar señales de tránsito en tiempo real (mediante cámara web o archivos de video) y emite alertas de voz descriptivas en español para asistir al conductor.

---

## Configuración Rápida (Un Solo Comando)

Se ha automatizado todo el proceso de configuración del entorno virtual, la instalación de la versión de Python correcta (v3.12) y la descarga e instalación de todas las dependencias (incluyendo PyTorch con soporte CUDA para aceleración por GPU si el hardware lo permite).

### Instrucciones de Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd ProyectoTecnoII
   ```

2. **Ejecuta el script de configuración correspondiente a tu sistema operativo:**
   * **En Windows (CMD o PowerShell):**
     ```cmd
     setup.bat
     ```
   * **En Linux o macOS:**
     ```bash
     chmod +x setup.sh
     ./setup.sh
     ```

*El script creará automáticamente el entorno virtual en la carpeta `.venv`, sincronizará todas las dependencias del archivo `uv.lock` y validará que todas las importaciones y la GPU/CUDA estén listas.*

---

## Ejecución del Sistema

Una vez finalizada la configuración del paso anterior, puedes lanzar el sistema de detección ejecutando un único comando dentro del directorio raíz del proyecto:

```bash
uv run main.py
```

### Opciones de Ejecución Personalizadas

El script `main.py` acepta múltiples parámetros para adaptar la experiencia a tus necesidades:

* **Desactivar alertas por voz:**
   Si prefieres usar la detección visual únicamente y silenciar las alertas de voz en español:
   ```bash
   uv run main.py --no-voice
   ```

* **Ajustar el umbral de confianza:**
   Por defecto es `0.40`. Puedes subirlo para evitar falsos positivos o bajarlo para detectar más señales:
   ```bash
   uv run main.py --conf 0.50
   ```

* **Especificar una ruta de video u otra cámara:**
   Por defecto se utiliza la webcam principal (`0`). Puedes pasar la ruta a un archivo de video o cambiar el índice de la cámara:
   ```bash
   uv run main.py --source "ruta/al/video.mp4"
   ```
   O para usar la cámara secundaria:
   ```bash
   uv run main.py --source 1
   ```

* **Usar un modelo específico:**
   Por defecto se carga el modelo entrenado ubicado en `models/best.pt` (el cual ya viene precargado en este repositorio para asegurar las mismas pruebas). Si deseas cambiar el modelo:
   ```bash
   uv run main.py --model "models/otro_modelo.pt"
   ```

---

## 📁 Estructura Principal del Proyecto

* 📂 **`configs/`**: Contiene `settings.py` con las configuraciones globales, rutas de carpetas y el mapeo de clases de señales de tránsito a español.
* 📂 **`services/`**:
  * `model_loader.py`: Lógica para cargar modelos YOLOv8 y colocarlos en GPU/CPU.
  * `detector.py`: Pipeline básico de inferencia sobre imágenes.
  * `realtime_detection.py`: Procesamiento del flujo de video y coordinación de alertas de voz.
  * `voice_service.py`: Motor de conversión de texto a voz (TTS) en español con control de enfriamiento (cooldown).
* 📂 **`models/`**: Carpeta donde reside el modelo entrenado óptimo (`best.pt`).
* 📂 **`utils/`**: Funciones auxiliares de preprocesamiento, dibujo en pantalla y utilidades.
* 📂 **`notebooks/`**: Notebooks de desarrollo paso a paso del proyecto.
* 📄 **`pyproject.toml`** y **`uv.lock`**: Definición precisa de dependencias y versiones de librerías para replicabilidad absoluta.
* 📄 **`test_imports.py`**: Script de autodiagnóstico del entorno.

---

## Pruebas de Diagnóstico del Entorno

Si en cualquier momento deseas verificar que el entorno virtual y el soporte para GPU (CUDA) estén respondiendo correctamente, puedes ejecutar:

```bash
uv run test_imports.py
```
Imprimirá una lista confirmando el estado y versión de cada biblioteca esencial.