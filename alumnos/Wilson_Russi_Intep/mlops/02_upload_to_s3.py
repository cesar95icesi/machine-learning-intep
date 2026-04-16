"""
Clase 7 - Empaquetar Lambda y subir a S3
Ejecutar: python3 02_upload_to_s3.py
Prerequisito: haber ejecutado 01_train_and_package.py
"""
import boto3
import subprocess
import shutil
import zipfile
import os

print("=" * 55)
print("  PASO 2: Empaquetar Lambda y subir a S3")
print("=" * 55)

# ── 1. Verificar que existe el modelo ──
MODEL_FILE = "model_artifact/model.joblib"
if not os.path.exists(MODEL_FILE):
    print(f"\n[ERROR] No se encontro '{MODEL_FILE}'")
    print("   Primero ejecuta: python3 01_train_and_package.py")
    exit(1)

# ── 2. Crear directorio temporal para el paquete ──
PKG_DIR = "lambda_package"
ZIP_FILE = "lambda_package.zip"

if os.path.exists(PKG_DIR):
    shutil.rmtree(PKG_DIR)
os.makedirs(PKG_DIR)

# ── 3. Instalar dependencias para Linux (Lambda) ──
print("\n[INFO] Instalando dependencias para Lambda (linux)...")
subprocess.run([
    "pip", "install",
    "scikit-learn", "joblib", "numpy",
    "--target", PKG_DIR,
    "--platform", "manylinux2014_x86_64",
    "--only-binary=:all:",
    "--implementation", "cp",
    "--python-version", "3.12",
    "--quiet"
], check=True)

# ── 4. Copiar handler y modelo ──
print("[INFO] Copiando handler y modelo...")
shutil.copy("lambda_function.py", PKG_DIR)
shutil.copy(MODEL_FILE, os.path.join(PKG_DIR, "model.joblib"))

# ── 5. Crear ZIP ──
print("[INFO] Creando lambda_package.zip...")
with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PKG_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, PKG_DIR)
            zf.write(file_path, arcname)

size_mb = os.path.getsize(ZIP_FILE) / (1024 * 1024)
print(f"   Tamanio: {size_mb:.1f} MB")

# ── 6. Subir a S3 ──
BUCKET_NAME = input("\nIngresa el nombre del bucket S3 (de terraform output): ").strip()
S3_KEY = "lambda/lambda_package.zip"

print(f"\n[INFO] Subiendo {ZIP_FILE} a s3://{BUCKET_NAME}/{S3_KEY}...")
s3 = boto3.client("s3")
s3.upload_file(ZIP_FILE, BUCKET_NAME, S3_KEY)

print(f"[OK] Paquete Lambda subido exitosamente")
print(f"   Ubicacion: s3://{BUCKET_NAME}/{S3_KEY}")

# ── 7. Limpiar archivos temporales ──
shutil.rmtree(PKG_DIR)
print("\n[INFO] Ahora ejecuta: terraform apply (para crear la Lambda)")
print("=" * 55)
