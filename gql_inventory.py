import os
import asyncio
import aiohttp
import funcoes_comuns as fc
import pandas as pd
import requests
import time
import time
import json
import nest_asyncio
from dotenv import load_dotenv
nest_asyncio.apply()
load_dotenv()

# Configure store details (via .env)
shop_url = os.getenv('SHOPIFY_SHOP_URL')
admin_api_key = os.getenv('SHOPIFY_ADMIN_API_KEY')
api_version = os.getenv('SHOPIFY_API_VERSION', '2025-07')
url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'
sem = asyncio.Semaphore(100)

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token' : admin_api_key}


async def fetch_data(url, headers, data):
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                return await response.json()


def add_suffix(cod_produto):
    if cod_produto.startswith('AN') or cod_produto.startswith('AL'):
        suffixes = ['-10', '-11', '-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20', '-21', '-22', '-23', '-24', '-25', '-26']
        return [cod_produto + suffix for suffix in suffixes]
    else:
        return [cod_produto]


def query_searchInventoryItemId():

    query = """query searchInvetoryItemId($first: Int!, $searchQuery: String!) {
                inventoryItems(first: $first, query: $searchQuery) {
                    nodes {
                    id
                    sku
                    }}}"""

    return query


def variables_searchInventoryItemId(sku):

    variables = {
        "first": 1,
        "searchQuery": f"sku:{sku}"
        }

    return variables


async def searchInventoryItemId(df):

    InventoryItemDf = fc.readCSV('shopify_csv/InventoryItemDict.csv', sep=';')

    print('Total de produtos: ', len(InventoryItemDf))

    df = df[~df['Cod. Prod.'].isin(InventoryItemDf['sku'])].reset_index(drop=True)

    print('Total de produtos: ', len(df))

    InventoryItemDict = {
        'Sku': [],
        'InventoryItemId': []
    }

    query = query_searchInventoryItemId()

    print('Total de produtos: ', range(len(df)))

    for i in range(len(df)):

        try:

            produto = add_suffix(df['Cod. Prod.'].iloc[i])

            qtdProdutos = len(produto)

            print('Produto: ', df['Cod. Prod.'].iloc[i], ' - ', qtdProdutos)

            for j in range(qtdProdutos):

                variables = variables_searchInventoryItemId(produto[j])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                InventoryItemDict['Sku'].append(produto[j])
                InventoryItemDict['InventoryItemId'].append(res['data']['inventoryItems']['nodes'][0]['id'])

                print(i,' - Cod_Produto: ', produto[j] ,' - InventoryItemId: ', res['data']['inventoryItems']['nodes'][0]['id'])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Cod_Produto: ', df['Cod. Prod.'].iloc[i])

    InventoryItemDict_df = pd.DataFrame(InventoryItemDict)
    InventoryItemDf = pd.concat([InventoryItemDf, InventoryItemDict_df], ignore_index=True)
    print('Total de produtos: ', len(InventoryItemDf))
    InventoryItemDf.to_csv('shopify_csv/InventoryItemDict.csv', index=False, sep=';')


def query_inventoryItemUpdate():

    query = """mutation inventoryItemUpdate($id: ID!, $input: InventoryItemUpdateInput!) {
                inventoryItemUpdate(id: $id, input: $input) {
                    userErrors {
                    message
                    field
                    }
                    inventoryItem {
                    id
                    tracked
                    }
                }
                }"""

    return query


def variables_inventoryItemUpdate(InventoryItemId):

    variables = {
        "id": str(InventoryItemId),
        "input": {
            "tracked": True
        }
    }

    return variables


async def inventoryItemUpdate(df):

    InventoryItemDf = fc.readCSV('shopify_csv/inventoryTracked.csv', sep=';')
    df = df[~df['Sku'].isin(InventoryItemDf['Sku'])].reset_index(drop=True)

    InventoryItemDict = {
        'Sku': [],
        'Tracked': []
    }

    query = query_inventoryItemUpdate()

    for i in range(len(df)):

        try:
            variables = variables_inventoryItemUpdate(df['InventoryItemId'].iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            InventoryItemDict['Sku'].append(df['Sku'].iloc[i])
            InventoryItemDict['Tracked'].append(True)

            print(i,' - Sku: ', df['Sku'].iloc[i])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Sku: ', df['Sku'].iloc[i])


    InventoryItemDict_df = pd.DataFrame(InventoryItemDict)
    InventoryItemDf = pd.concat([InventoryItemDf, InventoryItemDict_df], ignore_index=True)
    print('Total de produtos: ', len(InventoryItemDf))
    InventoryItemDf.to_csv('shopify_csv/inventoryTracked.csv', index=False, sep=';')


def query_inventoryActivation():

    query = """mutation inventoryBulkToggleActivation($inventoryItemId: ID!, $inventoryItemUpdates: [InventoryBulkToggleActivationInput!]!) {
        inventoryBulkToggleActivation(inventoryItemId: $inventoryItemId, inventoryItemUpdates: $inventoryItemUpdates) {
            inventoryItem {
                id
                }
                inventoryLevels {
                    id
                    location {
                        id
                        }
                        }
                        userErrors {
                            field
                            message
                            code
                            }}}"""

    return query


def variables_inventoryActivation(InventoryItemId):

    variables = {
        "inventoryItemId": str(InventoryItemId),
        "inventoryItemUpdates": [
            {
                "locationId": "gid://shopify/Location/88040833319",
                "activate": True
                },
            {
                "locationId": "gid://shopify/Location/88041226535",
                "activate": True
                },
            {
                "locationId": "gid://shopify/Location/88734269735",
                "activate": True
                },
            {
                "locationId": "gid://shopify/Location/88734335271",
                "activate": True
                },
            {
                "locationId": "gid://shopify/Location/88040702247",
                "activate": True
                }
            ]
        }

    return variables


async def inventoryActivation(df):

    InventoryItemDf = fc.readCSV('shopify_csv/inventoryActivation.csv', sep=';')
    df = df[~df['Sku'].isin(InventoryItemDf['Sku'])].reset_index(drop=True)

    InventoryItemDict = {
        'Sku': [],
        'activate': []
    }

    query = query_inventoryActivation()

    for i in range(len(df)):

        try:
            variables = variables_inventoryActivation(df['InventoryItemId'].iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            InventoryItemDict['Sku'].append(df['Sku'].iloc[i])
            InventoryItemDict['activate'].append(True)

            print(i,' - Sku: ', df['Sku'].iloc[i])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Sku: ', df['Sku'].iloc[i])


    InventoryItemDict_df = pd.DataFrame(InventoryItemDict)
    InventoryItemDf = pd.concat([InventoryItemDf, InventoryItemDict_df], ignore_index=True)
    print('Total de produtos: ', len(InventoryItemDf))
    InventoryItemDf.to_csv('shopify_csv/inventoryActivation.csv', index=False, sep=';')


def query_inventoryAdjustQuantities():

    query = """mutation inventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!) {
        inventoryAdjustQuantities(input: $input) {
            userErrors {
                code
                field
                message
                }
                inventoryAdjustmentGroup {
                    id
                    reason
                    }
                    }}"""

    return query


def variables_inventoryAdjustQuantities(inventoryItemId, locationId, delta):

    variables = {
        "input":{
            "reason": "correction",
            "name": "available",
            "changes": {
                "delta": int(delta),
                "inventoryItemId": str(inventoryItemId),
                "locationId": str(locationId)
                }
            }
        }

    return variables


async def inventoryAdjustQuantities(df):

    # InventoryItemDf = fc.readCSV('shopify_csv/inventoryQuantities.csv', sep=';')
    # df = df[~df['Sku'].isin(InventoryItemDf['Sku'])].reset_index(drop=True)

    InventoryQuantitiesDict = {
        'Sku': [],
        'inventoryItemId': [],
        'locationId': [],
        'actualQuantities': [],
        'delta': []
    }

    query = query_inventoryAdjustQuantities()

    for i in range(len(df)):

        try:
            variables = variables_inventoryAdjustQuantities(df['inventoryItem_id'].iloc[i], df['location_id'].iloc[i], df['delta'].iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            InventoryQuantitiesDict['Sku'].append(df['variant.sku'].iloc[i])
            InventoryQuantitiesDict['inventoryItemId'].append(df['inventoryItem_id'].iloc[i])
            InventoryQuantitiesDict['locationId'].append(df['location_id'].iloc[i])
            InventoryQuantitiesDict['actualQuantities'].append(df['TotalQuantity'].iloc[i])
            InventoryQuantitiesDict['delta'].append(df['delta'].iloc[i])

            print(i,' - Sku: ', df['variant.sku'].iloc[i], ' - ', df['location_name'].iloc[i],  df['delta'].iloc[i])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Sku: ', df['variant.sku'].iloc[i])


    InventoryItemDict_df = pd.DataFrame(InventoryQuantitiesDict)
    # InventoryItemDf = pd.concat([InventoryItemDf, InventoryItemDict_df], ignore_index=True)
    print('Total de produtos: ', len(InventoryItemDict_df))
    InventoryItemDict_df.to_csv('shopify_csv/inventoryQuantities.csv', index=False, sep=';')


def prepare_df_estoque():

    estoque_capta = fc.readCSV('capta_csv/fEstoque.csv', sep=';')
    estoque_capta['ID_Location'] = estoque_capta['RefId'] + '-' + estoque_capta['WarehouseId']
    estoque_capta = estoque_capta[['RefId', 'WarehouseId', 'WarehouseName', 'TotalQuantity', 'ID_Location']].astype(str)

    # print('Qtd produtos em estoque:', len(estoque_capta))

    produtosShopify = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';').astype(str)
    produtosShopify[~produtosShopify['id'].str.contains('ProductVariant')].reset_index(drop=True)
    produtosShopify = produtosShopify[['variant.sku', 'inventoryItem_id', 'location_id', 'location_name', 'Qty']]
    produtosShopify = produtosShopify[~produtosShopify['location_name'].str.contains('Encomenda')].reset_index(drop=True)
    produtosShopify['Metal_Sh'] = produtosShopify['location_name'].str.split(' - ').str[1]
    produtosShopify['Metal_Sh'] = produtosShopify['Metal_Sh'].astype(str).str.upper()
    produtosShopify['ID_Location'] = produtosShopify['variant.sku'] + '-' + produtosShopify['location_id']

    # print('Qtd produtos Shopify:', len(produtosShopify))

    produtosShopify = produtosShopify.merge(estoque_capta, how='left', left_on='ID_Location', right_on='ID_Location')
    produtosShopify = produtosShopify[~produtosShopify['RefId'].isna()].reset_index(drop=True)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].fillna(0)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].astype(int)
    produtosShopify['Qty'] = produtosShopify['Qty'].astype(int)

    produtosShopify['delta'] = (produtosShopify['TotalQuantity'] - produtosShopify['Qty'])

    produtosShopify = produtosShopify[produtosShopify['delta'] != 0].reset_index(drop=True)

    print('Qtd produtos com estoque para atualizar:', len(produtosShopify['RefId'].unique()))

    fc.saveCSV(produtosShopify, 'shopify_csv/em_estoque.csv', ';')

    return produtosShopify


def prepare_df_zerar_estoque():

    estoque_capta = fc.readCSV('capta_csv/fEstoque.csv', sep=';')
    estoque_capta['ID_Location'] = estoque_capta['RefId'] + '-' + estoque_capta['WarehouseId']
    estoque_capta = estoque_capta[['RefId', 'WarehouseId', 'WarehouseName', 'TotalQuantity', 'ID_Location']].astype(str)

    # print('Qtd produtos em estoque:', len(estoque_capta))

    produtosShopify = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';').astype(str)
    produtosShopify[~produtosShopify['id'].str.contains('ProductVariant')].reset_index(drop=True)
    produtosShopify = produtosShopify[['variant.sku', 'inventoryItem_id', 'location_id', 'location_name', 'Qty']]
    produtosShopify = produtosShopify[~produtosShopify['location_name'].str.contains('Encomenda')].reset_index(drop=True)
    produtosShopify['Metal_Sh'] = produtosShopify['location_name'].str.split(' - ').str[1]
    produtosShopify['Metal_Sh'] = produtosShopify['Metal_Sh'].astype(str).str.upper()
    produtosShopify['ID_Location'] = produtosShopify['variant.sku'] + '-' + produtosShopify['location_id']

    # print('Qtd produtos Shopify:', len(produtosShopify))

    produtosShopify = produtosShopify.merge(estoque_capta, how='outer', left_on='ID_Location', right_on='ID_Location', indicator=True)
    produtosShopify = produtosShopify[~produtosShopify['variant.sku'].isna()].reset_index(drop=True)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].fillna(0)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].astype(int)

    produtosShopify = produtosShopify[produtosShopify['_merge'] != 'both'].reset_index(drop=True)

    produtosShopify['Qty'] = produtosShopify['Qty'].astype(int)

    produtosShopify['delta'] = (produtosShopify['TotalQuantity'] - produtosShopify['Qty'])

    produtosShopify = produtosShopify[produtosShopify['delta'] != 0].reset_index(drop=True)

    print('Qtd produtos sem estoque para atualizar:', len(produtosShopify['variant.sku'].unique()))

    fc.saveCSV(produtosShopify, 'shopify_csv/zerar_estoque.csv', ';')

    return produtosShopify


def prepare_df_encomendavel():

    estoque_capta = fc.readCSV('capta_csv/fEstoqueEnc.csv', sep=';')
    estoque_capta = estoque_capta[estoque_capta['RefId'].notna()].reset_index(drop=True)
    estoque_capta = estoque_capta[estoque_capta['RefId'] != ''].reset_index(drop=True)
    estoque_capta['ID_Location'] = (estoque_capta['RefId'] + '-' + estoque_capta['WarehouseId'] + '-' + estoque_capta['Metal'])
    estoque_capta = estoque_capta.drop_duplicates(subset=['ID_Location']).reset_index(drop=True)
    estoque_capta = estoque_capta[['RefId', 'WarehouseId', 'WarehouseName', 'TotalQuantity', 'ID_Location', 'Metal']].astype(str)

    # print('Qtd produtos encomendáveis:', len(estoque_capta))

    produtosShopify = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';')
    produtosShopify[~produtosShopify['id'].str.contains('ProductVariant')].reset_index(drop=True)
    produtosShopify = produtosShopify[['variant.sku', 'inventoryItem_id', 'location_id', 'location_name', 'Qty']]
    produtosShopify = produtosShopify[produtosShopify['location_name'].str.contains('Encomenda')].reset_index(drop=True)
    produtosShopify['Metal_Sh'] = produtosShopify['location_name'].str.split(' - ').str[1]
    produtosShopify['Metal_Sh'] = produtosShopify['Metal_Sh'].str.upper()
    produtosShopify['ID_Location'] = produtosShopify['variant.sku'] + '-' + produtosShopify['location_id'] + '-' + produtosShopify['Metal_Sh']
    produtosShopify = produtosShopify.drop_duplicates(subset=['ID_Location']).reset_index(drop=True)

    # print('Qtd produtos Shopify:', len(produtosShopify))

    produtosShopify = produtosShopify.merge(estoque_capta, how='left', left_on='ID_Location', right_on='ID_Location')
    produtosShopify = produtosShopify[~produtosShopify['RefId'].isna()].reset_index(drop=True)

    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].fillna(0)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].astype(int)
    produtosShopify['Qty'] = produtosShopify['Qty'].astype(int)

    produtosShopify['delta'] = (produtosShopify['TotalQuantity'] - produtosShopify['Qty'])

    produtosShopify = produtosShopify[produtosShopify['delta'] != 0].reset_index(drop=True)

    print('Qtd produtos encomendaveis para atualizar:', len(produtosShopify['RefId'].unique()))

    fc.saveCSV(produtosShopify, 'shopify_csv/encomendavel.csv', ';')

    return produtosShopify


def prepare_df_zerar_encomendaveis():

    estoque_capta = fc.readCSV('capta_csv/fEstoqueEnc.csv', sep=';')
    estoque_capta = estoque_capta[estoque_capta['RefId'].notna()].reset_index(drop=True)
    estoque_capta = estoque_capta[estoque_capta['RefId'] != ''].reset_index(drop=True)
    estoque_capta['ID_Location'] = (estoque_capta['RefId'] + '-' + estoque_capta['WarehouseId'] + '-' + estoque_capta['Metal'])
    estoque_capta = estoque_capta.drop_duplicates(subset=['ID_Location']).reset_index(drop=True)
    estoque_capta = estoque_capta[['RefId', 'WarehouseId', 'WarehouseName', 'TotalQuantity', 'ID_Location', 'Metal']].astype(str)

    # # print('Qtd produtos em estoque:', len(estoque_capta))

    produtosShopify = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';')
    produtosShopify[~produtosShopify['id'].str.contains('ProductVariant')].reset_index(drop=True)
    produtosShopify = produtosShopify[['variant.sku', 'inventoryItem_id', 'location_id', 'location_name', 'Qty']]
    produtosShopify = produtosShopify[produtosShopify['location_name'].str.contains('Encomenda')].reset_index(drop=True)
    produtosShopify['Metal_Sh'] = produtosShopify['location_name'].str.split(' - ').str[1]
    produtosShopify['Metal_Sh'] = produtosShopify['Metal_Sh'].str.upper()
    produtosShopify['ID_Location'] = produtosShopify['variant.sku'] + '-' + produtosShopify['location_id'] + '-' + produtosShopify['Metal_Sh']
    produtosShopify = produtosShopify.drop_duplicates(subset=['ID_Location']).reset_index(drop=True)

    # # print('Qtd produtos Shopify:', len(produtosShopify))

    produtosShopify = produtosShopify.merge(estoque_capta, how='outer', left_on='ID_Location', right_on='ID_Location', indicator=True)
    produtosShopify = produtosShopify[~produtosShopify['variant.sku'].isna()].reset_index(drop=True)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].fillna(0)
    produtosShopify['TotalQuantity'] = produtosShopify['TotalQuantity'].astype(int)

    produtosShopify = produtosShopify[produtosShopify['_merge'] != 'both'].reset_index(drop=True)

    produtosShopify['Qty'] = produtosShopify['Qty'].astype(int)

    produtosShopify['delta'] = (produtosShopify['TotalQuantity'] - produtosShopify['Qty'])

    produtosShopify = produtosShopify[produtosShopify['delta'] != 0].reset_index(drop=True)

    print('Qtd produtos sem estoque para atualizar:', len(produtosShopify['variant.sku'].unique()))

    fc.saveCSV(produtosShopify, 'shopify_csv/zerar_encomendaveis.csv', ';')

    return produtosShopify


def query_InventoryItemId():

    mutation = '''mutation bulkOperationRunQuery {
        bulkOperationRunQuery(
        query:  """{inventoryItems(first: 10) {
                    edges{
                    node {
                        id
                        sku
                        }
                }

                    }
                    }
                """) {
                        bulkOperation {
                            id
                            status
                            }
                            userErrors {
                                field
                                message
                                }
                            }
                    }'''

    return mutation


def query_InventoryLevels():

    mutation = '''mutation bulkOperationRunQuery {
        bulkOperationRunQuery(
        query: """{productVariants(first: 10) {
                    edges {
                    node {
                        id
                        sku
                        product {
                        id
                        title
                        totalVariants
                        }
                        inventoryItem {
                        id
                        inventoryLevels(first: 10) {
                            edges {
                            node {
                                id
                                location {
                                id
                                name
                                }
                                quantities(names: "available") {
                                quantity
                                name
                                updatedAt
                                }
                            }
                            }
                        }
                        variant {
                            id
                            sku
                            title
                        }
                        }
                    }
                    }
                }
                } """) {
                        bulkOperation {
                            id
                            status
                            }
                            userErrors {
                                field
                                message
                                }
                            }
                    }'''

    return mutation


def run_query(mutation):

    response = requests.post(url, json={'query': mutation}, headers=headers)

    if response.status_code == 200:
        res = response.json()
        # print(res)
        print('bulkOperation ID:', res['data']['bulkOperationRunQuery']['bulkOperation']['id'], '\n', 'Status:', res['data']['bulkOperationRunQuery']['bulkOperation']['status'], '\n')
        return res['data']['bulkOperationRunQuery']['bulkOperation']['id']
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


def retrieve_bulkOperation(id):

        query = '''query {
            node(id: "''' + id + '''") {
                ... on BulkOperation {
                    id
                    status
                    errorCode
                    createdAt
                    completedAt
                    objectCount
                    url
                    partialDataUrl
                }
            }}'''

        response = requests.post(url, json={'query': query}, headers=headers)

        if response.status_code == 200:
            res = response.json()
            print('Status:', res['data']['node']['status'])

            while res['data']['node']['status'] != 'COMPLETED':
                print('Aguardando 30 segundos para executar a próxima requisição...')
                time.sleep(30)
                response = requests.post(url, json={'query': query}, headers=headers)
                res = response.json()
                print('Status:', res['data']['node']['status'], '\n')

            print('ID:', res['data']['node']['id'])
            print('Status:', res['data']['node']['status'], '\n')
            return res['data']['node']['url']
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")


def read_url_InventoryLevels(url):

    df = pd.read_json(url, lines=True)

    df2 = df
    df2.fillna(method='ffill', inplace=True)
    df2 = df2[df2['quantities'].notna()].reset_index(drop=True)

    df_normalized1 = pd.json_normalize(df2['product'])
    df_normalized1.rename(columns={'id':'product_id', 'title':'product_title'}, inplace=True)
    df2 = pd.concat([df2, df_normalized1], axis=1)
    df2.drop(columns='product', inplace=True)

    df_normalized2 = pd.json_normalize(df2['inventoryItem'])
    df_normalized2.rename(columns={'id':'inventoryItem_id'}, inplace=True)
    df2 = pd.concat([df2, df_normalized2], axis=1)
    df2.drop(columns='inventoryItem', inplace=True)

    df_normalized3 = pd.json_normalize(df2['location'])
    df_normalized3.rename(columns={'id':'location_id', 'name':'location_name'}, inplace=True)
    df2 = pd.concat([df2, df_normalized3], axis=1)
    df2.drop(columns='location', inplace=True)

    df2['Qty'] = df2['quantities'].apply(lambda x: x[0]['quantity'])
    df2.drop(columns='quantities', inplace=True)

    df2 = df2[~df2['id'].str.contains('ProductVariant')].reset_index(drop=True)

    df2['sku_2'] = df2['sku'].str.split('-').str[0]

    fc.saveCSV(df2, 'shopify_csv/InventoryLevels.csv', ';')

    return df2


def read_url_InventoryItemId(url):

    df = pd.read_json(url, lines=True)

    fc.saveCSV(df, 'shopify_csv/InventoryItemDict.csv', sep=';')

    return df


def run_query_InventoryLevels():

    print('\nIniciando requisição InventoryLevels...')

    mutation = query_InventoryLevels()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_InventoryLevels(url)

    return df


def run_query_InventoryItemId():

    print('\nIniciando requisição InventoryItemId...')

    mutation = query_InventoryItemId()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_InventoryItemId(url)

    return df











