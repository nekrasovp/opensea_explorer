import json
import requests
import streamlit as st
from pandas import DataFrame
from web3 import Web3

from opensea_api_client import Client


# page init
client = Client()
def render_asset(asset):
    if asset['name'] is not None:
        st.subheader(asset['name'])
    else:
        st.subheader(f"{asset['collection']['name']} #{asset['token_id']}")

    if asset['description'] is not None:
        st.write(asset['description'])
    else:
        st.write(asset['collection']['description'])

    if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
        st.video(asset['image_url'])
    elif asset['image_url'].endswith('svg'):
        svg = requests.get(asset['image_url']).content.decode()
        st.image(svg)
    elif asset['image_url']:
        st.image(asset['image_url'])

st.sidebar.header("Endpoints")
endpoint_choices = ['Assets', 'Events', 'Rarity']
endpoint = st.sidebar.selectbox("Choose an Endpoint", endpoint_choices)

st.title(f"OpenSea API Explorer - {endpoint}")

if endpoint == 'Assets':
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner")
    collection = st.sidebar.text_input("Collection", 'nft-worlds')
    assets_resp = client.get_assets(collection=collection, owner=owner, limit=5)
    for asset in assets_resp['assets']:
        render_asset(asset)

if endpoint == 'Events':
    collection = st.sidebar.text_input("Collection")
    asset_contract_address = st.sidebar.text_input("Contract Address")
    token_id = st.sidebar.text_input("Token ID")
    event_type = st.sidebar.selectbox("Event Type", ['offer_entered', 'cancelled', 'bid_withdrawn', 'transfer', 'approve'])

    events_resp = client.get_events()

    event_list = []
    for event in events_resp['asset_events']:
        if event_type == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']), 'ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']

            event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['collection']['name'], event['asset']['token_id']])

    df = DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])
    st.write(df)
    
    st.write(events_resp)

if endpoint == 'Rarity':
    with open('assets.json') as f:
        data = json.loads(f.read())
        asset_rarities = []

        for asset in data['assets']:
            asset_rarity = 1

            for trait in asset['traits']:
                trait_rarity = trait['trait_count'] / 8888
                asset_rarity *= trait_rarity

            asset_rarities.append({
                'token_id': asset['token_id'],
                'name': f"Wanderers {asset['token_id']}",
                'description': asset['description'],
                'rarity': asset_rarity,
                'traits': asset['traits'],
                'image_url': asset['image_url'],
                'collection': asset['collection']
            })

        assets_sorted = sorted(asset_rarities, key=lambda asset: asset['rarity']) 

        for asset in assets_sorted[:20]:
            render_asset(asset)
            st.subheader(f"{len(asset['traits'])} Traits")
            for trait in asset['traits']:
                st.write(f"{trait['trait_type']} - {trait['value']} - {trait['trait_count']} have this")