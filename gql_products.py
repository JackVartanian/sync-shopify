import os
import asyncio
import aiohttp
import funcoes_comuns as fc
import funcoes_capta as funcoes_capta
import pandas as pd
import json
import requests
import time
import nest_asyncio
from dotenv import load_dotenv
nest_asyncio.apply()
load_dotenv()

# Configure store details (via .env)
# ATENCAO: este modulo usa um token proprio (SHOPIFY_ADMIN_API_KEY_PRODUCTS),
# que no codigo original era diferente do usado nos outros modulos.
shop_url = os.getenv('SHOPIFY_SHOP_URL')
admin_api_key = os.getenv('SHOPIFY_ADMIN_API_KEY_PRODUCTS') or os.getenv('SHOPIFY_ADMIN_API_KEY')
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


def add_suffix(cod_produto):
    if cod_produto.startswith('AN') or cod_produto.startswith('AL'):
        suffixes = ['-10', '-11', '-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20', '-21', '-22', '-23', '-24', '-25', '-26']
        return [cod_produto + suffix for suffix in suffixes]
    else:
        return [cod_produto]


def query_searchProductSKU():

    query = """query searchProductsSKU($searchQuery: String!) {
                products(first: 3, query: $searchQuery) {
                    edges {
                    node {
                        id
                        title
                        images(first: 1) {
                        edges {
                            node {
                            url
                            }
                        }
                        }
                        variants(first: 14) {
                        edges {
                            node {
                            sku
                            id
                            title
                            price
                            }
                        }
                        }

                    }
                    }
                }
                }"""

    return query


def query_searchProductVariants():

    query = """query searchProductsSKU($searchQuery: String!) {
                productVariants(first: 15, query: $searchQuery) {
                    edges {
                    node {
                        product {
                        id
                        title
                        totalInventory
                        totalVariants
                        mediaCount
                        images(first: 1) {
                            edges {
                            node {
                                url
                            }
                            }
                        }
                        variants(first: 15) {
                            edges {
                            node {
                                id
                                sku
                                title
                                price
                            }
                            }
                        }
                        }
                        id
                        sku
                        title
                        price
                    }
                    }
                }
                }"""

    return query


def variables_searchProductSKU(sku):

    inputs = {
        "searchQuery": "sku:"+str(sku)
        }

    return inputs


async def get_product_Sku(df):

    product_SkuDf = fc.readCSV('shopify_csv/product_Sku.csv', sep=';')
    df = df[~df['Cod. Prod.'].isin(product_SkuDf['Cod_Produto'])].reset_index(drop=True)

    productDict = {
        'Cod_Produto': [],
        'Id_Product': [],
        'Title_Product': [],
        'image_url': [],
        'Sku': [],
        'Id_Variant': [],
        'Title_Variant': [],
        'Price': []
        }

    query = query_searchProductSKU()

    for i in range(len(df)):

        try:
            inputs = variables_searchProductSKU(df['Cod. Prod.'].iloc[i])

            data = {
                'query': query,
                'variables': inputs
            }

            res = await fetch_data(url, headers, data)

            noProducts = len(res['data']['products']['edges'])
            qtdProdutos = len(res['data']['products']['edges'])

            if qtdProdutos > 0:
                noImages = len(res['data']['products']['edges'][0]['node']['images']['edges'])
                qtdVariants = len(res['data']['products']['edges'][0]['node']['variants']['edges'])

            if noProducts == 0:
                print('Não esta no Shopify: ', noProducts, ' - Cod_Produto: ', df['Cod. Prod.'].iloc[i])

                productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                productDict['Id_Product'].append('')
                productDict['Title_Product'].append('')
                productDict['image_url'].append('')
                productDict['Sku'].append('')
                productDict['Id_Variant'].append('')
                productDict['Title_Variant'].append('')
                productDict['Price'].append('')

            elif noImages == 0 and qtdProdutos == 1 and qtdVariants == 1:

                print( 'Sem imagem, 1 produto, 1 Variante' ,'Qtd produtos: , ', qtdProdutos, 'Qtd Variants',  qtdVariants, ' SKU: ', df['Cod. Prod.'].iloc[i])

                productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                productDict['Id_Product'].append(res['data']['products']['edges'][0]['node']['id'])
                productDict['Title_Product'].append(res['data']['products']['edges'][0]['node']['title'])
                productDict['image_url'].append('')
                productDict['Sku'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['sku'])
                productDict['Id_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['id'])
                productDict['Title_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['title'])
                productDict['Price'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['price'])

            elif noImages == 0 and qtdProdutos > 1 and qtdVariants == 1:

                print( 'Sem imagem, +1 produto, 1 Variante' ,'Qtd produtos: , ', qtdProdutos, 'Qtd Variants',  qtdVariants, ' SKU: ', df['Cod. Prod.'].iloc[i])

                for qtt in range(qtdProdutos):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['products']['edges'][qtt]['node']['id'])
                    productDict['Title_Product'].append(res['data']['products']['edges'][qtt]['node']['title'])
                    productDict['image_url'].append('')
                    productDict['Sku'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['title'])
                    productDict['Price'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['price'])

            elif noImages > 0 and qtdProdutos >= 1 and qtdVariants == 1:

                print( 'Com imagem, +1 produto, 1 Variante' ,'Qtd produtos: , ', qtdProdutos, 'Qtd Variants',  qtdVariants, ' SKU: ', df['Cod. Prod.'].iloc[i])

                for qtt in range(qtdProdutos):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['products']['edges'][qtt]['node']['id'])
                    productDict['Title_Product'].append(res['data']['products']['edges'][qtt]['node']['title'])
                    productDict['image_url'].append(res['data']['products']['edges'][0]['node']['images']['edges'][0]['node']['url'])
                    productDict['Sku'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['title'])
                    productDict['Price'].append(res['data']['products']['edges'][qtt]['node']['variants']['edges'][0]['node']['price'])

            elif noImages == 0 and qtdVariants >= 1:

                print( 'Sem imagem, +1 Variante' , 'Qtd Variants',  qtdVariants, ' SKU: ', df['Cod. Prod.'].iloc[i])

                for qttv in range(qtdVariants):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['products']['edges'][0]['node']['id'])
                    productDict['Title_Product'].append(res['data']['products']['edges'][0]['node']['title'])
                    productDict['image_url'].append('')
                    productDict['Sku'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['title'])
                    productDict['Price'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['price'])

            elif noImages > 0 and qtdVariants >= 1:

                print( 'Com imagem, +1 Variante' , 'Qtd Variants',  qtdVariants, ' SKU: ', df['Cod. Prod.'].iloc[i])

                for qttv in range(qtdVariants):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['products']['edges'][0]['node']['id'])
                    productDict['Title_Product'].append(res['data']['products']['edges'][0]['node']['title'])
                    productDict['image_url'].append(res['data']['products']['edges'][0]['node']['images']['edges'][0]['node']['url'])
                    productDict['Sku'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['title'])
                    productDict['Price'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][qttv]['node']['price'])

            else:

                print( 'ELSE', ' SKU: ', df['Cod. Prod.'].iloc[i], 'Qtd de produtos:', qtdProdutos, 'Qtd Variants',  qtdVariants, 'Qtd Images', noImages)

                print(res)

                productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                productDict['Id_Product'].append(res['data']['products']['edges'][0]['node']['id'])
                productDict['Title_Product'].append(res['data']['products']['edges'][0]['node']['title'])
                productDict['image_url'].append(res['data']['products']['edges'][0]['node']['images']['edges'][0]['node']['url'])
                productDict['Sku'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['sku'])
                productDict['Id_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['id'])
                productDict['Title_Variant'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['title'])
                productDict['Price'].append(res['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['price'])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Cod_Produto: ', df['Cod. Prod.'].iloc[i], 'Qtd de produtos:', noProducts )
            continue

    productDict_df = pd.DataFrame(productDict)
    df = pd.concat([product_SkuDf, productDict_df], ignore_index=True)
    df.to_csv('shopify_csv/product_Sku.csv', index=False, sep=';')

    return df


async def get_ProductVariants(df):

    inativos = funcoes_capta.produtosInativos()

    product_SkuDf = fc.readCSV('shopify_csv/product_Sku.csv', sep=';')
    product_SkuDf = product_SkuDf[product_SkuDf['Id_Product'] != ''].reset_index(drop=True)
    product_SkuDf = product_SkuDf.drop_duplicates(subset=['Cod_Produto'], keep='first').reset_index(drop=True)

    df = df[~df['Cod. Prod.'].isin(inativos['Cod. Prod.'])].reset_index(drop=True)
    df = df[~df['Cod. Prod.'].isin(product_SkuDf['Cod_Produto'])].reset_index(drop=True)

    print('Qtde de produtos para consultar: ', len(df))

    productDict = {
        'Cod_Produto': [],
        'Id_Product': [],
        'Title_Product': [],
        'image_url': [],
        'Sku': [],
        'Id_Variant': [],
        'Title_Variant': [],
        'Price': []
        }

    query = query_searchProductVariants()

    for i in range(len(df)):

        try:
            sku = add_suffix(df['Cod. Prod.'].iloc[i])
            qtdSkus = len(sku)

            print('Qtd de Skus: ', qtdSkus)

            for j in range(qtdSkus):

                variables = variables_searchProductSKU(sku[j])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                qtdProdutos = len(res['data']['productVariants']['edges'])

                if qtdProdutos > 0:
                    noImages = len(res['data']['productVariants']['edges'][0]['node']['product']['images']['edges'])
                    qtdVariants = len(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'])

                if qtdProdutos == 0:
                    print('Não esta no Shopify: ', '- Cod_Produto: ', df['Cod. Prod.'].iloc[i])

                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append('')
                    productDict['Title_Product'].append('')
                    productDict['image_url'].append('')
                    productDict['Sku'].append('')
                    productDict['Id_Variant'].append('')
                    productDict['Title_Variant'].append('')
                    productDict['Price'].append('')

                elif noImages == 0 and qtdVariants >= 1:

                    print( 'Sem imagem, +1 Variante' , 'Qtd Variants',  qtdVariants, ' SKU: ', sku[j], 'J', j)

                    # for qttv in range(qtdSkus):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['productVariants']['edges'][0]['node']['product']['id'])
                    productDict['Title_Product'].append(res['data']['productVariants']['edges'][0]['node']['product']['title'])
                    productDict['image_url'].append('')
                    productDict['Sku'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['title'])
                    productDict['Price'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['price'])

                elif noImages > 0 and qtdVariants >= 1:

                    print( 'Com imagem, +1 Variante' , 'Qtd Variants',  qtdVariants, ' SKU: ', sku[j], 'J', j)

                    # for qttv in range(qtdSkus):
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['productVariants']['edges'][0]['node']['id'])
                    productDict['Title_Product'].append(res['data']['productVariants']['edges'][0]['node']['title'])
                    productDict['image_url'].append(res['data']['productVariants']['edges'][0]['node']['product']['images']['edges'][0]['node']['url'])
                    productDict['Sku'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['title'])
                    productDict['Price'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['price'])

                else:

                    print( 'ELSE', ' SKU: ', sku[j], 'Qtd de produtos:', qtdProdutos, 'Qtd Variants',  qtdVariants, 'Qtd Images', noImages)
                    productDict['Cod_Produto'].append(df['Cod. Prod.'].iloc[i])
                    productDict['Id_Product'].append(res['data']['productVariants']['edges'][0]['node']['id'])
                    productDict['Title_Product'].append(res['data']['productVariants']['edges'][0]['node']['title'])
                    productDict['image_url'].append(res['data']['productVariants']['edges'][0]['node']['product']['images']['edges'][0]['node']['url'])
                    productDict['Sku'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['sku'])
                    productDict['Id_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['id'])
                    productDict['Title_Variant'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['title'])
                    productDict['Price'].append(res['data']['productVariants']['edges'][0]['node']['product']['variants']['edges'][j]['node']['price'])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage, i, ' - Cod_Produto: ', sku[j])
            continue

    productDict_df = pd.DataFrame(productDict)
    df = pd.concat([product_SkuDf, productDict_df], ignore_index=True)
    df.to_csv('shopify_csv/product_Sku.csv', index=False, sep=';')

    return print(df.shape)


async def get_products():

    data = {
            "query": """
            query {
                    products(first: 10, reverse: true) {
                      edges {
                        node {
                          id
                          productCategory {
                            productTaxonomyNode {
                              fullName
                              id
                              name
                            }
                          }
                          productType
                          inCollection: collections(first: 1) {
                            edges {
                              node {
                                id
                                title
                                handle
                              }
                            }
                          }
                          title
                          description
                          handle
                          tags
                          }
                        }
                      }
                    }
        """}

    res = await fetch_data(url, headers, data)

    productTaxonomyNode = [edge['node']['productCategory']['productTaxonomyNode'] for edge in res['data']['products']['edges']]
    productTaxonomyNodeDf = pd.DataFrame(productTaxonomyNode)
    productTaxonomyNodeDf = productTaxonomyNodeDf.drop(['fullName'], axis=1)
    productTaxonomyNodeDf = productTaxonomyNodeDf.rename(columns={'id': 'category_id', 'name': 'category_name'})

    inCollectionNode = [edge['node']['inCollection']['edges'][0]['node'] for edge in res['data']['products']['edges']]
    inCollectionNodeDf = pd.DataFrame(inCollectionNode)
    inCollectionNodeDf = inCollectionNodeDf.rename(columns={'id': 'collection_id', 'title': 'collection_title', 'handle': 'collection_handle'})

    productNodes = [edge['node'] for edge in res['data']['products']['edges']]
    productNodesDf = pd.DataFrame(productNodes)
    productNodesDf = productNodesDf.drop(['productCategory', 'inCollection'], axis=1)
    productNodesDf = productNodesDf.rename(columns={'id': 'product_id', 'title': 'product_title', 'description': 'product_description', 'handle': 'product_handle'})

    df = pd.concat([productNodesDf, productTaxonomyNodeDf, inCollectionNodeDf], axis=1)

    return df


def load_csv(sheet):

    collections = fc.readCSV(f'shopify_csv/collections.csv', ';')
    collections = collections.rename(columns={'id': 'collection_id'})
    collections = collections[['collection_id', 'title']]

    products = fc.readExcelSheet('capta_csv/para_cadastrar.xlsx', sheet=sheet)
    products['Title'] = products['Title'].str.title()
    products['Collections'] = products['Collections'].str.title()
    products['Categoria'] = products['Categoria'].str.title()
    products['productType'] = products['productType'].str.title()
    products['Pedras'] = products['Pedras'].str.title()
    products['Cobertura'] = products['Cobertura'].str.title()
    products['Metal'] = products['Metal'].str.title()
    products['handle'] = products['handle'].str.title()

    df = pd.merge(products, collections, how='left', left_on='Collections', right_on='title')
    df['Pedra'] = df['Pedras'].str.split(' E ')
    df = df.explode('Pedras')
    df = df.drop(['Pedras'], axis=1)
    df = df.rename(columns={'Pedra': 'Pedras'})

    df['categoryId'] = df['categoryId'].astype(str)
    df['Price'] = df['Price'].astype(str)
    df['count'] = df['Pedras'].str.len()

    df['Collections'] = df['Collections'].str.replace('Jv Man', 'JV MAN', case=False)
    df['Title'] = df['Title'].str.replace('Jv Man', 'JV MAN', case=False)

    df['Collections'] = df['Collections'].str.replace('Jv Man Ii', 'JV MAN II', case=False)
    df['Title'] = df['Title'].str.replace('Jv Man Ii', 'JV MAN II', case=False)

    return df


def queryProduct():
    query = """mutation productCreate($input: ProductInput!) {
        productCreate(input: $input) {
            product {
                id
                title
                variants(first: 25) {
                    edges {
                    node {
                        id
                        sku
                        title
                        price
                    }
                    }
                }
                }
                userErrors {
                    field
                    message}}}"""
    return query


def variables_variants(row):

    title = str(row['Title']).split(' - ')[0]

    if row['QtyV'] == 2 and row['Pedras'][0] == 'Sem Pedra':

        print('Função variables_variants com 2 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['Variants'][0],
                        "price": str(row['Price']),
                        "options": row['Variants'][2]
                    },
                    {
                        "sku": row['Variants'][1],
                        "price": str(row['Price']),
                        "options": row['Variants'][3]
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": str(row['cuidados'])
                    }
                    ]
                }
            }
    elif row['QtyV'] == 3 and row['Pedras'][0] == 'Sem Pedra':

        print('Função variables_variants com 3 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['Variants'][0],
                        "price": str(row['Price']),
                        "options": row['Variants'][3]
                    },
                    {
                        "sku": row['Variants'][1],
                        "price": str(row['Price']),
                        "options": row['Variants'][4]
                    },
                    {
                        "sku": row['Variants'][2],
                        "price": str(row['Price']),
                        "options": row['Variants'][5]
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }
    elif row['QtyV'] == 2:

        print('Função variables_variants com 2 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['Variants'][0],
                        "price": str(row['Price']),
                        "options": row['Variants'][2]
                    },
                    {
                        "sku": row['Variants'][1],
                        "price": str(row['Price']),
                        "options": row['Variants'][3]
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }
    elif row['QtyV'] == 3:

        print('Função variables_variants com 3 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['Variants'][0],
                        "price": str(row['Price']),
                        "options": row['Variants'][3]
                    },
                    {
                        "sku": row['Variants'][1],
                        "price": str(row['Price']),
                        "options": row['Variants'][4]
                    },
                    {
                        "sku": row['Variants'][2],
                        "price": str(row['Price']),
                        "options": row['Variants'][5]
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    return variables


def variables_size(row):

    title = str(row['Title'])


    if row['Pedras'][0] == 'Sem Pedra':

        print('Função variables_size sem pedra')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": row['Tamanho']
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    elif row['count'] == 2:

        print('Função variables_size com 2 pedras')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": row['Tamanho']
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\", \"{row['Pedras'][1]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    else:

        print('Função variables_size com 1 pedra')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": row['Tamanho']
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }



    return variables


def variables_rings(row):

    title = str(row['Title'])

    if row['Pedras'][0] == 'Sem Pedra':

        print('Função variables_rings sem pedra')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU']+'-'+ str(10),
                        "price": str(row['Price']),
                        "options":"10"
                    },
                    {
                        "sku": row['SKU']+'-'+str(11),
                        "price": str(row['Price']),
                        "options": "11"
                    },
                    {
                        "sku": row['SKU']+'-'+str(12),
                        "price": str(row['Price']),
                        "options": "12"
                    },
                    {
                        "sku": row['SKU']+'-'+str(13),
                        "price": str(row['Price']),
                        "options": "13"
                    },
                    {
                        "sku": row['SKU']+'-'+str(14),
                        "price": str(row['Price']),
                        "options": "14"
                    },
                    {
                        "sku": row['SKU']+'-'+str(15),
                        "price": str(row['Price']),
                        "options": "15"
                    },
                    {
                        "sku": row['SKU']+'-'+str(16),
                        "price": str(row['Price']),
                        "options": "16"
                    },
                    {
                        "sku": row['SKU']+'-'+str(17),
                        "price": str(row['Price']),
                        "options": "17"
                    },
                    {
                        "sku": row['SKU']+'-'+str(18),
                        "price": str(row['Price']),
                        "options": "18"
                    },
                    {
                        "sku": row['SKU']+'-'+str(19),
                        "price": str(row['Price']),
                        "options": "19"
                    },
                    {
                        "sku": row['SKU']+'-'+str(20),
                        "price": str(row['Price']),
                        "options": "20"
                    },
                    {
                        "sku": row['SKU']+'-'+str(21),
                        "price": str(row['Price']),
                        "options": "21"
                    },
                    {
                        "sku": row['SKU']+'-'+str(22),
                        "price": str(row['Price']),
                        "options": "22"
                    },
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    elif row['count'] == 2:

        print('Função variables_rings com 2 pedras')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU']+'-'+str(10),
                        "price": str(row['Price']),
                        "options":"10"
                    },
                    {
                        "sku": row['SKU']+'-'+str(11),
                        "price": str(row['Price']),
                        "options": "11"
                    },
                    {
                        "sku": row['SKU']+'-'+str(12),
                        "price": str(row['Price']),
                        "options": "12"
                    },
                    {
                        "sku": row['SKU']+'-'+str(13),
                        "price": str(row['Price']),
                        "options": "13"
                    },
                    {
                        "sku": row['SKU']+'-'+str(14),
                        "price": str(row['Price']),
                        "options": "14"
                    },
                    {
                        "sku": row['SKU']+'-'+str(15),
                        "price": str(row['Price']),
                        "options": "15"
                    },
                    {
                        "sku": row['SKU']+'-'+str(16),
                        "price": str(row['Price']),
                        "options": "16"
                    },
                    {
                        "sku": row['SKU']+'-'+str(17),
                        "price": str(row['Price']),
                        "options": "17"
                    },
                    {
                        "sku": row['SKU']+'-'+str(18),
                        "price": str(row['Price']),
                        "options": "18"
                    },
                    {
                        "sku": row['SKU']+'-'+str(19),
                        "price": str(row['Price']),
                        "options": "19"
                    },
                    {
                        "sku": row['SKU']+'-'+str(20),
                        "price": str(row['Price']),
                        "options": "20"
                    },
                    {
                        "sku": row['SKU']+'-'+str(21),
                        "price": str(row['Price']),
                        "options": "21"
                    },
                    {
                        "sku": row['SKU']+'-'+str(22),
                        "price": str(row['Price']),
                        "options": "22"
                    },
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\", \"{row['Pedras'][1]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    elif row['count'] == 1:

        print('Função variables_rings com 1 pedra')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Size",
                "variants": [
                    {
                        "sku": row['SKU']+'-'+str(10),
                        "price": str(row['Price']),
                        "options":"10"
                    },
                    {
                        "sku": row['SKU']+'-'+str(11),
                        "price": str(row['Price']),
                        "options": "11"
                    },
                    {
                        "sku": row['SKU']+'-'+str(12),
                        "price": str(row['Price']),
                        "options": "12"
                    },
                    {
                        "sku": row['SKU']+'-'+str(13),
                        "price": str(row['Price']),
                        "options": "13"
                    },
                    {
                        "sku": row['SKU']+'-'+str(14),
                        "price": str(row['Price']),
                        "options": "14"
                    },
                    {
                        "sku": row['SKU']+'-'+str(15),
                        "price": str(row['Price']),
                        "options": "15"
                    },
                    {
                        "sku": row['SKU']+'-'+str(16),
                        "price": str(row['Price']),
                        "options": "16"
                    },
                    {
                        "sku": row['SKU']+'-'+str(17),
                        "price": str(row['Price']),
                        "options": "17"
                    },
                    {
                        "sku": row['SKU']+'-'+str(18),
                        "price": str(row['Price']),
                        "options": "18"
                    },
                    {
                        "sku": row['SKU']+'-'+str(19),
                        "price": str(row['Price']),
                        "options": "19"
                    },
                    {
                        "sku": row['SKU']+'-'+str(20),
                        "price": str(row['Price']),
                        "options": "20"
                    },
                    {
                        "sku": row['SKU']+'-'+str(21),
                        "price": str(row['Price']),
                        "options": "21"
                    },
                    {
                        "sku": row['SKU']+'-'+str(22),
                        "price": str(row['Price']),
                        "options": "22"
                    },
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    return variables


def variables_pendants(row):

    title = str(row['Title'])

    if row['Pedras'][0] == 'Sem Pedra':

        print('Função variables_pendants sem pedra')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Style",
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options":"A"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "B"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "C"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "D"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "E"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "F"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "G"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "H"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "I"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "J"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "K"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "L"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "M"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options":"N"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "O"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "P"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Q"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "R"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "S"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "T"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "U"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "V"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "W"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "X"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Y"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Z"
                    }

                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    elif row['QtyV'] == 23:

        print('Função variables_pendants com 23 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Style",
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options":"A"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "B"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "C"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "D"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "E"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "F"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "G"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "H"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "I"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "J"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "K"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "L"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "M"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options":"N"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "O"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "P"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Q"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "R"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "S"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "T"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "U"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "V"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "W"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "X"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Y"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Z"
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    elif row['QtyV'] == 9:

        print('Função variables_pendants com 9 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Style",
                "variants": [
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options":"A"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "B"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "C"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "D"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "E"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "F"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "G"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "H"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "I"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "J"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "K"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "L"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "M"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options":"N"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "O"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "P"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Q"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "R"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "S"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "T"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "U"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "V"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "W"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "X"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Y"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "Z"
                    # }
                    ]
                }
            }

    elif row['QtyV'] == 8:

        print('Função variables_pendants com 8 variantes')

        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "options": "Style",
                "variants": [
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options":"A"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "B"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "C"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "D"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "E"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "F"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "G"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "H"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "I"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "J"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "K"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "L"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "M"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options":"N"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "O"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "P"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Q"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "R"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "S"
                    # },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "T"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "U"
                    },
                    # {
                    #     "sku": row['SKU'],
                    #     "price": str(row['Price']),
                    #     "options": "V"
                    # },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "W"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "X"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Y"
                    },
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                        "options": "Z"
                    }
                    ]
                }
            }

    return variables


def variables_pedras(row):

    title = str(row['Title'])

    print('Função variables_pedras')

    if row['count'] == 2:
        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                    }
                    ],

                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\", \"{row['Pedras'][1]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }
    else:
        variables = {
            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                    }
                    ],

                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }

    return variables


def variables_sem_pedras(row):

    title = str(row['Title'])

    print('Função variables_sem_pedras')

    variables = {
        "input": {
            "title": title,
            "descriptionHtml": row['descriptionHtml'],
            "productCategory": {
                "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                },
            "productType": row['productType'],
            "status": "DRAFT",
            "handle": row['handle'],
            "collectionsToJoin": [
                "gid://shopify/Collection/453681479975",
                row['collection_id']
                ],
            "seo": {
                # "description": "SEO Description",
                "title": title
                },
            "variants": [
                {
                    "sku": row['SKU'],
                    "price": str(row['Price']),
                }
                ],

            "metafields": [
                {
                    "key": "genero",
                    "namespace": "custom",
                    "type": "list.single_line_text_field",
                    "value": f"[\"{row['Genero']}\"]"
                    },
                {
                    "key": "metal",
                    "namespace": "custom",
                    "type":"single_line_text_field",
                    "value": row['Metal']
                    },
                {
                    "key": "cobertura",
                    "namespace": "custom",
                    "type":"single_line_text_field",
                    "value": row['Cobertura']
                    },
                {
                    "key": "cuidadospeca",
                    "namespace": "custom",
                    "type":"multi_line_text_field",
                    "value": row['cuidados']
                }
                ]
            }
        }

    return variables


def variables_default(row):

    title = str(row['Title'])

    print('Função variables_default')

    variables = {

            "input": {
                "title": title,
                "descriptionHtml": row['descriptionHtml'],
                "productCategory": {
                    "productTaxonomyNodeId": "gid://shopify/ProductTaxonomyNode/" + str(row['categoryId'])
                    },
                "productType": row['productType'],
                "status": "DRAFT",
                "handle": row['handle'],
                "collectionsToJoin": [
                    "gid://shopify/Collection/453681479975",
                    row['collection_id']
                    ],
                "seo": {
                    # "description": "SEO Description",
                    "title": title
                    },
                "variants": [
                    {
                        "sku": row['SKU'],
                        "price": str(row['Price']),
                    }
                    ],
                "metafields": [
                    {
                        "key": "genero",
                        "namespace": "custom",
                        "type": "list.single_line_text_field",
                        "value": f"[\"{row['Genero']}\"]"
                        },
                    {
                        "key": "metal",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Metal']
                        },
                    {
                        "key": "cobertura",
                        "namespace": "custom",
                        "type":"single_line_text_field",
                        "value": row['Cobertura']
                        },
                    {
                        "key": "pedra",
                        "namespace": "custom",
                        "type":"list.single_line_text_field",
                        "value":f"[\"{row['Pedras'][0]}\"]"
                        },
                    {
                        "key": "cuidadospeca",
                        "namespace": "custom",
                        "type":"multi_line_text_field",
                        "value": row['cuidados']
                    }
                    ]
                }
            }
    return variables


def prepare_variables(row):

    if row['Categoria'] == 'Anel' or row['Categoria'] == 'Alianca':
        variables = variables_rings(row)
    # elif row['QtyV'] != '' and row['Tamanho'] != '':
    #     variables = variables_variants(row)
    # elif row['QtyV'] != '':
    #     variables = variables_pendants(row)
    elif row['Tamanho'] != '':
        variables = variables_size(row)
    elif row['Pedras'][0] == 'Sem Pedra':
        variables = variables_sem_pedras(row)
    elif row['count'] == 2:
        variables = variables_pedras(row)
    elif row['count'] == 1:
        variables = variables_pedras(row)
    else:
        variables = variables_default(row)

    return variables


async def createProducts(df):

    print('Iniciando a criação dos produtos\n')

    async with sem:

        inativos = funcoes_capta.produtosInativos()

        shopify_products = fc.readCSV('shopify_csv/product_Sku.csv', sep=';')
        shopify_products = shopify_products[shopify_products['product_id'] != ''].reset_index(drop=True)
        shopify_products = shopify_products.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
        shopify_products['sku_2'] = shopify_products['sku'].str.split('-').str[0]

        df = df[~df['SKU'].isin(shopify_products['sku_2'])].reset_index(drop=True)
        df = df[~df['SKU'].isin(inativos['Cod. Prod.'])].reset_index(drop=True)

        print('Quantidade de produtos a serem criados: ', df.__len__() ,'\n')

        productsDict = {
            'Cod_Produto': [],
            'Id': [],
            'Title': [],
            'Sku': [],
            'Id_Variant': [],
            'Title_Variant': [],
            'Price': [],
        }

        productsErrorDict = {
            'Cod_Produto': [],
            'Message_Error': []
        }

        query = queryProduct()

        for i in range(len(df)):

            try:
                variables = prepare_variables(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                print('Resposta:', df.iloc[i]['SKU'], res, '\n')

                productId = res['data']['productCreate']['product']['id']

                await updateChannels(productId)

                if res['data']['productCreate']['userErrors']:

                    productsErrorDict['Cod_Produto'].append(df.iloc[i]['SKU'])
                    productsErrorDict['Message_Error'].append(res['data']['productCreate']['userErrors'][0]['message'])

                    print('Linha: ', i,' - Cod_Produto: ', df.iloc[i]['SKU'] ,' - Erro: ', res['data']['productCreate']['userErrors'][0]['message'], '\n')
                else:
                    productsDict['Cod_Produto'].append(df.iloc[i]['SKU'])
                    productsDict['Id'].append(res['data']['productCreate']['product']['id'])
                    productsDict['Title'].append(res['data']['productCreate']['product']['title'])
                    productsDict['Sku'].append(res['data']['productCreate']['product']['variants']['edges'][0]['node']['sku'])
                    productsDict['Id_Variant'].append(res['data']['productCreate']['product']['variants']['edges'][0]['node']['id'])
                    productsDict['Title_Variant'].append(res['data']['productCreate']['product']['variants']['edges'][0]['node']['title'])
                    productsDict['Price'].append(res['data']['productCreate']['product']['variants']['edges'][0]['node']['price'])

                    print(i,' - Cod_Produto: ', df.iloc[i]['SKU'] ,' - Name: ', df.iloc[i]['Title'], ' - Qtd_Linhas: ', productsDict['Cod_Produto'].__len__(), '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)


async def updateChannels(product_id):

    query = """mutation productPublishablePublish($id: ID!, $input: [PublicationInput!]!) {
        publishablePublish(id: $id, input: $input) {
                userErrors {
                    field
                    message}}}"""

    variables1 = {
        "id": str(product_id),
        "input":
            {
                "publicationId": "gid://shopify/Publication/178667192615"
                }
        }

    data1 = {
            'query': query,
            'variables': variables1
            }

    res = await fetch_data(url, headers, data1)

    variables2 = {
        "id": str(product_id),
        "input":
            {
                "publicationId": "gid://shopify/Publication/178667258151"
                }
        }

    data2 = {
                    'query': query,
                    'variables': variables2
                }

    res = await fetch_data(url, headers, data2)

    variables3 = {
        "id": str(product_id),
        "input":
            {
                "publicationId": "gid://shopify/Publication/178667290919"
                }
        }

    data3 = {
                    'query': query,
                    'variables': variables3
                }

    res = await fetch_data(url, headers, data3)

    variables4 = {
        "id": str(product_id),
        "input":
            {
                "publicationId": "gid://shopify/Publication/178667421991"
                }
        }

    data4 = {
                    'query': query,
                    'variables': variables4
                }

    res = await fetch_data(url, headers, data4)

    variables5 = {
        "id": str(product_id),
        "input":
            {
                "publicationId": "gid://shopify/Publication/178667520295"
                }
        }

    data5 = {
                    'query': query,
                    'variables': variables5
                }

    res = await fetch_data(url, headers, data5)

    return


def cuidadoOuro():

    texto = "Evite o contato de uma joia com a outra. Guarde-as separadamente nas embalagens fornecidas pela Jack Vartanian;\
            Com o uso, fechos e tarraxas podem necessitar de ajustes para que fiquem com a pressão adequada. Entre em contato conosco;\
            Após o uso, aconselhamos limpar a joia com flanela de algodão para tirar possíveis resíduos de produtos como maquiagem e perfume;\
            Evite o contato com água do mar, cremes, perfumes e produtos químicos."

    return texto


def cuidadoPrata():

    texto = "Evite o contato de uma joia com a outra. Guarde-as separadamente nas embalagens fornecidas pela Jack Vartanian;\
            Com o uso, fechos e tarraxas podem necessitar de ajustes para que fiquem com a pressão adequada. Entre em contato conosco;\
            Após o uso, aconselhamos limpar a joia com flanela de algodão para tirar possíveis resíduos de produtos como maquiagem e perfume;\
            Evite o contato com água do mar, cremes, perfumes e produtos químicos;\
            Para peças em prata o primeiro banho é cortesia;\
            Para peças ocas, evite atritos ou batidas."

    return texto


async def deleteProduct(df):

    query = """mutation productDelete($input: ProductDeleteInput!) {
                productDelete(input: $input) {
                    userErrors {
                    field
                    message
                    }
                }
                }"""

    for i in range(len(df)):

        variables = {
                "input": {
                    "id": df['id'].iloc[i]
                    }}
        data = {
                "query": query,
                "variables": variables
            }

        res = await fetch_data(url, headers, data)
        print(res)


def query_update_template():

    mutation = """ mutation productUpdate($input: ProductInput!) {
                    productUpdate(input: $input) {
                        product {
                        id
                        templateSuffix
                        }
                    }
                    } """
    return mutation


def variable_update_template(row):

    variables = {
        "input": {
            "id": str(row['product_id']),
            "templateSuffix": "aneis"
            }
        }

    return variables


async def update_templates(df):

    query = query_update_template()

    for i in range(len(df)):

        try:
            variables = variable_update_template(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


def query_update_composicao():

    mutation = """ mutation metafieldComposicao($inputData: ProductInput!) {
        productUpdate(input: $inputData) {
            product {
                id
                title
                }
                }
                }"""
    return mutation


def variable_update_composicao(row):

    variables = {
        "inputData":{
            "id": str(row['product_id']),
            "metafields": [
                {
                    "key": "composicao_text",
                    "namespace": "custom",
                    "type": "multi_line_text_field",
                    "value": str(row['composicao'])
                        }]}}

    return variables


async def update_composicao(df):

    query = query_update_composicao()

    for i in range(len(df)):

        try:
            variables = variable_update_composicao(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Resposta: ', res)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


def query_update_metal():

    mutation = """ mutation productUpdateMetal($input: ProductInput!) {
                    productUpdate(input: $input) {
                        userErrors {
                        field
                        message
                        }
                        product {
                        id
                        title
                        }
                    }
                    } """
    return mutation


def variable_update_metal(row):

    variables = {
                "input": {
                    "metafields": [
                    {   "namespace": "custom",
                        "key": "metal_filters",
                        "type": "list.single_line_text_field",
                        "value": str("[\"OURO\"]")
                    }
                    ],
                    "id": str(row['product_id'])
                }
                }

    return variables


async def update_metal(df):

    query = query_update_metal()

    for i in range(len(df)):

        try:
            variables = variable_update_metal(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Resposta: ', res)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


def query_update_grupo():

    mutation = """ mutation productUpdateMetal($input: ProductInput!) {
                    productUpdate(input: $input) {
                        userErrors {
                        field
                        message
                        }
                        product {
                        id
                        title
                        }
                    }
                    } """
    return mutation


def variable_update_grupo(row):

    variables = {
                "input": {
                    "id": str(row['product_id']),
                    "metafields": [
                    {
                        "key": "categoria",
                        "namespace": "custom",
                        "type": "single_line_text_field",
                        "value": str(row['grupo'])}]}}

    return variables


async def update_grupo(df):

    query = query_update_grupo()

    for i in range(len(df)):

        try:
            variables = variable_update_grupo(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Resposta: ', res)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


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
                        mediaCount
                        metafields(first: 10, namespace: "custom") {
                            edges {
                                node {
                                    id
                                    key
                                    namespace
                                    type
                                    value
                                    }
                                    }
                                    }
                        }
                        id
                        sku
                        title
                        price
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

def run_query_default(query):

        response = requests.post(url, json={'query': query}, headers=headers)

        if response.status_code == 200:
            return response.json()
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


def read_url_productVariants(url):

    df = pd.read_json(url, lines=True)
    df.rename(columns={'inventoryQuantity':'Inventario'}, inplace=True)
    df_product = pd.json_normalize(df['product'])
    df_product.rename(columns={'id':'product_id'}, inplace=True)
    df2 = pd.concat([df, df_product], axis=1)
    df2.drop(columns='product', inplace=True)

    df2 = df2[df2['product_id'] != ''].reset_index(drop=True)
    df3 = df2
    df3['sku_2'] = df3['sku'].str.split('-').str[0]
    fc.saveCSV(df3, 'shopify_csv/product_test_Sku.csv', sep=';')
    df2 = df2.drop_duplicates(subset=['product_id'], keep='first').reset_index(drop=True)
    df2['sku_2'] = df2['sku'].str.split('-').str[0]

    fc.saveCSV(df2, 'shopify_csv/product_Sku.csv', sep=';')

    return df2


def read_url_productMetal(url):

    df = pd.read_json(url, lines=True)

    fc.saveCSV(df, 'shopify_csv/productMetal.csv', sep=';')

    return df


def run_query_productVariants():

    print('\nIniciando requisição productVariants...')

    mutation = query_productVariants()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_productVariants(url)

    return df


def run_query_productMetal():

    print('\nIniciando requisição productMetal...')

    mutation = query_productMetal()
    bulkId = run_query(mutation)
    url = retrieve_bulkOperation(bulkId)
    df = read_url_productMetal(url)

    return df


def query_update_price():
    return """
    mutation UpdateVariantPrices($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        productVariants {
          id
          sku
          title
          price
          compareAtPrice
        }
        userErrors {
          field
          message
        }
      }
    }
    """

def query_update_composition_title_description():
    return """
    mutation UpdateProdAndMeta($input: ProductInput!, $metafields: [MetafieldsSetInput!]!) {
      productUpdate(input: $input) {
        product {
          id
          title
          descriptionHtml
        }
        userErrors {
          field
          message
        }
      }
      metafieldsSet(metafields: $metafields) {
        metafields {
          id
          namespace
          key
          value
        }
        userErrors {
          field
          message
        }
      }
    }
    """


def variable_update_price(row):
    variables = {
        "productId": str(row["product_id"]),
        "variants": [
            {
                "id": str(row["id"]),
                "price": f'{float(row["priceCapta"]):.2f}'
            }
        ]
    }
    return variables

def variable_update_composition_title_description(row):
    # helper para transformar NaN/None/"nan" em string vazia
    def to_clean_str(v):
        if pd.isna(v):
            return ""
        s = str(v).strip()
        return "" if s.lower() == "nan" else s


    title_capta = to_clean_str(row.get('tituloCapta'))
    desc_capta  = to_clean_str(row.get('descricaoCaptaBR'))
    comp_capta  = to_clean_str(row.get('composicaoCapta'))
    product_gid = to_clean_str(row.get('product_id'))  # gid://shopify/Product/...

    # Se a descrição vier texto puro e você quiser preservar quebras:
    # desc_capta = desc_capta.replace('\n', '<br>')

    return {
        "input": {
            "id": product_gid,
            "title": title_capta,
            "descriptionHtml": desc_capta
        },
        "metafields": [
            {
                "ownerId": product_gid,
                "namespace": "custom",
                "key": "composicao_text",
                "type": "multi_line_text_field",
                "value": comp_capta
            }
        ]
    }




async def update_price(df):

        query = query_update_price()

        for i in range(len(df)):

            try:
                variables = variable_update_price(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                print('Produto atualizado: ', df.iloc[i]['sku'], '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)

async def update_composition_title_description(df):

        query = query_update_composition_title_description()

        for i in range(len(df)):

            try:
                variables = variable_update_composition_title_description(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                print('Produto atualizado: ', df.iloc[i]['sku'], '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)


def query_update_price_black():
    query = '''
    mutation productVariantUpdate($input: ProductVariantInput!) {
        productVariantUpdate(input: $input) {
            productVariant {
            sku
            title
            price
            compareAtPrice
            }

        }
        }
    '''

    return query

def variable_update_price_black(row):
    variables = {
        "input": {
            "id": str(row['id']),
            "price": str(row['price']),
            #"compareAtPrice": str(row['comparePrice'])
        }
    }

    return variables

def variable_return_price_black(row):
    variables = {
        "input": {
            "id": str(row['id']),
            "price": str(row['compareAtPrice']),
            #"compareAtPrice": str(row['comparePrice'])
        }
    }

    return variables

async def update_price_black(df):

        query = query_update_price_black()

        for i in range(len(df)):

            try:
                variables = variable_update_price_black(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                print('Produto atualizado black: ', df.iloc[i]['sku'], '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)

async def return_price_black(df):

        query = query_update_price_black()

        for i in range(len(df)):

            try:
                variables = variable_return_price_black(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                print('Produto retornar preço original: ', df.iloc[i]['sku'], '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)


def query_update_badges():

    mutation = """ mutation productUpdateBadges($input: ProductInput!) {
                    productUpdate(input: $input) {
                        userErrors {
                        field
                        message
                        }
                        product {
                        id
                        title
                        }
                    }
                    } """
    return mutation

def query_get_metafield_id():
    query = """query MyQuery($id: ID!, $key: String!, $name: String!) {
                product(id: $id) {
                    metafield(key: $key, namespace: $name) {
                        id
                    }
                }
            }"""

    return query

def variable_get_metafield_id(row):
    variables = {
        "id": str(row['product_id']),
        "key": "badges",
        "name": "custom"
    }
    return variables


def query_get_metafield_id_sale():
    query = """query MyQuery($id: ID!, $key: String!, $name: String!) {
                product(id: $id) {
                    metafield(key: $key, namespace: $name) {
                        id
                    }
                }
            }"""

    return query

def variable_get_metafield_id_sale(row):
    variables = {
        "id": str(row['product_id']),
        "key": "sale",
        "name": "custom"
    }
    return variables


def variable_update_badges(row):

    variables = {
                "input": {
                    "metafields": [
                    {   "namespace": "custom",
                        "key": "badges",
                        "type": "list.single_line_text_field",
                        "value": str("[\"Entregamos antes do Natal\"]")
                    }
                    ],
                    "id": str(row['product_id'])
                }
                }

    return variables

def variable_remove_badges(row):

    variables = {
                "input": {
                    "metafields": [
                    {   "namespace": "custom",
                        "key": "badges",
                        "type": "list.single_line_text_field",
                        "value": str("[\"\"]")
                    }
                    ],
                    "id": str(row['product_id'])
                }
                }

    return variables

async def update_badges(df):

    query = query_update_badges()

    for i in range(len(df)):

        try:
            variables = variable_update_badges(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Update Badge Resposta: ', res)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

async def remove_badges(df):

    query = query_update_badges()

    for i in range(len(df)):

        try:
            variables = variable_remove_badges(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Resposta: ', res)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


async def get_metafield_id(df):
        #create dataframe
        newdf = pd.DataFrame()
        #create dataframe with product.id column
        newdf['product_id'] = df['product_id']
        newdf['metafield_id'] = ''


        query = query_get_metafield_id()

        for i in range(len(df)):

            try:
                variables = variable_get_metafield_id(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }


                res = await fetch_data(url, headers, data)

                #print metafield
                print('Metafield: ', res['data']['product']['metafield']['id'] + '- SKU: ', df.iloc[i]['sku'])
                #append in a new column
                newdf = newdf.append({'metafield_id': res['data']['product']['metafield']['id']}, ignore_index=True)

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)

        return newdf

async def get_metafield_id_sale(df):
        #create dataframe
        newdf = pd.DataFrame()
        #create dataframe with product.id column
        newdf['product_id'] = df['product_id']
        newdf['metafield_id'] = ''


        query = query_get_metafield_id()

        for i in range(len(df)):

            try:
                variables = variable_get_metafield_id_sale(df.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }


                res = await fetch_data(url, headers, data)

                #print metafield
                print('Metafield: ', res['data']['product']['metafield']['id'] + '- SKU: ', df.iloc[i]['sku'])
                #concatenate in a new column without using append
                newdf.loc[i, 'metafield_id'] = res['data']['product']['metafield']['id']


            except Exception as e:

                errorMessage = str(e)

                print('Erro Except stage 1: ', errorMessage)
        #save in a csv file
        fc.saveCSV(newdf, 'shopify_csv/sale/backup/sview.csv', sep=';')

        return newdf

def query_update_metafield():
    mutation = """mutation MyMutation ($input: MetafieldDeleteInput!){
                    metafieldDelete(input: $input) {
                        deletedId
                        userErrors {
                        field
                        message
                        }
                    }
                }"""

    return mutation

def variable_update_metafield(row):
    variables = {
        "input": {
            "id": str(row['metafield_id'])
        }
    }
    return variables

async def update_metafield(df):
    query = query_update_metafield()

    for i in range(len(df)):

        try:
            variables = variable_update_metafield(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            # print('Metafield excluido: ', res['data']['product']['metafield']['id'] + '- SKU: ', df.iloc[i]['sku'])
            print('Metafield excluido')

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except sending: ', errorMessage)

async def removing_metafield(df):
    query = query_update_metafield()

    for i in range(len(df)):

        try:
            variables = variable_update_metafield(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Metafield excluido: ', res['data']['product']['metafield']['id'] + '- SKU: ', df.iloc[i]['sku'])

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

def query_get_collections(query):
    query = '''query GetColletion {
  collections(query: "title:'''+query+'''", first: 1) {
    nodes {
      products(first: 250) {
        nodes {
          id
        }
      }
    }
  }
}'''
    return query

def query_metafield_variant_encomendavel():
    mutation = '''mutation MudarValorMetafield($metafields: [MetafieldsSetInput!]!) {
                    metafieldsSet(metafields: $metafields) {
                        metafields {
                        key
                        namespace
                        value
                        }
                        userErrors {
                        field
                        message
                        code
                        }
                    }
                    }
                '''
    return mutation

def variable_metafield_variant_encomendavel(row):
    variables = {
  "metafields": [
    {
      "key": "encomendavel",
      "namespace": "custom",
      "ownerId": row['variant.id'],
      "type": "boolean",
      "value": row['Encomendavel'].astype(str)
    }
  ]
}
    return variables

async def update_metafield_variant_encomendavel(df):
    query = query_metafield_variant_encomendavel()

    for i in range(len(df)):

        try:
            variables = variable_metafield_variant_encomendavel(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Valor de metafield encomendavel adicionado: ' + df.iloc[i]['variant.sku'] + ' - ' + df.iloc[i]['Encomendavel'].astype(str))

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

def query_tags():
    mutation = '''mutation MyMutation($input: ProductInput!) {
                    productUpdate(input: $input) {
                        product {
                        id
                        tags
                        }
                        userErrors {
                        field
                        message
                        }
                    }
                    }
                '''
    return mutation

def variable_tags(row):
    variables = {
        "input": {
            "id": str(row['product_id']),
            "tags": 'Ouro_Branco_Diamantes'
        }
    }
    return variables

async def update_tags(df):
    query = query_tags()

    for i in range(len(df)):

        try:
            variables = variable_tags(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Tags atualizadas: ', df.iloc[i]['sku'], '\n')

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

async def update_metafield_variant_em_estoque(df):
    query = query_metafield_variant_encomendavel()

    for i in range(len(df)):

        try:
            variables = variable_metafield_variant_em_estoque(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Valor de metafield em estoque adicionado: ' + df.iloc[i]['variant.sku'] + ' - ' + df.iloc[i]['Encomendavel'].astype(str))

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

def variable_metafield_variant_em_estoque(row):
    variables = {
  "metafields": [
    {
      "key": "com_estoque",
      "namespace": "custom",
      "ownerId": row['variant.id'],
      "type": "boolean",
      "value": row['Em estoque'].astype(str)
    }
  ]
}
    return variables


async def update_metafield_product_pronta_entrega(df, status):
    query = query_metafield_variant_encomendavel()

    for i in range(len(df)):

        try:
            variables = variable_metafield_product_pronta_entrega(df.iloc[i], status)

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Valor de metafield pronta entrega adicionado: ' + df.iloc[i]['product_id'] + ' - ' + status)

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)


def variable_metafield_product_pronta_entrega(row, status):
    variables = {
  "metafields": [
    {
      "key": "pronta_entrega",
      "namespace": "custom",
      "ownerId": row['product_id'],
      "type": "boolean",
      "value": status
    }
  ]
}
    return variables


def query_update_metafield_sale():

    mutation = """ mutation productUpdateBadges($input: ProductInput!) {
                    productUpdate(input: $input) {
                        userErrors {
                        field
                        message
                        }
                        product {
                        id
                        title
                        }
                    }
                    } """
    return mutation

def variable_metafield_sale(row):

    variables = {
                "input": {
                    "metafields": [
                    {   "namespace": "custom",
                        "key": "sale",
                        "type": "boolean",
                        "value": "true"
                    }
                    ],
                    "id": str(row['product_id'])
                }
                }

    return variables

def variable_metafield_sale_remove(row):

    variables = {
                "input": {
                    "metafields": [
                    {   "namespace": "custom",
                        "key": "sale",
                        "type": "boolean",
                        "value": "false"
                    }
                    ],
                    "id": str(row['product_id'])
                }
                }

    return variables

async def update_metafield_sale(df):
    query = query_update_metafield_sale()

    for i in range(len(df)):

        try:
            variables = variable_metafield_sale(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Valor de metafield sale adicionado: ' + df.iloc[i]['sku_2'] + ' - ' + 'True')

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)

async def remove_metafield_sale(df):
    query = query_update_metafield_sale()

    for i in range(len(df)):

        try:
            variables = variable_metafield_sale_remove(df.iloc[i])

            data = {
                'query': query,
                'variables': variables
            }

            res = await fetch_data(url, headers, data)

            print('Valor de metafield sale adicionado: ' + df.iloc[i]['sku_2'] + ' - ' + 'False')

        except Exception as e:

            errorMessage = str(e)

            print('Erro Except: ', errorMessage)
