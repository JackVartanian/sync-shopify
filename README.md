# sync-shopify

Sincronização Capta → Shopify. Lê o ERP Capta (SQL Server) e atualiza a loja
Shopify (estoque, preço e metafields de disponibilidade) via Admin GraphQL API.

Migrado do Agendador do Windows para rodar no servidor Linux (Hostinger).
Diferente dos outros ETLs, este **escreve na loja de produção** — teste com cuidado.

## Fluxo (shopifyUpdates.py)

Ao rodar `python shopifyUpdates.py`, executa em ordem (as chamadas estão no fim do arquivo):

1. `getStocksLevels()` — lê níveis de estoque/variantes atuais do Shopify (leitura)
2. `updatesCapta()` — puxa produtos/estoque/encomenda do Capta para CSVs locais
3. `activateStocks()` — ativa rastreamento de estoque das variantes
4. `updateStocks()` — ajusta quantidade em estoque (físico e encomenda ouro/prata)
5. `updatePrices()` — atualiza preço das variantes
6. `updateTagEncomenda()` — atualiza o metafield `custom.encomendavel` das variantes
7. `updateTagEmEstoque()` — atualiza o metafield de "em estoque"

O bloco de título/descrição/composição e as campanhas sazonais estão comentados.

## Credenciais (.env)

- `CAPTA_DB_*` — SQL Server do ERP (exige rede/VPN; no servidor usa o IP público)
- `SHOPIFY_SHOP_URL`, `SHOPIFY_API_VERSION`
- `SHOPIFY_ADMIN_API_KEY` — usado pela maioria dos módulos
- `SHOPIFY_ADMIN_API_KEY_PRODUCTS` — usado pelo módulo de produtos (no original era um token diferente)

## Setup no servidor

```bash
cd ~/sync-shopify        # (ou o nome que voce deu no clone)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cp .env.example .env
nano .env                # preencher credenciais
chmod 600 .env
```

## Teste

```bash
# 1) Conexoes (SEGURO, so leitura - nao altera nada)
./venv/bin/python testa_conexoes.py

# 2) Fluxo real (ATENCAO: escreve na loja de producao)
./venv/bin/python shopifyUpdates.py
```

## Pastas de runtime

`capta_csv/`, `shopify_csv/` (e `shopify_csv/metafield/`), `log/` são criadas/preenchidas
em runtime. Os arquivos de **estado** de comparação dos metafields ficam em
`shopify_csv/metafield/` (ex.: `InventoryLevelsNatal_base.csv`) — se vierem da
máquina Windows, a comparação continua de onde parou; se não existirem, a primeira
execução das etapas 6/7 pode falhar ao ler o base.
