import json
import time
import argparse

from opensea_api_client import Client


parser = argparse.ArgumentParser()
parser.add_argument("collection", help="Return all assets from all contracts in a collection", default='nft-worlds')
args = parser.parse_args()

client = Client()
offset = 0
data = {'assets': []}
print("Start downloading assets data...")
while True:
    response = client.get_assets(
        collection=args.collection, 
        order_direction='asc',
        offset=offset,
        limit=20)
    data['assets'].extend(response['assets'])
    if len(response['assets']) < 20:
        break
    
    offset += 20
    break
    print(f"Fetched {offset // 20} part")
    time.sleep(1)

with open('assets.json', 'w') as fp:
    json.dump(data, fp)