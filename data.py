import yfinance as yf
import pandas as pd

def get_xauusd_data(interval="15m", period="5d"):
    ticker = "GC=F"
    
    # Si on demande du H4, on télécharge du 1h et on regroupe
    if interval == "4h":
        download_interval = "1h"
        # On a besoin de plus d'historique pour avoir assez de bougies H4
        download_period = "1mo" 
    else:
        download_interval = interval
        download_period = period

    data = yf.download(ticker, interval=download_interval, period=download_period, progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    data = data[["Open", "High", "Low", "Close", "Volume"]].dropna()

    # Si on est en H4, on regroupe les bougies de 1h en 4h
    if interval == "4h":
        # Règles d'agrégation :
        # Open = premier prix, High = prix max, Low = prix min, Close = dernier prix, Volume = somme
        data = data.resample('4h').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

    return data
