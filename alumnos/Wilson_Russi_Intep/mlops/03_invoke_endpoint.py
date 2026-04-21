"""
Clase 7 - Consumir el endpoint de API Gateway
Ejecutar: python3 03_invoke_endpoint.py
Prerequisito: Lambda + API Gateway desplegados con terraform apply
"""
import json
import subprocess

# ── Configuracion ──
API_URL = input("Ingresa la URL del endpoint (de terraform output 'api_url'): ").strip()

# ── Datos de prueba ──
# Transaccion sospechosa (probablemente fraude)
transaccion_sospechosa = {
    "monto": 3500.0,
    "hora": 2.0,
    "dia_semana": 6,
    "distancia_km": 200.0,
    "intentos_pin": 3,
    "transacciones_24h": 10
}

# Transaccion normal
transaccion_normal = {
    "monto": 45.0,
    "hora": 14.0,
    "dia_semana": 2,
    "distancia_km": 3.0,
    "intentos_pin": 1,
    "transacciones_24h": 2
}


def invocar_endpoint(datos, nombre=""):
    """Enviar datos al endpoint y obtener prediccion."""
    payload = json.dumps(datos)

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", API_URL,
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] curl fallo: {result.stderr}")
        return None

    respuesta_raw = json.loads(result.stdout)

    # Extraer body si viene envuelto
    if isinstance(respuesta_raw, dict) and "body" in respuesta_raw:
        resultado = json.loads(respuesta_raw["body"])
    elif isinstance(respuesta_raw, dict) and "predicciones" in respuesta_raw:
        resultado = respuesta_raw
    else:
        print(f"  [DEBUG] Respuesta: {respuesta_raw}")
        resultado = respuesta_raw

    print(f"\n{'='*45}")
    print(f"  {nombre}")
    print(f"{'='*45}")
    print(f"  Monto: ${datos['monto']:,.0f}")
    print(f"  Hora: {datos['hora']:.0f}:00")
    print(f"  Distancia: {datos['distancia_km']} km")
    print(f"  Intentos PIN: {datos['intentos_pin']}")
    print(f"  Transacciones 24h: {datos['transacciones_24h']}")
    print(f"  ---")
    prediccion = resultado["predicciones"][0]
    etiqueta = resultado["etiquetas"][0]
    print(f"  Prediccion: {'[ALERTA] FRAUDE' if prediccion == 1 else '[OK] Normal'}")
    return resultado


# ── Ejecutar predicciones ──
print("[INFO] Invocando endpoint API Gateway...\n")

invocar_endpoint(transaccion_sospechosa, "Transaccion Sospechosa")
invocar_endpoint(transaccion_normal, "Transaccion Normal")

print(f"\n\n[INFO] El endpoint esta en: {API_URL}")
print("   Tambien puedes invocarlo desde Postman con POST + JSON (sin autenticacion)")
