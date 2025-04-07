from kafka import KafkaProducer
import time
import json
import requests
from datetime import datetime

# קונפיגורציה
KAFKA_TOPIC = 'crypto_prices'
KAFKA_BOOTSTRAP_SERVERS = ['course-kafka:9092']
API_BASE = 'https://api.coingecko.com/api/v3'

# יצירת Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"Starting Crypto Historical Data Loader - sending to topic: {KAFKA_TOPIC}")

# מטבעות לאיסוף נתונים היסטוריים
coins = [
    'bitcoin', 'ethereum', 'tether', 'ripple', 'binancecoin', 
    'usd-coin', 'solana', 'dogecoin', 'tron', 'cardano',
    'lido-staked-ether', 'wrapped-bitcoin', 'leo-token', 'usds', 'the-open-network'
]

# סמלים למטבעות (אופציונלי - נשתמש בזה אם הערכים שונים מהערכים המקוריים)
coin_symbols = {
    'ripple': 'xrp',
    'binancecoin': 'bnb',
    'usd-coin': 'usdc',
    'the-open-network': 'ton'
}

# שמות תצוגה למטבעות (אופציונלי - נשתמש בזה אם הערכים שונים מהערכים המקוריים)
coin_names = {
    'ripple': 'XRP',
    'binancecoin': 'BNB',
    'usd-coin': 'USDC',
    'lido-staked-ether': 'Lido Staked Ether',
    'the-open-network': 'Toncoin'
}

# הגדרת מספר הימים לאחור
days = 30  # ניתן לשנות ל-90 או פחות בהתאם למגבלות API

# פונקציה למשיכת נתונים היסטוריים ושליחתם ל-Kafka
def load_historical_data():
    total_records = 0
    
    for coin_id in coins:
        print(f"Fetching historical data for {coin_id}...")
        
        # קבלת נתונים היסטוריים
        url = f"{API_BASE}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'  # נתונים יומיים
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # הנתונים מגיעים במבנה מערכים: [[timestamp, value], ...]
                prices = data['prices']
                market_caps = data['market_caps']
                
                print(f"Got {len(prices)} historical data points for {coin_id}")
                coin_records = 0
                
                for i in range(len(prices)):
                    timestamp_ms = prices[i][0]  # חותמת זמן במילישניות
                    price = prices[i][1]  # מחיר
                    market_cap = market_caps[i][1] if i < len(market_caps) else 0
                    
                    # חישוב שינוי מחיר יומי
                    price_change_24h = 0
                    price_change_percentage_24h = 0
                    if i > 0:
                        price_change_24h = price - prices[i-1][1]
                        price_change_percentage_24h = (price_change_24h / prices[i-1][1]) * 100
                    
                    # המרת timestamp למחרוזת תאריך
                    date = datetime.fromtimestamp(timestamp_ms / 1000.0).isoformat()
                    
                    # בקשת הסמל והשם מהמילונים, אם לא קיים - השתמש בערך ברירת מחדל
                    symbol = coin_symbols.get(coin_id, coin_id[:3])
                    name = coin_names.get(coin_id, coin_id.capitalize())
                    
                    # יצירת הודעה
                    message = {
                        'id': coin_id,
                        'symbol': symbol,
                        'name': name,
                        'current_price': price,
                        'market_cap': market_cap,
                        'market_cap_rank': 0,  # לא זמין בנתונים היסטוריים
                        'price_change_24h': price_change_24h,
                        'price_change_percentage_24h': price_change_percentage_24h,
                        'timestamp': date
                    }
                    
                    # שליחה ל-Kafka
                    producer.send(KAFKA_TOPIC, value=message)
                    coin_records += 1
                    
                    # הדפסת עדכון כל 5 רשומות
                    if coin_records % 5 == 0 or coin_records == len(prices):
                        print(f"Sent {coin_records}/{len(prices)} records for {name}")
                
                total_records += coin_records
                print(f"Historical data for {coin_id} completed. Total records: {coin_records}")
                
                # המתנה בין בקשות למניעת שגיאות rate limit
                time.sleep(2)
            
            elif response.status_code == 429:  # Too Many Requests
                print(f"Rate limit hit for {coin_id}. Waiting 60 seconds...")
                time.sleep(60)
                # ניסיון נוסף
                coins.append(coin_id)  # הוסף מטבע בחזרה לסוף הרשימה לניסיון נוסף
            
            else:
                print(f"Error fetching data for {coin_id}. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Error processing {coin_id}: {e}")
    
    print(f"Historical data loading completed. Total records sent to Kafka: {total_records}")

# הרצת הפונקציה
load_historical_data()
print("Historical data loading finished. You can now start the regular producer.")