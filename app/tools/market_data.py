import os
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv

load_dotenv()

ALPHAVANTAGE_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

def get_stock_quote(symbol: str) -> dict:
    """Fetch the latest real-time quote for a given stock symbol."""
    if not ALPHAVANTAGE_KEY:
        return {"error": "Missing Alpha Vantage API key. Please set ALPHAVANTAGE_API_KEY in .env."}

    try:
        ts = TimeSeries(key=ALPHAVANTAGE_KEY, output_format='json')
        data, meta = ts.get_quote_endpoint(symbol)
        return {
            "symbol": symbol.upper(),
            "price": float(data["05. price"]),
            "volume": int(data["06. volume"]),
            "change_percent": data["10. change percent"],
            "timestamp": data["07. latest trading day"],
        }
    except Exception as e:
        return {"error": str(e)}
    
def get_stock_timeseries(symbol: str, interval="daily"):
    """Fetch historical stock price data."""
    ts = TimeSeries(key=ALPHAVANTAGE_KEY, output_format='pandas')
    if interval == "intraday":
        data, _ = ts.get_intraday(symbol=symbol, interval='60min', outputsize='compact')
    else:
        data, _ = ts.get_daily(symbol=symbol, outputsize='compact')
    return data
