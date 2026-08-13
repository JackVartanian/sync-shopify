
    SELECT
CASE
        WHEN RTRIM( a.emps ) LIKE 'IGL' THEN 'IGU'
        WHEN RTRIM( a.emps ) LIKE 'FSM' THEN 'DES'
        WHEN RTRIM( a.emps ) LIKE 'BAL' THEN 'BAT'
        WHEN RTRIM( a.emps ) LIKE 'CUR' THEN 'BAT'
        WHEN RTRIM( a.emps ) LIKE 'FTH' THEN 'WEB'
        WHEN RTRIM( a.emps ) LIKE 'FFL' THEN 'BEL'
        WHEN RTRIM( a.emps ) LIKE 'LMA' THEN 'MAT'
        WHEN RTRIM( a.emps ) LIKE 'MPV' THEN 'MP2'
        ELSE RTRIM( a.emps )
            END AS "Empresa",
        RTRIM( a.dopes ) AS "Operacao",
        CAST (a.numes AS INTEGER ) AS "No.Oper",

        CASE
        WHEN CAST( h.Data AS DATE ) IS NULL THEN CAST( a.datas AS DATE )
        ELSE CAST( h.Data AS DATE )
        END AS "Data",

        --CONVERT(DATE, a.datas, 103) AS "Data",
        CASE
                WHEN A.ICLIS LIKE '110401%' THEN (CASE
                WHEN F.OPERS = 'S' THEN RTRIM( G.CONTADS )
                ELSE RTRIM( G.CONTAOS )
                END)
                ELSE RTRIM( a.iclis )
                END AS "Cod. Cliente",
        CASE
                WHEN A.ICLIS = '' THEN ''
                ELSE (CASE
                WHEN A.ICLIS LIKE '110401%' THEN (CASE
                WHEN F.OPERS = 'S' THEN RTRIM( I.RCLIS )
                ELSE RTRIM( J.RCLIS )
                END)
                ELSE RTRIM( a.rclis )
                END)
                END AS "Nome Cliente",
        CASE
                        WHEN RTRIM( a.vends ) IS NULL THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0399/6' THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0531/5' THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0720/2' THEN 'WEB'
                        ELSE RTRIM( a.vends )
                    END AS "Cod. Vend.",
        CASE
                        WHEN RTRIM( K.RCLIS ) IS NULL THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'ZAGO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'PERSIO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'MENINO' + '%' THEN 'WEB'
                        ELSE RTRIM( K.RCLIS )
                    END AS "Consultora",
        RTRIM( a.resps ) AS "Cod. Acomp.",
        RTRIM( e.rclis ) AS "Acompanhante",
        RTRIM( a.ggrus ) AS "Grande Grupo",
        RTRIM( x.colecoes ) AS "Cod. Modelo",
        RTRIM( a.cpros ) AS "Cod. Prod.",
        RTRIM( a.codbarras ) AS "Cod. Barras",
        RTRIM( a.codtams ) AS "Tamanho",
        CAST( a.qtds AS INTEGER ) AS "Qtd",
        CAST( a.totas AS DECIMAL(10) ) AS "Total Liq.",
        CAST( a.valrats AS DECIMAL(10) ) AS "Desconto",
        CAST( a.custos AS DECIMAL(10) ) AS "Custo",
        CASE
        WHEN f.opers = 'S' THEN CAST(  f.totas AS DECIMAL(10) )
        ELSE CAST( -1 * F.TOTAS AS DECIMAL(10) )
        END AS "Total Brt",
        RTRIM( g.notas ) AS "NF",
        CONCAT( RTRIM( a.iclis ),'-',  CASE
        WHEN CAST
( h.Data AS DATE ) IS NULL THEN CAST
( a.datas AS DATE )
        ELSE CAST
( h.Data AS DATE )
END) AS ID_Venda,
        CONCAT( RTRIM( a.iclis ),'-',  RTRIM( g.notas )) AS ID_Pedido,
        RTRIM( h.ID_Vtex ) AS "ID_Vtex",
        RTRIM( G.CODEVENTS ) AS "Evento"
    FROM sljgdmi AS a with (nolock)
        LEFT JOIN sljcli AS e with (nolock) ON a.resps = e.iclis
        LEFT JOIN sljeesti AS f with (nolock) ON a.empdopnums + CONVERT (CHAR (8), a.codbarras) = f.empdopnums + CONVERT (CHAR (8), f.codbarras)
        LEFT JOIN sljeest AS g with (nolock) ON a.empdopnums = g.empdopnums
        LEFT JOIN SLJCLI AS J with (nolock) ON G.CONTAOS = J.ICLIS
        LEFT JOIN SLJCLI AS I with (nolock) ON G.CONTADS = I.ICLIS
        LEFT JOIN SLJCLI AS K with (nolock) ON K.ICLIS = A.VENDS
        LEFT JOIN sljpro AS x with (nolock) ON a.cpros = x.cpros
        LEFT JOIN(
            SELECT
            CAST( b.dtemis AS DATE ) AS 'Data',
            RTRIM( b.nemps) AS 'ID_Vtex',
            CONCAT( RTRIM( b.contads ),'-',  RTRIM( b.notas )) AS ID_Pedido
        FROM sljeest b WITH(NOLOCK)
        WHERE RTRIM(dopes) = 'PEDIDO E-COMM'
        ) AS h ON CONCAT( RTRIM( a.iclis ) ,'-',  RTRIM( g.notas )) = h.ID_Pedido

    WHERE a.codbarras <> 0
        AND a.emps <> 'NY'
        AND a.vvistas <> 0
        AND a.tipoops NOT IN (91, 92)
        AND A.DOPES <> 'ADTO ENCOMENDA'
        AND (a.dopes <> 'VENDA PERMUTA'
        AND a.dopes <> 'VENDA FUNCIONARIO'
        AND a.dopes <> 'VENDA ENCOMENDA'
        AND a.dopes <> 'VENDA ENC E-COMM' )


UNION ALL
    SELECT
        CASE
                WHEN RTRIM( a.emps ) LIKE 'IGL' THEN 'IGU'
                WHEN RTRIM( a.emps ) LIKE 'BAL' THEN 'BAT'
                WHEN RTRIM( a.emps ) LIKE 'CUR' THEN 'BAT'
                WHEN RTRIM( a.emps ) LIKE 'FSM' THEN 'DES'
                WHEN RTRIM( a.emps ) LIKE 'FTH' THEN 'WEB'
                WHEN RTRIM( a.emps ) LIKE 'FFL' THEN 'BEL'
                WHEN RTRIM( a.emps ) LIKE 'LMA' THEN 'MAT'
                WHEN RTRIM( a.emps ) LIKE 'MPV' THEN 'MP2'
                ELSE RTRIM( a.emps )
            END AS "Empresa",
        RTRIM(a.dopes) AS "Operacao",
        CAST (a.numes AS INTEGER) AS "No.Oper",

        CASE
        WHEN CAST( h.Data AS DATE ) IS NULL THEN CAST( a.datas AS DATE )
        ELSE CAST( h.Data AS DATE )
        END AS "Data",

        --CONVERT(DATE, a.datas, 103) AS "Data",
        CASE
                WHEN RTRIM( A.ICLIS ) LIKE '110401%' THEN RTRIM( G.CONTADS )
                ELSE RTRIM( a.iclis )
                END AS "Cod. Cliente",
        CASE
                WHEN RTRIM( A.ICLIS ) = '' THEN ''
                ELSE (CASE
                WHEN RTRIM( A.ICLIS ) LIKE '110401%' THEN RTRIM( I.RCLIS )
                ELSE RTRIM( a.rclis )
                END)
                END AS "Nome Cliente",
        CASE
                        WHEN RTRIM( a.vends ) IS NULL THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0399/6' THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0531/5' THEN 'WEB'
                        WHEN RTRIM( a.vends ) LIKE '0720/2' THEN 'WEB'
                        ELSE RTRIM( a.vends )
                    END AS "Cod. Vend.",
        CASE
                        WHEN RTRIM( K.RCLIS ) IS NULL THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'ZAGO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'PERSIO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'MENINO' + '%' THEN 'WEB'
                        ELSE RTRIM( K.RCLIS )
                    END AS "Consultora",
        RTRIM(a.resps) AS "Cod. Acomp.",
        RTRIM(e.rclis) AS "Acompanhante",
        RTRIM(a.ggrus) AS "Grande Grupo",
        RTRIM( x.colecoes ) AS "Cod. Modelo",
        RTRIM(a.cpros) AS "Cod. Prod.",
        RTRIM(a.codbarras) AS "Cod. Barras",
        RTRIM( a.codtams ) AS "Tamanho",
        CAST(a.qtds AS INTEGER ) AS "Qtd",
        CAST( a.totas AS DECIMAL(10) ) AS "Total Liq.",
        CAST( a.valrats AS DECIMAL(10) ) AS "Desconto",
        CAST( a.custos AS DECIMAL(10) ) AS "Custo",
        CAST( a.vvistas AS DECIMAL(10) ) AS "Total Brt",
        RTRIM( g.notas ) AS "NF",
        CONCAT( RTRIM( a.iclis ),'-',  CASE
        WHEN CAST
( h.Data AS DATE ) IS NULL THEN CAST
( a.datas AS DATE )
        ELSE CAST
( h.Data AS DATE )
END) AS ID_Venda,
        CONCAT( RTRIM( a.iclis ),'-',  RTRIM( g.notas )) AS ID_Pedido,
        RTRIM( h.ID_Vtex ) AS "ID_Vtex",
        RTRIM( G.CODEVENTS ) AS "Evento"
    FROM sljgdmi AS a with(nolock)
        LEFT JOIN sljcli AS e with(nolock) ON a.resps = e.iclis
        LEFT JOIN sljeest AS g with(nolock) ON a.empdopnums = g.empdopnums
        LEFT JOIN SLJCLI AS I with(nolock) ON G.CONTADS = I.ICLIS
        LEFT JOIN SLJCLI AS K with(nolock) ON K.ICLIS = A.VENDS
        LEFT JOIN sljpro AS x with (nolock) ON a.cpros = x.cpros
        LEFT JOIN(
            SELECT
            CAST( b.dtemis AS DATE ) AS 'Data',
            RTRIM( b.nemps) AS 'ID_Vtex',
            CONCAT( RTRIM( b.contads ),'-',  RTRIM( b.notas )) AS ID_Pedido
        FROM sljeest b WITH(NOLOCK)
        WHERE RTRIM(dopes) = 'PEDIDO E-COMM'
        ) AS h ON CONCAT( RTRIM( a.iclis ) ,'-',  RTRIM( g.notas )) = h.ID_Pedido
    WHERE a.codbarras = 0
        AND a.emps <> 'NY'
        AND a.vvistas <> 0
        AND a.tipoops NOT IN (91, 92)
        AND a.dopes <> 'ADTO ENCOMENDA'
        AND (a.dopes <> 'VENDA PERMUTA'
        AND a.dopes <> 'VENDA FUNCIONARIO'
        AND a.dopes <> 'VENDA ENCOMENDA'
        AND a.dopes <> 'VENDA ENC E-COMM')


UNION ALL
    SELECT
        CASE
                WHEN RTRIM( EEST.emps ) LIKE 'IGL' THEN 'IGU'
                WHEN RTRIM( EEST.emps ) LIKE 'BAL' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'CUR' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'FSM' THEN 'DES'
                WHEN RTRIM( EEST.emps ) LIKE 'FTH' THEN 'WEB'
                WHEN RTRIM( EEST.emps ) LIKE 'FFL' THEN 'BEL'
                WHEN RTRIM( EEST.emps ) LIKE 'LMA' THEN 'MAT'
                WHEN RTRIM( EEST.emps ) LIKE 'MPV' THEN 'MP2'
                ELSE RTRIM( EEST.emps )
            END AS "Empresa",
        RTRIM(EEST.dopes) AS "Operacao",
        CAST (EEST.numes AS INTEGER ) AS "No.Oper",

        CASE
        WHEN CAST( z.Data AS DATE ) IS NULL THEN CAST( EEST.datas AS DATE )
        ELSE CAST( z.Data AS DATE )
        END AS "Data",

        --CONVERT(DATE, EEST.datas, 103) AS "Data",
        RTRIM( EEST.Contads ) AS "Cod. Cliente",
        RTRIM( H.RCLIS ) AS "Nome Cliente",
        CASE
                        WHEN RTRIM( EEST.vends ) IS NULL THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0399/6' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0531/5' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0720/2' THEN 'WEB'
                        ELSE RTRIM( EEST.vends )
                    END AS "Cod. Vend.",
        CASE
                        WHEN RTRIM( K.RCLIS ) IS NULL THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'ZAGO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'PERSIO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'MENINO' + '%' THEN 'WEB'
                        ELSE RTRIM( K.RCLIS )
                    END AS "Consultora",
        RTRIM(EEST.resps) AS "Cod. Acomp.",
        RTRIM(e.rclis) AS "Acompanhante",
        RTRIM(B.MERCS) AS "Grande Grupo",
        RTRIM( b.colecoes ) AS "Cod. Modelo",
        RTRIM( EESTI.cpros ) AS "Cod. Prod.",
        RTRIM(EESTI.codbarras) AS "Cod. Barras",
        RTRIM(M.codtams) AS "Tamanho",
        CAST( EESTI.qtds AS INTEGER ) AS "Qtd",
        CAST( EESTI.totas + eesti.valrats AS DECIMAL(10) ) AS "Total Liq.",
        CAST( EESTI.valrats AS DECIMAL(10) ) AS "Desconto",
        CAST( B.PCUSS AS DECIMAL(10) ) AS "Custo",
        CAST( EESTI.unitorigs AS DECIMAL(10) ) AS "Total Brt",
        RTRIM( g.notas ) AS "NF",
        CONCAT( EEST.Contads,'-',  CASE
        WHEN CAST
( z.Data AS DATE ) IS NULL THEN CAST
( EEST.datas AS DATE )
        ELSE CAST
( z.Data AS DATE )
END) as ID_Venda,
        CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) AS ID_Pedido,
        RTRIM( z.ID_Vtex ) AS "ID_Vtex",
        RTRIM( g.codevents ) AS "Evento"
    FROM SLJEEST AS EEST with(nolock)
        LEFT JOIN SLJEESTI AS EESTI with(nolock) ON EEST.EMPDOPNUMS = EESTI.EMPDOPNUMS
        LEFT JOIN sljpro AS b with(nolock) ON EESTI.cpros = b.cpros
        LEFT JOIN sljcli AS e with(nolock) ON EEST.resps = e.iclis
        LEFT JOIN sljeest AS g with(nolock) ON EEST.empdopnums = g.empdopnums
        LEFT JOIN sljcli AS h with(nolock) ON EEST.CONTADS = h.iclis
        LEFT JOIN SLJCLI AS K with(nolock) ON K.ICLIS = EEST.VENDS
        LEFT JOIN sljeti AS M with(nolock) ON EESTI.codbarras = M.cbars

        LEFT JOIN(
            SELECT
            CAST( b.dtemis AS DATE ) AS 'Data',
            RTRIM( b.nemps) AS 'ID_Vtex',
            CONCAT( RTRIM( b.contads ),'-',  RTRIM( b.notas )) AS ID_Pedido
        FROM sljeest b WITH(NOLOCK)
        WHERE RTRIM(dopes) = 'PEDIDO E-COMM'
        )  AS z ON CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) = z.ID_Pedido

    WHERE EEST.DOPES IN ('ADTO ENCOMENDA ', 'ENCOMENDA E-COMM')
        AND EEST.emps <> 'NY'
        AND EESTI.unitorigs <> 0
        AND EEST.datas < CONCAT( CONVERT( date, GETDATE()), ' 00:00:00')
        AND ( EEST.dopes <> 'VENDA PERMUTA'
        AND EEST.dopes <> 'VENDA FUNCIONARIO'
        AND EEST.dopes <> 'VENDA ENCOMENDA'
        AND EEST.dopes <> 'VENDA ENC E-COMM')


UNION ALL
    SELECT
        CASE
                WHEN RTRIM( EEST.emps ) LIKE 'IGL' THEN 'IGU'
                WHEN RTRIM( EEST.emps ) LIKE 'BAL' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'CUR' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'FSM' THEN 'DES'
                WHEN RTRIM( EEST.emps ) LIKE 'FTH' THEN 'WEB'
                WHEN RTRIM( EEST.emps ) LIKE 'FFL' THEN 'BEL'
                WHEN RTRIM( EEST.emps ) LIKE 'LMA' THEN 'MAT'
                WHEN RTRIM( EEST.emps ) LIKE 'MPV' THEN 'MP2'
                ELSE RTRIM( EEST.emps )
            END AS "Empresa",
        RTRIM(EEST.dopes) AS "Operacao",
        CAST (EEST.numes AS INTEGER) AS "No.Oper",

        CASE
        WHEN CAST( z.Data AS DATE ) IS NULL THEN CAST( EEST.datas AS DATE )
        ELSE CAST( z.Data AS DATE )
        END AS "Data",

        --CONVERT(DATE, EEST.datas, 103) AS "Data",
        RTRIM( EEST.Contads ) AS "Cod. Cliente",
        RTRIM( H.RCLIS ) AS "Nome Cliente",
        CASE
                        WHEN RTRIM( EEST.vends ) IS NULL THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0399/6' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0531/5' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0720/2' THEN 'WEB'
                        ELSE RTRIM( EEST.vends )
                    END AS "Cod. Vend.",
        CASE
                        WHEN RTRIM( K.RCLIS ) IS NULL THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'ZAGO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'PERSIO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'MENINO' + '%' THEN 'WEB'
                        ELSE RTRIM( K.RCLIS )
                    END AS "Consultora",
        RTRIM(EEST.resps) AS "Cod. Acomp.",
        RTRIM(e.rclis) AS "Acompanhante",
        RTRIM(B.MERCS) AS "Grande Grupo",
        RTRIM( b.colecoes ) AS "Cod. Modelo",
        RTRIM(EESTI.cpros) AS "Cod. Prod.",
        RTRIM(EESTI.codbarras) AS "Cod. Barras",
        RTRIM(M.codtams) AS "Tamanho",
        CAST( EESTI.qtds AS INTEGER ) AS "Qtd",
        CAST( EESTI.totas + eesti.valrats AS DECIMAL(10) ) AS "Total Liq.",
        CAST( EESTI.valrats AS DECIMAL(10) ) AS "Desconto",
        CAST( B.PCUSS AS DECIMAL(10) ) AS "Custo",
        CAST( EESTI.unitorigs AS DECIMAL(10) ) AS "Total Brt",
        RTRIM( g.notas ) AS "NF",
        CONCAT( EEST.Contads,'-',  CONVERT( DATE, EEST.datas, 3)) as ID_Venda,
        CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) AS ID_Pedido,
        RTRIM( z.ID_Vtex ) AS "ID_Vtex",
        RTRIM(g.codevents) AS "Evento"
    FROM SLJEEST AS EEST with(nolock)
        LEFT JOIN SLJEESTI AS EESTI with(nolock) ON EEST.EMPDOPNUMS = EESTI.EMPDOPNUMS
        LEFT JOIN sljpro AS b with(nolock) ON EESTI.cpros = b.cpros
        LEFT JOIN sljcli AS e with(nolock) ON EEST.resps = e.iclis
        LEFT JOIN sljeest AS g with(nolock) ON EEST.empdopnums = g.empdopnums
        LEFT JOIN sljcli AS h with(nolock) ON EEST.CONTADS = h.iclis
        LEFT JOIN SLJCLI AS K with(nolock) ON K.ICLIS = EEST.VENDS
        LEFT JOIN sljeti AS M with(nolock) ON EESTI.codbarras = M.cbars

        LEFT JOIN(
                    SELECT
            CAST( b.dtemis AS DATE ) AS 'Data',
            RTRIM( b.nemps) AS 'ID_Vtex',
            CONCAT( RTRIM( b.contads ),'-',  RTRIM( b.notas )) AS ID_Pedido
        FROM sljeest b WITH(NOLOCK)
        WHERE RTRIM(dopes) = 'PEDIDO E-COMM'
                )  AS z ON CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) = z.ID_Pedido

    WHERE
        RTRIM( EEST.DOPES) IN ('ADTO ENCOMENDA', 'ENCOMENDA E-COMM', 'VENDA E-COMMERCE', 'VENDA', 'VENDA FR',
        'VENDA CONSIGNACAO', 'TROCA')
        AND EEST.emps <> 'NY'
        AND EEST.emps <> 'FTH'
        AND EESTI.unitorigs <> 0
        AND ( EEST.dopes <> 'VENDA PERMUTA'
        AND EEST.dopes <> 'VENDA FUNCIONARIO'
        AND EEST.dopes <> 'VENDA ENCOMENDA'
        AND EEST.dopes <> 'VENDA ENC E-COMM')
        AND EEST.datas >= CONCAT( CONVERT( date, GETDATE()), ' 00:00:00')

UNION ALL
    SELECT
        CASE
                WHEN RTRIM( EEST.emps ) LIKE 'IGL' THEN 'IGU'
                WHEN RTRIM( EEST.emps ) LIKE 'BAL' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'CUR' THEN 'BAT'
                WHEN RTRIM( EEST.emps ) LIKE 'FSM' THEN 'DES'
                WHEN RTRIM( EEST.emps ) LIKE 'FTH' THEN 'WEB'
                WHEN RTRIM( EEST.emps ) LIKE 'FFL' THEN 'BEL'
                WHEN RTRIM( EEST.emps ) LIKE 'LMA' THEN 'MAT'
                WHEN RTRIM( EEST.emps ) LIKE 'MPV' THEN 'MP2'
                ELSE RTRIM( EEST.emps )
            END AS "Empresa",
        RTRIM(EEST.dopes) AS "Operacao",
        CAST (EEST.numes AS INTEGER) AS "No.Oper",

        CASE
        WHEN CAST( z.Data AS DATE ) IS NULL THEN CAST( EEST.datas AS DATE )
        ELSE CAST( z.Data AS DATE )
        END AS "Data",

        --CONVERT(DATE, EEST.datas, 103) AS "Data",
        RTRIM( EEST.Contads ) AS "Cod. Cliente",
        RTRIM( H.RCLIS ) AS "Nome Cliente",
        CASE
                        WHEN RTRIM( EEST.vends ) IS NULL THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0399/6' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0531/5' THEN 'WEB'
                        WHEN RTRIM( EEST.vends ) LIKE '0720/2' THEN 'WEB'
                        ELSE RTRIM( EEST.vends )
                    END AS "Cod. Vend.",
        CASE
                        WHEN RTRIM( K.RCLIS ) IS NULL THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'ZAGO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'PERSIO' + '%' THEN 'WEB'
                        WHEN RTRIM( K.RCLIS ) LIKE '%' + 'MENINO' + '%' THEN 'WEB'
                        ELSE RTRIM( K.RCLIS )
                    END AS "Consultora",
        RTRIM(EEST.resps) AS "Cod. Acomp.",
        RTRIM(e.rclis) AS "Acompanhante",
        RTRIM(B.MERCS) AS "Grande Grupo",
        RTRIM( b.colecoes ) AS "Cod. Modelo",
        RTRIM(b.cpros) AS "Cod. Prod.",
        RTRIM(EESTI.codbarras) AS "Cod. Barras",
        RTRIM(M.codtams) AS "Tamanho",
        CAST( EESTI.qtds AS INTEGER ) AS "Qtd",
        CAST( EESTI.totas + eesti.valrats AS DECIMAL(10) ) AS "Total Liq.",
        CAST( EESTI.valrats AS DECIMAL(10) ) AS "Desconto",
        CAST( B.PCUSS AS DECIMAL(10) ) AS "Custo",
        CAST( EESTI.unitorigs AS DECIMAL(10) ) AS "Total Brt",
        RTRIM( g.notas ) AS "NF",
        CONCAT( EEST.Contads,'-',  CONVERT( DATE, EEST.datas, 3)) as ID_Venda,
        CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) AS ID_Pedido,
        RTRIM( z.ID_Vtex ) AS "ID_Vtex",
        RTRIM(g.codevents) AS "Evento"
    FROM SLJEEST AS EEST with(nolock)
        LEFT JOIN SLJEESTI AS EESTI with(nolock) ON EEST.EMPDOPNUMS = EESTI.EMPDOPNUMS
        LEFT JOIN sljpro AS b with(nolock) ON EESTI.cpros = b.cpros
        LEFT JOIN sljcli AS e with(nolock) ON EEST.resps = e.iclis
        LEFT JOIN sljeest AS g with(nolock) ON EEST.empdopnums = g.empdopnums
        LEFT JOIN sljcli AS h with(nolock) ON EEST.CONTADS = h.iclis
        LEFT JOIN SLJCLI AS K with(nolock) ON K.ICLIS = EEST.VENDS
        LEFT JOIN sljeti AS M with(nolock) ON EESTI.codbarras = M.cbars

        LEFT JOIN(
                    SELECT
            CAST( b.dtemis AS DATE ) AS 'Data',
            RTRIM( b.nemps) AS 'ID_Vtex',
            CONCAT( RTRIM( b.contads ),'-',  RTRIM( b.notas )) AS ID_Pedido
        FROM sljeest b WITH(NOLOCK)
        WHERE RTRIM(dopes) = 'PEDIDO E-COMM'
                )  AS z ON CONCAT( EEST.Contads,'-',  RTRIM( g.notas )) = z.ID_Pedido

    WHERE
        RTRIM( EEST.DOPES) IN ('ADTO ENCOMENDA', 'ENCOMENDA E-COMM', 'VENDA E-COMMERCE', 'VENDA', 'VENDA FR',
        'VENDA CONSIGNACAO', 'TROCA')
        AND EEST.emps = 'FTH'
        -- AND EESTI.unitorigs <> 0
        AND ( EEST.dopes <> 'VENDA PERMUTA'
        AND EEST.dopes <> 'VENDA FUNCIONARIO'
        AND EEST.dopes <> 'VENDA ENCOMENDA'
        AND EEST.dopes <> 'VENDA ENC E-COMM')
        AND EEST.datas >= CONCAT( CONVERT( date, GETDATE()), ' 00:00:00')
ORDER BY "Data" DESC
