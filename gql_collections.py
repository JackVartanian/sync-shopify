import os
import requests
import json
import funcoes_comuns as fc
import pandas as pd
import aiohttp
import asyncio
import nest_asyncio
from dotenv import load_dotenv
nest_asyncio.apply()
load_dotenv()

# Configure store details (via .env)
shop_url = os.getenv('SHOPIFY_SHOP_URL')
admin_api_key = os.getenv('SHOPIFY_ADMIN_API_KEY')
api_version = os.getenv('SHOPIFY_API_VERSION', '2025-07')
sem = asyncio.Semaphore(100)

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token' : admin_api_key}

async def fetch_data(url, headers, data):
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                return await response.json()


async def get_collections():

    url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'

    data = {
        "query": """
        query {
            collections(first: 150) {
                edges {
                    node {
                        id
                        title
                        handle
                        updatedAt
                        productsCount
                        sortOrder
                        }}}}"""}

    res = await fetch_data(url, headers, data)

    nodes = [edge['node'] for edge in res['data']['collections']['edges']]

    df = pd.DataFrame(nodes)

    fc.saveCSV(df, 'collections')

    return df
