from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json

# Kafka configuration
KAFKA_TOPIC = 'crypto_prices'
KAFKA_BOOTSTRAP_SERVERS = ['course-kafka:9092']
CONSUMER_GROUP = 'crypto_consumer_group'

# Elasticsearch configuration
ES_HOST = 'elasticsearch'
ES_PORT = 9200
ES_SCHEME = 'http'
ES_INDEX = 'cryptoprices'

# Connect to Elasticsearch
es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': ES_SCHEME}])

# Check if index exists, if not - create it with proper mapping
if not es.indices.exists(index=ES_INDEX):
    # Define mapping for numeric and text fields
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "symbol": {"type": "keyword"},
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "current_price": {"type": "float"},
                "market_cap": {"type": "long"},
                "market_cap_rank": {"type": "integer"},
                "price_change_24h": {"type": "float"},
                "price_change_percentage_24h": {"type": "float"},
                "timestamp": {"type": "date"}
            }
        }
    }
    
    # Create the index with mapping
    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"Created Elasticsearch index: {ES_INDEX} with custom mapping")

# Create Kafka consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id=CONSUMER_GROUP,
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"Starting Crypto Price Consumer - reading from topic: {KAFKA_TOPIC}")
print(f"Indexing data to Elasticsearch: {ES_INDEX}")

# Consume messages from Kafka and write to Elasticsearch
message_count = 0
for message in consumer:
    try:
        document = message.value
        
        # Add document to Elasticsearch index
        # Use combination of crypto id and timestamp as a unique ID
        doc_id = f"{document['id']}_{document['timestamp']}"
        es.index(index=ES_INDEX, id=doc_id, body=document)
        
        message_count += 1
        if message_count % 10 == 0:
            print(f"Successfully indexed {message_count} documents to Elasticsearch")
    
    except Exception as e:
        print(f"Error processing message: {e}")