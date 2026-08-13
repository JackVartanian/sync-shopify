import read_SQL as rSQL
import pandas as pd
import funcoes_comuns as fc


def produtosAtivos():

    produtos = fc.readCSV('capta_csv/produtos.csv', sep=';')
    produtosAtivos = produtos[produtos['STATUS_FINAL'] == 'ATIVO'].reset_index(drop=True)
    filterColecoes = ['LETRA', 'CHARNEIRA', 'NUMEROS', 'MARIE', 'CUSTOMIZAD', 'DESENVOL', 'FASANO', 'MOSTRUARIO', 'PEDRA', 'PEDRO L', 'MKT']
    produtosAtivos = produtosAtivos[~produtosAtivos['Cod. Modelo'].isin(filterColecoes)].reset_index(drop=True)

    print('Qtde de produtos ativos: ', len(produtosAtivos))

    fc.saveCSV(produtosAtivos, 'capta_csv/produtosAtivos.csv', ';')

    return produtosAtivos


def produtosInativos():

    produtos = fc.readCSV('capta_csv/produtos.csv', sep=';')
    produtosAtivos = produtos[produtos['STATUS_FINAL'] == 'INATIVO'].reset_index(drop=True)
    filterColecoes = ['CUSTOMIZAD', 'DESENVOL', 'FASANO', 'MOSTRUARIO', 'PEDRA', 'PEDRO L', 'MKT']
    produtosAtivos = produtosAtivos[~produtosAtivos['Cod. Modelo'].isin(filterColecoes)].reset_index(drop=True)

    print('Qtde de produtos inativos: ', len(produtosAtivos))

    fc.saveCSV(produtosAtivos, 'capta_csv/produtosInativos.csv', ';')

    return produtosAtivos


def estoqueCapta():

    estoque = fc.readCSV('capta_csv/fEstoque.csv', sep=';')

    return estoque
