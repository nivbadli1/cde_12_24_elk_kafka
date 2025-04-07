from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])

# Index name
index_name = 'cryptoprices'

# Aggregation query: Average price by cryptocurrency
query_body_avg_price = {
    "size": 0,
    "aggs": {
        "avg_price_by_crypto": {
            "terms": {
                "field": "name.keyword",
                "size": 20,
                "order": {
                    "average_price": "desc"
                }
            },
            "aggs": {
                "average_price": {
                    "avg": {
                        "field": "current_price"
                    }
                }
            }
        }
    }
}

response = es.search(index=index_name, body=query_body_avg_price)

print("Average Price by Cryptocurrency:")
print("-" * 50)
for bucket in response['aggregations']['avg_price_by_crypto']['buckets']:
    print(f"Cryptocurrency: {bucket['key']}, Average Price: ${bucket['average_price']['value']:.2f}")

print("\n")
print("Note: Equivalent Kibana/Dev Tools query:")
print("""
POST /cryptoprices/_search
{
  "size": 0,
  "aggs": {
    "avg_price_by_crypto": {
      "terms": {
        "field": "name.keyword",
        "size": 20,
        "order": {
          "average_price": "desc"
        }
      },
      "aggs": {
        "average_price": {
          "avg": {
            "field": "current_price"
          }
        }
      }
    }
  }
}
""")