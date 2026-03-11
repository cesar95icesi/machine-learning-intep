# Machine Learning aplicado a procesos empresariales — Clase 2

Primer modelo de **Regresión Lineal** para predicción de ventas usando Python y scikit-learn.

## Contenido del repositorio

| Archivo | Descripción |
|---------|-------------|
| `Clase2_ML_Primer_Modelo_Regresion.ipynb` | Notebook con el laboratorio completo |
| `ventas_ml_clase2.csv` | Dataset sintético de ventas |
| `requirements.txt` | Dependencias de Python necesarias |

## Requisitos previos

- **Python 3.10 o superior** instalado en el sistema.
- **pip** (incluido con Python).
- **Git** (opcional, para clonar el repositorio).

## Instrucciones de instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd machine-learning-intep
```

### 2. Crear un entorno virtual de Python

#### En macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### En Windows (CMD)

```bash
python -m venv venv
venv\Scripts\activate
```

#### En Windows (PowerShell)

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

> Una vez activado, el prompt de la terminal mostrará `(venv)` al inicio.

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el notebook

```bash
jupyter notebook Clase2_ML_Primer_Modelo_Regresion.ipynb
```

Esto abrirá el navegador con Jupyter. Ejecuta las celdas en orden con **Shift + Enter**.

### 5. Desactivar el entorno virtual (al terminar)

```bash
deactivate
```

## Descripcion del laboratorio

1. **Exploración de datos (EDA):** carga y análisis del dataset de ventas.
2. **Definición del problema:** predicción de ventas a partir de marketing, precio, temporada, tienda y canal.
3. **Pipeline de preprocesamiento:** One-Hot Encoding para variables categóricas.
4. **Entrenamiento:** Regresión Lineal con scikit-learn.
5. **Evaluación:** métricas MAE, RMSE y R².
6. **Interpretación:** coeficientes del modelo y análisis de variables de mayor impacto.
7. **Simulación What-if:** escenario de aumento de inversión en marketing.

## Configuración del entorno de desarrollo con Git

### Notebooks y control de versiones (nbstripout)

Este repositorio usa [`nbstripout`](https://github.com/kynan/nbstripout) para evitar que los metadatos volátiles de los notebooks (outputs de celdas, contadores de ejecución, kernelspec, etc.) generen cambios falsos en git.

**Cada colaborador debe ejecutar este comando una sola vez después de clonar el repositorio:**

```bash
pip install nbstripout
nbstripout --install
```

Sin este paso, `git status` mostrará los notebooks como modificados aunque no hayas cambiado el código, y los `git pull` fallarán con conflictos.

> El archivo `.gitattributes` ya está configurado en el repositorio. Solo necesitas instalar el filtro localmente.

## Tecnologías utilizadas

- Python 3.10+
- pandas
- numpy
- scikit-learn
- Jupyter Notebook
- nbstripout
