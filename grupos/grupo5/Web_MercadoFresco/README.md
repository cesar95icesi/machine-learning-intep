# MercadoFresco – Predictor de Conversión
## App Streamlit con Random Forest

---

## Archivos necesarios en la misma carpeta

```
app.py                          ← app principal
caso5_campana_marketing.csv     ← dataset original
requirements.txt                ← dependencias
```

---

## Instalación y ejecución (3 pasos)

### Paso 1 — Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 2 — Ejecutar la app
```bash
streamlit run app.py
```

### Paso 3 — Abrir en el navegador
Se abre automáticamente en:
```
http://localhost:8501
```

---

## ¿Qué incluye la app?

| Sección | Descripción |
|---|---|
| Panel lateral | Sliders y selectbox para configurar el perfil del cliente y la campaña |
| Predicción | Resultado visual (✓ COMPRARÍA / ✗ NO COMPRARÍA) con probabilidad y barra de progreso |
| Tips contextuales | Alertas inteligentes según el perfil ingresado |
| Feature Importance | Gráfica de barras con las variables más importantes del modelo |
| Curva ROC | Visualización del AUC-ROC en el conjunto de test |
| Heatmap Canal × Hora | Tasa de conversión histórica por combinación |
| Simulador de segmento | Predice 10 clientes aleatorios con la campaña configurada |

---

## Publicar en la nube (gratis)

1. Crea cuenta en [streamlit.io](https://streamlit.io)
2. Sube los archivos a un repositorio de GitHub
3. En Streamlit Cloud: **New app → selecciona el repo → Deploy**
4. Obtienes un link público para compartir

---

## Notas técnicas

- El modelo se entrena automáticamente al iniciar la app (usa `@st.cache_resource` para no re-entrenarlo en cada interacción)
- Split 80/20 estratificado, `random_state=42` para reproducibilidad
- `class_weight='balanced'` para compensar el desbalance 66%/34%
