SELECT
    COUNT(DISTINCT InvoiceNo) AS facturas_canceladas,
    COUNT(*) AS lineas_canceladas,
    SUM(Quantity) AS unidades_canceladas,
    ROUND(SUM(total_amount), 2) AS impacto_total_cancelaciones
FROM `data-engenieer.online_retail_dw.fact_sales`
WHERE STARTS_WITH(InvoiceNo, 'C');