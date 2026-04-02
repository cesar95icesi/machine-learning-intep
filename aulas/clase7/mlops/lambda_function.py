"""
Handler de AWS Lambda para prediccion de fraude.
Carga el modelo sklearn desde el paquete y predice.
"""
import json
import joblib
import os
import numpy as np

# Cargar modelo una sola vez (se reutiliza entre invocaciones)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
model = joblib.load(MODEL_PATH)


def preparar_features(t):
    """Crear features derivadas igual que en el entrenamiento."""
    t["es_madrugada"] = int(t["hora"] <= 5)
    t["es_fin_semana"] = int(t["dia_semana"] >= 5)
    t["monto_alto"] = int(t["monto"] > 500)
    t["ratio_monto_trans"] = t["monto"] / (t["transacciones_24h"] + 1)
    t["pin_multiple"] = int(t["intentos_pin"] > 1)

    features_orden = [
        "monto", "hora", "dia_semana", "distancia_km", "intentos_pin",
        "transacciones_24h", "es_madrugada", "es_fin_semana",
        "monto_alto", "ratio_monto_trans", "pin_multiple"
    ]
    return [t[f] for f in features_orden]


def handler(event, context):
    """Handler principal de Lambda."""
    try:
        # Parsear body (soporta API Gateway y Function URL)
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        elif isinstance(event.get("body"), dict):
            body = event["body"]
        else:
            body = event

        # Soportar formato dict con campos o array directo
        if isinstance(body, dict):
            features = [preparar_features(body)]
        elif isinstance(body, list):
            if isinstance(body[0], dict):
                features = [preparar_features(t) for t in body]
            else:
                features = body
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Formato no soportado"})
            }

        predicciones = model.predict(features).tolist()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "predicciones": predicciones,
                "etiquetas": ["FRAUDE" if p == 1 else "Normal" for p in predicciones]
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
