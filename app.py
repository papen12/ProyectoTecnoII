import streamlit as st
import cv2
import numpy as np
import datetime
import time
from pathlib import Path
from configs import settings
from services.detector import TrafficSignDetector
from services.voice_service import VoiceAlertService
from utils.drawing import draw_detections, draw_fps, draw_info_panel
from utils.fps import FPSCounter
from utils.camera import CameraManager

st.set_page_config(
    page_title="Detector de Señales de Tránsito",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0e0e0e; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #FFD700; font-family: 'Segoe UI', sans-serif; }
    .stMetric label { color: #aaa !important; }
    .stMetric value { color: #FFD700 !important; }
    .detection-box {
        background: #1a1a1a;
        border: 1px solid #FF8C00;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.4rem;
        color: #f0f0f0;
        font-size: 0.9rem;
    }
    .no-detection {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Detector de Señales de Tránsito - YOLOv8s")

if "detector" not in st.session_state:
    st.session_state.detector = None
if "voice_service" not in st.session_state:
    st.session_state.voice_service = None
if "fps_counter" not in st.session_state:
    st.session_state.fps_counter = FPSCounter()
if "detection_log" not in st.session_state:
    st.session_state.detection_log = []
if "running" not in st.session_state:
    st.session_state.running = False
if "total_detections" not in st.session_state:
    st.session_state.total_detections = 0

with st.sidebar:
    st.header("Configuración")

    model_path = st.text_input(
        "Ruta del modelo",
        value=str(Path(settings.MODELS_DIR) / "best.pt")
    )
    conf_threshold = st.slider(
        "Umbral de confianza",
        min_value=0.10,
        max_value=0.95,
        value=float(settings.CONFIDENCE_THRESHOLD),
        step=0.05
    )
    camera_source = st.text_input(
        "Origen de video / Cámara",
        value=str(settings.CAMERA_INDEX)
    )
    enable_voice = st.toggle("Alertas de voz", value=True)
    rotate_ccw = st.toggle("Corregir rotación (90° Izq. para modelo)", value=settings.ROTATE_INPUT_90_CCW)
    settings.ROTATE_INPUT_90_CCW = rotate_ccw

    st.divider()

    col_start, col_stop = st.columns(2)
    with col_start:
        start_btn = st.button("Iniciar", use_container_width=True, type="primary")
    with col_stop:
        stop_btn = st.button("Detener", use_container_width=True)

    st.divider()
    st.caption("Registro de detecciones")
    log_placeholder = st.empty()

col_video, col_stats = st.columns([3, 1])

with col_video:
    frame_placeholder = st.empty()

with col_stats:
    st.subheader("Estado")
    metric_fps       = st.empty()
    metric_detects   = st.empty()
    metric_last      = st.empty()
    st.divider()
    st.subheader("Detecciones activas")
    detections_panel = st.empty()

if start_btn:
    model_file = Path(model_path)
    if not model_file.exists():
        st.sidebar.error(f"Modelo no encontrado: {model_path}")
    else:
        st.session_state.detector = TrafficSignDetector(
            model_path=model_file,
            confidence=conf_threshold
        )
        st.session_state.voice_service = VoiceAlertService() if enable_voice else None
        st.session_state.fps_counter.reset()
        st.session_state.running = True
        st.session_state.detection_log = []
        st.session_state.total_detections = 0

if stop_btn:
    st.session_state.running = False
    if st.session_state.voice_service:
        st.session_state.voice_service.shutdown()
        st.session_state.voice_service = None

if st.session_state.running and st.session_state.detector:
    # Parsear origen de video: si es numérico se convierte a entero, de lo contrario se deja como string
    parsed_source = camera_source.strip()
    if parsed_source.isdigit():
        parsed_source = int(parsed_source)

    camera = CameraManager(
        source=parsed_source,
        width=settings.FRAME_WIDTH,
        height=settings.FRAME_HEIGHT
    )

    if not camera.is_opened():
        st.error(f"No se pudo abrir la cámara ({camera_source}). Verifica la conexión.")
        st.session_state.running = False
    else:
        detector     = st.session_state.detector
        voice_svc    = st.session_state.voice_service
        fps_counter  = st.session_state.fps_counter

        consecutive_failures = 0
        frame_idx = 0
        while st.session_state.running:
            ret, frame = camera.read_frame()
            if not ret or frame.size == 0:
                consecutive_failures += 1
                if consecutive_failures > 150:  # ~1.5 segundos sin recibir imagen
                    st.warning("Fallo en la adquisición de fotogramas (se perdió el stream).")
                    break
                time.sleep(0.01)
                continue
            
            consecutive_failures = 0
            frame_idx += 1

            detections = detector.detect(frame, conf_override=conf_threshold)
            fps_counter.tick()
            fps_val = fps_counter.get_fps()

            last_sign = "Ninguna"
            if detections:
                d = detections[0]
                last_sign = f"{d.class_name} ({d.confidence*100:.1f}%)"

            current_info = {
                "Modelo": settings.MODEL_NAME,
                "Conf":   f"{conf_threshold:.2f}",
                "Camara": camera_source,
                "Voz":    "Activa" if enable_voice else "Inactiva",
                "Ultima": last_sign
            }

            annotated = draw_detections(frame, detections)
            annotated = draw_fps(annotated, fps_val)
            annotated = draw_info_panel(annotated, current_info)

            # Codificar a JPEG usando OpenCV (muy rápido, reduce el tamaño enviado por WebSockets de ~1MB a ~40KB)
            success, jpeg_buf = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if success:
                frame_placeholder.image(jpeg_buf.tobytes(), use_container_width=True)

            # 1. Actualizar el estado de los datos e iniciar alertas de voz inmediatamente en cada fotograma
            if detections:
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                for det in detections:
                    st.session_state.total_detections += 1
                    log_entry = f"[{now_str}] {det.class_name} — {det.confidence*100:.1f}%"
                    st.session_state.detection_log.insert(0, log_entry)
                    st.session_state.detection_log = st.session_state.detection_log[:50]
                    if voice_svc:
                        voice_svc.alert(det.class_name)

            # 2. Renderizar los widgets de texto de Streamlit solo cada 8 fotogramas (3-4 veces por segundo)
            # Esto evita saturar el canal de WebSockets de Streamlit con miles de actualizaciones y acelera el renderizado.
            if frame_idx % 8 == 0:
                metric_fps.metric("FPS", f"{fps_val:.1f}")
                metric_detects.metric("Total detectadas", st.session_state.total_detections)
                metric_last.metric("Última señal", last_sign if last_sign != "Ninguna" else "—")

                if detections:
                    active_html = "".join(
                        f'<div class="detection-box">[Señal] {d.class_name}<br><small>{d.confidence*100:.1f}% confianza</small></div>'
                        for d in detections
                    )
                    detections_panel.markdown(active_html, unsafe_allow_html=True)
                else:
                    detections_panel.markdown(
                        '<div class="no-detection">Sin detecciones activas</div>',
                        unsafe_allow_html=True
                    )

                log_md = "\n".join(f"- {e}" for e in st.session_state.detection_log[:15])
                log_placeholder.markdown(log_md if log_md else "_Sin registros aún_")

            # Ceder CPU brevemente para dar tiempo de CPU al hilo de la cámara y evitar bloqueos (starvation)
            time.sleep(0.01)

        camera.release()

elif not st.session_state.running:
    frame_placeholder.markdown("""
    <div style='background:#111;border:2px dashed #444;border-radius:12px;
                height:400px;display:flex;align-items:center;justify-content:center;
                color:#555;font-size:1.2rem;'>
        Presiona <strong style='color:#FFD700;margin:0 6px'>Iniciar</strong> para activar la cámara
    </div>
    """, unsafe_allow_html=True)