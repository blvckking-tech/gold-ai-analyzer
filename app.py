import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data import get_xauusd_data
from indicators import add_indicators, get_support_resistance
from strategy import analyze_signal, get_signal_history
from backtest import run_backtest
from biquote import Biquote

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gold AI Analyzer", page_icon="🥇", layout="wide")

# --- INJECTION DU CSS PERSONNALISÉ ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f2b 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    h1, h2, h3 {
        color: #e6b800 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #e6b800 !important;
        border-bottom-color: #e6b800 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #e6b800;
        color: #000000;
        border-radius: 5px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ffcc00;
        color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("# 🥇")
    st.title("Navigation")
    
    st.markdown("### ⚙️ Paramètres")
    timeframe = st.selectbox("Choisir l'unité de temps", ["5m", "15m", "30m", "1h", "4h"])
    
    st.markdown("### 📉 Indicateurs à afficher")
    indicateurs_choisis = st.multiselect(
        "Choisissez les éléments à voir sur le graphique",
        ["EMA 20", "EMA 50", "EMA 200", "Support & Résistance"],
        default=["EMA 50", "EMA 200", "Support & Résistance"]
    )
    
    if st.button("🔄 Rafraîchir les données", use_container_width=True):
        st.rerun()
        
    st.markdown("---")
    st.markdown("**Règles de la stratégie :**")
    st.markdown("- Tendance EMA 50 / 200")
    st.markdown("- Momentum (bougie verte/rouge)")
    st.markdown("- Filtre RSI (14)")
    st.markdown("- Éloignement Support/Résistance")
    st.markdown("- Session (08h - 20h)")
    st.markdown("### 🛡️ Gestion du risque")
    use_trailing = st.checkbox("Activer le Trailing Stop dans le backtest", value=False)

# --- TITRE PRINCIPAL ---
# --- TITRE PRINCIPAL ---
st.title("🥇 Gold AI Analyzer - XAUUSD")
st.markdown("Bienvenue sur votre outil d'analyse technique automatisé pour l'Or.")

# --- CHARGEMENT DES DONNÉES ---
with st.spinner("⏳ Connexion aux marchés et téléchargement des données XAUUSD..."):
    df = get_xauusd_data(interval=timeframe, period="5d")
    if df.empty:
        st.error("Impossible de récupérer les données. Vérifie ta connexion.")
        st.stop()

    df = add_indicators(df)
    df = get_support_resistance(df, window=20)

# --- CRÉATION DES ONGLETS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Graphique & Signal", 
    "📊 Backtest & Statistiques", 
    "📖 Règles de la Stratégie",
    "📅 Calendrier Économique",
    "🧮 Calculateur"
])
# ==========================================
# ONGLET 1 : GRAPHIQUE & SIGNAL
# ==========================================
with tab1:
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Prix XAUUSD", "RSI (14)", "ATR (14)")
    )

    # Les chandeliers restent toujours affichés
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="XAUUSD"), row=1, col=1)
    
    # Affichage conditionnel des EMA
    if "EMA 20" in indicateurs_choisis:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], line=dict(color="blue", width=1), name="EMA 20"), row=1, col=1)
    if "EMA 50" in indicateurs_choisis:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], line=dict(color="orange", width=1), name="EMA 50"), row=1, col=1)
    if "EMA 200" in indicateurs_choisis:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], line=dict(color="red", width=1), name="EMA 200"), row=1, col=1)
    
    # Affichage conditionnel des Supports et Résistances
    if "Support & Résistance" in indicateurs_choisis:
        fig.add_trace(go.Scatter(x=df.index, y=df["Resistance"], line=dict(color="gray", width=1, dash="dot"), name="Résistance"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["Support"], line=dict(color="gray", width=1, dash="dot"), name="Support"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="purple", width=1), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ATR"], line=dict(color="teal", width=1), name="ATR"), row=3, col=1)

    fig.update_layout(height=700, xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚦 Signal Actuel")
    signal = analyze_signal(df)
    
    # Notifications visuelles (st.toast)
    if signal["signal"] == "BUY":
        st.toast("🟢 Signal d'ACHAT détecté sur XAUUSD !", icon="📈")
        st.success(f"🟢 **SIGNAL D'ACHAT (BUY)** détecté sur le XAUUSD en {timeframe} !")
    elif signal["signal"] == "SELL":
        st.toast("🔴 Signal de VENTE détecté sur XAUUSD !", icon="📉")
        st.error(f"🔴 **SIGNAL DE VENTE (SELL)** détecté sur le XAUUSD en {timeframe} !")
    else:
        st.info("🔵 **AUCUN SIGNAL (WAIT)** - Le marché n'est pas dans une configuration optimale.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Type", signal["signal"])
    if signal["entry"]:
        col2.metric("Prix d'Entrée", f"{signal['entry']:.2f}")
        col3.metric("Stop Loss / Take Profit", f"{signal['sl']:.2f} / {signal['tp']:.2f}")
    else:
        col2.metric("Prix d'Entrée", "-")
        col3.metric("Stop Loss / Take Profit", "-")

    st.subheader("📋 10 derniers signaux")
    history = get_signal_history(df)
    if history:
        history_df = pd.DataFrame(history)
        st.dataframe(history_df.sort_values(by="Date", ascending=False).head(10), use_container_width=True)
    else:
        st.info("Aucun signal détecté sur la période.")

# ==========================================
# ONGLET 2 : BACKTEST
# ==========================================
with tab2:
    st.subheader("📊 Résultats du Backtest")
    st.markdown("Simulation basée sur un lot de **0.10** pour le calcul des profits en dollars.")
    
    backtest_results = run_backtest(df, use_trailing=use_trailing)    
    if not backtest_results.empty:
        total_trades = len(backtest_results)
        gagnes = len(backtest_results[backtest_results["Résultat"] == "Gagné (TP)"])
        perdus = len(backtest_results[backtest_results["Résultat"] == "Perdu (SL)"])
        win_rate = (gagnes / (gagnes + perdus) * 100) if (gagnes + perdus) > 0 else 0
        profit_total = backtest_results["Profit ($)"].sum()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Signaux", total_trades)
        col2.metric("Gagnés (TP)", gagnes)
        col3.metric("Perdus (SL)", perdus)
        col4.metric("Taux de réussite", f"{win_rate:.1f} %")
        
        if profit_total > 0:
            col5.metric("Profit Total (0.1 Lot)", f"+{profit_total:.2f} $", delta="Gain")
        else:
            col5.metric("Profit Total (0.1 Lot)", f"{profit_total:.2f} $", delta="Perte", delta_color="inverse")
            
        st.markdown("---")
        with st.expander("Voir le détail des trades du Backtest"):
            st.dataframe(backtest_results.sort_values(by="Date", ascending=False), use_container_width=True)
            
            csv = backtest_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger l'historique (CSV)",
                data=csv,
                file_name='backtest_xauusd.csv',
                mime='text/csv',
            )
    else:
        st.info("Pas assez de données pour effectuer un backtest sur cette période.")

# ==========================================
# ONGLET 3 : RÈGLES DE LA STRATÉGIE
# ==========================================
with tab3:
    st.subheader("📚 Comprendre la Stratégie")
    st.write("""
    Cette application utilise une stratégie de **suivi de tendance** avec plusieurs filtres de sécurité.
    Voici les conditions exactes qui doivent être remplies pour qu'un signal soit généré :
    """)
    
    st.markdown("#### 🟢 Conditions pour un ACHAT (BUY)")
    st.markdown("""
    1. **Session** : Il doit être entre 8h00 et 20h00.
    2. **Tendance** : Le prix doit être au-dessus de l'EMA 50, et l'EMA 50 au-dessus de l'EMA 200.
    3. **Momentum** : La bougie actuelle doit être haussière (verte).
    4. **RSI** : Le RSI doit être compris entre 40 et 70 (ni suracheté, ni survendu).
    5. **Résistance** : Le prix ne doit pas être trop proche de la résistance (distance supérieure à 0.5 ATR).
    """)
    
    st.markdown("#### 🔴 Conditions pour une VENTE (SELL)")
    st.markdown("""
    1. **Session** : Il doit être entre 8h00 et 20h00.
    2. **Tendance** : Le prix doit être en-dessous de l'EMA 50, et l'EMA 50 en-dessous de l'EMA 200.
    3. **Momentum** : La bougie actuelle doit être baissière (rouge).
    4. **RSI** : Le RSI doit être compris entre 30 et 60.
    5. **Support** : Le prix ne doit pas être trop proche du support (distance supérieure à 0.5 ATR).
    """)
    
    st.markdown("#### 🎯 Gestion du risque")
    st.markdown("""
    *   **Stop Loss (SL)** : Placé à 1.0 x l'ATR (Aide à limiter les pertes).
    *   **Take Profit (TP)** : Placé à 1.5 x l'ATR (Ratio Risque/Récompense de 1:1.5).
    """)

# ==========================================
# ONGLET 4 : CALENDRIER ÉCONOMIQUE
# ==========================================
with tab4:
    st.subheader("📅 Prochains événements économiques à fort impact")
    st.markdown("Ces annonces peuvent créer une forte volatilité sur l'Or (XAUUSD).")
    
    try:
        bq = Biquote()
        events = bq.calendar(importance="high", countries="US,EU,GB")
        
        if events:
            for event in events[:10]:
                date_str = event.get("time", "Date inconnue")
                country = event.get("countryCode", "??")
                name = event.get("name", "Événement")
                st.warning(f"**{date_str}** | {country} | {name}")
        else:
            st.info("Aucun événement à fort impact prévu pour le moment.")
            
    except Exception as e:
        st.error(f"Impossible de récupérer le calendrier : {e}")
# ==========================================
# ONGLET 5 : CALCULATEUR DE POSITION
# ==========================================
with tab5:
    st.subheader("🧮 Calculateur de Taille de Position")
    st.markdown("""
    Cet outil vous aide à calculer la taille de votre lot pour ne risquer qu'un pourcentage précis de votre capital.
    Il se base sur le prix d'entrée et le Stop Loss du **signal actuel**.
    """)
    
    # On vérifie si un signal est actif
    signal_calcul = analyze_signal(df)
    
    if signal_calcul["entry"] is None:
        st.info("ℹ️ Aucun signal n'est actif pour le moment. Le calculateur s'activera dès qu'un signal BUY ou SELL apparaîtra.")
    else:
        col_input1, col_input2 = st.columns(2)
        capital = col_input1.number_input("Votre Capital ($)", min_value=100.0, value=1000.0, step=100.0)
        risque_pct = col_input2.number_input("Risque par trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        
        # Calcul de la distance du Stop Loss
        distance_sl = abs(signal_calcul["entry"] - signal_calcul["sl"])
        
        # Calcul de la taille du lot
        # Formule : (Capital * Risque%) / (Distance SL * 100)
        # Le *100 vient du fait que 1 lot standard = 100 onces.
        if distance_sl > 0:
            montant_risque = capital * (risque_pct / 100)
            taille_lot = montant_risque / (distance_sl * 100)
            
            st.markdown("---")
            st.markdown(f"**Signal Actuel : {signal_calcul['signal']}**")
            st.markdown(f"Prix d'Entrée : `{signal_calcul['entry']:.2f}`")
            st.markdown(f"Stop Loss : `{signal_calcul['sl']:.2f}`")
            st.markdown(f"Distance jusqu'au Stop Loss : `{distance_sl:.2f}` points")
            
            st.success(f"💰 **Taille de lot recommandée : {taille_lot:.2f} lots**")
            
            st.markdown(f"""
            **Résumé du risque :**
            *   Si le Stop Loss est touché, vous perdrez environ **{montant_risque:.2f} $** (soit {risque_pct}% de votre capital).
            *   Si le Take Profit est touché, vous gagnerez environ **{(abs(signal_calcul['tp'] - signal_calcul['entry']) * taille_lot * 100):.2f} $**.
            """)
        else:
            st.warning("La distance du Stop Loss est de 0, impossible de calculer.")
