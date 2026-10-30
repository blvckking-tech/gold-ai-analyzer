import pandas as pd

def run_backtest(df, lot_size=0.10, use_trailing=False):
    trades = []
    
    for i in range(len(df) - 1):
        row = df.iloc[i]
        
        if pd.isna(row["EMA200"]) or pd.isna(row["ATR"]) or pd.isna(row["RSI"]) or pd.isna(row["Resistance"]):
            continue
            
        signal_type = "WAIT"
        entry, sl, tp = None, None, None
        
        est_en_session = 8 <= df.index[i].hour < 20
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
            result = "En cours"
            profit_usd = 0.0
            
            # Variables pour le Trailing Stop
            current_sl = sl
            trailing_activated = False
            
            for j in range(i + 1, len(df)):
                future_row = df.iloc[j]
                
                if signal_type == "BUY":
                    # Vérifier si le SL est touché
                    if future_row["Low"] <= current_sl:
                        result = "Perdu (SL)"
                        profit_usd = (current_sl - entry) * lot_size * 100
                        break
                    
                    # Vérifier le Take Profit (si on n'utilise pas le trailing)
                    if not use_trailing and future_row["High"] >= tp:
                        result = "Gagné (TP)"
                        profit_usd = (tp - entry) * lot_size * 100
                        break
                    
                    # Logique du Trailing Stop
                    if use_trailing:
                        # Si le prix monte de 1.0 ATR, on remonte le SL à l'entrée (Break Even)
                        if not trailing_activated and future_row["High"] >= entry + (1.0 * row["ATR"]):
                            current_sl = entry
                            trailing_activated = True
                        # Si le prix continue de monter, on remonte le SL
                        elif trailing_activated:
                            new_sl = future_row["High"] - (1.0 * row["ATR"])
                            if new_sl > current_sl:
                                current_sl = new_sl
                                
                elif signal_type == "SELL":
                    # Vérifier si le SL est touché
                    if future_row["High"] >= current_sl:
                        result = "Perdu (SL)"
                        profit_usd = (entry - current_sl) * lot_size * 100
                        break
                    
                    # Vérifier le Take Profit
                    if not use_trailing and future_row["Low"] <= tp:
                        result = "Gagné (TP)"
                        profit_usd = (entry - tp) * lot_size * 100
                        break
                    
                    # Logique du Trailing Stop
                    if use_trailing:
                        if not trailing_activated and future_row["Low"] <= entry - (1.0 * row["ATR"]):
                            current_sl = entry
                            trailing_activated = True
                        elif trailing_activated:
                            new_sl = future_row["Low"] + (1.0 * row["ATR"])
                            if new_sl < current_sl:
                                current_sl = new_sl

            # Si on utilise le trailing et que le trade est toujours ouvert à la fin, on calcule le profit latent
            if use_trailing and result == "En cours":
                last_close = df.iloc[-1]["Close"]
                if signal_type == "BUY":
                    profit_usd = (last_close - entry) * lot_size * 100
                else:
                    profit_usd = (entry - last_close) * lot_size * 100
                result = "Fermé (Fin de données)"
            
            trades.append({
                "Date": df.index[i].strftime('%Y-%m-%d %H:%M'),
                "Signal": signal_type,
                "Résultat": result,
                "Profit ($)": round(profit_usd, 2)
            })
            
            i += 5 
            
    return pd.DataFrame(trades)
