SELECT c.nombre AS cliente, d.anio, d.mes, SUM(f.total) AS total_mes
FROM fact_pedido_item f
JOIN dim_cliente c USING (cliente_sk)
JOIN dim_fecha d USING (fecha_sk)

SELECT c.nombre AS cliente, d.anio, d.mes, SUM(f.total) AS total_mes
FROM fact_pedido_item f
JOIN dim_cliente c USING (cliente_sk)
JOIN dim_fecha d USING (fecha_sk)
GROUP BY 1, 2, 3 ORDER BY 2, 3, 4 DESC;