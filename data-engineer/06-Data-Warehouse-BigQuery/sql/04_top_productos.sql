SELECT
    p.StockCode,
    p.Description_Principal,
    SUM(f.Quantity) AS unidades_vendidas,
    ROUND(SUM(f.total_amount), 2) AS ventas_totales
FROM `data-engenieer.online_retail_dw.fact_sales` f
JOIN `data-engenieer.online_retail_dw.dim_product` p
    ON f.product_key = p.product_key
GROUP BY
    p.StockCode,
    p.Description_Principal
ORDER BY
    unidades_vendidas DESC
LIMIT 20;