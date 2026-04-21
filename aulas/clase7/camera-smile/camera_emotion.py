"""
Clase 7 - Detector de emociones faciales en tiempo real con webcam
Ejecutar: python3 camera_emotion.py
Prerequisito: haber entrenado el modelo con train_model.py
"""
import cv2
import numpy as np
import joblib
import os
import sys

# ── 1. Cargar modelo entrenado ──
MODELO_PATH = "modelo_emociones.joblib"
ETIQUETAS_PATH = "etiquetas.joblib"

if not os.path.exists(MODELO_PATH) or not os.path.exists(ETIQUETAS_PATH):
    print("[ERROR] No se encontraron los archivos del modelo.")
    print("   Primero ejecuta: python3 train_model.py")
    sys.exit(1)

print("[INFO] Cargando modelo...")
pipeline = joblib.load(MODELO_PATH)
etiquetas = joblib.load(ETIQUETAS_PATH)
print("[OK] Modelo cargado")

# ── 2. Colores por emoción (BGR para OpenCV) ──
COLORES = {
    0: (0, 0, 255),      # Enojado    → Rojo
    1: (0, 128, 128),    # Asco       → Oliva
    2: (128, 0, 128),    # Miedo      → Púrpura
    3: (0, 255, 0),      # Feliz      → Verde
    4: (255, 128, 0),    # Triste     → Azul claro
    5: (0, 255, 255),    # Sorpresa   → Amarillo
    6: (200, 200, 200),  # Neutral    → Gris
}

# ── 3. Inicializar cámara y detector de rostros ──
print("[INFO] Buscando cámaras disponibles...")

cap = None
for idx in range(5):
    test_cap = cv2.VideoCapture(idx)
    if test_cap.isOpened():
        ret, frame = test_cap.read()
        if ret:
            print(f"   [OK] Cámara encontrada en índice {idx}")
            cap = test_cap
            break
    test_cap.release()

if cap is None:
    print("[ERROR] No se encontró ninguna cámara disponible.")
    print("   Verifica que la cámara esté conectada y con permisos.")
    print("   En macOS: Configuración del Sistema > Privacidad y Seguridad > Cámara")
    sys.exit(1)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("[OK] Cámara lista. Presiona 'q' para salir.")
print("=" * 50)


def dibujar_barras_probabilidad(frame, probabilidades, x_inicio, y_inicio):
    """Dibuja barras horizontales con las probabilidades de cada emoción."""
    ancho_max = 120
    alto_barra = 16
    espacio = 4

    for idx in range(len(etiquetas)):
        y = y_inicio + idx * (alto_barra + espacio)
        prob = probabilidades[idx]
        ancho = int(prob * ancho_max)
        color = COLORES.get(idx, (200, 200, 200))

        cv2.rectangle(frame, (x_inicio, y), (x_inicio + ancho, y + alto_barra), color, -1)
        cv2.rectangle(frame, (x_inicio, y), (x_inicio + ancho_max, y + alto_barra), (100, 100, 100), 1)

        texto = f"{etiquetas[idx]}: {prob:.0%}"
        cv2.putText(frame, texto, (x_inicio + ancho_max + 8, y + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)


# ── 4. Loop principal ──
while True:
    ret, frame = cap.read()
    if not ret:
        print("[WARN] Error al leer frame de la cámara.")
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rostros = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5, minSize=(48, 48)
    )

    for (x, y, w, h) in rostros:
        roi = gray[y:y+h, x:x+w]
        roi_resized = cv2.resize(roi, (48, 48))
        pixels = roi_resized.flatten().astype(np.float32) / 255.0
        pixels = pixels.reshape(1, -1)

        emocion_idx = pipeline.predict(pixels)[0]
        probabilidades = pipeline.predict_proba(pixels)[0]
        confianza = probabilidades.max()

        emocion_nombre = etiquetas[emocion_idx]
        color = COLORES.get(emocion_idx, (200, 200, 200))

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        label = f"{emocion_nombre} ({confianza:.0%})"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x, y - th - 10), (x + tw, y), color, -1)
        cv2.putText(frame, label, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        dibujar_barras_probabilidad(frame, probabilidades, x + w + 10, y)

    cv2.putText(frame, "Presiona 'q' para salir", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    n_rostros = len(rostros)
    cv2.putText(frame, f"Rostros: {n_rostros}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Detector de Emociones - ML INTEP", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ── 5. Limpiar recursos ──
cap.release()
cv2.destroyAllWindows()
print("\n[INFO] Cámara cerrada. Hasta luego!")
