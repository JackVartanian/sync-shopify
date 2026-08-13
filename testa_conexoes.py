# -*- coding: utf-8 -*-
"""
Teste de conexao SEGURO (somente leitura) do projeto sync-shopify.
Nao altera nada no Capta nem no Shopify. Serve para validar, no servidor,
que as credenciais do .env funcionam antes de rodar o fluxo real.

Uso:
    python testa_conexoes.py
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

print('=' * 55)
print('TESTE DE CONEXOES - sync-shopify (somente leitura)')
print('=' * 55)

ok = True

# 1) Capta (SQL Server)
print('\n[1/2] Capta (SQL Server)...')
try:
    import pymssql
    conn = pymssql.connect(
        os.getenv('CAPTA_DB_SERVER'), os.getenv('CAPTA_DB_USERNAME'),
        os.getenv('CAPTA_DB_PASSWORD'), os.getenv('CAPTA_DB_DATABASE'),
        login_timeout=15)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sljpro WITH(NOLOCK)")
    print('      OK - conectou. Produtos na sljpro:', cur.fetchone()[0])
    conn.close()
except Exception as e:
    print('      FALHOU:', e)
    ok = False

# 2) Shopify (Admin API - so uma leitura do shop)
print('\n[2/2] Shopify (Admin API)...')
shop = os.getenv('SHOPIFY_SHOP_URL')
ver = os.getenv('SHOPIFY_API_VERSION', '2025-07')


def testa_token(nome, token):
    if not token:
        print(f'      {nome}: nao definido no .env')
        return False
    url = f'https://{shop}/admin/api/{ver}/graphql.json'
    headers = {'Content-Type': 'application/json',
               'X-Shopify-Access-Token': token}
    query = '{ shop { name myshopifyDomain } }'
    try:
        r = requests.post(url, json={'query': query}, headers=headers, timeout=20)
        j = r.json()
        if r.status_code == 200 and 'data' in j and j['data'].get('shop'):
            print(f'      {nome}: OK - loja "{j["data"]["shop"]["name"]}"')
            return True
        print(f'      {nome}: FALHOU - status {r.status_code} - {j}')
        return False
    except Exception as e:
        print(f'      {nome}: FALHOU -', e)
        return False


t1 = testa_token('SHOPIFY_ADMIN_API_KEY', os.getenv('SHOPIFY_ADMIN_API_KEY'))
t2 = testa_token('SHOPIFY_ADMIN_API_KEY_PRODUCTS', os.getenv('SHOPIFY_ADMIN_API_KEY_PRODUCTS'))
ok = ok and t1 and t2

print('\n' + '=' * 55)
print('RESULTADO:', 'TUDO OK' if ok else 'HOUVE FALHA (ver acima)')
print('=' * 55)
sys.exit(0 if ok else 1)
