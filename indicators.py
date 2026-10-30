import pandas as pd
import numpy as np

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def add_indicators(df):
    df = df.copy()
    df["EMA20"] = calculate_ema(df["Close"], 20)
    df["EMA50"] = calculate_ema(df["Close"], 50)
    df["EMA200"] = calculate_ema(df["Close"], 200)
    df["RSI"] = calculate_rsi(df["Close"], 14)
    df["ATR"] = calculate_atr(df["High"], df["Low"], df["Close"], 14)
    return df
def get_support_resistance(df, window=20):
    """
    Calcule les supports et résistances sur une fenêtre glissante.
    """
    # Le plus bas des 20 dernières bougies (Support)
    df["Support"] = df["Low"].rolling(window=window).min()
    # Le plus haut des 20 dernières bougies (Résistance)
    df["Resistance"] = df["High"].rolling(window=window).max()
    return df
