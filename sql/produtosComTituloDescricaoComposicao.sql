SELECT
RTRIM( a.colecoes ) AS "Cod. Modelo",
RTRIM(CONVERT(VARCHAR(8000), a.dprosits))    AS "Titulo_BR",
RTRIM(CONVERT(VARCHAR(8000), a.dproisits))   AS "Titulo_EN",
RTRIM( f.dgrus ) AS "Desc. Gr.",
RTRIM( g.descricaos ) AS "Desc. Subgr.",
RTRIM( a.cpros ) AS "Cod. Prod.",
RTRIM( a.dpros ) AS "Desc. Produto",
RTRIM(CONVERT(VARCHAR(8000), a.dprosit2s))   AS "Descricao_BR",
RTRIM(CONVERT(VARCHAR(8000), a.dproisit2s))  AS "Descricao_EN",
RTRIM(CONVERT(VARCHAR(8000), a.dspalchave))  AS "Composicao",
RTRIM(CONVERT(VARCHAR(8000), a.codscols))    AS "Cluster",
CAST(a.pvens AS INT) AS "Pr Venda unit",
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

-- RTRIM( a.mercs ) AS "Gde. Gr.",
RTRIM( a.nivelqs ) AS "Metal",
RTRIM( a.codcors ) AS "Cor Padrao",
RTRIM( c.descs ) AS "Desc Cor",
RTRIM( a.cftios ) AS "Tab. Pr.",
RTRIM( a.obspes) AS "Obs_1 Prod.",
RTRIM( a.obspeds ) AS "Obs_2 Prod.",

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
