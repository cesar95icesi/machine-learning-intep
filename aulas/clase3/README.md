# Machine Learning aplicado a procesos empresariales -- Clase 3

Clasificacion binaria y metricas de evaluacion aplicadas a un problema real de abandono de clientes (churn).

## Contenido del repositorio

| Archivo | Descripcion |
|---------|-------------|
| `Clase3_Clasificacion_Metricas.ipynb` | Notebook con el laboratorio completo |
| `abandono_clientes.csv` | Dataset sintetico de 800 clientes |
| `generar_dataset.py` | Script que genera el dataset (para referencia) |
| `README.md` | Este archivo |

## Requisitos previos

- **Python 3.10 o superior** instalado en el sistema.
- **uv** como gestor de paquetes y entornos virtuales (ver instrucciones abajo).

## Instalacion de uv

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes y entornos virtuales para Python, extremadamente rapido. Reemplaza a `pip`, `venv` y `pip-tools` en un solo comando.

### Instalar uv

#### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Despues de instalar, cierra y vuelve a abrir la terminal para que el comando `uv` este disponible.

Para verificar que se instalo correctamente:

```bash
uv --version
```

### Comandos elementales de uv

| Comando | Que hace |
|---------|----------|
| `uv venv` | Crea un entorno virtual en `.venv/` usando la version de Python del proyecto |
| `uv sync` | Instala todas las dependencias definidas en `pyproject.toml` dentro del `.venv/` |
| `uv run <comando>` | Ejecuta un comando dentro del entorno virtual sin necesidad de activarlo manualmente |
| `uv add <paquete>` | Agrega una nueva dependencia al proyecto (actualiza `pyproject.toml` y `uv.lock`) |
| `uv remove <paquete>` | Elimina una dependencia del proyecto |
| `uv add -r requirements.txt` | Importa todas las dependencias de un `requirements.txt` al `pyproject.toml` |
| `uv lock` | Regenera el archivo `uv.lock` con las versiones exactas resueltas |

**Nota:** `uv run` activa automaticamente el entorno virtual antes de ejecutar el comando. No es necesario hacer `source .venv/bin/activate` manualmente, aunque tambien se puede.

## Instrucciones de ejecucion

### 1. Crear el entorno virtual e instalar dependencias

```bash
# Desde la raiz del proyecto
uv venv
uv sync
```

### 2. Ejecutar el notebook

```bash
uv run jupyter notebook aulas/clase3/Clase3_Clasificacion_Metricas.ipynb
```

### 3. (Alternativa) Activar el entorno manualmente

Si prefieres activar el entorno virtual de forma tradicional:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows CMD
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Una vez activado, puedes ejecutar comandos directamente sin `uv run`:

```bash
jupyter notebook aulas/clase3/Clase3_Clasificacion_Metricas.ipynb
```

Ejecuta las celdas en orden con **Shift + Enter**.

---

## Conceptos clave de esta clase

### 1. Clasificacion binaria

Un modelo de clasificacion binaria predice una de dos categorias posibles. A diferencia de la regresion (donde predecimos un numero como ventas = $383.72), aqui predecimos una etiqueta: SI o NO, 1 o 0.

Ejemplos:
- Este cliente abandonara el servicio? (SI / NO)
- Esta transaccion es fraude? (SI / NO)
- Este correo es spam? (SI / NO)

En este laboratorio, la pregunta es: **este cliente va a abandonar?**

### 2. Regresion Logistica

A pesar de su nombre, es un modelo de **clasificacion** (no de regresion). Funciona en tres pasos:

1. Calcula una puntuacion lineal combinando las variables de entrada (igual que regresion lineal).
2. Pasa esa puntuacion por una **funcion sigmoide** que la convierte en una probabilidad entre 0 y 1.
3. Si la probabilidad es mayor a 0.5, predice "abandona" (1). Si no, predice "permanece" (0).

Es el modelo mas simple de clasificacion y el punto de partida recomendado antes de probar modelos mas complejos.

### 3. Matriz de confusion

Es una tabla 2x2 que desglosa las predicciones del modelo en cuatro categorias:

```
                        PREDICCION DEL MODELO
                    |  Permanece (0)  |  Abandona (1)  |
  ---------------------------------------------------------
  REALIDAD  Perm(0) |  VN (acierto)   |  FP (error)    |
            Aban(1) |  FN (error)     |  VP (acierto)  |
  ---------------------------------------------------------
```

- **VN (Verdadero Negativo):** Dijo "permanece" y acerto.
- **VP (Verdadero Positivo):** Dijo "abandona" y acerto.
- **FP (Falso Positivo):** Dijo "abandona" pero el cliente se quedo. **Falsa alarma.**
- **FN (Falso Negativo):** Dijo "permanece" pero el cliente se fue. **No lo detecto.**

### 4. Metricas de evaluacion

#### Accuracy (exactitud)

```
Accuracy = (VP + VN) / Total
```

Que porcentaje de predicciones fueron correctas. Es intuitiva pero puede ser **enganosa** cuando las clases estan desbalanceadas. Si el 95% de clientes no abandona, un modelo que siempre diga "no abandona" tendria 95% de accuracy pero seria completamente inutil.

#### Precision

```
Precision = VP / (VP + FP)
```

De todos los clientes que el modelo dijo que abandonarian, cuantos **realmente** abandonaron?

- Precision alta = pocas falsas alarmas.
- Priorizar cuando el **Falso Positivo es costoso** (ejemplo: filtro de spam, donde marcar un correo importante como spam es grave).

#### Recall (sensibilidad)

```
Recall = VP / (VP + FN)
```

De todos los clientes que **realmente** abandonaron, cuantos logro detectar el modelo?

- Recall alto = detecta la mayoria de los casos positivos.
- Priorizar cuando el **Falso Negativo es costoso** (ejemplo: abandono de clientes, diagnostico medico, fraude).

#### F1-Score

```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

Promedio armonico entre Precision y Recall. Util cuando se quiere un solo numero que equilibre ambas metricas.

### 5. El costo del error

En problemas reales, **no todos los errores cuestan lo mismo.** La eleccion de la metrica depende del contexto de negocio:

| Escenario | Error mas costoso | Metrica a priorizar |
|-----------|-------------------|---------------------|
| Abandono de clientes | FN (no detectar al que se va) | Recall |
| Filtro de spam | FP (marcar correo importante como spam) | Precision |
| Diagnostico de enfermedad | FN (no detectar la enfermedad) | Recall |
| Aprobacion de credito | FP (aprobar a quien no puede pagar) | Precision |

En nuestro caso de abandono:
- **FP (falsa alarma):** Le ofrecemos un descuento a alguien que no lo necesitaba. Costo bajo (~$20).
- **FN (no detectado):** Perdemos al cliente sin hacer nada. Costo alto (~$500 en ingresos futuros).

Por eso, en este problema priorizamos el **Recall**: preferimos contactar a algunos clientes de mas (FP) antes que dejar escapar a uno que realmente se iba a ir (FN).

---

## Tabla resumen

| Metrica | Formula | Pregunta que responde | Cuando priorizarla |
|---------|---------|-----------------------|--------------------|
| Accuracy | (VP+VN)/Total | Que % de predicciones acerte? | Clases balanceadas |
| Precision | VP/(VP+FP) | De los que dije positivos, cuantos acerte? | FP es costoso |
| Recall | VP/(VP+FN) | De los positivos reales, cuantos detecte? | FN es costoso |
| F1-Score | 2*(P*R)/(P+R) | Balance entre Precision y Recall | Ambos importan |

## Dataset

El archivo `abandono_clientes.csv` contiene 800 clientes sinteticos con las siguientes variables:

| Variable | Descripcion | Tipo | Rango |
|----------|-------------|------|-------|
| antiguedad_meses | Meses como cliente | Numerica | 1 a 72 |
| factura_mensual | Valor mensual del plan en dolares | Numerica | 20 a 120 |
| llamadas_soporte | Llamadas al soporte tecnico | Numerica | 0 a 10 |
| contrato | Tipo de contrato | Categorica | Mensual, Anual, Dos_anios |
| satisfaccion | Nivel de satisfaccion | Numerica | 1 a 5 |
| **abandono** | **Variable objetivo** | **Binaria** | **0 = permanece, 1 = abandona** |

La distribucion de la variable objetivo es aproximadamente 65% permanece / 35% abandona, lo cual refleja un desbalanceo moderado similar a escenarios reales.

## Tecnologias utilizadas

- Python 3.10+
- pandas
- numpy
- scikit-learn
- matplotlib
- Jupyter Notebook
