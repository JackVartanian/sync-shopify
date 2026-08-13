SELECT
RTRIM( a.colecoes ) AS "Cod. Modelo",

CASE
    WHEN RTRIM( e.descs ) LIKE '%COLECAO%' THEN REPLACE(RTRIM( e.descs ), 'COLECAO', '')
    WHEN RTRIM( e.descs ) LIKE '%COLEÇÃO%' THEN REPLACE(RTRIM( e.descs ), 'COLEÇÃO', '')
    ELSE RTRIM( e.descs )
    END AS "Colecao",

RTRIM( f.dgrus ) AS "Desc. Gr.",
CASE
    WHEN RTRIM( f.dgrus ) = 'ANEL' THEN '340'
    WHEN RTRIM( f.dgrus ) = 'BRINCO' THEN '337'
    WHEN RTRIM( f.dgrus ) = 'COLAR' THEN '339'
    WHEN RTRIM( f.dgrus ) = 'CORRENTE' THEN '339'
    WHEN RTRIM( f.dgrus ) = 'PIERCING' THEN '337'
    WHEN RTRIM( f.dgrus ) = 'PINGENTE' THEN '336'
    WHEN RTRIM( f.dgrus ) = 'PULSEIRA' THEN '334'
    WHEN RTRIM( f.dgrus ) = 'ABOTOADURA' THEN '335'
    WHEN RTRIM( f.dgrus ) = 'ALIANCA' THEN '342'
    ELSE '331'
    END AS "Cod. Gr. Shopify",

RTRIM( g.descricaos ) AS "Desc. Subgr.",
RTRIM( a.cpros ) AS "Cod. Prod.",
RTRIM( a.dpros ) AS "Desc. Produto",
CAST(a.pvens AS INT) AS "Pr Venda unit",

CASE
    WHEN RTRIM( a.dpros ) LIKE '%COMETA%' THEN 'COMETA'
    ELSE ''
    END AS "Cometa",

-- CASE
--     WHEN RTRIM( a.nivelqs ) = 'PRATA' AND RTRIM( g.descricaos ) = 'SEM PEDRA' AND 'Cometa' = ''
--     THEN CONCAT(RTRIM( f.dgrus ), ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' COM ', RTRIM( c.descs ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'PRATA' AND RTRIM( g.descricaos ) = 'SEM PEDRA' AND 'Cometa' <> ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', 'Cometa', ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' COM ', RTRIM( c.descs ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'PRATA' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND 'Cometa' = ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'PRATA' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND 'Cometa' <> ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', 'Cometa', ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) = 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) <> 'FETICHE' AND 'Cometa' = ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' 18K', ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) = 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) <> 'FETICHE' AND 'Cometa' <> ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', 'Cometa', ' ', RTRIM( e.descs ), ' DE ', RTRIM( a.nivelqs ), ' 18K', ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) = 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) = 'FETICHE' AND RTRIM( f.dgrus ) = 'COLAR'
--         THEN CONCAT(RTRIM( f.dgrus ), ' ALGEMA DE ', RTRIM( a.nivelqs ), ' 18K', ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) = 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) = 'FETICHE' AND RTRIM( f.dgrus ) = 'PULSEIRA'
--         THEN CONCAT(RTRIM( f.dgrus ), ' ALGEMINHA DE ', RTRIM( a.nivelqs ), ' 18K', ' COM ', RTRIM( c.descs ), ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) <> 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) <> 'FETICHE' AND 'Cometa' = ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', RTRIM( e.descs ), ' DE ', RTRIM( c.descs ), ' 18K', ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) <> 'RODIO NEGRO' AND RTRIM( g.descricaos ) <> 'SEM PEDRA' AND RTRIM( e.descs ) <> 'FETICHE' AND 'Cometa' <> ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', 'Cometa', ' ', RTRIM( e.descs ), ' DE ', RTRIM( c.descs ), ' 18K', ' E ', RTRIM( g.descricaos ),
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) <> 'RODIO NEGRO' AND RTRIM( g.descricaos ) = 'SEM PEDRA' AND 'Cometa' = ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', RTRIM( e.descs ), ' DE ', RTRIM( c.descs ), ' 18K',
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     WHEN RTRIM( a.nivelqs ) = 'OURO' AND RTRIM( c.descs ) <> 'RODIO NEGRO' AND RTRIM( g.descricaos ) = 'SEM PEDRA' AND 'Cometa' <> ''
--         THEN CONCAT(RTRIM( f.dgrus ), ' ', 'Cometa', ' ', RTRIM( e.descs ), ' DE ', RTRIM( c.descs ), ' 18K',
--                     CASE WHEN [@[Tam.]] <> '' THEN CONCAT(' - ', [@[Tam.]]) ELSE '' END)
--     END AS Resultado,

-- RTRIM( a.mercs ) AS "Gde. Gr.",
RTRIM( a.nivelqs ) AS "Metal",
RTRIM( a.codcors ) AS "Cor Padrao",
RTRIM( c.descs ) AS "Desc Cor",
RTRIM( a.cftios ) AS "Tab. Pr.",

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
END AS "STATUS_FINAL"

-- CAST(a.dtincs AS DATE) AS "Data Inclusao"

FROM sljpro a with(nolock)
LEFT JOIN sljcor c WITH(NOLOCK) ON a.codcors = c.cods
LEFT JOIN sljgru f WITH(NOLOCK) ON a.cgrus = f.cgrus
LEFT JOIN sljsgru g WITH(NOLOCK) ON a.cgrus+ + a.sgrus = g.cgrucods
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
WHERE a.mercs = 'PA' AND a.pvens > 1
ORDER BY a.colecoes, f.dgrus, a.cpros
