from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

# Connect to Elasticsearch
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])

# Index name
index_name = 'cryptoprices'

# Market Cap Histogram data
query_market_cap_hist = {
    "size": 0,
    "aggs": {
        "market_cap_ranges": {
            "histogram": {
                "field": "market_cap",
                "interval": 10000000000  # 10 billion dollar intervals
            }
        }
    }
}

# Market trend query - average price changes
query_market_trend = {
    "size": 0,
    "aggs": {
        "top_cryptos": {
            "terms": {
                "field": "name.keyword",
                "size": 10
            },
            "aggs": {
                "avg_price_change": {
                    "avg": {
                        "field": "price_change_percentage_24h"
                    }
                }
            }
        },
        "overall_market_trend": {
            "avg": {
                "field": "price_change_percentage_24h"
            }
        }
    }
}

# Execute queries
market_cap_response = es.search(index=index_name, body=query_market_cap_hist)
market_trend_response = es.search(index=index_name, body=query_market_trend)

# Display results - Market Cap Histogram
print("Market Cap Distribution:")
print("-" * 50)
for bucket in market_cap_response['aggregations']['market_cap_ranges']['buckets']:
    min_value = bucket['key'] / 1000000000  # Convert to billions of dollars
    max_value = (bucket['key'] + 10000000000) / 1000000000
    count = bucket['doc_count']
    print(f"${min_value:.1f}B - ${max_value:.1f}B: {count} cryptocurrencies")

# Display results - Overall market trend
overall_trend = market_trend_response['aggregations']['overall_market_trend']['value']
print("\nOverall Market Trend:")
print("-" * 50)
print(f"Average 24-hour price change: {overall_trend:.2f}%")

# Display results - Individual cryptocurrency trends
print("\nPrice Change Trends by Cryptocurrency:")
print("-" * 50)
for bucket in market_trend_response['aggregations']['top_cryptos']['buckets']:
    name = bucket['key']
    avg_change = bucket['avg_price_change']['value']
    trend_icon = "📈" if avg_change > 0 else "📉"
    print(f"{name}: {avg_change:.2f}% {trend_icon}")

print("\n")
print("Note: Equivalent Kibana/Dev Tools query for market trends:")
print("""
GET /cryptoprices/_search
{
  "size": 0,
  "aggs": {
    "top_cryptos": {
      "terms": {
        "field": "name.keyword",
        "size": 10
      },
      "aggs": {
        "avg_price_change": {
          "avg": {
            "field": "price_change_percentage_24h"
          }
        }
      }
    },
    "overall_market_trend": {
      "avg": {
        "field": "price_change_percentage_24h"
      }
    }
  }
}
""")