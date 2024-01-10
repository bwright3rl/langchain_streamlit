SELECT
    EXTRACT(
        YEAR
        FROM
            "transaction_at"
    ) AS "year",
    SUM(
        CASE
            WHEN "department" = 'HANDBAGS' THEN "usd_amount"
            ELSE 0
        END
    ) AS "Handbag Sales",
    SUM(
        CASE
            WHEN "department" = 'HANDBAGS' THEN "usd_amount"
            ELSE 0
        END
    ) - LAG(
        SUM(
            CASE
                WHEN "department" = 'HANDBAGS' THEN "usd_amount"
                ELSE 0
            END
        ),
        1
    ) OVER (
        ORDER BY
            EXTRACT(
                YEAR
                FROM
                    "transaction_at"
            )
    ) AS "Year on Year Growth"
FROM
    CIX_PROD_DB.FOUNDATION.FCT_TRANSACTION_DETAILS AS fct
    JOIN CIX_PROD_DB.FOUNDATION.DIM_PRODUCTS AS dim ON fct."product_id" = dim."product_id"
WHERE
    EXTRACT(
        YEAR
        FROM
            "transaction_at"
    ) BETWEEN YEAR(DATEADD(YEAR, -5, GETDATE()))
    AND YEAR(GETDATE())
GROUP BY
    EXTRACT(
        YEAR
        FROM
            "transaction_at"
    )
ORDER BY
    EXTRACT(
        YEAR
        FROM
            "transaction_at"
    ) DESC;