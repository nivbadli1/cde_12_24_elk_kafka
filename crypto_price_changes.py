from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])

# Index name
index_name = 'cryptoprices'

# Query: Top 5 gainers in the last 24 hours
# query_top_gainers = {
#     "size": 5,
#     "sort": [
#         {
#             "price_change_percentage_24h": {
#                 "order": "desc"
#             }
#         }
#     ],
#     "query": {
#         "range": {
#             "price_change_percentage_24h": {
#                 "gt": 0
#             }
#         }
#     },
#     "_source": ["name", "symbol", "current_price", "price_change_percentage_24h", "timestamp"]
# }

# "query": {
#     "bool": {
#         "must": [
#             {
#                 "range": {
#                     "price_change_percentage_24h": {
#                         "gt": 0
#                     }
#                 }
#             },
#             {
#                 "range": {
#                     "timestamp": {
#                         "gte": "now-24h/h"
#                     }
#                 }
#             }
#         ]
#     }
# }


# Query: Top 5 losers in the last 24 hours
query_top_losers = {
    "size": 5,
    "sort": [
        {
            "price_change_percentage_24h": {
                "order": "asc"
            }
        }
    ],
    "query": {
        "range": {
            "price_change_percentage_24h": {
                "lt": 0
            }
        }
    },
    "_source": ["name", "symbol", "current_price", "price_change_percentage_24h", "timestamp"]
}

# Execute queries
gainers_response = es.search(index=index_name, body=query_top_gainers)
losers_response = es.search(index=index_name, body=query_top_losers)

# Display results - Top gainers
print("Top 5 Gainers in the Last 24 Hours:")
print("-" * 70)
for hit in gainers_response['hits']['hits']:
    source = hit['_source']
    print(f"{source['name']} ({source['symbol'].upper()}): +{source['price_change_percentage_24h']:.2f}%, Current Price: ${source['current_price']}")

# Display results - Top losers
print("\nTop 5 Losers in the Last 24 Hours:")
print("-" * 70)
for hit in losers_response['hits']['hits']:
    source = hit['_source']
    print(f"{source['name']} ({source['symbol'].upper()}): {source['price_change_percentage_24h']:.2f}%, Current Price: ${source['current_price']}")

print("\n")
print("Note: Equivalent Kibana/Dev Tools query for top gainers:")
print("""
GET /cryptoprices/_search
{
  "size": 5,
  "sort": [
    {
      "price_change_percentage_24h": {
        "order": "desc"
      }
    }
  ],
  "query": {
    "range": {
      "price_change_percentage_24h": {
        "gt": 0
      }
    }
  },
  "_source": ["name", "symbol", "current_price", "price_change_percentage_24h", "timestamp"]
}
""")