# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.10-slim AS base

# System dependencies required by OpenCV and TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn==21.2.0 && \
    pip install --no-cache-dir -r requirements.txt

# ── DeepFace model weights (baked into the image — no runtime downloads) ─────
# DEEPFACE_HOME points DeepFace to /opt/deepface_home instead of ~
ENV DEEPFACE_HOME=/opt/deepface_home
RUN mkdir -p /opt/deepface_home/.deepface/weights

# Copy the three weight files from the local models/ directory.
# Expected files:
#   models/facial_expression_model_weights.h5   (~6 MB)
#   models/deploy.prototxt                       (~28 KB)
#   models/res10_300x300_ssd_iter_140000.caffemodel (~10 MB)
COPY models/ /opt/deepface_home/.deepface/weights/

# Copy application source
COPY . .

EXPOSE 5000

# Single worker + threads keeps the shared emotion state consistent
CMD ["gunicorn", \
     "--workers=1", \
     "--threads=4", \
     "--worker-class=gthread", \
     "--bind=0.0.0.0:5000", \
     "--timeout=120", \
     "--access-logfile=-", \
     "app:app"]
