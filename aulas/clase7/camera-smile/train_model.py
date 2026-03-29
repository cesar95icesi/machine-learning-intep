"""
Clase 7 - Entrenar modelo de reconocimiento de emociones faciales
Ejecutar: python3 train_model.py
Resultado: modelo_emociones.joblib y etiquetas.joblib
Prerequisito: descargar dataset FER2013 de Kaggle (carpetas train/ y test/)
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
import cv2
import os
import time

print("=" * 60)
print("  RECONOCIMIENTO DE EMOCIONES FACIALES - Entrenamiento")
print("  Modelo: PCA + SVM (scikit-learn)")
print("=" * 60)

# ── 1. Verificar dataset ──
TRAIN_DIR = os.path.join("archive", "train")
TEST_DIR = os.path.join("archive", "test")

if not os.path.exists(TRAIN_DIR) or not os.path.exists(TEST_DIR):
    print(f"\n[ERROR] No se encontraron las carpetas '{TRAIN_DIR}/' y '{TEST_DIR}/'")
    print("   Descárgalas de: https://www.kaggle.com/datasets/msambare/fer2013")
    print("   Estructura esperada:")
    print("     camera-smile/")
    print("       ├── train/")
    print("       │   ├── angry/")
    print("       │   ├── disgust/")
    print("       │   ├── fear/")
    print("       │   ├── happy/")
    print("       │   ├── sad/")
    print("       │   ├── surprise/")
    print("       │   └── neutral/")
    print("       └── test/")
    print("           └── (mismas subcarpetas)")
    exit(1)

CARPETA_A_ETIQUETA = {
    "angry": 0,
    "disgust": 1,
    "fear": 2,
    "happy": 3,
    "sad": 4,
    "surprise": 5,
    "neutral": 6,
}

ETIQUETAS = {
    0: "Enojado",
    1: "Asco",
    2: "Miedo",
    3: "Feliz",
    4: "Triste",
    5: "Sorpresa",
    6: "Neutral"
}


def cargar_imagenes(directorio):
    """Carga imágenes de las subcarpetas y retorna arrays X, y."""
    imagenes = []
    labels = []
    for carpeta, idx in CARPETA_A_ETIQUETA.items():
        ruta = os.path.join(directorio, carpeta)
        if not os.path.exists(ruta):
            print(f"   [WARN] Carpeta no encontrada: {ruta}")
            continue
        archivos = [f for f in os.listdir(ruta) if f.endswith((".jpg", ".png", ".jpeg"))]
        for archivo in archivos:
            img = cv2.imread(os.path.join(ruta, archivo), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (48, 48))
            imagenes.append(img.flatten())
            labels.append(idx)
    return np.array(imagenes, dtype=np.float32), np.array(labels)


# ── 2. Cargar imágenes de train/ y test/ ──
print("\n[INFO] Cargando imágenes de entrenamiento...")
X_train, y_train = cargar_imagenes(TRAIN_DIR)
print(f"   Train: {len(X_train)} imágenes")

print("\n[INFO] Cargando imágenes de prueba...")
X_test, y_test = cargar_imagenes(TEST_DIR)
print(f"   Test: {len(X_test)} imágenes")

# ── 3. Preprocesar datos ──
print("\n[INFO] Preprocesando datos...")
X_train = X_train / 255.0
X_test = X_test / 255.0

print(f"   Shape X_train: {X_train.shape} (muestras, pixeles 48x48)")
print(f"   Clases: {list(ETIQUETAS.values())}")

for idx, nombre in ETIQUETAS.items():
    count_train = np.sum(y_train == idx)
    count_test = np.sum(y_test == idx)
    print(f"     {nombre}: {count_train} train / {count_test} test")

# ── 4. Crear pipeline PCA + SVM ──
print("\n[INFO] Creando pipeline: PCA(150 componentes) + SVM(kernel RBF)...")
print("   PCA reduce 2304 dimensiones → 150 componentes principales")
print("   SVM busca hiperplanos óptimos para separar las 7 emociones")

pipeline = Pipeline([
    ("pca", PCA(n_components=150, whiten=True, random_state=42)),
    ("svm", SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42))
])

# ── 5. Entrenar modelo ──
print("\n[TRAIN] Entrenando modelo (esto puede tardar 2-5 minutos)...")
inicio = time.time()
pipeline.fit(X_train, y_train)
duracion = time.time() - inicio
print(f"   Entrenamiento completado en {duracion:.1f} segundos")

# ── 6. Evaluar modelo ──
print("\n[EVAL] Evaluando modelo en datos de prueba...")
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n   Accuracy global: {accuracy:.2%}")
print(f"\n{classification_report(y_test, y_pred, target_names=list(ETIQUETAS.values()))}")

# ── 7. Varianza explicada por PCA ──
varianza = pipeline.named_steps["pca"].explained_variance_ratio_.sum()
print(f"   Varianza explicada por PCA (150 componentes): {varianza:.2%}")

# ── 8. Guardar modelo y etiquetas ──
print("\n[SAVE] Guardando modelo...")
joblib.dump(pipeline, "modelo_emociones.joblib")
joblib.dump(ETIQUETAS, "etiquetas.joblib")

size_modelo = os.path.getsize("modelo_emociones.joblib") / (1024 * 1024)
print(f"   modelo_emociones.joblib ({size_modelo:.1f} MB)")
print(f"   etiquetas.joblib")

print("\n" + "=" * 60)
print("  [OK] Modelo entrenado y guardado exitosamente")
print("  Siguiente paso: python3 camera_emotion.py")
print("=" * 60)
