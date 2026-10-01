SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.InvoiceNo) AS facturas,
    SUM(f.Quantity) AS unidades_vendidas,
    ROUND(SUM(f.total_amount), 2) AS ventas_totales
FROM `data-engenieer.online_retail_dw.fact_sales` f
JOIN `data-engenieer.online_retail_dw.dim_date` d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;