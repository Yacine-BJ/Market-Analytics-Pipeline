import requests
from confluent_kafka import Producer
import json
import time
from datetime import datetime, timedelta
import pytz

BASE_URL = 'https://api.polygon.io'
API_KEY = '8bM0j3ChLzoS3D8yzUG54Pb82qQrv8EA' 
SYMBOLS = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']
KAFKA_TOPIC = "polygon"
BOOTSTRAP_SERVERS = "kafka:9092"

def get_histdata_polygon(ticker, start_date, end_date, timespan, multiplier):
   
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Erreur pour {ticker}: {response.status_code} - {response.text}")
        return []

def delivery_report(err, msg):
   
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def main():
    producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})
    
    for _ in range(7):  # 7 appels toutes les 5 minutes
        now = datetime.now(pytz.utc)
        end_date = now.strftime('%Y-%m-%d')
        start_date = (now - timedelta(days=3)).strftime('%Y-%m-%d') 
        
        print(f"Fetching data from {start_date} to {end_date}")
        
        for symbol in SYMBOLS:
            data = get_histdata_polygon(symbol, start_date, end_date, 'minute', '5') 
            
            for agg in data:
                message = {
                    "symbol": symbol,
                    "timestamp": agg['t'],
                    "open": agg['o'],
                    "high": agg['h'],
                    "low": agg['l'],
                    "close": agg['c'],
                    "volume": agg['v']
                }
                producer.produce(
                    KAFKA_TOPIC,
                    key=symbol,
                    value=json.dumps(message),
                    callback=delivery_report
                )
        
        producer.flush()
        time.sleep(300)  

if __name__ == "__main__":
    main()