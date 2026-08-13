SELECT
    RTRIM(b.cpros) AS 'Cod_Prod',
    ISNULL(CAST(SUM(y.Qtd) AS INT), 0) AS 'TotalQuantity',
    CONCAT(RTRIM(b.cpros), '-') AS 'RefId',
    CASE
        WHEN b.situas = 1 THEN 'TRUE'
        ELSE 'FALSE'
    END AS IsActive,
    CASE
        WHEN 'TotalQuantity' > '0' THEN 'FALSE'
        WHEN b.encoms = 1 THEN 'TRUE'
        ELSE 'FALSE'
    END AS UnlimitedQuantity
FROM sljpro b with(nolock)
INNER JOIN
(
    SELECT RTRIM( z.cpros ) AS 'Cod_Prod',
    CAST(SUM(z.qtds) AS INT) AS "Qtd"
FROM sljeti z with(nolock)
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
)
AS y ON b.cpros = y.[Cod_Prod]
WHERE
    b.mercs = 'PA'
    AND b.encoms = 2
    AND b.situas = 2
GROUP BY
    b.cpros,
    b.situas,
    b.encoms
