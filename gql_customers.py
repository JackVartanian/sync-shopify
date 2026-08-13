import os
import requests
import json
import funcoes_comuns as fc
import pandas as pd
import numpy as np
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
semaphore = asyncio.Semaphore(10)

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token' : admin_api_key}

async def fetch_data(url, headers, data):
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                return await response.json()


async def getCustomers():

    url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'

    query ={
    "query":
        """
            query {
                    customers(first: 200) {
                        edges {
                        node {
                            id
                            firstName
                            lastName
                        }
                        }
                    }
                    }
            """
            }

    res = await fetch_data(url, headers, query)

    nodes = [edge['node'] for edge in res['data']['customers']['edges']]

    df = pd.DataFrame(nodes)

    return df


async def createCustomer(df_chunk):

    async with semaphore:

        customersDf = fc.readCSV('shopify_csv/customerDict.csv', sep=';')
        customersErrorDf = fc.readCSV('shopify_csv/customerErrorDict.csv', sep=';')

        df_chunk = df_chunk[~df_chunk['Cod_Cliente'].isin(customersDf['Cod_Cliente'])].reset_index(drop=True)
        df_chunk = df_chunk[~df_chunk['Cod_Cliente'].isin(customersErrorDf['Cod_Cliente'])].reset_index(drop=True)

        customerDict = {
            'Cod_Cliente': [],
            'Id': [],
            'First Name': [],
            'Last Name': [],
        }

        customerErrorDict = {
            'Cod_Cliente': [],
            'Message_Error': []
        }

        df_chunk.loc[:, 'Phone'] = df_chunk['Phone'].apply(lambda x: '+' + str(int(float(x))) if pd.notnull(x) else x)
        df_chunk.loc[:, 'First Name'] = df_chunk['First Name'].str.title()
        df_chunk.loc[:, 'Last Name'] = df_chunk['Last Name'].str.title()
        df_chunk['count_phone'] = df_chunk['Phone'].str.len().fillna(0).astype(int)

        url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'

        query = """
                mutation customerCreate($input: CustomerInput!) {
                    customerCreate(input: $input) {
                        userErrors {
                            field
                            message
                        }
                        customer {
                            id
                            firstName
                            lastName
                        }
                    }
                }
            """

        for i in range(len(df_chunk)):

            try:
                variables = prepare_variables(df_chunk.iloc[i])

                data = {
                    'query': query,
                    'variables': variables
                }

                res = await fetch_data(url, headers, data)

                if res['data']['customerCreate']['userErrors']:
                    # raise Exception(res['data']['customerCreate']['userErrors'][0]['message'])

                    customerErrorDict['Cod_Cliente'].append(df_chunk.iloc[i]['Cod_Cliente'])
                    customerErrorDict['Message_Error'].append(res['data']['customerCreate']['userErrors'][0]['message'])

                    print('Linha: ', i,' - Cod_Cliente: ', df_chunk.iloc[i]['Cod_Cliente'] ,' - Erro: ', res['data']['customerCreate']['userErrors'][0]['message'], '\n')

                else:
                    customerDict['Cod_Cliente'].append(df_chunk.iloc[i]['Cod_Cliente'])
                    customerDict['Id'].append(res['data']['customerCreate']['customer']['id'])
                    customerDict['First Name'].append(res['data']['customerCreate']['customer']['firstName'])
                    customerDict['Last Name'].append(res['data']['customerCreate']['customer']['lastName'])

                    print(i,' - Cod_Cliente: ', df_chunk.iloc[i]['Cod_Cliente'] ,' - Name: ', df_chunk.iloc[i]['First Name'], df_chunk.iloc[i]['Last Name'], ' - Qtd_Linhas: ', customerDict['Cod_Cliente'].__len__(), '\n')

            except Exception as e:

                errorMessage = str(e)

                print('Erro Except: ', errorMessage)

        customerDict_df = pd.DataFrame(customerDict)
        customersDf = pd.concat([customersDf, customerDict_df], ignore_index=True)
        customersDf.to_csv('shopify_csv/customerDict.csv', index=False, sep=';')

        customerErrorDict_df = pd.DataFrame(customerErrorDict)
        customersErrorDf = pd.concat([customersErrorDf, customerErrorDict_df], ignore_index=True)
        customerErrorDict_df.to_csv('shopify_csv/customerErrorDict.csv', index=False, sep=';')


async def createCustomerChunk(df):

    df = chunkDataFrame(df, 100)
    print('Qtd loops: ', len(df))

    # df = df[0:3]

    for i in range(len(df)):
        await createCustomer(df[i])


async def process_in_batches(df):

    chunks = chunkDataFrame(df, 10)

    tasks = [createCustomer(chunk) for chunk in chunks]

    await asyncio.gather(*tasks)


def prepare_variables(row):

    # No address and no phone
    if (pd.isna(row['Phone']) and pd.isna(row['Address1'])) or ((row['count_phone'] < 14 and row['count_phone'] > 0) and pd.isna(row['Address1'])):
        # print('Sem endereço e sem Telefone: ', row['First Name'] + ' ' + row['Last Name'])
        variables = {
            "input": {
                "firstName": row['First Name'],
                "lastName": row['Last Name'],
                "email": row['Email'],
                "emailMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "metafields": {
                    "key": "codclient",
                    "type": "single_line_text_field",
                    "value": row['Cod_Cliente'],
                    "namespace": "custom"
                    }
                }
        }
    # No phone
    elif (row['count_phone'] < 14 and row['count_phone'] > 0) or (pd.isna(row['Phone'])):
        # print('Telefone inválido ou sem telefone: ', row['First Name'] + ' ' + row['Last Name'])
        variables = {
            "input": {
                "firstName": row['First Name'],
                "lastName": row['Last Name'],
                "email": row['Email'],
                "emailMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "addresses": {
                    "address1": row['Address1'],
                    "city": row['City'],
                    "provinceCode": row['Province Code'],
                    "countryCode": row['Country Code'],
                    "zip": row['Zip']
                    },
                "metafields": {
                    "key": "codclient",
                    "type": "single_line_text_field",
                    "value": row['Cod_Cliente'],
                    "namespace": "custom"
                    }
                }
        }
    # No address and with phone
    elif pd.isna(row['Address1']):
        # print('Sem endereço: ', row['First Name'] + ' ' + row['Last Name'])
        variables = {
            "input": {
                "firstName": row['First Name'],
                "lastName": row['Last Name'],
                "email": row['Email'],
                "emailMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "phone": str(row['Phone']),
                "smsMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "metafields": {
                    "key": "codclient",
                    "type": "single_line_text_field",
                    "value": row['Cod_Cliente'],
                    "namespace": "custom"
                    }
                }
        }
    else:
        # print('Cadastro completo: ', row['First Name'] + ' ' + row['Last Name'])
        variables = {
            "input": {
                "firstName": row['First Name'],
                "lastName": row['Last Name'],
                "email": row['Email'],
                "emailMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "addresses": {
                    "address1": row['Address1'],
                    "city": row['City'],
                    "provinceCode": row['Province Code'],
                    "countryCode": row['Country Code'],
                    "zip": row['Zip']
                    },
                "phone": str(row['Phone']),
                "smsMarketingConsent": {
                    "marketingState": "SUBSCRIBED",
                    "marketingOptInLevel": "SINGLE_OPT_IN"
                    },
                "metafields": {
                    "key": "codclient",
                    "type": "single_line_text_field",
                    "value": row['Cod_Cliente'],
                    "namespace": "custom"
                    }
                }
        }
    return variables


def chunkDataFrame(df, chunkSize):
    df = np.array_split(df, len(df) // chunkSize + 1)
    return df


async def deleteCustomer(id):

    url = f'https://{shop_url}/admin/api/{api_version}/graphql.json'

    query = """
                mutation customerDelete($input: CustomerDeleteInput!) {
            customerDelete(input: $input) {
                deletedCustomerId
                userErrors {
                field
                message
                }}}"""

    variables = {
        "input": {
            "id": id
            }
    }

    data = {
        'query': query,
        'variables': variables
    }

    res = await fetch_data(url, headers, data)

    print(res)
