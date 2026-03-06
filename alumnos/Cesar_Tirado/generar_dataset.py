"""
Script para generar el dataset sintetico de abandono de clientes.

Genera un archivo CSV con 800 clientes ficticios de una empresa de
telecomunicaciones. Cada fila representa un cliente con variables que
influyen en la probabilidad de abandonar el servicio (churn).

Variables generadas:
    - antiguedad_meses: meses como cliente (1 a 72)
    - factura_mensual: valor mensual del plan en dolares (20 a 120)
    - llamadas_soporte: cantidad de llamadas al soporte tecnico (0 a 10)
    - contrato: tipo de contrato (Mensual, Anual, Dos_anios)
    - satisfaccion: nivel de satisfaccion del 1 al 5
    - abandono: 1 si el cliente abandono, 0 si permanece (variable objetivo)

Ejecutar:
    python generar_dataset.py
"""

import numpy as np
import pandas as pd

# Semilla para reproducibilidad: siempre genera los mismos datos
np.random.seed(42)

n = 800  # Cantidad de clientes a generar

# ---------------------------------------------------------------
# 1. Generar las variables independientes (features)
# ---------------------------------------------------------------

# Antiguedad: meses como cliente (entre 1 y 72 meses = 6 anios)
antiguedad_meses = np.random.randint(1, 73, size=n)

# Factura mensual: valor del plan en dolares (entre 20 y 120)
factura_mensual = np.round(np.random.uniform(20, 120, size=n), 2)

# Llamadas a soporte: entre 0 y 10 llamadas
# Usamos una distribucion de Poisson (lambda=2) para que la mayoria
# tenga pocas llamadas y unos pocos tengan muchas
llamadas_soporte = np.minimum(np.random.poisson(lam=2, size=n), 10)

# Tipo de contrato: Mensual, Anual o Dos_anios
# Los contratos mensuales son mas comunes (50%), anuales (30%), dos anios (20%)
contrato = np.random.choice(
    ["Mensual", "Anual", "Dos_anios"],
    size=n,
    p=[0.50, 0.30, 0.20]
)

# Satisfaccion: escala del 1 al 5
satisfaccion = np.random.randint(1, 6, size=n)

# ---------------------------------------------------------------
# 2. Calcular la probabilidad de abandono (logica del negocio)
# ---------------------------------------------------------------
# La probabilidad de abandono depende de las variables anteriores.
# Usamos una funcion logistica (sigmoide) para convertir una
# puntuacion lineal en una probabilidad entre 0 y 1.
#
# Logica de negocio simulada:
#   - Mas llamadas a soporte -> mas probabilidad de irse
#   - Factura mas alta -> mas probabilidad de irse
#   - Mayor antiguedad -> menos probabilidad de irse (lealtad)
#   - Contrato mensual -> mas probabilidad de irse (sin compromiso)
#   - Menor satisfaccion -> mas probabilidad de irse

# Puntuacion lineal (log-odds)
score = (
    -1.0                                           # base (intercepto)
    + 0.35 * llamadas_soporte                      # mas soporte = mas riesgo
    + 0.015 * factura_mensual                      # factura alta = mas riesgo
    - 0.03 * antiguedad_meses                      # mas antiguedad = menos riesgo
    - 0.30 * satisfaccion                          # mas satisfaccion = menos riesgo
    + 0.8 * (contrato == "Mensual").astype(float)  # contrato mensual = mas riesgo
    - 0.3 * (contrato == "Dos_anios").astype(float)  # contrato largo = menos riesgo
)

# Funcion sigmoide: convierte el score en probabilidad (0 a 1)
probabilidad = 1 / (1 + np.exp(-score))

# Generar la variable objetivo (0 o 1) segun la probabilidad
# Si la probabilidad es 0.7, hay un 70% de chance de que abandone
abandono = (np.random.random(n) < probabilidad).astype(int)

# ---------------------------------------------------------------
# 3. Crear el DataFrame y guardarlo como CSV
# ---------------------------------------------------------------
df = pd.DataFrame({
    "antiguedad_meses": antiguedad_meses,
    "factura_mensual": factura_mensual,
    "llamadas_soporte": llamadas_soporte,
    "contrato": contrato,
    "satisfaccion": satisfaccion,
    "abandono": abandono,
})

# Guardar el archivo CSV (sin el indice numerico de pandas)
df.to_csv("abandono_clientes.csv", index=False)

# ---------------------------------------------------------------
# 4. Resumen del dataset generado
# ---------------------------------------------------------------
print(f"Dataset generado: {n} clientes")
print(f"Archivo guardado: abandono_clientes.csv")
print()
print(f"Distribucion de abandono:")
print(f"  Permanece (0): {(abandono == 0).sum()} ({(abandono == 0).mean()*100:.1f}%)")
print(f"  Abandona  (1): {(abandono == 1).sum()} ({(abandono == 1).mean()*100:.1f}%)")
print()
print("Primeras 5 filas:")
print(df.head().to_string(index=False))