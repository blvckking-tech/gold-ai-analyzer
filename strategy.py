import pandas as pd

def analyze_signal(df):
    last = df.iloc[-1]
    heure = df.index[-1].hour
    est_en_session = 8 <= heure < 20
    
    trend_up = last["Close"] > last["EMA50"] and last["EMA50"] > last["EMA200"]
    trend_down = last["Close"] < last["EMA50"] and last["EMA50"] < last["EMA200"]
    bougie_verte = last["Close"] > last["Open"]
    bougie_rouge = last["Close"] < last["Open"]
    rsi_ok_for_buy = 40 < last["RSI"] < 70
    rsi_ok_for_sell = 30 < last["RSI"] < 60
    
    marge = 0.5 * last["ATR"]
    pas_proche_resistance = (last["Resistance"] - last["Close"]) > marge
    pas_proche_support = (last["Close"] - last["Support"]) > marge
    
    if est_en_session and trend_up and bougie_verte and rsi_ok_for_buy and pas_proche_resistance:
        entry = last["Close"]
        atr = last["ATR"]
        sl = entry - (1.0 * atr)
        tp = entry + (1.5 * atr)
        return {"signal": "BUY", "entry": entry, "sl": sl, "tp": tp}
    
    if est_en_session and trend_down and bougie_rouge and rsi_ok_for_sell and pas_proche_support:
        entry = last["Close"]
        atr = last["ATR"]
        sl = entry + (1.0 * atr)
        tp = entry - (1.5 * atr)
        return {"signal": "SELL", "entry": entry, "sl": sl, "tp": tp}
    
    return {"signal": "WAIT", "entry": None, "sl": None, "tp": None}


def get_signal_history(df):
    history = []
    
    for index, row in df.iterrows():
        if pd.isna(row["EMA200"]) or pd.isna(row["ATR"]) or pd.isna(row["RSI"]) or pd.isna(row["Resistance"]):
            continue
            
        signal_type = "WAIT"
        entry, sl, tp = None, None, None
        
        est_en_session = 8 <= index.hour < 20
        trend_up = row["Close"] > row["EMA50"] and row["EMA50"] > row["EMA200"]
        trend_down = row["Close"] < row["EMA50"] and row["EMA50"] < row["EMA200"]
        bougie_verte = row["Close"] > row["Open"]
        bougie_rouge = row["Close"] < row["Open"]
        rsi_ok_for_buy = 40 < row["RSI"] < 70
        rsi_ok_for_sell = 30 < row["RSI"] < 60
        
        marge = 0.5 * row["ATR"]
        pas_proche_resistance = (row["Resistance"] - row["Close"]) > marge
        pas_proche_support = (row["Close"] - row["Support"]) > marge
        
        if est_en_session and trend_up and bougie_verte and rsi_ok_for_buy and pas_proche_resistance:
            signal_type = "BUY"
            entry = row["Close"]
            sl = entry - (1.0 * row["ATR"])
            tp = entry + (1.5 * row["ATR"])
            
        elif est_en_session and trend_down and bougie_rouge and rsi_ok_for_sell and pas_proche_support:
            signal_type = "SELL"
            entry = row["Close"]
            sl = entry + (1.0 * row["ATR"])
            tp = entry - (1.5 * row["ATR"])
            
        if signal_type != "WAIT":
            history.append({
                "Date": index.strftime('%Y-%m-%d %H:%M'),
                "Signal": signal_type,
                "Prix entrée": round(entry, 2),
                "SL": round(sl, 2),
                "TP": round(tp, 2)
            })
            
    return history
