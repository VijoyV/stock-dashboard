from flask import Flask, jsonify, render_template
import requests
import json
import time
import threading
import logging

app = Flask(__name__)

# Load stock symbols and config from config.json
with open('config.json') as f:
    config = json.load(f)
    stock_symbols = config['stock_symbols']
    refresh_interval_seconds = config.get("refresh_interval_seconds", 15)  # Fetch refresh interval or default to 15 seconds

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/',
    'DNT': '1',
}

cached_stock_data = []  # Global variable to store cached stock data
previous_values = {}  # To store previous values of Last Price, Day High, and Day Low

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch stock data for a given symbol
def fetch_stock_data(symbol, serial_number):
    url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol["symbol"]}'
    session = requests.Session()
    session.headers.update(headers)

    try:
        # Fetch initial page to establish session and cookies
        session.get(f'https://www.nseindia.com/get-quotes/equity?symbol={symbol["symbol"]}', timeout=10)

        # Fetch actual stock data
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()

        # Perform calculations
        last_price = round(data['priceInfo']['lastPrice'], 2)
        day_high = round(data['priceInfo']['intraDayHighLow']['max'], 2)
        day_low = round(data['priceInfo']['intraDayHighLow']['min'], 2)
        average_price = symbol['average_price']
        qoh = symbol['quantity_available']
        change = round(last_price - average_price, 2)
        percentage_change = round((change / average_price) * 100, 2) if average_price else 0
        average_value = round(qoh * average_price, 2)
        current_value = round(qoh * last_price, 2)

        # Determine if Last Price is up or down based on previous fetch
        prev_last_price = previous_values.get(symbol['symbol'], {}).get('last_price', last_price)
        prev_day_high = previous_values.get(symbol['symbol'], {}).get('day_high', day_high)
        prev_day_low = previous_values.get(symbol['symbol'], {}).get('day_low', day_low)

        # Update previous values cache
        previous_values[symbol['symbol']] = {
            'last_price': last_price,
            'day_high': day_high,
            'day_low': day_low
        }

        stock_info = {
            'serial_number': f"{serial_number:02d}",
            'symbol': data['info']['symbol'],
            'company_name': data['info']['companyName'],  # Tooltip in frontend
            'qoh': qoh,
            'average_price': average_price,
            'last_price': last_price,
            'last_updated': data['metadata']['lastUpdateTime'],
            'prev_last_price': prev_last_price,
            'prev_day_high': prev_day_high,
            'prev_day_low': prev_day_low,
            'change': change,
            'percentage_change': percentage_change,
            'previous_close': round(data['priceInfo']['previousClose'], 2),
            'open_price': round(data['priceInfo']['open'], 2),
            'day_high': day_high,
            'day_low': day_low,
            'week_high': round(data['priceInfo']['weekHighLow']['max'], 2),
            'week_low': round(data['priceInfo']['weekHighLow']['min'], 2),
            'average_value': average_value,
            'current_value': current_value
        }
        return stock_info
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {symbol['symbol']}: {e}")
    return None

# Function to fetch data for all symbols and update the cache
def update_stock_data():
    global cached_stock_data
    while True:
        stock_data = []
        for idx, symbol in enumerate(stock_symbols, start=1):
            stock_info = fetch_stock_data(symbol, idx)
            if stock_info:
                stock_data.append(stock_info)
        cached_stock_data = stock_data
        logger.info(f"Stock data updated: {cached_stock_data}")
        time.sleep(refresh_interval_seconds)  # Sleep for the refresh interval

# API to get cached stock data
@app.route('/api/stocks', methods=['GET'])
def get_stocks_data():
    return jsonify(cached_stock_data)

# Route to serve the dashboard page
@app.route('/')
def index():
    return render_template('index.html')

# Start a background thread to update stock data every 15 seconds
def start_background_thread():
    thread = threading.Thread(target=update_stock_data)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_background_thread()  # Start the background thread
    app.run(debug=True)
