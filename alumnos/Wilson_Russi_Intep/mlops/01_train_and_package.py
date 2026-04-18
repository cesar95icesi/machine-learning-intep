"""
Clase 7 - Entrenar modelo Random Forest y empaquetarlo para SageMaker
Ejecutar: python3 01_train_and_package.py
Resultado: model.tar.gz listo para subir a S3
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report
import joblib
import tarfile
import os

print("=" * 55)
print("  PASO 1: Entrenar y empaquetar modelo para SageMaker")
print("=" * 55)

# ── 1. Generar dataset sintético ──
np.random.seed(42)
n_normal, n_fraude = 9500, 500

normal = pd.DataFrame({
    'monto': np.random.exponential(80, n_normal).round(2),
    'hora': np.random.normal(14, 4, n_normal).clip(0, 23).round(0),
    'dia_semana': np.random.randint(0, 7, n_normal),
    'distancia_km': np.random.exponential(5, n_normal).round(1),
    'intentos_pin': np.random.choice([1, 1, 1, 2], n_normal),
    'transacciones_24h': np.random.poisson(3, n_normal),
    'fraude': 0
})

fraude = pd.DataFrame({
    'monto': np.random.uniform(500, 5000, n_fraude).round(2),
    'hora': np.random.choice([0, 1, 2, 3, 4, 22, 23], n_fraude).astype(float),
    'dia_semana': np.random.randint(0, 7, n_fraude),
    'distancia_km': np.random.uniform(50, 500, n_fraude).round(1),
    'intentos_pin': np.random.choice([2, 3, 3, 4], n_fraude),
    'transacciones_24h': np.random.poisson(8, n_fraude),
    'fraude': 1
})

df = pd.concat([normal, fraude], ignore_index=True).sample(frac=1, random_state=42)
print(f"\nDataset: {len(df)} transacciones ({n_fraude} fraudes)")

# ── 2. Feature Engineering ──
df['es_madrugada'] = ((df['hora'] >= 0) & (df['hora'] <= 5)).astype(int)
df['es_fin_semana'] = (df['dia_semana'] >= 5).astype(int)
df['monto_alto'] = (df['monto'] > 500).astype(int)
df['ratio_monto_trans'] = df['monto'] / (df['transacciones_24h'] + 1)
df['pin_multiple'] = (df['intentos_pin'] > 1).astype(int)

features = ['monto', 'hora', 'dia_semana', 'distancia_km', 'intentos_pin',
            'transacciones_24h', 'es_madrugada', 'es_fin_semana',
            'monto_alto', 'ratio_monto_trans', 'pin_multiple']

X = df[features]
y = df['fraude']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 3. Entrenar con GridSearchCV ──
print("\nEntrenando con GridSearchCV...")
grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid={
        'n_estimators': [100, 200],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5]
    },
    cv=5, scoring='f1', n_jobs=-1
)
grid.fit(X_train, y_train)

y_pred = grid.predict(X_test)
print(f"\nMejores params: {grid.best_params_}")
print(f"F1 Score (test): {f1_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraude']))

# ── 4. Guardar modelo en formato SageMaker ──
# SageMaker espera un archivo model.joblib dentro de model.tar.gz
os.makedirs("model_artifact", exist_ok=True)
joblib.dump(grid.best_estimator_, "model_artifact/model.joblib")

# Crear model.tar.gz (formato requerido por SageMaker)
with tarfile.open("model.tar.gz", "w:gz") as tar:
    tar.add("model_artifact/model.joblib", arcname="model.joblib")

print("\n[OK] model.tar.gz creado (listo para subir a S3)")
print(f"   Tamaño: {os.path.getsize('model.tar.gz') / 1024:.1f} KB")
print("=" * 55)
