SELECT
    c.CustomerID,
    COUNT(DISTINCT f.InvoiceNo) AS facturas,
    SUM(f.Quantity) AS unidades_compradas,
    ROUND(SUM(f.total_amount), 2) AS ventas_totales
FROM `data-engenieer.online_retail_dw.fact_sales` f
JOIN `data-engenieer.online_retail_dw.dim_customer` c
    ON f.customer_key = c.customer_key
GROUP BY
    c.CustomerID
ORDER BY
    ventas_totales DESC
LIMIT 20;