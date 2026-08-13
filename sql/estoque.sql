SELECT RTRIM( z.cpros ) AS 'Cod_Prod',
    CAST(SUM(z.qtds) AS INT) AS 'TotalQuantity',
    CASE
        WHEN RTRIM(z.empos) LIKE 'IGL' THEN 'gid://shopify/Location/88040702247'
        WHEN RTRIM(z.empos) LIKE 'FTH' THEN 'gid://shopify/Location/87677665575'
        -- WHEN RTRIM(z.empos) LIKE 'LMA' THEN 'gid://shopify/Location/87677665575'
        -- WHEN RTRIM(z.empos) LIKE 'LMA' THEN 'gid://shopify/Location/105261007143'
        WHEN RTRIM(z.empos) LIKE 'BAL' THEN 'gid://shopify/Location/88041226535'
        WHEN RTRIM(z.empos) LIKE 'FFL' THEN 'gid://shopify/Location/88040833319'
        ELSE ''
    END AS 'WarehouseId',
    CASE
        WHEN RTRIM(z.empos) LIKE 'IGL' THEN 'Iguatemi'
        WHEN RTRIM(z.empos) LIKE 'FTH' THEN 'Matriz'
        WHEN RTRIM(z.empos) LIKE 'BAL' THEN 'Curitiba'
        WHEN RTRIM(z.empos) LIKE 'FFL' THEN 'Bela Cintra'
        -- WHEN RTRIM(z.empos) LIKE 'LMA' THEN 'Showroom'
        ELSE ''
    END AS 'WarehouseName',
    -- RTRIM( f.dgrus ) AS "Desc. Gr.",

    CASE
        WHEN RTRIM( f.dgrus ) LIKE 'ANEL' THEN CONCAT(RTRIM(z.cpros), '-', RTRIM(z.codtams))
        WHEN RTRIM( f.dgrus ) LIKE 'ALIANCA' THEN CONCAT(RTRIM(z.cpros), '-', RTRIM(z.codtams))
        ELSE RTRIM( z.cpros )
    END AS 'RefId',
    -- CONCAT(RTRIM(z.cpros), '-', RTRIM(z.codtams)) AS 'RefId',
    CASE
        WHEN b.situas = 1 THEN 'TRUE'
        ELSE 'FALSE'
    END AS IsActive,
    CASE
        WHEN 'TotalQuantity' > '0' THEN 'FALSE'
        WHEN b.encoms = 1 THEN 'TRUE'
        ELSE 'FALSE'
    END AS UnlimitedQuantity,
    CAST(b.pvens AS INT) AS 'PrVenda',
    RTRIM( b.nivelqs ) AS 'Metal',
    RTRIM( c.rclis ) AS 'CONTA_ESTOQUE'
FROM
    sljeti z with(nolock)
    LEFT JOIN sljpro b with(nolock) ON z.cpros = b.cpros
    LEFT JOIN sljgru f WITH(NOLOCK) ON b.cgrus = f.cgrus
    LEFT JOIN sljgccr d with(nolock) ON z.grupos = d.codigos
    LEFT JOIN sljcli c with(nolock) ON z.contas = c.iclis
WHERE
    z.empos NOT IN ('DES', 'NY')
    AND b.mercs = 'PA'
    AND z.contas <> '          '
    AND CONCAT( RTRIM( z.empos ), ' - ' , RTRIM( d.descrs )) NOT IN
                        ('LMA - CONSERTOS',
                        'LMA - ESTOQUE CONSIGNADO',
                        'MAT - CONSERTOS',
                        'LMA - ESTOQUE ESPECIAL',
                        'LMA - ESTOQUE LMA.PRIMA',
                        'MAT - ESTOQUE MAT.PRIMA',
                        -- 'LMA - ESTOQUE TRANSIT PROD',
                        -- 'MAT - ESTOQUE TRANSIT PROD',
                        -- 'LMA - ESTOQUE TRANSITO',
                        -- 'MAT - ESTOQUE TRANSITO',
                        'MPV - ESTOQUE PRODUTOS',
                        'NY - ESTOQUE CONSIG EXT',
                        'NY - ESTOQUE CONSIGNADO',
                        'NY - ESTOQUE PRODUTOS',
                        'NY - ESTOQUE TRANSITO',
                        'FFL - ESTOQUE CONSIGNADO',
                        -- 'FFL - ESTOQUE TRANSITO',
                        'FFL - RESERVA DE PRODUTOS',
                        'IGL - ESTOQUE CONSIGNADO',
                        -- 'IGL - ESTOQUE TRANSITO',
                        'IGL - RESERVA DE PRODUTOS',
                        'LMA - ESTOQUE CONSIGNADO')
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
        z.cpros,
        z.empos,
        f.dgrus,
        z.cpros,
        z.codtams,
        b.encoms,
        b.situas,
        b.pvens,
        b.nivelqs,
        c.rclis
