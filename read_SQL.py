import os

import pymssql
import pandas as pd
import funcoes_comuns as fc
from dotenv import load_dotenv
from warnings import simplefilter

load_dotenv()

simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=Warning)

def conn_pymssql():

    # Parametros do banco de dados (via .env)
    server = os.getenv('CAPTA_DB_SERVER')
    database = os.getenv('CAPTA_DB_DATABASE')
    username = os.getenv('CAPTA_DB_USERNAME')
    password = os.getenv('CAPTA_DB_PASSWORD')

    # Criar Conexão com banco de dados
    conn = pymssql.connect(
        server, username, password, database
    )
    return conn


def conn_cursor():
    conn = conn_pymssql()
    cursor = conn.cursor()
    return cursor

# Produtos e preços
def produtosPrecosToPandas():

    print('Produtos e Preços')

    precos = 'sql/precos.sql'
    conn = conn_pymssql()
    query = open(precos, 'r').read()
    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/precos.csv', ';')

    return df

# Produtos
def produtosToPandas():

    print('Produtos')

    with open('sql/produtos.sql', 'r') as f:
        query = f.read()

    # precos = 'sql/produtos.sql'
    conn = conn_pymssql()
    # query = open(precos, 'r').read()
    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/produtos.csv', ';')

    return df


def generatingCaptaProductsExcel():

    print('Gerando Excel de Produtos do Capta ...')

    with open('sql/produtosComTituloDescricaoComposicao.sql', 'r') as f:
        query = f.read()

    # precos = 'sql/produtos.sql'
    conn = conn_pymssql()
    # query = open(precos, 'r').read()
    df = pd.read_sql(query, conn)
    fc.saveCSVSigEncoding(df, 'capta_csv/produtosComTituloDescricaoComposicao.csv', ';')

    return df


# Produtos
def produtosSEOToPandas():

    print('Produtos SEO')

    with open('sql/produtos_SEO.sql', 'r') as f:
        query = f.read()

    conn = conn_pymssql()
    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/produtos_seo.csv', ';')

    return df


# Estoque venda
def estoqueToPandas():

    print('Estoque Venda')

    estoque = 'sql/estoque.sql'
    conn = conn_pymssql()
    query = open(estoque, 'r').read()
    df = pd.read_sql(query, conn)

    print('Qtde de produtos em estoque: ', len(df['Cod_Prod'].unique()))

    fc.saveCSV(df, 'capta_csv/fEstoque.csv', ';')

    return df

def estoqueToPandasBlack():
    print('Estoque Venda')

    estoque = 'sql/estoque.sql'
    conn = conn_pymssql()
    query = open(estoque, 'r').read()
    df = pd.read_sql(query, conn)
    #unir linhas com o mesmo Cod_Prod, RefId e WarehouseId e somar TotalQuantity
    df = df.groupby(['Cod_Prod', 'WarehouseId', 'RefId'], as_index=False).agg({'TotalQuantity': 'sum'})

    print('Qtde de produtos em estoque: ', len(df['Cod_Prod'].unique()))

    fc.saveCSV(df, 'capta_csv/fEstoqueBlack.csv', ';')

    return df

# Estoque encomendavel
def estoqueEncToPandas():

    print('Estoque Encomendavel')

    encomendavel = 'sql/encomendaveis.sql'
    conn = conn_pymssql()
    query = open(encomendavel, 'r').read()

    df = pd.read_sql(query, conn)
    df = df.drop_duplicates(subset=['RefId']).reset_index(drop=True)

    print('Qtde de produtos encomendaveis: ', len(df['Cod_Prod'].unique()))

    fc.saveCSV(df, 'capta_csv/fEstoqueEnc.csv', ';')

    return df

# Estoque inativos
def inativosToPandas():

    print('Estoque Inativos')

    inativos = 'sql/inativos.sql'
    conn = conn_pymssql()
    query = open(inativos, 'r').read()

    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/inativos.csv', ';')

    return df

# Estoque inativos others
def inativosOthersToPandas():

    print('Estoque Inativos Others')

    inativos_others = 'sql/inativos_others.sql'
    conn = conn_pymssql()
    query = open(inativos_others, 'r').read()

    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/inativos_others.csv', ';')

    return df

# Vendas
def vendasToPandas():

    print('Vendas')

    vendas = 'sql/vendas.sql'
    conn = conn_pymssql()
    query = open(vendas, 'r').read()
    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/fVendas.csv', ';')

    return df

# Ler arquivo SQL
def sqlToPandas(sql, exportCsv, conn):

    conn = conn_pymssql()
    query = open(sql, 'r').read()

    df = pd.read_sql(query, conn)
    fc.saveCSV(df, exportCsv, ';')

    return df

def productsUpToPandas():

    print('Produtos Up')

    products_up = 'sql/products_up.sql'
    conn = conn_pymssql()
    query = open(products_up, 'r').read()
    df = pd.read_sql(query, conn)
    fc.saveCSV(df, 'capta_csv/products_up.csv', ';')

    return df
