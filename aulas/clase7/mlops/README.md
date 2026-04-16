# Clase 7 - Despliegue de ML en AWS con Lambda + Terraform

## Arquitectura

```
Developer -> S3 (paquete zip) -> Lambda Function -> Function URL (endpoint publico)
                                                          |
                                                  Postman / Python / curl
```

## Por que Lambda en vez de SageMaker?

| Aspecto | SageMaker | Lambda |
|---|---|---|
| Diseñado para | Modelos de ML | Funciones generales |
| Carga del modelo | Se mantiene en memoria | Se carga en cold start (~3-10s) |
| Tamaño maximo | Sin limite practico | 250 MB (codigo + dependencias) |
| GPU | Soporta GPU | Solo CPU |
| Costo | Instancia siempre activa | Pago por invocacion |
| Complejidad | Mayor (endpoint, config, model) | Menor (funcion + URL) |

Para modelos pequeños como el de esta clase, Lambda es suficiente y mas simple de desplegar.

## Prerequisitos

- Cuenta AWS (sandbox de Pluralsight)
- Terraform instalado
- Python 3.10+ con boto3, scikit-learn, joblib

## Paso 0: Configurar credenciales de AWS

Cada estudiante debe abrir su sandbox de Pluralsight y obtener las credenciales (Access Key Id y Secret Access Key).

Ejecutar en la terminal:

```bash
export AWS_ACCESS_KEY_ID=<tu_access_key_id>
export AWS_SECRET_ACCESS_KEY=<tu_secret_access_key>
export AWS_DEFAULT_REGION=us-east-1
```

Reemplazar `<tu_access_key_id>` y `<tu_secret_access_key>` con los valores que aparecen en el sandbox.

Para verificar que las credenciales estan configuradas:

```bash
aws sts get-caller-identity
```

Si muestra tu Account ID, las credenciales estan correctas.

> **Nota:** Las credenciales del sandbox son temporales y expiran cuando el sandbox se apaga. Nunca subir credenciales al repositorio.

## Paso 1: Entrenar y empaquetar el modelo

Todos los comandos se ejecutan desde la carpeta `mlops/`:

```bash
cd aulas/clase7/mlops
python3 01_train_and_package.py
```

Esto entrena un modelo Random Forest para deteccion de fraude y genera `model_artifact/model.joblib`.

## Paso 2: Crear la infraestructura base con Terraform

```bash
terraform init
terraform apply -target=aws_s3_bucket.ml_bucket -target=aws_iam_role.lambda_role -target=aws_iam_role_policy_attachment.lambda_basic -target=aws_iam_role_policy_attachment.lambda_s3
```

Esto crea solo el bucket S3 y el rol IAM primero. Terraform pedira confirmacion, escribir `yes`.

Copiar el valor de `s3_bucket_name` del output, se necesita en el siguiente paso.

## Paso 3: Empaquetar Lambda y subir a S3

```bash
python3 02_upload_to_s3.py
```

Este script:
1. Instala las dependencias de sklearn para Linux (compatible con Lambda)
2. Empaqueta el handler + modelo + dependencias en un ZIP
3. Sube el ZIP a S3

Ingresar el nombre del bucket que Terraform mostro en el paso anterior.

## Paso 4: Crear la Lambda y el endpoint

```bash
terraform apply
```

Esto crea: Lambda Function -> Function URL (con autenticacion AWS).

Copiar el valor de `api_url` del output, es la URL del endpoint.

## Paso 5: Invocar el endpoint

```bash
python3 03_invoke_endpoint.py
```

Ingresar la URL del endpoint que Terraform mostro en el paso anterior.

## Desde Postman

La Function URL requiere autenticacion AWS Signature. Para invocar desde Postman:

1. Method: **POST**
2. URL: la `api_url` del output de Terraform
3. Pestaña **Authorization**:
   - Type: **AWS Signature**
   - Access Key: `<tu_access_key_id>`
   - Secret Key: `<tu_secret_access_key>`
   - Region: `us-east-1`
   - Service: `lambda`
4. Body > raw > JSON:

```json
{
    "monto": 3500.0,
    "hora": 2.0,
    "dia_semana": 6,
    "distancia_km": 200.0,
    "intentos_pin": 3,
    "transacciones_24h": 10
}
```

> **Nota:** El campo Service debe ser `lambda` (no `execute-api`).

## Limpiar recursos (IMPORTANTE)

```bash
terraform destroy
```

Esto elimina TODOS los recursos creados en AWS para evitar cobros. Escribir `yes` para confirmar.

> **Recordar:** El sandbox de Pluralsight se apaga automaticamente. Siempre ejecutar `terraform destroy` antes de que expire para mantener buenas practicas.

## Estructura de archivos

```
mlops/
├── main.tf                     # Infraestructura (Lambda + S3 + IAM)
├── lambda_function.py          # Handler de Lambda (inferencia)
├── 01_train_and_package.py     # Entrena modelo -> model.joblib
├── 02_upload_to_s3.py          # Empaqueta Lambda + sube a S3
├── 03_invoke_endpoint.py       # Consume el endpoint
└── README.md                   # Esta guia
```
