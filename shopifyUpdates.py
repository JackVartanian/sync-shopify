import aiohttp
import pandas as pd
import gql_inventory as gi
import gql_products as gp
import gql_customers as gc
import gql_collections as gcol
import funcoes_shopify as fs
import funcoes_comuns as fc
import read_SQL as rSQL
import asyncio
import json
import nest_asyncio
from warnings import simplefilter
nest_asyncio.apply()
simplefilter(action='ignore', category=FutureWarning)


def updatesCapta():

    print('Atualizando dados da Capta...')

    rSQL.produtosToPandas()
    rSQL.estoqueToPandas()
    rSQL.estoqueEncToPandas()


def createCaptaProductsExcel():

    rSQL.generatingCaptaProductsExcel()



def activateStocks():

    print('Ativando estoque...')

    gi.run_query_InventoryItemId()

    df = fc.readCSV('shopify_csv/InventoryItemDict.csv', sep=';')
    df.rename(columns={'sku':'Sku', 'id': 'InventoryItemId'}, inplace=True)

    asyncio.run(gi.inventoryItemUpdate(df))
    asyncio.run(gi.inventoryActivation(df))

# Essa função altera a planilha product_test_Sku
def getStocksLevels():

    print('Atualizando níveis de estoque...')

    fs.run_query_productVariants()
    fs.run_query_InventoryLevels()


def updateStocks():

    print('Atualizando estoque...')

    encomendavel = fs.prepare_df_encomendavel()
    zerar_encomendaveis = fs.prepare_df_zerar_encomendaveis()
    zerar_estoque = fs.prepare_df_zerar_estoque()
    estoque = fs.prepare_df_estoque()
    #save estoque as csv
    fc.saveCSV(estoque, 'shopify_csv/test_log_estoque.csv', ';')

    asyncio.run(gi.inventoryAdjustQuantities(zerar_encomendaveis))
    asyncio.run(gi.inventoryAdjustQuantities(encomendavel))

    asyncio.run(gi.inventoryAdjustQuantities(zerar_estoque))
    asyncio.run(gi.inventoryAdjustQuantities(estoque))


def updatePrices():

    print('Atualizando Precos dos Produtos...')

    df = fs.prepare_df_price_shopify()
    produtos = fs.prepare_df_price_capta()
    #inventory = fs.prepare_df_price_aneis()

    merge = fs.merge_price(produtos, df)

    asyncio.run(gp.update_price(merge))


def updateShopifyProductTitleDescriptionComposition():

    print('Comparando Produtos Capta X Shopify...')

    df = fs.prepare_df_title_description_composition_shopify()
    produtos = fs.prepare_df_title_description_composition_capta()
    #inventory = fs.prepare_df_price_aneis()

    merge = fs.merge_title_description_composition(produtos, df)

    asyncio.run(gp.update_composition_title_description(merge))



def createShopifyProductsExcel():

    print('Gerando Planilha do Excel Com Produtos do Shopify ...')

    fs.runningShopifyProductsMutation()

# def updateBlackNovembro():
#    fs.filter_encomendaveis_stock()
#    fs.update_prices_stock_black()
#    fs.verify_last_cycle()
#    fs.verify_last_cycle_black()

def updateNatal():
    fs.get_natal_collections()
    fs.prepararDF()
    fs.filterEncomendaveis()
    fs.verify_last_cycle_natal()

def updateTagEncomenda():
    fs.remodelInventoryLevels()
    fs.checkNewEncomendavel()

def updateTagEmEstoque():
    fs.prepareEmEstoque()
    fs.checkNewEmEstoque()

def updateMetafieldSale():
    fs.get_sale_collections()
    fs.prepararDataFrameSale()
    fs.filterEncomendaveisSale()
    fs.verify_last_cycle_sale()

def updateProntaEntrega():
    fs.getEmEstoqueProducts()
    fs.checkNewProntaEntrega()


# Descomentar
getStocksLevels()
updatesCapta()
activateStocks()
updateStocks()
updatePrices()
updateTagEncomenda()
updateTagEmEstoque()

# INICIO - Atualizar Titulo, Descricao, Composicao
# createCaptaProductsExcel()
# createShopifyProductsExcel()
# updateShopifyProductTitleDescriptionComposition()
# FIM - Atualizar Titulo, Descricao, Composicao


# Manter comentado
# updateNatal()
# updateMetafieldSale()
# updateProntaEntrega()
