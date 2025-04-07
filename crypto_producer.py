from kafka import KafkaProducer
import time
import json
import requests
from datetime import datetime

# Kafka producer configuration
KAFKA_TOPIC = 'crypto_prices'
KAFKA_BOOTSTRAP_SERVERS = ['course-kafka:9092']
API_ENDPOINT = 'https://api.coingecko.com/api/v3/coins/markets'

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"Starting Crypto Price Producer - sending to topic: {KAFKA_TOPIC}")

while True:
    try:
        # Fetch current data on top cryptocurrencies
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 15,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(API_ENDPOINT, params=params)
        
        # Check for successful response
        if response.status_code == 200:
            crypto_data = response.json()
            
            # Send each record as a separate message to Kafka
            for crypto in crypto_data:
                # Add current timestamp
                crypto['timestamp'] = datetime.now().isoformat()
                
                # Add only important fields to reduce data size
                message = {
                    'id': crypto['id'],
                    'symbol': crypto['symbol'],
                    'name': crypto['name'],
                    'current_price': crypto['current_price'],
                    'market_cap': crypto['market_cap'],
                    'market_cap_rank': crypto['market_cap_rank'],
                    'price_change_24h': crypto['price_change_24h'],
                    'price_change_percentage_24h': crypto['price_change_percentage_24h'],
                    'timestamp': crypto['timestamp']
                }
                
                # Send to Kafka
                producer.send(KAFKA_TOPIC, value=message)
                print(f"Sent: {message['name']} - ${message['current_price']}")
            
            print(f"Batch completed at {datetime.now()}")
        else:
            print(f"API Error: Status code {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Send data every 60 seconds
    time.sleep(60)