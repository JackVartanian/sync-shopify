-- Cria uma tabela temporária
WITH nums AS (SELECT 10 as num
UNION ALL
SELECT num + 1
FROM nums
WHERE num < 22)

SELECT
    RTRIM(b.cpros) AS 'Cod_Prod',
    CAST(AVG(5) AS INT) AS 'TotalQuantity',
    CASE
        WHEN RTRIM(b.nivelqs) = 'PRATA' THEN 'gid://shopify/Location/88734335271'
        WHEN RTRIM(b.nivelqs) = 'OURO' THEN 'gid://shopify/Location/88734269735'
        ELSE '55FA1999-752C-41AA-836C-29E4C11B458C'
    END AS 'WarehouseId',
    CASE
        WHEN RTRIM(b.nivelqs) = 'PRATA' THEN 'Encomenda - Prata'
        WHEN RTRIM(b.nivelqs) = 'OURO' THEN 'Encomenda - Ouro'
        ELSE '55FA1999-752C-41AA-836C-29E4C11B458C'
    END AS 'WarehouseName',
    -- CASE
    --     WHEN RTRIM(b.cgrus) LIKE 'AN' THEN CONCAT(RTRIM(b.cpros), '-', RTRIM(z.codtams))
    --     WHEN RTRIM(b.cgrus) LIKE 'AL' THEN CONCAT(RTRIM(b.cpros), '-', RTRIM(z.codtams))
    --     ELSE RTRIM(b.cpros)
    -- END AS 'RefId',
    CASE
        WHEN RTRIM(b.cgrus) IN ('AN', 'AL') THEN CONCAT(RTRIM(b.cpros), '-', n.num)
        ELSE RTRIM(b.cpros)
    END AS 'RefId',
    RTRIM(b.nivelqs) AS "Metal"
FROM
    sljpro b with(nolock)
    -- LEFT JOIN sljeti z with (nolock) ON b.cpros = z.cpros
    LEFT JOIN (
        SELECT
        DISTINCT RTRIM(cpros) AS 'cpros',
        IIF(dcompos LIKE '%ELETROLITICA%', 'Eletro', '') AS 'Formacao'
    FROM
        sljcomp2 WITH (NOLOCK)
    WHERE
            cgrus = 'MET'
        AND dcompos LIKE '%ELETROLITICA%'
        AND cpros NOT LIKE 'CO%'
        AND cpros NOT IN ('PI01380', 'PU01937T', 'CL04314', 'PU01915T')
    ) c ON b.cpros = c.cpros
    CROSS JOIN nums AS n
WHERE b.mercs = 'PA'
    AND b.encoms = 1
    -- AND b.cpros IN ('AL0129')
GROUP BY
    b.cpros,
    b.cgrus,
    -- z.cpros,
    -- z.codtams,
    b.pvens,
    b.nivelqs,
    n.num
ORDER BY
    b.cpros
