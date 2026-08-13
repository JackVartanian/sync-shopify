SELECT
    RTRIM( b.cpros ) AS 'Cod_Prod',
    CONCAT(RTRIM(b.cpros), '-', RTRIM(z.codtams)) AS 'RefId',
    CAST(b.pvens AS INT) AS 'PrVenda'
    FROM sljpro b with(nolock)
    LEFT JOIN sljeti z with(nolock) ON b.cpros = z.cpros
    WHERE b.mercs = 'PA'

