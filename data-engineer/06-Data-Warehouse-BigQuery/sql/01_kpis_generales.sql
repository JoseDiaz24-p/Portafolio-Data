SELECT
    COUNT(*) AS total_registros,
    COUNT(DISTINCT InvoiceNo) AS facturas,
    ROUND(SUM(total_amount), 2) AS ventas_totales,
    SUM(Quantity) AS unidades_totales
FROM `data-engenieer.online_retail_dw.fact_sales`;