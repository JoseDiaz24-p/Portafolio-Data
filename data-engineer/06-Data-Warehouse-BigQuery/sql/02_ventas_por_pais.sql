SELECT
    c.Country,
    COUNT(DISTINCT f.InvoiceNo) AS facturas,
    SUM(f.Quantity) AS unidades_vendidas,
    ROUND(SUM(f.total_amount), 2) AS ventas_totales
FROM `data-engenieer.online_retail_dw.fact_sales` f
JOIN `data-engenieer.online_retail_dw.dim_country` c
    ON f.country_key = c.country_key
GROUP BY c.Country
ORDER BY ventas_totales DESC;