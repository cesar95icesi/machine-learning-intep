# Clase 7 - Reconocimiento de Emociones Faciales con Webcam

Programa que detecta emociones faciales en tiempo real usando la cámara web y un modelo de Machine Learning entrenado con **scikit-learn**.

## Arquitectura del Modelo

```
FER2013 (48x48 px, escala de grises)
        │
        ▼
  Normalización (/255)
        │
        ▼
  PCA (2304 → 150 componentes)    ← Reducción de dimensionalidad
        │
        ▼
  SVM (kernel RBF, C=10)          ← Clasificador
        │
        ▼
  7 emociones predichas
```

### Pipeline en tiempo real

```
Webcam → Frame → Escala de grises → Haar Cascade (detección de rostro)
                                          │
                                          ▼
                                   Recortar rostro → Resize 48x48 → Flatten → Modelo → Emoción
```

## Modelo utilizado

| Componente | Detalle |
|---|---|
| **Reducción dimensional** | PCA con 150 componentes y whitening (~95% varianza retenida) |
| **Clasificador** | SVM con kernel RBF (C=10, gamma=scale) |
| **Framework** | scikit-learn (sklearn) |
| **Detección de rostros** | OpenCV Haar Cascade (`haarcascade_frontalface_default.xml`) |
| **Accuracy esperado** | ~60-65% en 7 clases |

### Emociones detectadas

| ID | Emocion | Color en pantalla |
|---|---|---|
| 0 | Enojado | Rojo |
| 1 | Asco | Oliva |
| 2 | Miedo | Purpura |
| 3 | Feliz | Verde |
| 4 | Triste | Azul claro |
| 5 | Sorpresa | Amarillo |
| 6 | Neutral | Gris |

## Dataset

**FER2013** (Facial Expression Recognition 2013):
- ~35,000 imagenes en escala de grises de 48x48 pixeles
- 7 categorias de emociones
- Formato: carpetas `train/` y `test/` con subcarpetas por emocion (angry, disgust, fear, happy, sad, surprise, neutral)
- Descarga: [Kaggle - FER2013](https://www.kaggle.com/datasets/msambare/fer2013)

## Prerequisitos

- Python 3.10+
- Webcam funcional
- Dependencias del proyecto (sklearn, numpy, pandas, matplotlib)
- opencv-python

## Paso a paso

### 1. Descargar el dataset

Descargar el dataset FER2013 desde Kaggle y extraer la carpeta `archive/` en esta carpeta:

```
camera-smile/
  └── archive/
      ├── train/
      │   ├── angry/
      │   ├── disgust/
      │   ├── fear/
      │   ├── happy/
      │   ├── sad/
      │   ├── surprise/
      │   └── neutral/
      └── test/
          └── (mismas subcarpetas)
```

> **Nota:** La carpeta `archive/` no se sube al repositorio (.gitignore).

### 2. Instalar dependencias

Con uv (recomendado):
```bash
uv sync
```

O con pip:
```bash
pip install opencv-python
```

### 3. Entrenar el modelo

```bash
python3 train_model.py
```

Esto genera dos archivos de salida:

- **`modelo_emociones.joblib`** — Contiene el pipeline completo entrenado (PCA + SVM). Este archivo guarda los componentes principales aprendidos por PCA y los vectores de soporte del SVM, es decir, todo lo que el modelo "aprendio" del dataset. Es el archivo que se carga en `camera_emotion.py` para hacer predicciones en tiempo real.

- **`etiquetas.joblib`** — Contiene el diccionario que mapea los indices numericos (0-6) a los nombres de las emociones en español (Enojado, Asco, Miedo, Feliz, Triste, Sorpresa, Neutral). Se usa para traducir la prediccion numerica del modelo a texto legible.

#### Que es el formato `.joblib`?

**joblib** es una libreria de Python (incluida con scikit-learn) que permite serializar (guardar en disco) objetos de Python de forma eficiente, especialmente arrays de NumPy y modelos de ML. Es el formato recomendado por scikit-learn para persistir modelos entrenados porque:

- Es mas rapido que `pickle` para objetos con arrays grandes
- Comprime los datos automaticamente
- Permite cargar el modelo en cualquier momento sin necesidad de re-entrenar

El entrenamiento tarda aproximadamente 2-5 minutos.

### 4. Ejecutar la camara

```bash
python3 camera_emotion.py
```

- Se abre una ventana con el video de la camara
- Los rostros detectados muestran la emocion predicha y su confianza
- Barras de probabilidad muestran la distribucion de todas las emociones
- Presionar **q** para salir

## Estructura de archivos

```
camera-smile/
├── train_model.py          # Entrena PCA + SVM con FER2013
├── camera_emotion.py       # Camara con prediccion en vivo
├── README.md               # Esta guia
├── .gitignore              # Excluye imagenes y modelos generados
├── archive/                # (descargar) carpeta con train/ y test/
├── modelo_emociones.joblib # (generado) modelo entrenado
└── etiquetas.joblib        # (generado) mapeo de etiquetas
```

## Conceptos de ML aplicados

- **PCA (Analisis de Componentes Principales):** Reduce las 2304 dimensiones (pixeles) a 150 componentes principales, eliminando ruido y acelerando el entrenamiento.
- **SVM (Maquina de Vectores de Soporte):** Encuentra hiperplanos optimos en un espacio de alta dimension para separar las 7 clases de emociones. El kernel RBF permite fronteras de decision no lineales.
- **Pipeline:** Encadena PCA + SVM en un solo objeto, asegurando que el preprocesamiento sea consistente entre entrenamiento e inferencia.
- **Haar Cascade:** Algoritmo clasico de vision por computador para deteccion rapida de rostros basado en caracteristicas tipo Haar.

## Posibles mejoras al modelo

| Mejora | Accuracy estimado | Tiempo de entrenamiento |
|---|---|---|
| Actual (PCA + SVM) | ~60-65% | 2-5 min |
| + HOG features | ~65-70% | 3-5 min |
| + GridSearchCV | ~68-72% | 15-30 min |
| + Augmentation + Ensemble | ~70-75% | 20-40 min |

- **HOG (Histogram of Oriented Gradients):** En lugar de usar pixeles raw, extrae patrones de bordes y gradientes del rostro, que son mas informativos para distinguir expresiones faciales.
- **GridSearchCV:** Busca automaticamente los mejores valores de hiperparametros (C, gamma, n_components) en lugar de usar valores fijos.
- **Data Augmentation:** Voltear las imagenes horizontalmente para duplicar los datos de entrenamiento. Mas datos = mejor generalizacion.
- **Ensemble (VotingClassifier):** Combina SVM + Random Forest + KNN mediante votacion. Cada modelo tiene fortalezas distintas y la votacion conjunta mejora la prediccion.

## Notas para macOS

Si la camara no se abre, verificar que Python/Terminal tenga permisos de camara en:
**Configuracion del Sistema > Privacidad y Seguridad > Camara**
