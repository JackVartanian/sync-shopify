SELECT
RTRIM( a.colecoes ) AS "Cod. Modelo",
CASE
    WHEN RTRIM( e.descs ) LIKE '%COLECAO%' THEN REPLACE (RTRIM( e.descs ), 'COLECAO', '')
    WHEN RTRIM( e.descs ) LIKE '%COLEÇÃO%' THEN REPLACE (RTRIM( e.descs ), 'COLEÇÃO', '')
    ELSE RTRIM( e.descs )
END AS "Colecao",
RTRIM( a.cgrus ) AS "Cod. Gr.",
RTRIM( f.dgrus ) AS "Desc. Gr.",
RTRIM( a.sgrus ) AS "Cod. Subgr.",
RTRIM( g.descricaos ) AS "Desc. Subgr.",
RTRIM( a.cpros ) AS "Cod. Prod.",
RTRIM( a.dpros ) AS "Desc. Produto",
CAST( a.markupa AS DECIMAL(10,2)) AS "Markup Aplic",
CAST( a.pcuss AS DECIMAL(10,2)) AS "Pr. Custo",
CAST(a.pvens AS DECIMAL(10)) AS "Pr Venda unit",
CASE
    WHEN a.pvens <= 5000 AND a.nivelqs = 'OURO' THEN '08. Ate 5.000'
    WHEN a.pvens <= 10000 AND a.nivelqs = 'OURO' THEN '07. De 5.000 a 10.000'
    WHEN a.pvens <= 20000 AND a.nivelqs = 'OURO' THEN '06. De 10.000 a 20.000'
    WHEN a.pvens <= 50000 AND a.nivelqs = 'OURO' THEN '05. De 20.000 a 50.000'
    WHEN a.pvens <= 100000 AND a.nivelqs = 'OURO' THEN '04. De 50.000 a 100.000'
    WHEN a.pvens <= 200000 AND a.nivelqs = 'OURO' THEN '03. De 100.000 a 200.000'
    WHEN a.pvens <= 500000 AND a.nivelqs = 'OURO' THEN '02. De 200.000 a 500.000'
    WHEN a.pvens > 500000 AND a.nivelqs = 'OURO' THEN '01. Acima de 500.000'

    WHEN a.pvens <= 2000 AND a.nivelqs = 'PRATA' THEN '03. Ate 2.000'
    WHEN a.pvens <= 4000 AND a.nivelqs = 'PRATA' THEN '02. De 2.000 a 4.000'
    WHEN a.pvens > 4000 AND a.nivelqs = 'PRATA' THEN '01. De 4.000 a 9.000'
    ELSE ''
END AS "Faixa de Preco",

RTRIM( a.mercs ) AS "Gde. Gr.",
RTRIM( a.nivelqs ) AS "Metal",
RTRIM( a.codcors ) AS "Cor Padrao",
RTRIM( c.descs ) AS "Desc Cor",
RTRIM( a.codscols ) AS "Sub Nivel",
RTRIM( a.cftios ) AS "Tab. Pr.",
RTRIM( a.codtams) AS "Tamanho",

CONCAT('https://jvphotos.com.br/cms/wp-content/uploads/fotos/',RTRIM( a.cpros ),'.JPG') AS "Foto",

CASE
    WHEN a.encoms = 1 THEN 'Sim'
    ELSE 'Nao'
END AS "Encomendavel",

CASE
    WHEN a.situas = 1 THEN 'Ativo'
    ELSE 'Inativo'
END AS "Status",

CASE
    WHEN [Qtd_Estoque] > 0 THEN [Qtd_Estoque]
    ELSE 0
END AS "Estoque",

CASE
    WHEN a.encoms = 1 THEN 'ATIVO'
    WHEN [Qtd_Estoque] > 0 THEN 'ATIVO'
    WHEN [Qtd_Estoque] < 1 AND a.encoms = 1 THEN 'ATIVO'
    WHEN [Qtd_Estoque] > 0 AND a.encoms = 1 THEN 'ATIVO'
    WHEN [Qtd_Estoque] < 1 AND a.encoms = 0 THEN 'INATIVO'
    ELSE 'INATIVO'
END AS "STATUS_FINAL",

CAST(a.dtincs AS DATE)AS "Data Inclusao",
CAST(a.pesoms AS DECIMAL(10,2))AS "Peso",
RTRIM( a.cclass ) AS "Classificacao",
RTRIM( a.linhas ) AS "Linha"

FROM sljpro a with(nolock)
INNER JOIN sljcor c WITH(NOLOCK) ON a.codcors = c.cods
INNER JOIN sljgru f WITH(NOLOCK) ON a.cgrus = f.cgrus
INNER JOIN sljsgru g WITH(NOLOCK) ON a.cgrus+ + a.sgrus = g.cgrucods
INNER JOIN sljcol e WITH(NOLOCK) ON a.colecoes = e.colecoes
LEFT JOIN(

    SELECT RTRIM( z.cpros ) AS 'Cod_Prod',
    CAST(SUM(z.qtds) AS INT) AS 'Qtd_Estoque'
FROM
    sljeti z with(nolock)
    LEFT JOIN sljpro b with(nolock) ON z.cpros = b.cpros
    LEFT JOIN sljgccr d with(nolock) ON z.grupos = d.codigos
    LEFT JOIN sljcli c with(nolock) ON z.contas = c.iclis
WHERE
    z.empos NOT IN ('LMA', 'MAT', 'DES', 'NY')
    AND b.mercs = 'PA'
    AND z.contas <> '          '
    AND RTRIM( c.rclis ) NOT IN ('CASSIA AVILA',
                            'ESTOQUE COFRE (JV)',
                            'ESTOQUE DE DEVOLUÇÃO',
                            'ESTOQUE ENCOMENDA',
                            'ESTOQUE FABRICA / DESENVOLVIMENTO',
                            'ESTOQUE LMA NY',
                            'ESTOQUE MARKETING',
                            'ESTOQUE MODELOS',
                            'ESTOQUE PRODUCAO',
                            'ESTOQUE TRANSITO AUDITORIA',
                            'JACK VARTANIAN',
                            'JACK VARTANIAN - IGUATEMI')
    GROUP BY
        z.cpros
) AS est ON a.cpros = est.Cod_Prod
WHERE a.mercs = 'PA'
-- AND a.cpros = 'CL04318'
-- STATUS_FINAL = 'ATIVO'
-- AND STATUS_FINAL LIKE '%ATIVO%'

ORDER BY a.colecoes, f.dgrus, a.cpros
