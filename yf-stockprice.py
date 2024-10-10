import yfinance as yf

# Fetch stock data for a company listed on NSE (e.g., TCS)
stock = yf.Ticker("TCS.NS")

# Get live market data (slightly delayed)
data = stock.history(period="1d", interval="1m")
print(data.tail(5))  # Last 5 entries (1-minute intervals)
