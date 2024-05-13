import boto3
import json

# import sys
# from pip._internal import main

# main(['install', 'OpenSearch', '--target', '/tmp/'])
# sys.path.insert(0,'/tmp/')

import requests
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth 

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
httpbasicauth=HTTPBasicAuth("username", "password")

host = 'OS domain endpoint' # The OpenSearch domain endpoint with https:// and without a trailing slash
index = 'opensearch_dashboards_sample_data_flights'
url = host + '/' + index + '/_search'

# Lambda execution starts here
def lambda_handler(event, context):
    # print(event['Query'])
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
        "size": 3,
        "query": {
            "bool": {
                "must": [{
                    "match": {
                        "OriginCountry": event['origin']
                        }
                    },
                    {
                    "match": {
                        "DestCountry": event['destination']
                        }
                    },
                    ]
                }
            }
        }
                # "fields": ["OriginCountry", "DestCountry", "FlightNum", "OriginCityName", "DestCityName", "AvgTicketPrice", "DistanceMiles"]

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=httpbasicauth, headers=headers, data=json.dumps(query))

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    results = {}
    results['body'] = r.text
    results['body'] = json.loads(results['body'])
    
    if('hits' in results['body']):
        response["body"] = results['body']['hits']
        
        # if('hits' in response['hits']):
        #     response['body'] = response['hits']['hits']

    
    return response
