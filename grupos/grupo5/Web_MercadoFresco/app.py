"""
╔══════════════════════════════════════════════════════╗
║  MercadoFresco – Predictor de Conversión             ║
║  Modelo: Random Forest Classifier                    ║
║  Ejecutar: streamlit run app.py                      ║
╚══════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

# ── CONFIGURACIÓN DE PÁGINA ───────────────────────────────────
st.set_page_config(
    page_title="MercadoFresco – Predictor",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ESTILOS CUSTOM ────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-val { font-size: 2rem; font-weight: 700; margin: 0; }
    .metric-lbl { font-size: 0.78rem; color: #64748B; margin: 0; text-transform: uppercase; letter-spacing: .04em; }
    .pred-box {
        border-radius: 14px;
        padding: 1.8rem;
        text-align: center;
        margin: 1rem 0;
    }
    .pred-compra  { background: #DCFCE7; border: 2px solid #16A34A; }
    .pred-nocompra{ background: #FEE2E2; border: 2px solid #DC2626; }
    .pred-titulo  { font-size: 1.6rem; font-weight: 800; margin: 0; }
    .pred-prob    { font-size: 1rem; margin: 0.4rem 0 0; color: #374151; }
    .tip-box {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        font-size: 0.87rem;
        color: #1E40AF;
        margin: 0.5rem 0;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        border-bottom: 2px solid #0D9488;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }
    .stSlider > div > div > div { background: #0D9488 !important; }
</style>
""", unsafe_allow_html=True)


# ── CARGA Y ENTRENAMIENTO DEL MODELO ─────────────────────────
@st.cache_resource(show_spinner="Cargando modelo Random Forest...")
def cargar_modelo():
    """Entrena el modelo directamente desde el CSV."""
    try:
        df = pd.read_csv("caso5_campana_marketing.csv")
    except FileNotFoundError:
        st.error("❌ No se encontró 'caso5_campana_marketing.csv'. "
                 "Asegúrate de que esté en la misma carpeta que app.py")
        st.stop()

    df_model = df.copy()
    cat_cols = ["genero", "rango_ingreso", "canal_marketing",
                "dia_envio", "hora_envio", "categoria_producto"]
    encoders = {}
    mappings = {}
    for col in cat_cols:
        le = LabelEncoder()
        df_model[col] = le.fit_transform(df_model[col])
        encoders[col] = le
        mappings[col] = list(le.classes_)

    X = df_model.drop("realizo_compra", axis=1)
    y = df_model["realizo_compra"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_split=10,
        min_samples_leaf=5, class_weight="balanced",
        random_state=42, n_jobs=-1
    )
    modelo.fit(X_train, y_train)

    feat_imp = pd.Series(modelo.feature_importances_, index=X.columns)
    auc = roc_auc_score(y_test, modelo.predict_proba(X_test)[:, 1])

    return modelo, encoders, mappings, X_test, y_test, feat_imp, auc, X.columns.tolist()


modelo, encoders, mappings, X_test, y_test, feat_imp, auc_score, feature_cols = cargar_modelo()


# ── SIDEBAR – PERFIL DEL CLIENTE ─────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 MercadoFresco")
    st.markdown("**Predictor de conversión**")
    st.markdown("---")
    st.markdown("### Perfil del cliente")

    edad = st.slider("Edad del cliente", 18, 64, 35)
    genero = st.selectbox("Género", mappings["genero"])
    rango_ingreso = st.selectbox("Rango de ingreso", mappings["rango_ingreso"])
    compras_previas = st.slider("Compras previas", 0, 30, 10)
    dias_inactivo = st.slider("Días inactivo", 0, 180, 45)

    st.markdown("---")
    st.markdown("### Configuración de campaña")

    canal = st.selectbox("Canal de marketing", mappings["canal_marketing"])
    dia_envio = st.selectbox("Día de envío", mappings["dia_envio"])
    hora_envio = st.selectbox("Hora de envío", mappings["hora_envio"])
    descuento = st.slider("Descuento ofrecido (%)", 0, 30, 10)
    categoria = st.selectbox("Categoría del producto", mappings["categoria_producto"])

    st.markdown("---")
    predecir_btn = st.button("🔮 Predecir conversión", use_container_width=True, type="primary")


# ── FUNCIÓN DE PREDICCIÓN ─────────────────────────────────────
def hacer_prediccion():
    entrada = {
        "edad_cliente": edad,
        "genero": encoders["genero"].transform([genero])[0],
        "rango_ingreso": encoders["rango_ingreso"].transform([rango_ingreso])[0],
        "canal_marketing": encoders["canal_marketing"].transform([canal])[0],
        "dia_envio": encoders["dia_envio"].transform([dia_envio])[0],
        "hora_envio": encoders["hora_envio"].transform([hora_envio])[0],
        "compras_previas": compras_previas,
        "dias_inactivo": dias_inactivo,
        "descuento_porcentaje": descuento,
        "categoria_producto": encoders["categoria_producto"].transform([categoria])[0],
    }
    X_pred = pd.DataFrame([entrada])[feature_cols]
    prob = modelo.predict_proba(X_pred)[0][1]
    pred = int(prob >= 0.5)
    return prob, pred, X_pred


# ── CABECERA PRINCIPAL ────────────────────────────────────────
st.markdown("# 🛒 MercadoFresco – Predictor de Conversión")
st.markdown(
    "Modelo **Random Forest** entrenado con 700 registros reales. "
    "Ajusta el perfil del cliente en el panel izquierdo y presiona **Predecir conversión**."
)
st.markdown("---")

# ── MÉTRICAS GLOBALES DEL MODELO ─────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metricas = [
    (c1, f"{auc_score:.3f}", "AUC-ROC", "#0D9488"),
    (c2, "700",              "Registros",  "#3B82F6"),
    (c3, "200",              "Árboles RF", "#8B5CF6"),
    (c4, "33.6%",            "Tasa conversión dataset", "#F59E0B"),
]
for col, val, lbl, color in metricas:
    col.markdown(
        f'<div class="metric-card">'
        f'<p class="metric-val" style="color:{color}">{val}</p>'
        f'<p class="metric-lbl">{lbl}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── RESULTADO DE PREDICCIÓN ───────────────────────────────────
col_pred, col_gauge = st.columns([1, 1])

with col_pred:
    st.markdown('<p class="section-title">Resultado de la predicción</p>', unsafe_allow_html=True)

    if predecir_btn or True:   # muestra resultado por defecto
        prob, pred, X_pred = hacer_prediccion()
        pct = round(prob * 100, 1)

        if pred == 1:
            st.markdown(
                f'<div class="pred-box pred-compra">'
                f'<p class="pred-titulo" style="color:#15803D">✓ COMPRARÍA</p>'
                f'<p class="pred-prob">Probabilidad de compra: <strong>{pct}%</strong></p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="pred-box pred-nocompra">'
                f'<p class="pred-titulo" style="color:#B91C1C">✗ NO COMPRARÍA</p>'
                f'<p class="pred-prob">Probabilidad de compra: <strong>{pct}%</strong></p>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Barra de probabilidad
        st.markdown("**Probabilidad de compra**")
        prog_color = "#16A34A" if pred == 1 else "#DC2626"
        st.markdown(
            f"""
            <div style="background:#E2E8F0;border-radius:8px;height:22px;width:100%;overflow:hidden;">
              <div style="background:{prog_color};width:{pct}%;height:100%;border-radius:8px;
                          display:flex;align-items:center;justify-content:flex-end;
                          padding-right:8px;color:white;font-size:12px;font-weight:700;">
                {pct}%
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tips contextuales
        st.markdown("<br>", unsafe_allow_html=True)
        if dias_inactivo > 90:
            st.markdown(
                '<div class="tip-box">⚠️ Cliente con más de 90 días inactivo — '
                'considera una campaña de reactivación antes del envío estándar.</div>',
                unsafe_allow_html=True
            )
        if canal == "Email" and hora_envio == "Noche":
            st.markdown(
                '<div class="tip-box" style="background:#F0FDF4;border-color:#16A34A;color:#15803D">'
                '★ Combinación óptima: Email + Noche tiene 48.8% de conversión histórica.</div>',
                unsafe_allow_html=True
            )
        if descuento == 0 and compras_previas < 5:
            st.markdown(
                '<div class="tip-box" style="background:#FFFBEB;border-color:#D97706;color:#92400E">'
                '💡 Cliente nuevo sin descuento — un incentivo del 15–20% puede triplicar la conversión.</div>',
                unsafe_allow_html=True
            )

with col_gauge:
    st.markdown('<p class="section-title">Perfil ingresado</p>', unsafe_allow_html=True)

    perfil_data = {
        "Variable": ["Edad", "Género", "Ingreso", "Canal", "Día envío",
                     "Hora envío", "Compras previas", "Días inactivo",
                     "Descuento", "Categoría"],
        "Valor": [f"{edad} años", genero, rango_ingreso, canal, dia_envio,
                  hora_envio, str(compras_previas), f"{dias_inactivo} días",
                  f"{descuento}%", categoria],
    }
    st.dataframe(
        pd.DataFrame(perfil_data),
        use_container_width=True,
        hide_index=True,
        height=370
    )

st.markdown("---")

# ── VISUALIZACIONES ───────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Feature Importance", "📈 Curva ROC", "🔥 Heatmap Canal × Hora"])

# TAB 1 – FEATURE IMPORTANCE
with tab1:
    st.markdown("#### Importancia de variables del modelo")
    st.caption("Indica cuánto contribuye cada variable a la predicción. "
               "Barras verdes = top 3 más importantes.")

    fig, ax = plt.subplots(figsize=(9, 4))
    fi_sorted = feat_imp.sort_values(ascending=True)
    colors = ["#0D9488" if v >= fi_sorted.nlargest(3).min() else "#CBD5E1"
              for v in fi_sorted.values]
    bars = ax.barh(fi_sorted.index, fi_sorted.values * 100,
                   color=colors, edgecolor="white", height=0.65)
    for bar, val in zip(bars, fi_sorted.values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val*100:.1f}%", va="center", fontsize=9, color="#374151")
    ax.set_xlabel("Importancia (%)", fontsize=10)
    ax.set_xlim(0, fi_sorted.max() * 100 * 1.22)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# TAB 2 – CURVA ROC
with tab2:
    st.markdown("#### Curva ROC del modelo en test set")
    st.caption(f"AUC = {auc_score:.3f}. Cuanto más arriba a la izquierda, mejor el modelo.")

    y_prob_test = modelo.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob_test)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.plot(fpr, tpr, color="#0D9488", lw=2.5, label=f"Random Forest (AUC = {auc_score:.3f})")
    ax.fill_between(fpr, tpr, alpha=0.08, color="#0D9488")
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Clasificador aleatorio (AUC = 0.5)")
    ax.set_xlabel("Tasa de Falsos Positivos", fontsize=10)
    ax.set_ylabel("Tasa de Verdaderos Positivos", fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# TAB 3 – HEATMAP CANAL × HORA
with tab3:
    st.markdown("#### Tasa de conversión real: canal × hora de envío (%)")
    st.caption("Combinaciones con mayor conversión en el dataset histórico.")

    try:
        df_raw = pd.read_csv("caso5_campana_marketing.csv")
        pivot = df_raw.pivot_table(
            values="realizo_compra", index="canal_marketing",
            columns="hora_envio", aggfunc="mean"
        ) * 100
        orden_hora = [h for h in ["Manana", "Mediodia", "Tarde", "Noche"] if h in pivot.columns]
        pivot = pivot.reindex(columns=orden_hora)

        fig, ax = plt.subplots(figsize=(7, 3.5))
        im = ax.imshow(pivot.values, cmap="YlGn", aspect="auto", vmin=20, vmax=55)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_yticks(range(len(pivot.index)))
        ax.set_xticklabels(pivot.columns, fontsize=10)
        ax.set_yticklabels(pivot.index, fontsize=10)
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                color = "white" if val > 42 else "#1E293B"
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                        fontsize=11, fontweight="bold", color=color)
        plt.colorbar(im, ax=ax, label="% conversión")
        ax.set_facecolor("white"); fig.patch.set_facecolor("white")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    except Exception as e:
        st.info("Carga el CSV para ver el heatmap.")

st.markdown("---")

# ── SIMULADOR DE SEGMENTO ─────────────────────────────────────
st.markdown("### 🎯 Simulador de segmento")
st.caption("Simula 10 clientes aleatorios y ve cuántos convertirían con la configuración actual de campaña.")

if st.button("Simular 10 clientes aleatorios"):
    try:
        df_raw = pd.read_csv("caso5_campana_marketing.csv")
        muestra = df_raw.sample(10, random_state=np.random.randint(0, 999)).copy()

        # aplica la campaña actual a los 10 clientes
        muestra["canal_marketing"] = canal
        muestra["hora_envio"] = hora_envio
        muestra["dia_envio"] = dia_envio
        muestra["descuento_porcentaje"] = descuento
        muestra["categoria_producto"] = categoria

        df_enc = muestra.copy()
        for col in ["genero","rango_ingreso","canal_marketing","dia_envio","hora_envio","categoria_producto"]:
            df_enc[col] = encoders[col].transform(df_enc[col])

        X_sim = df_enc[feature_cols]
        probs = modelo.predict_proba(X_sim)[:, 1]
        preds = (probs >= 0.5).astype(int)

        resultado = muestra[["edad_cliente","genero","compras_previas","dias_inactivo"]].copy()
        resultado["Prob. compra"] = [f"{p*100:.1f}%" for p in probs]
        resultado["Predicción"] = ["✅ Compraría" if p == 1 else "❌ No compraría" for p in preds]
        resultado.columns = ["Edad","Género","Compras prev.","Días inactivo","Prob. compra","Predicción"]

        st.dataframe(resultado, use_container_width=True, hide_index=True)

        convertidores = preds.sum()
        col_a, col_b = st.columns(2)
        col_a.metric("Clientes que convertirían", f"{convertidores} / 10")
        col_b.metric("Tasa de conversión estimada", f"{convertidores*10}%")
    except Exception as e:
        st.error(f"Error en simulación: {e}")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94A3B8;font-size:0.8rem;'>"
    "MercadoFresco · Caso 5 · Ciencia de Datos · Random Forest Classifier"
    "</p>",
    unsafe_allow_html=True
)
