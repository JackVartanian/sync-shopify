import os
import datetime
import pandas as pd
import funcoes_comuns as fc
import gql_products as gp
import asyncio
import aiohttp
import json
import requests
import time
import nest_asyncio
from dotenv import load_dotenv
nest_asyncio.apply()
load_dotenv()

today = datetime.date.today()
now = datetime.datetime.now()
now = now.strftime("%d-%m-%Y %H-%M-%S")

# Configure store details (via .env)
shop_url = os.getenv('SHOPIFY_SHOP_URL')
admin_api_key = os.getenv('SHOPIFY_ADMIN_API_KEY')
api_version = os.getenv('SHOPIFY_API_VERSION', '2025-07')
url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'
sem = asyncio.Semaphore(100)

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': admin_api_key}


async def fetch_data(url, headers, data):
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                return await response.json()



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
    fc.saveCSV(produtosShopify, 'log/estoque/em_estoque_log-' + str(now) +'.csv', sep=';')

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
    fc.saveCSV(produtosShopify, 'log/estoque/zerar_estoque_log-' + str(now) +'.csv', sep=';')

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
    fc.saveCSV(produtosShopify, 'log/estoque/encomendavel-' + str(now) +'.csv', sep=';')

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
    fc.saveCSV(produtosShopify, 'log/estoque/zerar_encomendaveis_log-' + str(now) +'.csv', sep=';')

    return produtosShopify


def prepare_df_price_shopify():
    df = fc.readCSV('shopify_csv/product_test_Sku.csv', sep=';')
    df = df[df['product_id'] != ''].reset_index(drop=True)
    #df = df.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)
    df = df[['sku_2', 'id','product_id', 'price', 'compareAtPrice']]
    df.rename(columns={'sku_2'
                       :'sku'}, inplace=True)
    return df

def prepare_df_title_description_composition_shopify():
    df = fc.readCSV('shopify_csv/product_title_description_composition_df3.csv', sep=';')
    df.columns.values[2] = 'second_title'
    df.columns.values[7] = 'title'
    df = df[df['product_id'] != ''].reset_index(drop=True)
    #df = df.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)
    df = df[['sku_2', 'id','product_id', 'metafield.value', 'description', 'title']]
    df.rename(columns={'sku_2'
                       :'sku'}, inplace=True)
    return df


def prepare_df_price_capta():
    produtos = fc.readCSV('capta_csv/produtos.csv', sep=';')
    produtos = produtos[produtos['Cod. Prod.'] != ''].reset_index(drop=True)
    produtos = produtos[['Cod. Prod.', 'Pr Venda unit']]
    produtos.rename(columns={'Cod. Prod.':'sku', 'Pr Venda unit':'priceCapta'}, inplace=True)
    return produtos

def prepare_df_title_description_composition_capta():
    produtos = fc.readCSV('capta_csv/produtosComTituloDescricaoComposicao.csv', sep=';')
    produtos = produtos[produtos['Cod. Prod.'] != ''].reset_index(drop=True)
    produtos = produtos[['Cod. Prod.', 'Composicao', 'Descricao_BR', 'Titulo_BR']]
    produtos.rename(columns={'Cod. Prod.':'sku', 'Composicao':'composicaoCapta', 'Descricao_BR':'descricaoCaptaBR', 'Titulo_BR':'tituloCapta' }, inplace=True)
    return produtos


def prepare_df_price_aneis():
    inventory = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';')
    inventory = inventory[inventory['variant.sku'] != ''].reset_index(drop=True)
    inventory = inventory.drop_duplicates(subset=['variant.sku'], keep='first').reset_index(drop=True)
    inventory = inventory[['variant.sku','variant.id','product_id']]
    #split variant.sku by '-' and get first part
    inventory['sku_2'] = inventory['variant.sku'].str.split('-').str[0]
    #save as csv
    #fc.saveCSV(inventory, 'shopify_csv/test_inventory.csv', sep=';')
    return inventory


def drop_aneis(df):
    df = df[~df['sku'].str.startswith(('AN', 'AL'))].reset_index(drop=True)
    return df


def merge_price_base(produtos, df):
    merge = pd.merge(df, produtos, how='left', left_on='sku', right_on='sku')
    merge = merge[merge['price'] != merge['priceCapta']].reset_index(drop=True)
    merge['priceCapta'] = merge['priceCapta'].astype(float)
    merge['price'] = merge['price'].astype(float)
    merge['delta'] = merge['priceCapta'] - merge['price']
    merge['delta'] = merge['delta'].round(2)
    merge = merge[merge['delta'] != 0].reset_index(drop=True)
    merge = merge[['sku', 'id', 'product_id', 'price', 'priceCapta', 'delta']]
    #remove rows that are not in produtos.csv
    merge = merge[merge['priceCapta'].notna()].reset_index(drop=True)
    return merge

def merge_title_description_composition_base(produtos, df):
    # 1) Merge por SKU
    merge = pd.merge(df, produtos, how='left', on='sku')

    # 2) Normalização de texto (strip, colapsa espaços, trata NaN)
    def norm_col(s):
        return (
            s.astype(str)
             .fillna('')
             .str.replace(r'\s+', ' ', regex=True)
             .str.strip()
        )

    # Garante que as colunas existem (evita KeyError se algum CSV vier sem a coluna)
    for col in ['title', 'description', 'metafield.value',
                'tituloCapta', 'descricaoCaptaBR', 'composicaoCapta']:
        if col not in merge.columns:
            merge[col] = ''

    # 3) Cria flags de diferença por campo
    title_diff = norm_col(merge['title']) != norm_col(merge['tituloCapta'])
    desc_diff  = norm_col(merge['description']) != norm_col(merge['descricaoCaptaBR'])
    comp_diff  = norm_col(merge['metafield.value']) != norm_col(merge['composicaoCapta'])

    merge['title_diff'] = title_diff
    merge['desc_diff']  = desc_diff
    merge['comp_diff']  = comp_diff

    # 4) Mantém apenas linhas com pelo menos UMA diferença
    has_any_diff = title_diff | desc_diff | comp_diff

    # Também remove linhas que não existem no CAPTA (tudo vazio do lado CAPTA)
    has_capta_ref = (
        merge['tituloCapta'].notna() |
        merge['descricaoCaptaBR'].notna() |
        merge['composicaoCapta'].notna()
    )

    merge = merge[has_any_diff & has_capta_ref].reset_index(drop=True)

    # 5) Seleciona colunas úteis para atualização/log
    merge = merge[[
        'sku', 'id', 'product_id',
        # Shopify (origem)
        'title', 'description', 'metafield.value',
        # CAPTA (destino desejado)
        'tituloCapta', 'descricaoCaptaBR', 'composicaoCapta',
        # Flags de diferença
        'title_diff', 'desc_diff', 'comp_diff'
    ]]

    return merge


def merge_price_base2(produtos, df):
    merge = pd.merge(df, produtos, how='left', left_on='sku', right_on='sku')
    merge = merge[merge['compareAtPrice'] != merge['priceCapta']].reset_index(drop=True)
    merge['priceCapta'] = merge['priceCapta'].astype(float)
    merge['compareAtPrice'] = merge['compareAtPrice'].astype(float)
    merge['compareAtPrice'] = merge['priceCapta']
    merge['delta'] = merge['priceCapta'] - merge['price']
    merge['delta'] = merge['delta'].round(2)
    #merge = merge[merge['delta'] != 0].reset_index(drop=True)
    merge = merge[['sku', 'id', 'product_id', 'compareAtPrice', 'priceCapta', 'delta']]
    #remove rows that are not in produtos.csv
    merge = merge[merge['priceCapta'].notna()].reset_index(drop=True)
    #save as csv
    fc.saveCSV(merge, 'shopify_csv/test_merge.csv', sep=';')
    return merge


def filter_price_aneis(merge):
    aneis = merge[merge['sku'].str.startswith(('AN', 'AL'))].reset_index(drop=True)
    aneis = aneis[['sku', 'id', 'product_id', 'price', 'priceCapta', 'delta']]
    return aneis


def filter_price_aneis_inventory(inventory, aneis):
    #filter inventory by sku_2 in aneis
    inventory2 = pd.merge(inventory, aneis, how='inner', left_on='sku_2', right_on='sku')
    inventory2 = inventory2[['variant.sku', 'variant.id', 'product_id', 'price', 'priceCapta', 'delta']]
    inventory2 = inventory2.rename(columns={'variant.sku':'sku', 'variant.id':'id'})
    #save as csv
    #fc.saveCSV(inventory2, 'shopify_csv/test_price_aneis.csv', sep=';')
    return inventory2

def filter_price_variants(inventory, merge):
    #filter inventory by sku in merge
    inventory2 = pd.merge(inventory, merge, how='inner', left_on='product_id', right_on='product_id')
    inventory2 = inventory2[['variant.sku', 'variant.id', 'product_id', 'price', 'priceCapta', 'delta']]
    inventory2 = inventory2.rename(columns={'variant.sku':'sku', 'variant.id':'id'})
    #save as csv
    #fc.saveCSV(inventory2, 'shopify_csv/test_price_variants.csv', sep=';')
    return inventory2


def merge_price_final(d1, d2):
    #union of dataframes
    merge = pd.concat([d1, d2], axis=0)
    #remove duplicates
    merge = merge.drop_duplicates(subset=['sku'], keep='first').reset_index(drop=True)
    return merge


def merge_price(produtos, df):


    merge = merge_price_base(produtos, df)

    if len(merge) == 0:
        print('\nNão há preços para atualizar')
        return merge
    else:
        print('\nQtd de preços para atualizar:', len(merge))
        #save merge as log archive using time library
        fc.saveCSV(merge, 'log/precos/price_update_log-' + str(now) +'.csv', sep=';')

        return merge

def merge_title_description_composition(produtos, df):

    merge = merge_title_description_composition_base(produtos, df)

    print('Analisando Se Houve Mudanças Nos Produtos...')

    if len(merge) == 0:
        print('\nNão há preços para atualizar')
        return merge
    else:
        print('\nQtd de preços para atualizar:', len(merge))

        print('Atualizando Produtos no Shopify...')
        #save merge as log archive using time library
        fc.saveCSV(merge, 'log/precos/title_description_composition_update_log-' + str(now) +'.csv', sep=';')

        return merge

def merge_price2(produtos, df):


    merge = merge_price_base2(produtos, df)

    if len(merge) == 0:
        print('\nNão há preços para atualizar')
        return merge
    else:
        print('\nQtd de preços para atualizar:', len(merge))
        #save merge as log archive using time library
        fc.saveCSV(merge, 'log/price_update_log-' + str(now) +'.csv', sep=';')

        return merge

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


def query_productVariants():

    mutation = '''mutation bulkOperationRunQuery {
        bulkOperationRunQuery(
        query: """{productVariants(first: 15) {
                    edges {
                    node {
                        product {
                        id
                        title
                        totalInventory
                        totalVariants
                        mediaCount{
                            count
                        }
                        }
                        id
                        sku
                        title
                        price
                        compareAtPrice
                        inventoryQuantity
                    }
                    }
                }
                }""") {
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

def query_products_mutation():
    mutation = '''mutation bulkOperationRunQuery {
      bulkOperationRunQuery(
        query: """
        {
          productVariants(first: 15) {
            edges {
              node {
                product {
                  id
                  title
                  description
                  totalInventory
                  totalVariants
                  mediaCount { count }
                  metafield(namespace: "custom", key: "composicao_text") {
                    value
                  }
                }
                id
                sku
                title
                price
                compareAtPrice
                inventoryQuantity
              }
            }
          }
        }
        """
      ) {
        bulkOperation { id status }
        userErrors { field message }
      }
    }'''

    return mutation



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


def query_productMetal():

    mutation = '''mutation bulkOperationRunQuery {
        bulkOperationRunQuery(
        query:  """{products(first: 3) {
                        edges {
                        node {
                            id
                            title
                            metafields(first: 10) {
                            edges {
                                node {
                                id
                                key
                                value
                                }
                            }
                            }
                        }
                        }
                    }}
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
    df2 = df2.ffill()
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


def read_url_productVariants(url):

    df = pd.read_json(url, lines=True)
    df_product = pd.json_normalize(df['product'])
    df_product.rename(columns={'id':'product_id'}, inplace=True)
    df2 = pd.concat([df, df_product], axis=1)
    df2.drop(columns='product', inplace=True)

    df2 = df2[df2['product_id'] != ''].reset_index(drop=True)
    df3 = df2
    df3['sku_2'] = df3['sku'].str.split('-').str[0]

    fc.saveCSV(df3, 'shopify_csv/product_test_Sku.csv', sep=';')
    df2['sku_2'] = df2['sku'].str.split('-').str[0]
    df2 = df2.drop_duplicates(subset=['sku_2'], keep='first').reset_index(drop=True)

    fc.saveCSV(df2, 'shopify_csv/product_Sku.csv', sep=';')

    return df2

def generatingShopifyProductsExcel(url):
    df = pd.read_json(url, lines=True)
    df_product = pd.json_normalize(df['product'])
    df_product.rename(columns={'id':'product_id'}, inplace=True)
    df2 = pd.concat([df, df_product], axis=1)
    df2.drop(columns='product', inplace=True)

    df2 = df2[df2['product_id'] != ''].reset_index(drop=True)
    df3 = df2
    df3['sku_2'] = df3['sku'].str.split('-').str[0]

    fc.saveCSVSigEncoding(df3, 'shopify_csv/product_title_description_composition_df3.csv', sep=';')
    df2['sku_2'] = df2['sku'].str.split('-').str[0]
    df2 = df2.drop_duplicates(subset=['sku_2'], keep='first').reset_index(drop=True)

    fc.saveCSVSigEncoding(df2, 'shopify_csv/product_title_description_composition_df2.csv', sep=';')

    return df2




def read_url_InventoryItemId(url):

    df = pd.read_json(url, lines=True)

    fc.saveCSV(df, 'shopify_csv/InventoryItemDict.csv', sep=';')

    return df


def read_url_productMetal(url):

    df = pd.read_json(url, lines=True)

    fc.saveCSV(df, 'shopify_csv/productMetal.csv', sep=';')

    return df


def run_query_InventoryLevels():

    print('\nIniciando requisição InventoryLevels...')

    mutation = query_InventoryLevels()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_InventoryLevels(url)

    return df


def run_query_productVariants():

    print('\nIniciando requisição productVariants...')

    mutation = query_productVariants()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_productVariants(url)

    return df


def runningShopifyProductsMutation():

    print('Running Shopify Products Mutation ...')

    mutation = query_products_mutation()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = generatingShopifyProductsExcel(url)

    return df


def run_query_InventoryItemId():

    print('\nIniciando requisição InventoryItemId...')

    mutation = query_InventoryItemId()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_InventoryItemId(url)

    return df


def run_query_productMetal():

    print('\nIniciando requisição productMetal...')

    mutation = query_productMetal()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_productMetal(url)

    return df

def filter_encomendaveis_stock():
    #get csv from shopify
    df = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';')
    #drop rows with variant.sku empty
    df = df[df['variant.sku'] != ''].reset_index(drop=True)
    #drop rows where location_name contains Encomenda
    df = df[~df['location_name'].str.contains('Encomenda')].reset_index(drop=True)
    dfAux = df

    dfAux2 = pd.DataFrame(columns=['variant.id'])
    dfAux3 = pd.DataFrame(columns=['variant.id'])

    #get the first line of the dataframe
    #row1 = df.head(1)['variant.id']

    #dfAux = dfAux[dfAux['variant.id'] == row1[0]].reset_index(drop=True)
    dfAux['Qty'] = dfAux['Qty'].astype(int)

    #for until dfAux is empty
    while not df.empty:
        #get the first line of the dataframe
        row1 = df.head(1)['variant.id']
        #filter the dataframe by the first line
        dfAux = df[df['variant.id'] == row1[0]].reset_index(drop=True)
        #convert Qty to int

        #if the sum of the Qty is 0, save in a third dataframe
        if dfAux['Qty'].sum() == 0:
            dfAux2 = dfAux2.append(dfAux['variant.id'])
        else:
            dfAux3 = dfAux3.append(dfAux['variant.id'])
        #drop the rows that are in dfAux
        df = df[~df['variant.id'].isin(dfAux['variant.id'])].reset_index(drop=True)



    #if (dfAux['Qty'].iloc[0] and dfAux['Qty'].iloc[1] and dfAux['Qty'].iloc[2] and dfAux['Qty'].iloc[3]) == 0:
    #    #save in a third dataframe
    #    dfAux2 = dfAux2.append(dfAux['variant.id'].iloc[0])
    #    print('teste')
    #else:
    #    print('teste2')


    #get rows


    #return dfAux



    #save dfAux2 and dfAux3 in csv
    dfAux2.to_csv('shopify_csv/test_nao_alterar.csv', sep=';', index=False)
    dfAux3.to_csv('shopify_csv/test_alterar.csv', sep=';', index=False)

def update_prices_stock_black():
    #get csv from shopify
    dfAlt = fc.readCSV('shopify_csv/test_alterar.csv', sep=';')
    #drop variant.id column
    dfAlt = dfAlt.drop(columns=['variant.id'])
    #rename columns
    dfAlt.rename(columns={'0':'variant.id'}, inplace=True)
    #drop 1, 2, 3 columns
    dfAlt = dfAlt.drop(columns=['1', '2', '3'])

    #get csv from shopify
    dfNaoAlt = fc.readCSV('shopify_csv/test_nao_alterar.csv', sep=';')
    #drop variant.id column
    dfNaoAlt = dfNaoAlt.drop(columns=['variant.id'])
    #rename columns
    dfNaoAlt.rename(columns={'0':'variant.id'}, inplace=True)
    #drop 1, 2, 3 columns
    dfNaoAlt = dfNaoAlt.drop(columns=['1', '2', '3'])

    #remove rows that contains 'New Vintage' in title.1 column
    #dfAlt = dfAlt[~dfAlt['title.1'].str.contains('New Vintage')].reset_index(drop=True)
    #dfNaoAlt = dfNaoAlt[~dfNaoAlt['title.1'].str.contains('New Vintage')].reset_index(drop=True)

    #get product_test_sku.csv
    dfProd = fc.readCSV('shopify_csv/product_test_sku.csv', sep=';')

    #rename compareAtPrice column
    dfProd.rename(columns={'compareAtPrice':'comparePrice'}, inplace=True)
    #put comparePrice column in the end


    #merge dfAlt with dfProd
    dfAlt = pd.merge(dfAlt, dfProd, how='left', left_on='variant.id', right_on='id')
    #merge dfNaoAlt with dfProd
    dfNaoAlt = pd.merge(dfNaoAlt, dfProd, how='left', left_on='variant.id', right_on='id')

    #add comparePrice column
    dfAlt['comparePrice'] = dfAlt['comparePrice'].astype(float)


    #remove
    dfAlt = dfAlt[~dfAlt['title.1'].str.contains('New Vintage')].reset_index(drop=True)
    dfNaoAlt = dfNaoAlt[~dfNaoAlt['title.1'].str.contains('New Vintage')].reset_index(drop=True)

    dfProd = dfProd[['id', 'sku', 'title', 'price', 'product_id', 'title', 'totalInventory', 'totalVariants', 'mediaCount', 'sku_2', 'comparePrice']]

    dfBlack = fc.readCSV('shopify_csv/produtos_black.csv', sep=';')


    dfBlackUp = dfAlt[dfAlt['sku_2'].isin(dfBlack['SKU'])].reset_index(drop=True)
    #merge dfBlackUp with dfBlack
    dfBlackUp = pd.merge(dfBlackUp, dfBlack, how='left', left_on='sku_2', right_on='SKU')


    dfAlt['price'] = dfAlt['comparePrice']*0.9
    #drop dfAlt rows that sku_2 is in dfBlack
    dfAlt = dfAlt[~dfAlt['sku_2'].isin(dfBlack['SKU'])].reset_index(drop=True)


    #save dfAlt and dfNaoAlt in csv
    dfBlackUp.to_csv('shopify_csv/black_alterar.csv', sep=';', index=False)
    dfAlt.to_csv('shopify_csv/test_alterar2.csv', sep=';', index=False)
    dfNaoAlt.to_csv('shopify_csv/test_nao_alterar2.csv', sep=';', index=False)



def return_price(df):

    asyncio.run(gp.return_price_black(df))

def verify_last_cycle():
    #get test_alterar2.csv
    dfAlt = fc.readCSV('shopify_csv/test_alterar2.csv', sep=';')
    base = fc.readCSV('shopify_csv/base_alterar.csv', sep=';')

    #get rows that are in dfAlt and not in base
    dfAlt2 = dfAlt[~dfAlt['variant.id'].isin(base['variant.id'])].reset_index(drop=True)

    #get rows that are in base and not in dfAlt
    base2 = base[~base['variant.id'].isin(dfAlt['variant.id'])].reset_index(drop=True)

    #if dfAlt2 is empty, do nothing, else, append to base
    if dfAlt2.empty:
        print('dfAlt2 is empty')
    else:
        asyncio.run(gp.update_price_black(dfAlt2))
        base = base.append(dfAlt2)
        print('dfAlt2 is not empty')
        add_badges(dfAlt2)


    #if base2 is empty, do nothing, else, remove from base
    if base2.empty:
        print('base2 is empty')
    else:
        return_price(base2)
        #asyncio.run(gp.return_price_black(base2))
        print('base2 is not empty')
        base = base[~base['variant.id'].isin(base2['variant.id'])].reset_index(drop=True)
        remove_badges(base2)

    #save base in csv
    base.to_csv('shopify_csv/base_alterar.csv', sep=';', index=False)

def verify_last_cycle_black():
    #get black_alterar.csv
    dfAlt = fc.readCSV('shopify_csv/black_alterar.csv', sep=';')
    base = fc.readCSV('shopify_csv/black_base.csv', sep=';')

    #get rows that are in dfAlt and not in base
    dfAlt2 = dfAlt[~dfAlt['variant.id'].isin(base['variant.id'])].reset_index(drop=True)

    #get rows that are in base and not in dfAlt
    base2 = base[~base['variant.id'].isin(dfAlt['variant.id'])].reset_index(drop=True)

    dfAlt2['price'].astype(float)
    dfAlt2['Porcentagem'].astype(float)

    #multiply price column by porcentagem column
    dfAlt2['price'] = dfAlt['price'] - (dfAlt['price']*(dfAlt['Porcentagem']/100))

    #if dfAlt2 is empty, do nothing, else, append to base
    if dfAlt2.empty:
        print('Não há preços para atualizar\n')
    else:
        print('Atualizar preços e badges dos produto black\n')
        asyncio.run(gp.update_price_black(dfAlt2))
        base = base.append(dfAlt2)
        add_badges(dfAlt2)

    #if base2 is empty, do nothing, else, remove from base
    if base2.empty:
        print('Não há preços para retornar\n')
    else:
        return_price(base2)
        #asyncio.run(gp.return_price_black(base2))
        print('Retornar preços dos prpdutos black\n')
        base = base[~base['variant.id'].isin(base2['variant.id'])].reset_index(drop=True)
        remove_badges(base2)

    #save base in csv
    base.to_csv('shopify_csv/black_base.csv', sep=';', index=False)


def remove_badges(df):

    print("Adquirindo metafields...\n")
    get_metafields(df)

def remove_metafield_sale(df):

    print("Adquirindo metafields...\n")
    get_metafields_sale(df)

def remove_badges_black(df):

    dfEnc = df[df['Encomenda'].str.contains('Sim')].reset_index(drop=True)
    dfNenc = df[df['Encomenda'].str.contains('Nao')].reset_index(drop=True)

    #get rows that totalInventory > 0
    #dfEnc = dfEnc[dfEnc['totalInventory'] > 0].reset_index(drop=True)

    ##get rows of dfNenc that totalInventory/totalVariants > 5
    #dfNenc = dfNenc[dfNenc['totalInventory']/dfNenc['totalVariants'] > 5].reset_index(drop=True)

    #if totalVariants == 1, remove badge
    #dfUnique = df[df['totalVariants'] == 1].reset_index(drop=True)
    ##if totalVariants > 1, remove badge
    #dfMultiple = df[df['totalVariants'] > 1].reset_index(drop=True)

    if dfNenc.empty:
        print('Sem produtos não encomendáveis para remover badge\n')
    else:
        #asyncio.run(gp.remove_badges(dfUnique))
        print('Remover badges dos produtos não encomendáveis black\n')
        get_metafields(dfNenc)


    if dfEnc.empty:
        print('Sem produtos encomendáveis para remover badge\n')
    else:
        #drop rows where totalInventory/totalVariants > 5
        print('Remover badges dos produtos encomendáveis black\n')
        #astype int
        dfEnc['totalInventory'] = dfEnc['totalInventory'].astype(int)
        dfEnc['totalVariants'] = dfEnc['totalVariants'].astype(int)
        dfMultiple1 = dfEnc[dfEnc['totalInventory']/dfEnc['totalVariants'] == 5].reset_index(drop=True)
        dfMultiple2 = dfEnc[dfEnc['totalInventory']/dfEnc['totalVariants'] == 0].reset_index(drop=True)
        #append dfMultiple1 and dfMultiple2
        dfMultiple3 = dfMultiple1.append(dfMultiple2).reset_index(drop=True)

        #asyncio.run(gp.remove_badges(dfMultiple))
        get_metafields(dfMultiple3)

def add_badges(df):
    asyncio.run(gp.update_badges(df))

def get_metafields(df):

    newdf = asyncio.run(gp.get_metafield_id(df))
    #drop duplicates
    newdf = newdf.drop_duplicates(subset=['metafield_id'], keep='first').reset_index(drop=True)
    asyncio.run(gp.update_metafield(newdf))

def get_metafields_sale(df):

    newdf = asyncio.run(gp.get_metafield_id_sale(df))
    #drop duplicates
    newdf = newdf.drop_duplicates(subset=['metafield_id'], keep='first').reset_index(drop=True)
    asyncio.run(gp.update_metafield(newdf))

def prepararDF():
    #get csv from shopify
    df = fc.readCSV('shopify_csv/product_test_Sku.csv', sep=';')
    #get produtos_natal2.csv
    df2 = fc.readCSV('shopify_csv/natal/produtos_natal.csv', sep=';')

    #drop rows in df that are not in df2
    df = df[df['product_id'].isin(df2['id'])].reset_index(drop=True)

    #drop duplicates in product_id column
    df = df.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)

    #save df in csv
    df.to_csv('shopify_csv/natal/baseNatal.csv', sep=';', index=False)

def filterEncomendaveis():
    #get csv baseNatal.csv
    df = fc.readCSV('shopify_csv/natal/baseNatal.csv', sep=';')

    #drop rows that totalInventory is 0
    df = df[df['totalInventory'] != 0].reset_index(drop=True)

    #totalInventory and totalVariants to float
    df['totalInventory'] = df['totalInventory'].astype(float)
    df['totalVariants'] = df['totalVariants'].astype(float)


    #drop rows that totalInventory divided by totalVariants is equal to 1
    #df = df[df['totalInventory']%df['totalVariants'] != 1].reset_index(drop=True)


    #compare if totalInventory divided by totalVariants is greater than 1 and save in two different dataframes
    dfAlt = df[df['totalInventory']/df['totalVariants'] != 5].reset_index(drop=True)
    dfNaoAlt = df[df['totalInventory']/df['totalVariants'] == 5].reset_index(drop=True)

    #save dfAlt and dfNaoAlt in csv
    dfAlt.to_csv('shopify_csv/natal/natal_tag.csv', sep=';', index=False)
    dfNaoAlt.to_csv('shopify_csv/natal/natal_sem_tag.csv', sep=';', index=False)

def updateBadgesNatal(df):

    asyncio.run(gp.update_badges(df))

def verify_last_cycle_natal():
    #get natal_tag.csv
    dfAlt = fc.readCSV('shopify_csv/natal/natal_tag.csv', sep=';')
    base = fc.readCSV('shopify_csv/natal/base_natal_tag.csv', sep=';')

    #get rows that are in dfAlt and not in base
    dfAlt2 = dfAlt[~dfAlt['product_id'].isin(base['product_id'])].reset_index(drop=True)

    #get rows that are in base and not in dfAlt
    base2 = base[~base['product_id'].isin(dfAlt['product_id'])].reset_index(drop=True)

    #if dfAlt2 is empty, do nothing, else, append to base
    if dfAlt2.empty:
        print('Não há produtos para atualizar')
    else:
        #asyncio.run(gp.update_price_black(dfAlt2))
        base = base.append(dfAlt2)
        print('Produtos para atualizar tag')
        updateBadgesNatal(dfAlt2)


    #if base2 is empty, do nothing, else, remove from base
    if base2.empty:
        print('Não tags para remover')
    else:
        #return_price(base2)
        print('Produtos para remover tag')
        base = base[~base['product_id'].isin(base2['product_id'])].reset_index(drop=True)
        remove_badges(base2)

    #save base in csv
    base.to_csv('shopify_csv/natal/base_natal_tag.csv', sep=';', index=False)

def get_products_collections(title):
    query = gp.query_get_collections(title)
    #run query
    results = gp.run_query_default(query)
    return results

def normalize_json(json):
    json = json['data']['collections']['nodes'][0]['products']['nodes']
    #transform json in dataframe
    df = pd.json_normalize(json)
    return df

def get_natal_collections():
    print("Iniciando requisição Natal...\n")
    especial = "Especial Festas"
    jeans = "Do Jeans a Festa"
    desing = "DESING CLASSICO DA JV"
    edgy = "EDGY OUSADO"
    atemporal = "JOIAS ATEMPORAIS ALTA JOALHERIA"

    especial = get_products_collections(especial)
    especial = normalize_json(especial)

    jeans = get_products_collections(jeans)
    jeans = normalize_json(jeans)

    desing = get_products_collections(desing)
    desing = normalize_json(desing)

    edgy = get_products_collections(edgy)
    edgy = normalize_json(edgy)

    atemporal = get_products_collections(atemporal)
    atemporal = normalize_json(atemporal)

    #concatenate dataframes
    frames = [especial, jeans, desing, edgy, atemporal]
    df = pd.concat(frames)
    df = df.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
    print('Total de produtos: ', len(df))
    #save df in csv
    df.to_csv('shopify_csv/natal/produtos_natal.csv', sep=';', index=False)


def remodelInventoryLevels():
    #get csv from shopify
    df = fc.readCSV('shopify_csv/InventoryLevels.csv', sep=';')

    #drop rows with variant.sku empty
    df = df[df['variant.sku'] != ''].reset_index(drop=True)

    #drop rows that has no "gid://shopify/Location/88734269735" or "gid://shopify/Location/88734335271" in location_id column
    df = df[df['location_id'].str.contains('88734269735|88734335271')].reset_index(drop=True)

    #ordenar pelo variant.sku
    df = df.sort_values(by=['sku']).reset_index(drop=True)

    #deixar somente as colunas sku, location_name e Qty
    df = df[['variant.sku', 'variant.id', 'location_name', 'Qty']]

    #criar as colunas encomenda ouro e encomenda prata e preencher com 0
    df['encomenda ouro'] = 0
    df['encomenda prata'] = 0
    df['Encomendavel'] = 'false'
    df['Encomendavel'] = df['Encomendavel'].astype(str)

    #se a linha tiver "Encomenda Ouro" na coluna location_name, colocar o valor da Qty na coluna encomenda ouro
    df.loc[df['location_name'] == 'Encomenda - Ouro', 'encomenda ouro'] = df['Qty']
    df.loc[df['location_name'] == 'Encomenda - Prata', 'encomenda prata'] = df['Qty']

    df = df[['variant.sku', 'variant.id' ,'encomenda ouro', 'encomenda prata', 'Encomendavel']]

    #se a soma da coluna encomenda ouro com a coluna encomenda prata for maior que 0, colocar True na coluna Encomendavel




    #unir as linhas que tem o mesmo sku
    df = df.groupby(['variant.sku', 'variant.id', 'Encomendavel'], as_index=False).sum()

    ##reordenar
    df = df[['variant.sku', 'variant.id', 'encomenda ouro', 'encomenda prata', 'Encomendavel']]
    df.loc[(df['encomenda ouro'] + df['encomenda prata']) > 0, 'Encomendavel'] = 'true'

    ##head 25
    #df = df.head(25)


    #save df in csv
    df.to_csv('shopify_csv/metafield/InventoryLevelsNatal2.csv', sep=';', index=False)

def checkNewEncomendavel():
    #get csv from shopify
    df = fc.readCSV('shopify_csv/metafield/InventoryLevelsNatal2.csv', sep=';')

    #get csv from shopify
    df2 = fc.readCSV('shopify_csv/metafield/InventoryLevelsNatal_base.csv', sep=';')

    #check if each row in df are different from df2 using all information
    df3 = df[~df.apply(tuple,1).isin(df2.apply(tuple,1))].reset_index(drop=True)

    #if df is empty, do nothing, else, run update_metafield_variant_encomendavel
    if df3.empty:
        print('Não há produtos para atualizar')
    else:
        print('Produtos para atualizar')
        asyncio.run(gp.update_metafield_variant_encomendavel(df3))
        #save df in csv
        df.to_csv('shopify_csv/metafield/InventoryLevelsNatal_base.csv', sep=';', index=False)
        df3.to_csv('shopify_csv/metafield/InventoryLevelsNatal_new.csv', sep=';', index=False)

def prepareEmEstoque():
    variants = fc.readCSV('shopify_csv/product_test_Sku.csv', sep=';')
    inventory = fc.readCSV('shopify_csv/metafield/InventoryLevelsNatal2.csv', sep=';')

    #merge variants and inventory
    merge = pd.merge(variants, inventory, how='left', left_on='id', right_on='variant.id')

    merge['Em estoque'] = True
    # pandas 2.x nao aceita string em coluna bool; deixa a coluna como object
    merge['Em estoque'] = merge['Em estoque'].astype(object)

    #se a coluna Encomendavel for igual a true e inventoryQuantity maior que 0, colocar em estoque como true

    merge.loc[(merge['Encomendavel'] == False) & (merge['inventoryQuantity'] == 0), 'Em estoque'] = 'false'
    merge.loc[(merge['Encomendavel'] == True) & (merge['inventoryQuantity'] == 5), 'Em estoque'] = 'false'

    #drop rows that Encomendavel is empty
    merge = merge[merge['Encomendavel'].notna()].reset_index(drop=True)

    #save as csv
    fc.saveCSV(merge, 'shopify_csv/estoque/EmEstoque.csv', sep=';')

def checkNewEmEstoque():
    #get csv from shopify
    df = fc.readCSV('shopify_csv/estoque/EmEstoque.csv', sep=';')

    #get csv from shopify
    df2 = fc.readCSV('shopify_csv/estoque/EmEstoque_base.csv', sep=';')

    #check if each row in df are different from df2 using all information
    df3 = df[~df.apply(tuple,1).isin(df2.apply(tuple,1))].reset_index(drop=True)

    #if df is empty, do nothing, else, run update_metafield_variant_encomendavel
    if df3.empty:
        print('Não há produtos para atualizar')
    else:
        print('Produtos para atualizar')
        asyncio.run(gp.update_metafield_variant_em_estoque(df3))
        #save df in csv
        df.to_csv('shopify_csv/estoque/EmEstoque_base.csv', sep=';', index=False)
        df3.to_csv('shopify_csv/estoque/EmEstoque_new.csv', sep=';', index=False)

def query_getCollection_bulk_sale():

    mutation = '''mutation bulkOperationRunQuery {
        bulkOperationRunQuery(
        query: """{collection(id: "gid://shopify/Collection/478534140199") {
    products(first: 10) {
      edges {
        node {
          id
        }
      }
    }
  }
}""") {
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

def read_url_to_dataframe_salejul(url):

    df = pd.read_json(url, lines=True)
    #save to csv
    # df.to_csv('shopify_csv/sale/produtos_sale.csv', index=False)
    return df

def updateMetafieldSale(df):
    asyncio.run(gp.update_metafield_sale(df))

def removeMetafieldSale(df):
    asyncio.run(gp.remove_metafield_sale(df))

def get_products_collections_bulk():
    mutation = query_getCollection_bulk_sale()

    # print(mutation)

    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_productVariants(url)

    return df

def get_sale_collections():

    mutation = query_getCollection_bulk_sale()

    # print(mutation)

    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_to_dataframe_salejul(url)

    excluido = 'Excluidos - sale jun 2024'

    excluido = get_products_collections(excluido)
    excluido = normalize_json(excluido)

    #save excluido in csv
    excluido.to_csv('shopify_csv/sale/excluido.csv', sep=';', index=False)

    #exclude rows that are in excluido
    df = df[~df['id'].isin(excluido['id'])].reset_index(drop=True)

    #save df in csv
    df.to_csv('shopify_csv/sale/produtos_sale_jun_2024.csv', sep=';', index=False)

def prepararDataFrameSale():
    df = fc.readCSV('shopify_csv/product_test_Sku.csv', sep=';')
    #get produtos_natal2.csv
    df2 = fc.readCSV('shopify_csv/sale/produtos_sale_jun_2024.csv', sep=';')

    #drop rows in df that are not in df2
    df = df[df['product_id'].isin(df2['id'])].reset_index(drop=True)

    #drop duplicates in product_id column
    df = df.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)

    #save df in csv
    df.to_csv('shopify_csv/sale/baseSale.csv', sep=';', index=False)

def filterEncomendaveisSale():
    df = fc.readCSV('shopify_csv/sale/baseSale.csv', sep=';')

    #drop rows that totalInventory is 0
    df = df[df['totalInventory'] != 0].reset_index(drop=True)

    #totalInventory and totalVariants to float
    df['totalInventory'] = df['totalInventory'].astype(float)
    df['totalVariants'] = df['totalVariants'].astype(float)


    #drop rows that totalInventory divided by totalVariants is equal to 1
    #df = df[df['totalInventory']%df['totalVariants'] != 1].reset_index(drop=True)


    #compare if totalInventory divided by totalVariants is greater than 1 and save in two different dataframes
    dfAlt = df[df['totalInventory']/df['totalVariants'] != 5].reset_index(drop=True)
    dfNaoAlt = df[df['totalInventory']/df['totalVariants'] == 5].reset_index(drop=True)

    #save dfAlt and dfNaoAlt in csv
    dfAlt.to_csv('shopify_csv/sale/sale_tag.csv', sep=';', index=False)
    dfNaoAlt.to_csv('shopify_csv/sale/sale_sem_tag.csv', sep=';', index=False)

def verify_last_cycle_sale():
    #get natal_tag.csv
    dfAlt = fc.readCSV('shopify_csv/sale/sale_tag.csv', sep=';')
    base = fc.readCSV('shopify_csv/sale/base_sale_tag.csv', sep=';')

    #get rows that are in dfAlt and not in base
    dfAlt2 = dfAlt[~dfAlt['product_id'].isin(base['product_id'])].reset_index(drop=True)

    #get rows that are in base and not in dfAlt
    base2 = base[~base['product_id'].isin(dfAlt['product_id'])].reset_index(drop=True)

    #if dfAlt2 is empty, do nothing, else, append to base
    if dfAlt2.empty:
        print('Não há produtos para atualizar')
    else:
        #asyncio.run(gp.update_price_black(dfAlt2))
        frames = [base, dfAlt2]
        base = pd.concat(frames)
        print('Produtos para atualizar tag')
        updateMetafieldSale(dfAlt2)


    #if base2 is empty, do nothing, else, remove from base
    if base2.empty:
        print('Não tags para remover')
    else:
        #return_price(base2)
        print('Produtos para remover tag')
        base = base[~base['product_id'].isin(base2['product_id'])].reset_index(drop=True)
        # removeMetafieldSale(base2)
        remove_metafield_sale(base2)

    #save base in csv
    base.to_csv('shopify_csv/sale/base_sale_tag.csv', sep=';', index=False)

def getEmEstoqueProducts():
    dfCapta = fc.readCSV('capta_csv/fEstoque.csv', sep=';')
    dfShopify = fc.readCSV('shopify_csv/product_Sku.csv', sep=';')
    #drop duplicates
    dfCapta = dfCapta.drop_duplicates(subset=['Cod_Prod'], keep='first').reset_index(drop=True)
    #filter ['Cod_Prod']['IsActive'] columns
    dfCapta = dfCapta[['Cod_Prod']]
    # dfCapta['IsActive'] = False
    dfShopify = dfShopify[['sku_2', 'product_id']]
    dfShopify.drop_duplicates(subset=['sku_2'], keep='first').reset_index(drop=True)
    #merge
    dfCapta = pd.merge(dfCapta, dfShopify, how='left', left_on='Cod_Prod', right_on='sku_2')

    #remove rows that are empty on sku_2 column
    dfCapta = dfCapta[dfCapta['sku_2'].notna()].reset_index(drop=True)

    dfCapta = dfCapta.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)

    fc.saveCSV(dfCapta, 'shopify_csv/pronta_entrega/prontaEntrega.csv', ';')

def checkNewProntaEntrega():
    df = fc.readCSV('shopify_csv/pronta_entrega/prontaEntrega.csv', sep=';')

    #get csv from shopify
    df2 = fc.readCSV('shopify_csv/pronta_entrega/prontaEntrega_base.csv', sep=';')

    #get rows that are different from df2
    df3 = df[~df.apply(tuple,1).isin(df2.apply(tuple,1))].reset_index(drop=True)

    #get rows that are in df2 and not in df
    df4 = df2[~df2.apply(tuple,1).isin(df.apply(tuple,1))].reset_index(drop=True)
    df3['IsActive'] = True
    df4['IsActive'] = False
    #safe df3 in csv
    df3.to_csv('shopify_csv/pronta_entrega/prontaEntrega_new.csv', sep=';', index=False)
    # df4.to_csv('shopify_csv/pronta_entrega/prontaEntrega_remove.csv', sep=';', index=False)

    if df4.empty:
        print('Sem valores false')
    else:
        print('Pronta Entrega para remover')
        asyncio.run(gp.update_metafield_product_pronta_entrega(df4, 'False'))
        #save df in csv
        df4.to_csv('shopify_csv/pronta_entrega/prontaEntrega_remove.csv', sep=';', index=False)

    if df3.empty:
        print('Pronta Entrega em dia')
    else:
        print('Pronta Entrega para atualizar')
        asyncio.run(gp.update_metafield_product_pronta_entrega(df3, 'True'))
        #save df in csv
        df.to_csv('shopify_csv/pronta_entrega/prontaEntrega_base.csv', sep=';', index=False)
        df3.to_csv('shopify_csv/pronta_entrega/prontaEntrega_new.csv', sep=';', index=False)
