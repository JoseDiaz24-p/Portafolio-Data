SELECT
    CASE
        WHEN STARTS_WITH(InvoiceNo, 'C') THEN 'Cancelacion'
        ELSE 'Venta Normal'
    END AS tipo_transaccion,
    COUNT(DISTINCT InvoiceNo) AS facturas,
    COUNT(*) AS lineas,
    SUM(Quantity) AS unidades,
    ROUND(SUM(total_amount), 2) AS importe
FROM `data-engenieer.online_retail_dw.fact_sales`
GROUP BY tipo_transaccion
ORDER BY tipo_transaccion;