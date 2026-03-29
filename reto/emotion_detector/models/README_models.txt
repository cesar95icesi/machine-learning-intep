# Este directorio no va a git (ver .gitignore).
# Antes de hacer `docker build`, copia aquí los tres archivos de pesos de DeepFace:
#
#   Fuente: C:\Users\<tu_usuario>\.deepface\weights\
#
#   models/
#   ├── facial_expression_model_weights.h5         (~6 MB)
#   ├── deploy.prototxt                            (~28 KB)
#   └── res10_300x300_ssd_iter_140000.caffemodel   (~10 MB)
#
# Comando rápido (PowerShell desde la raíz del proyecto):
#   Copy-Item "$env:USERPROFILE\.deepface\weights\facial_expression_model_weights.h5" models\
#   Copy-Item "$env:USERPROFILE\.deepface\weights\deploy.prototxt" models\
#   Copy-Item "$env:USERPROFILE\.deepface\weights\res10_300x300_ssd_iter_140000.caffemodel" models\
