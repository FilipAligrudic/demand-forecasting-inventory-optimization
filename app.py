"""
Demand Forecasting & Inventory Optimization — Streamlit dashboard.

Pokretanje:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Omogući import iz src/
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.data_processing import (
    basic_summary,
    filter_series,
    load_sales_csv,
)  # noqa: E402
from src.feature_engineering import build_features  # noqa: E402
from src.forecasting import (  # noqa: E402
    baseline_moving_average,
    ensemble_forecast,
    evaluate_on_backtest,
    holt_winters_forecast,
    prophet_forecast,
    recursive_forecast_lgbm,
    rolling_origin_backtest,
    seasonal_naive_forecast,
    train_lightgbm,
)
from src.inventory_optimization import (  # noqa: E402
    InventoryParams,
    recommend_order,
    sensitivity_table,
)
from src.anomaly_detection import detect as detect_anomalies  # noqa: E402
from src.explainability import (  # noqa: E402
    explain_row,
    global_importance,
    humanize_feature,
)
from src.order_generator import (  # noqa: E402
    build_purchase_order,
    save_to_outputs,
    to_csv_bytes,
    to_excel_bytes,
)

# ============================================================================
# Page setup
# ============================================================================

st.set_page_config(
    page_title="Demand Forecasting & Inventory Optimization",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Paleta
PRIMARY = "#2563eb"
ACCENT = "#0ea5e9"
GOOD = "#16a34a"
WARN = "#d97706"
DANGER = "#dc2626"
MUTED = "#64748b"

CUSTOM_CSS = f"""
<style>
    .block-container {{padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Hero header */
    .hero {{
        background: linear-gradient(110deg, {PRIMARY} 0%, {ACCENT} 100%);
        color: #ffffff; padding: 20px 26px; border-radius: 16px; margin-bottom: 14px;
        box-shadow: 0 8px 24px rgba(37,99,235,0.18);
    }}
    .hero h1 {{color:#fff; font-size: 1.7rem; margin:0 0 4px 0; font-weight: 700;}}
    .hero p {{color: rgba(255,255,255,0.92); margin:0; font-size: 0.95rem;}}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background: #ffffff; padding: 16px 18px; border-radius: 14px;
        border: 1px solid #e6ebf2; box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }}
    div[data-testid="stMetric"] label {{color: {MUTED}; font-weight: 600;}}
    div[data-testid="stMetricValue"] {{color: {PRIMARY}; font-weight: 700;}}

    h2, h3 {{color: #0f1f33;}}
    section[data-testid="stSidebar"] {{background: #f7f9fc; border-right: 1px solid #e6ebf2;}}
    section[data-testid="stSidebar"] h2 {{font-size: 0.78rem; text-transform: uppercase;
        letter-spacing: 0.06em; color: {MUTED};}}

    /* Sidebar radio kao navigacija */
    div[role="radiogroup"] label {{padding: 2px 0;}}

    .pill {{display:inline-block; padding: 3px 10px; border-radius: 999px;
        font-size: 0.78rem; font-weight: 600; margin-right: 6px;}}
    .pill-good {{background:#dcfce7; color:{GOOD};}}
    .pill-warn {{background:#fef3c7; color:{WARN};}}
    .pill-info {{background:#e0f2fe; color:{ACCENT};}}
    .small-note {{color:{MUTED}; font-size:0.85rem;}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1>📦 Demand Forecasting &amp; Inventory Optimization</h1>
        <p>Predikcija potražnje · EOQ optimizacija zaliha · SHAP objašnjenja · automatska narudžbenica — alat za supply chain tim.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Streamlit width API shim: novije verzije (>=1.43) traže width="stretch",
# starije koriste use_container_width=True (koji se uklanja u budućnosti).
# Ovo radi čisto na obje strane — bez crash-a i bez deprecation spam-a.
_ST_VER = tuple(int(x) for x in (st.__version__.split(".") + ["0", "0"])[:2])
_NEW_WIDTH = _ST_VER >= (1, 43)


def pchart(fig, **kwargs):
    """st.plotly_chart preko cijele širine, kompatibilno kroz Streamlit verzije."""
    if _NEW_WIDTH:
        st.plotly_chart(fig, width="stretch", **kwargs)
    else:
        st.plotly_chart(fig, use_container_width=True, **kwargs)


def pdf(data, **kwargs):
    """st.dataframe preko cijele širine, kompatibilno kroz Streamlit verzije."""
    if _NEW_WIDTH:
        st.dataframe(data, width="stretch", **kwargs)
    else:
        st.dataframe(data, use_container_width=True, **kwargs)


def render_overview(df: pd.DataFrame, summary: dict) -> None:
    """Landing prikaz — koristi samo dataset (bez treniranja modela), pa je trenutan."""
    st.subheader("Pregled dataset-a i poslovni kontekst")

    date_min = pd.to_datetime(summary["date_min"]).strftime("%d.%m.%Y")
    date_max = pd.to_datetime(summary["date_max"]).strftime("%d.%m.%Y")

    def kpi_card(label: str, value: str, value_size: str = "1.65rem") -> None:
        st.markdown(
            f"""
            <div style="
                background: #ffffff;
                padding: 16px 18px;
                border-radius: 14px;
                border: 1px solid #e6ebf2;
                box-shadow: 0 2px 8px rgba(15,23,42,0.04);
                min-height: 104px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="
                    color: #64748b;
                    font-weight: 600;
                    font-size: 0.85rem;
                    margin-bottom: 8px;
                ">
                    {label}
                </div>
                <div style="
                    color: #2563eb;
                    font-weight: 700;
                    font-size: {value_size};
                    line-height: 1.15;
                    white-space: nowrap;
                ">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    o1, o2, o3, o4 = st.columns(4)

    with o1:
        kpi_card("Ukupna prodaja", f"{summary['total_sales']:,.0f}")

    with o2:
        kpi_card(
            "Prodavnice × proizvodi",
            f"{summary['n_stores']} × {summary['n_products']}",
        )

    with o3:
        kpi_card("Period", f"{date_min} – {date_max}", value_size="1.15rem")

    with o4:
        kpi_card("Dnevnih zapisa", f"{summary['rows']:,}")

    st.markdown("#### Ukupna dnevna prodaja (svi proizvodi i prodavnice)")
    daily_total = df.groupby("Date", as_index=False)["Sales"].sum()
    fig_tot = go.Figure()
    fig_tot.add_trace(
        go.Scatter(
            x=daily_total["Date"],
            y=daily_total["Sales"],
            mode="lines",
            line=dict(color=PRIMARY),
            name="Ukupna prodaja",
        )
    )
    fig_tot.add_trace(
        go.Scatter(
            x=daily_total["Date"],
            y=daily_total["Sales"].rolling(30, min_periods=7).mean(),
            mode="lines",
            line=dict(color=DANGER, dash="dash"),
            name="30-dnevni prosjek",
        )
    )
    fig_tot.update_layout(
        height=320,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.2),
    )
    pchart(fig_tot)

    cL, cR = st.columns(2)
    with cL:
        st.markdown("#### Top proizvodi po prodaji")
        top_p = (
            df.groupby("Product", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=True)
        )
        fig_p = go.Figure(
            go.Bar(
                x=top_p["Sales"],
                y=top_p["Product"],
                orientation="h",
                marker=dict(color=ACCENT),
            )
        )
        fig_p.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        pchart(fig_p)

    with cR:
        st.markdown("#### Prodaja po prodavnici")
        top_s = (
            df.groupby("Store", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=True)
        )
        fig_s2 = go.Figure(
            go.Bar(
                x=top_s["Sales"],
                y=top_s["Store"],
                orientation="h",
                marker=dict(color=PRIMARY),
            )
        )
        fig_s2.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        pchart(fig_s2)

    st.markdown("#### Kako koristiti alat")
    st.markdown(
        """
        1. **Odaberi seriju** (prodavnica + proizvod) i **horizont** u sidebaru.
        2. **📈 Forecast** — vidi predikciju potražnje sa intervalom pouzdanosti.
        3. **📦 Optimizacija zaliha** — EOQ, safety stock i preporuka narudžbe za izabrane parametre.
        4. **🎯 Evaluacija** — uporedi modele (backtest na zadnjih 28 dana).
        5. **🧾 Narudžbenica** — generiši preporuke za **sve** parove i izvezi u Excel/CSV.
        6. **What-if** (sidebar) — simuliraj promociju, promjenu cijene ili duži lead time.
        """
    )

def render_footer() -> None:
    st.markdown("---")
    st.caption(
        "ISZPO 2026 · Demand Forecasting & Inventory Optimization · "
        "Hibridni model (LightGBM + Holt-Winters) · EOQ / Safety stock / ROP · SHAP · Streamlit"
    )


def resample_weekly(dates, values, how: str = "sum"):
    """Agregiraj dnevne vrijednosti na sedmične (W-MON). Vraća (x, y)."""
    s = pd.Series(
        pd.to_numeric(pd.Series(values), errors="coerce").values,
        index=pd.to_datetime(pd.Series(dates).values),
    )
    r = s.resample("W-MON").mean() if how == "mean" else s.resample("W-MON").sum()
    return r.index, r.values


# ============================================================================
# Sidebar — navigacija, podaci, parametri
# ============================================================================

VIEWS = {
    "🏠 Pregled": "overview",
    "📈 Forecast": "forecast",
    "📦 Optimizacija zaliha": "inventory",
    "🚨 Anomalije": "anomaly",
    "🔍 Objašnjenja (SHAP)": "shap",
    "🧾 Narudžbenica": "orders",
    "🎯 Evaluacija modela": "eval",
}

st.sidebar.header("Navigacija")
view_label = st.sidebar.radio(
    "Prikaz", list(VIEWS.keys()), label_visibility="collapsed"
)
view = VIEWS[view_label]

st.sidebar.markdown("---")
st.sidebar.header("Podaci")
uploaded = st.sidebar.file_uploader("Učitaj CSV sa prodajom", type=["csv"])

DATA_PATH = ROOT / "data" / "rossmann_demo_30.csv"


@st.cache_data(show_spinner=False)
def load_default() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            "Nije pronađen data/rossmann_demo_30.csv. Ubaci Rossmann demo dataset sa 30 prodavnica u data folder."
        )
        st.stop()
    return load_sales_csv(DATA_PATH)


@st.cache_data(show_spinner=False)
def load_uploaded(buf) -> pd.DataFrame:
    return load_sales_csv(buf)


if uploaded is not None:
    try:
        df = load_uploaded(uploaded)
        st.sidebar.success(f"CSV učitan · {len(df):,} redova")
        mapping = df.attrs.get("column_mapping", {})
        renamed = {k: v for k, v in mapping.items() if k != v}
        if renamed:
            with st.sidebar.expander("Automatski prepoznate kolone", expanded=False):
                st.write({f"{v} → {k}": "" for k, v in renamed.items()})
                st.caption("Lijevo = naziv u tvom fajlu, desno = kako ga alat koristi.")
    except Exception as e:
        st.sidebar.error("Ne mogu učitati CSV.")
        st.error(f"**Greška pri učitavanju CSV-a:**\n\n{e}")
        st.info(
            "Učitavam demo dataset umjesto toga. Provjeri da fajl ima kolonu sa datumom i kolonu "
            "sa prodajom/količinom (npr. `Date`/`date`, `Sales`/`units_sold`/`quantity`)."
        )
        df = load_default()
else:
    df = load_default()
    st.sidebar.info("Rossmann demo dataset (data/rossmann_demo_30.csv)")
    st.sidebar.caption(
        "Rezultati su demonstracioni — postavi vlastiti CSV za realne vrijednosti."
    )

summary = basic_summary(df)
with st.sidebar.expander("Pregled dataset-a", expanded=False):
    st.json(summary)

stores = sorted(df["Store"].unique().tolist())
products = sorted(df["Product"].unique().tolist())

st.sidebar.markdown("---")
st.sidebar.header("Odabir serije")
store = st.sidebar.selectbox("Prodavnica", stores)
product = st.sidebar.selectbox("Proizvod", products)
horizon = st.sidebar.slider("Forecast horizont (dani)", 7, 60, 28)
model_choice = st.sidebar.selectbox(
    "Glavni model za prognozu",
    ["Ensemble (hibrid)", "LightGBM", "Holt-Winters", "Sezonski naivni"],
    index=0,
    help="Ensemble kombinuje LightGBM (ML) i Holt-Winters (klasičan sezonski) — hibridni model iz postavke zadatka.",
)
granularity = st.sidebar.radio(
    "Granularnost prikaza", ["Dnevno", "Sedmično"], horizontal=True
)

st.sidebar.markdown("---")
st.sidebar.header("Parametri zaliha")
ordering_cost = st.sidebar.number_input("Trošak narudžbe (€)", 1.0, 1000.0, 50.0)
holding_cost = st.sidebar.number_input("Holding cost po jed./god. (€)", 0.1, 100.0, 2.0)
stockout_cost = st.sidebar.number_input("Stockout cost po jed. (€)", 0.0, 200.0, 5.0)
lead_time = st.sidebar.number_input("Lead time (dani)", 1, 60, 7)
service_level = st.sidebar.slider("Service level", 0.80, 0.99, 0.95, 0.01)
current_stock = st.sidebar.number_input("Trenutni lager (jedinice)", 0.0, 100000.0, 0.0)

params = InventoryParams(
    ordering_cost=ordering_cost,
    holding_cost=holding_cost,
    stockout_cost=stockout_cost,
    lead_time_days=lead_time,
    service_level=service_level,
    review_period_days=7,
)

st.sidebar.markdown("---")
st.sidebar.header("What-if simulacija")
whatif_promo = st.sidebar.checkbox("Pokreni promociju tokom horizonta")
whatif_price_change = st.sidebar.slider("Promjena cijene (%)", -30, 30, 0)
whatif_lead_time_extra = st.sidebar.slider("Dodatno kašnjenje (dana)", 0, 14, 0)


# ============================================================================
# Treniranje i forecast — keširano (radi se SAMO kad se promijene df/serija/horizont)
# ============================================================================


@st.cache_data(show_spinner="Treniram LightGBM model...")
def cached_pipeline(df_in: pd.DataFrame, store: str, product: str, horizon: int):
    series = filter_series(df_in, store, product)
    if len(series) < 90:
        return None
    feat_df, features = build_features(series)
    models = train_lightgbm(feat_df, features=features)
    forecast = recursive_forecast_lgbm(feat_df, models, features, horizon=horizon)
    baseline = baseline_moving_average(feat_df, horizon=horizon)
    snaive = seasonal_naive_forecast(feat_df, horizon=horizon)
    hw = holt_winters_forecast(feat_df, horizon=horizon)
    ensemble = ensemble_forecast(
        {"LightGBM": forecast, "Holt-Winters": hw},
        weights={"LightGBM": 0.6, "Holt-Winters": 0.4},
    )
    return {
        "series": series,
        "feat_df": feat_df,
        "features": features,
        "models": models,
        "forecast": forecast,
        "baseline": baseline,
        "snaive": snaive,
        "hw": hw,
        "ensemble": ensemble,
    }


# Keširani teški delovi — argumenti sa "_" se ne hešuju (Streamlit konvencija),
# pa "key" string nosi identitet serije/horizonta.
@st.cache_data(show_spinner=False)
def cached_anomalies(_feat: pd.DataFrame, method: str, contamination: float, key: str):
    if method == "isolation_forest":
        return detect_anomalies(
            _feat.copy(), method="isolation_forest", contamination=contamination
        )
    return detect_anomalies(_feat.copy(), method="zscore", threshold=3.0)


@st.cache_data(show_spinner=False)
def cached_global_importance(_model, _X: pd.DataFrame, top_k: int, key: str):
    return global_importance(_model, _X, top_k=top_k)


@st.cache_data(show_spinner=False)
def cached_explain_row(_model, _X: pd.DataFrame, top_k: int, key: str):
    return explain_row(_model, _X, row_idx=-1, top_k=top_k)


# Overview se renderuje BEZ treniranja modela -> trenutno učitavanje (npr. odmah nakon upload-a).
if view == "overview":
    render_overview(df, summary)
    render_footer()
    st.stop()


pipe = cached_pipeline(df, store, product, horizon)

if pipe is None:
    st.error(
        "Premalo podataka za ovaj (Store, Product) par — odaberi drugi (potrebno ≥ 90 dana)."
    )
    st.stop()

series = pipe["series"]
feat_df = pipe["feat_df"]
features = pipe["features"]
models = pipe["models"]
baseline = pipe["baseline"]
snaive = pipe["snaive"]
hw = pipe["hw"]
ensemble = pipe["ensemble"]
series_key = f"{store}|{product}|{horizon}|{len(feat_df)}"

# Izaberi glavni model za prognozu/preporuku (sa fallback-om ako nije dostupan)
_forecast_options = {
    "LightGBM": pipe["forecast"],
    "Holt-Winters": hw,
    "Sezonski naivni": snaive,
    "Ensemble (hibrid)": ensemble,
}
forecast = _forecast_options.get(model_choice)
if forecast is None:
    forecast = pipe["forecast"]
    st.warning(
        f"Model '{model_choice}' nije dostupan za ovu seriju — koristi se LightGBM."
    )
forecast = forecast.copy()


# ============================================================================
# Primjeni what-if scenarije nad forecastom
# ============================================================================

forecast_adj = forecast.copy()
applied_notes = []

if whatif_promo:
    forecast_adj["yhat"] *= 1.35
    forecast_adj["yhat_lower"] *= 1.30
    forecast_adj["yhat_upper"] *= 1.40
    applied_notes.append("Promocija (+35% potražnja)")

if whatif_price_change != 0:
    # naivna elastičnost: -1.2  (rast cijene od 10% -> pad potražnje od ~12%)
    elasticity = -1.2
    factor = (1 + whatif_price_change / 100.0) ** elasticity
    forecast_adj["yhat"] *= factor
    forecast_adj["yhat_lower"] *= factor
    forecast_adj["yhat_upper"] *= factor
    applied_notes.append(f"Cijena {whatif_price_change:+d}% (elasticity={elasticity})")

params_adj = InventoryParams(
    **{
        **params.__dict__,
        "lead_time_days": params.lead_time_days + whatif_lead_time_extra,
    }
)
if whatif_lead_time_extra:
    applied_notes.append(f"Lead time +{whatif_lead_time_extra} dana")


# ============================================================================
# KPI strip (uvijek vidljiv — jeftino se računa)
# ============================================================================

rec = recommend_order(
    forecast_adj, series["Sales"], params_adj, current_stock=current_stock
)
val_metrics = models["val_metrics"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    "Forecast (suma horizonta)",
    f"{rec.forecast_horizon_demand:,.0f}",
    help=f"Ukupna predviđena potražnja ({model_choice}) u narednom periodu",
)
c2.metric("Preporučena narudžba", f"{rec.recommended_order_qty:,.0f}")
c3.metric("Safety stock", f"{rec.safety_stock:,.1f}")
c4.metric("Reorder point", f"{rec.reorder_point:,.1f}")
c5.metric(
    "MAPE (LGBM, 1-korak)",
    f"{val_metrics['MAPE']:.1f}%",
    help="Validaciona greška LightGBM-a za 1 korak. Realnu višednevnu tačnost daje tab Evaluacija (backtest).",
)

if applied_notes:
    st.info("**What-if aktivan:** " + "  ·  ".join(applied_notes))

st.markdown("")


# ============================================================================
# VIEW: Forecast
# ============================================================================

if view == "forecast":
    weekly = granularity == "Sedmično"
    gran_label = "sedmična" if weekly else "dnevna"
    st.subheader(
        f"Prodaja i forecast ({gran_label}) — {store} · {product} · model: {model_choice}"
    )

    history_show = series.tail(180)

    # Komparativni modeli (bez what-if -> apples-to-apples poređenje modela)
    COMP_COLORS = {
        "LightGBM": "#dc2626",
        "Holt-Winters": "#7c3aed",
        "Sezonski naivni": GOOD,
        "Ensemble (hibrid)": "#0ea5e9",
        "Baseline (moving avg)": MUTED,
    }
    comp_sources = {
        "LightGBM": pipe["forecast"],
        "Holt-Winters": hw,
        "Sezonski naivni": snaive,
        "Ensemble (hibrid)": ensemble,
        "Baseline (moving avg)": baseline,
    }
    comp_available = [
        m for m, f in comp_sources.items() if f is not None and m != model_choice
    ]

    colA, colB = st.columns([3, 1])
    with colB:
        compare = st.multiselect("Uporedi modele", comp_available, default=[])
        show_prophet = st.checkbox("Prophet (sporo, opciono)", value=False)
        st.caption("Komparativne linije su bez what-if korekcije.")

    fig = go.Figure()
    # Istorija
    hx, hy = (
        resample_weekly(history_show["Date"], history_show["Sales"])
        if weekly
        else (history_show["Date"], history_show["Sales"])
    )
    fig.add_trace(
        go.Scatter(
            x=hx, y=hy, mode="lines", name="Stvarna prodaja", line=dict(color=PRIMARY)
        )
    )

    # Glavni model + interval
    if weekly:
        fx, fy = resample_weekly(forecast_adj["Date"], forecast_adj["yhat"])
        _, flo = resample_weekly(forecast_adj["Date"], forecast_adj["yhat_lower"])
        _, fhi = resample_weekly(forecast_adj["Date"], forecast_adj["yhat_upper"])
        fx = list(fx)
    else:
        fx = list(forecast_adj["Date"])
        fy = forecast_adj["yhat"]
        flo = forecast_adj["yhat_lower"]
        fhi = forecast_adj["yhat_upper"]
    fig.add_trace(
        go.Scatter(
            x=fx,
            y=fy,
            mode="lines",
            name=f"Forecast ({model_choice})",
            line=dict(color=DANGER),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fx + fx[::-1],
            y=list(fhi) + list(flo[::-1]),
            fill="toself",
            fillcolor="rgba(220,38,38,0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Interval pouzdanosti",
            hoverinfo="skip",
        )
    )

    # Komparativni modeli
    for m in compare:
        cf = comp_sources[m]
        if weekly:
            cx, cy = resample_weekly(cf["Date"], cf["yhat"])
        else:
            cx, cy = cf["Date"], cf["yhat"]
        fig.add_trace(
            go.Scatter(
                x=cx,
                y=cy,
                mode="lines",
                name=m,
                line=dict(color=COMP_COLORS.get(m, MUTED), dash="dash"),
            )
        )

    fig.update_layout(
        height=460,
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.18),
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Prodaja (sedmična suma)" if weekly else "Prodaja (dnevno)",
    )
    with colA:
        pchart(fig)

    if show_prophet:
        with st.spinner("Treniram Prophet..."):
            pf = prophet_forecast(series, horizon)
        if pf is not None:
            st.success("Prophet istreniran — dodat kao zelena linija ispod.")
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=history_show["Date"],
                    y=history_show["Sales"],
                    mode="lines",
                    name="Stvarna prodaja",
                )
            )
            fig2.add_trace(
                go.Scatter(
                    x=pf["Date"], y=pf["yhat"], mode="lines", name="Prophet forecast"
                )
            )
            fig2.add_trace(
                go.Scatter(
                    x=list(pf["Date"]) + list(pf["Date"][::-1]),
                    y=list(pf["yhat_upper"]) + list(pf["yhat_lower"][::-1]),
                    fill="toself",
                    fillcolor="rgba(22,163,74,0.15)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Prophet 80% interval",
                    hoverinfo="skip",
                )
            )
            fig2.update_layout(
                height=380, hovermode="x unified", margin=dict(l=10, r=10, t=30, b=10)
            )
            pchart(fig2)
        else:
            st.warning(
                "Prophet nije dostupan (nije instaliran na Python 3.13). "
                "Klasičnu sezonalnost pokriva Holt-Winters, koji je uključen u Ensemble."
            )

    with st.expander("Tabela forecasta (glavni model)", expanded=False):
        pdf(forecast_adj)


# ============================================================================
# VIEW: Inventory optimization
# ============================================================================

elif view == "inventory":
    st.subheader("EOQ, safety stock, reorder point")
    cA, cB = st.columns([1, 1])
    with cA:
        st.markdown(f"""
            **Trenutna preporuka** (uz aktivne parametre i what-if):

            - Mean daily demand: **{rec.mean_daily_demand:.2f}** jed/dan
            - Std daily demand: **{rec.std_daily_demand:.2f}**
            - Godišnja potražnja (procjena): **{rec.annual_demand:,.0f}** jed/god
            - **EOQ:** {rec.eoq:,.1f} jed
            - **Safety stock:** {rec.safety_stock:,.1f} jed (z = {rec.service_level_z})
            - **Reorder point:** {rec.reorder_point:,.1f} jed
            - **Preporučena količina narudžbe:** **{rec.recommended_order_qty:,.0f}** jed
            - Očekivani godišnji trošak: **{rec.expected_annual_cost:,.0f} €**
            - Očekivani trošak manjka (po ciklusu): **{rec.expected_stockout_cost:,.2f} €**
            """)
        # Newsvendor: ekonomski optimalan service level iz odnosa stockout/holding
        delta = rec.suggested_service_level - service_level
        smjer = (
            "viši"
            if delta > 0.005
            else ("niži" if delta < -0.005 else "blizu trenutnog")
        )
        st.info(
            f"💡 **Ekonomski optimalan service level:** {rec.suggested_service_level:.0%} "
            f"(trenutno: {service_level:.0%} — {smjer}).  \n"
            f"Računa se iz odnosa *stockout cost* ({stockout_cost:.0f} €) i *holding cost* "
            f"po newsvendor modelu: SL\\* = Cu / (Cu + Co)."
        )
    with cB:
        st.markdown("**Osjetljivost na service level**")
        sens = sensitivity_table(
            params_adj, forecast_adj, series["Sales"], vary="service_level"
        )
        fig_s = go.Figure()
        fig_s.add_trace(
            go.Scatter(
                x=sens["service_level"],
                y=sens["safety_stock"],
                mode="lines+markers",
                name="Safety stock",
            )
        )
        fig_s.add_trace(
            go.Scatter(
                x=sens["service_level"],
                y=sens["recommended_order_qty"],
                mode="lines+markers",
                name="Recommended qty",
            )
        )
        fig_s.update_layout(
            height=320,
            xaxis_title="Service level",
            yaxis_title="Jedinice",
            margin=dict(l=10, r=10, t=30, b=10),
        )
        pchart(fig_s)

    st.markdown("**Osjetljivost na lead time**")
    sens_lt = sensitivity_table(
        params_adj, forecast_adj, series["Sales"], vary="lead_time_days"
    )
    fig_lt = go.Figure()
    fig_lt.add_trace(
        go.Scatter(
            x=sens_lt["lead_time_days"],
            y=sens_lt["safety_stock"],
            mode="lines+markers",
            name="Safety stock",
        )
    )
    fig_lt.add_trace(
        go.Scatter(
            x=sens_lt["lead_time_days"],
            y=sens_lt["reorder_point"],
            mode="lines+markers",
            name="Reorder point",
        )
    )
    fig_lt.update_layout(
        height=320,
        xaxis_title="Lead time (dani)",
        yaxis_title="Jedinice",
        margin=dict(l=10, r=10, t=30, b=10),
    )
    pchart(fig_lt)


# ============================================================================
# VIEW: Anomalies
# ============================================================================

elif view == "anomaly":
    st.subheader("Detekcija anomalija u istorijskoj prodaji")
    method = st.radio(
        "Metoda",
        ["isolation_forest", "zscore"],
        format_func=lambda x: (
            "Isolation Forest" if x == "isolation_forest" else "Z-score"
        ),
        horizontal=True,
    )
    contamination = st.slider("Procenat očekivanih anomalija", 0.005, 0.10, 0.03, 0.005)

    anom = cached_anomalies(feat_df, method, contamination, series_key)

    fig_a = go.Figure()
    fig_a.add_trace(
        go.Scatter(
            x=anom["Date"],
            y=anom["Sales"],
            mode="lines",
            name="Prodaja",
            line=dict(color=PRIMARY),
        )
    )
    anomalies = anom[anom["is_anomaly"]]
    fig_a.add_trace(
        go.Scatter(
            x=anomalies["Date"],
            y=anomalies["Sales"],
            mode="markers",
            name="Anomalija",
            marker=dict(color=DANGER, size=10, symbol="x"),
        )
    )
    fig_a.update_layout(
        height=420, hovermode="x unified", margin=dict(l=10, r=10, t=30, b=10)
    )
    pchart(fig_a)

    st.markdown(
        f"Detektovano **{int(anom['is_anomaly'].sum())}** anomalija od ukupno {len(anom)} dnevnih tačaka."
    )
    with st.expander("Tabela anomalija", expanded=False):
        pdf(
            anomalies[["Date", "Sales", "anomaly_score"]].sort_values(
                "anomaly_score", ascending=False
            ),
        )


# ============================================================================
# VIEW: SHAP
# ============================================================================

elif view == "shap":
    st.subheader("Objašnjenja prognoze (SHAP)")
    X_train = feat_df[features].dropna()
    if len(X_train) < 30:
        st.warning("Premalo podataka za SHAP.")
    else:
        with st.spinner("Računam SHAP vrijednosti..."):
            sample = X_train.tail(500)
            imp = cached_global_importance(models["point"], sample, 12, series_key)
        imp = imp.copy()
        imp["feature_label"] = imp["feature"].map(humanize_feature)

        fig_imp = go.Figure(
            go.Bar(
                x=imp["mean_abs_shap"][::-1],
                y=imp["feature_label"][::-1],
                orientation="h",
                marker=dict(color=GOOD),
            )
        )
        fig_imp.update_layout(
            height=440,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Prosječni |SHAP| (uticaj na prognozu)",
        )
        pchart(fig_imp)

        st.markdown(
            "**Objašnjenje posljednje istorijske tačke** — zašto je model za posljednji dan dao tu prognozu:"
        )
        local = cached_explain_row(models["point"], X_train.tail(50), 8, series_key)
        local = local.copy()
        local["feature_label"] = local["feature"].map(humanize_feature)
        local_show = local[["feature_label", "value", "shap", "direction"]].rename(
            columns={
                "feature_label": "Feature",
                "value": "Vrijednost",
                "shap": "SHAP",
                "direction": "Smjer",
            }
        )
        pdf(local_show)


# ============================================================================
# VIEW: Narudžbenica
# ============================================================================

elif view == "orders":
    st.subheader("Automatska narudžbenica")
    st.caption(
        "Generiše preporuku narudžbe za **sve** Store/Product parove u dataset-u na osnovu pojedinačnih forecast-a."
    )

    if st.button("Generiši narudžbenicu za sve parove", type="primary"):
        progress = st.progress(0.0, text="Treniram modele po seriji...")
        pairs = df[["Store", "Product"]].drop_duplicates().values.tolist()
        forecasts_by_pair = {}
        for i, (s, p) in enumerate(pairs, start=1):
            sub_series = filter_series(df, s, p)
            if len(sub_series) < 90:
                continue
            try:
                feat_df_p, feats_p = build_features(sub_series)
                models_p = train_lightgbm(feat_df_p, features=feats_p)
                fcst_p = recursive_forecast_lgbm(
                    feat_df_p, models_p, feats_p, horizon=horizon
                )
                forecasts_by_pair[(s, p)] = fcst_p
            except Exception as e:
                st.warning(f"Skip {s}/{p}: {e}")
            progress.progress(i / len(pairs), text=f"Obrađeno {i}/{len(pairs)}")
        progress.empty()

        po = build_purchase_order(df, forecasts_by_pair, params_adj)
        st.session_state["purchase_order"] = po

    if "purchase_order" in st.session_state:
        po = st.session_state["purchase_order"]
        total_units = (
            po["Recommended_order_qty"].sum() if "Recommended_order_qty" in po else 0
        )
        total_cost = (
            po["Expected_total_cost"].sum() if "Expected_total_cost" in po else 0
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Parova u narudžbenici", f"{len(po)}")
        m2.metric("Ukupno jedinica", f"{total_units:,.0f}")
        m3.metric("Procijenjeni trošak", f"{total_cost:,.0f} €")

        pdf(po)

        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.download_button(
                "Preuzmi CSV",
                data=to_csv_bytes(po),
                file_name="purchase_order.csv",
                mime="text/csv",
            )
        with cc2:
            st.download_button(
                "Preuzmi Excel",
                data=to_excel_bytes(po),
                file_name="purchase_order.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with cc3:
            if st.button("Snimi u outputs/"):
                path = save_to_outputs(po, ROOT / "outputs")
                st.success(f"Snimljeno: {path}")
    else:
        st.info("Klikni dugme iznad da generišeš narudžbenicu za sve parove.")


# ============================================================================
# VIEW: Evaluacija
# ============================================================================

elif view == "eval":
    st.subheader("Evaluacija i poređenje modela")
    st.caption(
        "Pošteno mjerenje višednevne prognoze: model se trenira na prošlosti i predviđa "
        "period koji NIJE vidio. Poredi Baseline / Sezonski naivni / LightGBM / Holt-Winters / Ensemble."
    )

    eval_mode = st.radio(
        "Metoda evaluacije",
        ["Brzi backtest (zadnjih 28 dana)", "Rolling-origin CV (3 prozora, sporije)"],
        horizontal=False,
    )
    is_cv = eval_mode.startswith("Rolling")

    if st.button("Pokreni evaluaciju", type="primary"):
        with st.spinner("Treniram modele i mjerim grešku..."):
            if is_cv:
                eval_df = rolling_origin_backtest(
                    feat_df, features, horizon=28, n_splits=3
                )
            else:
                eval_df = evaluate_on_backtest(feat_df, features, horizon=28)

        if eval_df.empty:
            st.warning("Premalo podataka za evaluaciju ove serije.")
        else:
            st.session_state[f"eval_df_{series_key}"] = eval_df
            st.session_state[f"eval_mode_{series_key}"] = eval_mode

    eval_key = f"eval_df_{series_key}"

    if eval_key in st.session_state:
        eval_df = st.session_state[eval_key]
        used_mode = st.session_state.get(f"eval_mode_{series_key}", eval_mode)

        best = eval_df.loc[eval_df["MAPE"].idxmin(), "Model"]
        st.success(f"**{used_mode}** — najbolji model po MAPE: **{best}**")

        metric_format = {
            "MAE": "{:,.0f}",
            "RMSE": "{:,.0f}",
            "MAPE": "{:.1f}%",
            "nMAE": "{:.1f}%",
            "nRMSE": "{:.1f}%",
            "MASE": "{:.2f}",
            "RMSSE": "{:.2f}",
        }

        format_cols = {
            col: fmt for col, fmt in metric_format.items() if col in eval_df.columns
        }

        highlight_cols = [
            c
            for c in ["MAPE", "nMAE", "nRMSE", "MASE", "RMSSE"]
            if c in eval_df.columns
        ]

        styled_eval = eval_df.style.format(format_cols)

        if highlight_cols:
            styled_eval = styled_eval.highlight_min(
                subset=highlight_cols,
                color="#dcfce7",
            )

        pdf(styled_eval)

        percent_metrics = [
            metric for metric in ("MAPE", "nMAE", "nRMSE") if metric in eval_df.columns
        ]

        if percent_metrics:
            fig_eval = go.Figure()

            for metric in percent_metrics:
                fig_eval.add_trace(
                    go.Bar(name=metric, x=eval_df["Model"], y=eval_df[metric])
                )

            fig_eval.update_layout(
                barmode="group",
                height=380,
                margin=dict(l=10, r=10, t=30, b=10),
                yaxis_title="Greška (%) — manje je bolje",
            )

            pchart(fig_eval)

        scaled_metrics = [
            metric for metric in ("MASE", "RMSSE") if metric in eval_df.columns
        ]

        if scaled_metrics:
            fig_scaled = go.Figure()

            for metric in scaled_metrics:
                fig_scaled.add_trace(
                    go.Bar(name=metric, x=eval_df["Model"], y=eval_df[metric])
                )

            fig_scaled.update_layout(
                barmode="group",
                height=330,
                margin=dict(l=10, r=10, t=30, b=10),
                yaxis_title="Skalirana greška — manje je bolje",
            )

            pchart(fig_scaled)

    else:
        st.info("Klikni **Pokreni evaluaciju** za poređenje svih modela.")

    st.markdown("**LightGBM validacija (1-korak, trenutna serija):**")

    has_normalized_metrics = all(
        key in val_metrics for key in ["nMAE", "nRMSE", "MASE", "RMSSE"]
    )

    if has_normalized_metrics:
        vm1, vm2, vm3, vm4, vm5 = st.columns(5)
        vm1.metric("MAPE", f"{val_metrics['MAPE']:.1f}%")
        vm2.metric("nMAE", f"{val_metrics['nMAE']:.1f}%")
        vm3.metric("nRMSE", f"{val_metrics['nRMSE']:.1f}%")
        vm4.metric("MASE", f"{val_metrics['MASE']:.2f}")
        vm5.metric("RMSSE", f"{val_metrics['RMSSE']:.2f}")

        with st.expander("Apsolutne greške u originalnim Sales jedinicama", expanded=False):
            am1, am2 = st.columns(2)
            am1.metric("MAE", f"{val_metrics['MAE']:,.0f} Sales")
            am2.metric("RMSE", f"{val_metrics['RMSE']:,.0f} Sales")

        st.caption(
            "MAPE, nMAE i nRMSE su procentualne/normalizovane metrike. "
            "MASE i RMSSE porede model sa sezonski naivnim benchmarkom; vrijednost ispod 1 znači da je model bolji od tog benchmarka. "
            "MAE i RMSE su apsolutne greške u originalnim Sales jedinicama i zato mogu izgledati veliko. "
            "Ova 1-korak validacija je optimistična jer koristi stvarne lag vrijednosti; "
            "realniju višednevnu tačnost daju backtest i rolling-origin CV iznad."
        )

    else:
        vm1, vm2, vm3 = st.columns(3)
        vm1.metric("MAPE", f"{val_metrics['MAPE']:.1f}%")
        vm2.metric("MAE", f"{val_metrics['MAE']:,.0f} Sales")
        vm3.metric("RMSE", f"{val_metrics['RMSE']:,.0f} Sales")

        st.caption(
            "MAE i RMSE su apsolutne greške u originalnim Sales jedinicama, "
            "zato kod Rossmann podataka mogu izgledati veliko. "
            "Za poređenje modela najlakše se tumači MAPE, jer je izražen u procentima. "
            "Ova 1-korak validacija je optimistična jer koristi stvarne lag vrijednosti; "
            "realniju višednevnu tačnost daju backtest i rolling-origin CV iznad."
        )


# ============================================================================
# Footer
# ============================================================================

render_footer()
