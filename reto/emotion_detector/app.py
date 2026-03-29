from flask import Flask, render_template, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import logging
import threading
from deepface import DeepFace

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

# Global state
current_emotion = {
    "emotion": "neutral",
    "confidence": 0,
    "all_emotions": {},
    "face_detected": False,
    "face_box": None,
    "face_boxes": [],
    "face_count": 0,
    "error": None,
    "detector_backend": None,
}
emotion_lock = threading.Lock()

DETECTOR_BACKENDS = ("opencv", "ssd")

# Emotion mapping to happy/sad
HAPPY_EMOTIONS = {"happy"}
SAD_EMOTIONS = {"sad", "fear", "disgust", "angry"}
NEUTRAL_EMOTIONS = {"neutral", "surprise"}

def map_emotion(emotion_data):
    """Map detected emotions to happy/sad/neutral with confidence."""
    emotions = emotion_data.get("emotion", {})
    happy_score = emotions.get("happy", 0)
    sad_score = (emotions.get("sad", 0) + emotions.get("fear", 0) * 0.5 + 
                 emotions.get("disgust", 0) * 0.5 + emotions.get("angry", 0) * 0.5)
    
    if happy_score > sad_score and happy_score > 20:
        state = "happy"
        confidence = min(happy_score, 100)
    elif sad_score > happy_score and sad_score > 20:
        state = "sad"
        confidence = min(sad_score, 100)
    else:
        state = "neutral"
        confidence = emotions.get("neutral", 50)
    
    return state, confidence, emotions


def detect_faces_with_fallbacks(frame):
    """Detect all faces with multiple detector backends."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    last_error = None

    for backend in DETECTOR_BACKENDS:
        try:
            faces = DeepFace.extract_faces(
                img_path=rgb_frame,
                detector_backend=backend,
                enforce_detection=False,
                align=True,
            )

            face_boxes = []
            for face in faces:
                region = face.get("facial_area", {})
                x = int(region.get("x", 0))
                y = int(region.get("y", 0))
                w = int(region.get("w", 0))
                h = int(region.get("h", 0))
                if w > 0 and h > 0:
                    face_boxes.append({"x": x, "y": y, "w": w, "h": h})

            face_boxes.sort(key=lambda box: box["w"] * box["h"], reverse=True)

            if face_boxes:
                return face_boxes, backend
        except Exception as exc:
            last_error = exc
            app.logger.warning("Face detection failed with backend '%s': %s", backend, exc)

    if last_error is not None:
        raise last_error

    return [], None


def analyze_emotion_for_face(frame, face_box):
    """Analyze emotion for a single face crop."""
    x = max(0, int(face_box["x"]))
    y = max(0, int(face_box["y"]))
    w = max(0, int(face_box["w"]))
    h = max(0, int(face_box["h"]))

    face_crop = frame[y:y + h, x:x + w]
    if face_crop.size == 0:
        raise ValueError("Empty face crop for emotion analysis")

    rgb_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    result = DeepFace.analyze(
        rgb_crop,
        actions=["emotion"],
        enforce_detection=False,
        detector_backend="skip",
        silent=True,
    )

    if isinstance(result, list):
        if not result:
            raise ValueError("DeepFace did not return emotion results for face crop.")
        result = result[0]

    return result

def process_frame_for_emotion(frame):
    """Analyze a frame for emotions using DeepFace."""
    try:
        face_boxes, backend = detect_faces_with_fallbacks(frame)
        if not face_boxes:
            with emotion_lock:
                current_emotion["face_detected"] = False
                current_emotion["face_box"] = None
                current_emotion["face_boxes"] = []
                current_emotion["face_count"] = 0
                current_emotion["error"] = None
                current_emotion["detector_backend"] = backend
            return

        primary_face = face_boxes[0]
        result = analyze_emotion_for_face(frame, primary_face)
        state, confidence, all_emotions = map_emotion(result)

        with emotion_lock:
            current_emotion["emotion"] = state
            current_emotion["confidence"] = round(confidence, 1)
            current_emotion["all_emotions"] = {k: round(v, 1) for k, v in all_emotions.items()}
            current_emotion["face_detected"] = True
            current_emotion["face_box"] = primary_face
            current_emotion["face_boxes"] = face_boxes
            current_emotion["face_count"] = len(face_boxes)
            current_emotion["error"] = None
            current_emotion["detector_backend"] = backend

    except Exception as e:
        app.logger.exception("Emotion analysis error")
        with emotion_lock:
            current_emotion["face_detected"] = False
            current_emotion["face_box"] = None
            current_emotion["face_boxes"] = []
            current_emotion["face_count"] = 0
            current_emotion["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/emotion_state")
def emotion_state():
    with emotion_lock:
        return jsonify(current_emotion.copy())


@app.route("/analyze_frame", methods=["POST"])
def analyze_frame():
    """Receive base64 frame from browser and analyze it."""
    from flask import request
    
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image data"}), 400
    
    try:
        # Decode base64 image
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image"}), 400
        
        # Process synchronously so UI receives fresh face boxes each request.
        process_frame_for_emotion(frame)
        
        with emotion_lock:
            return jsonify(current_emotion.copy())
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🎭 Emotion Detector starting...")
    print("📷 Open http://localhost:5000 in your browser")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
