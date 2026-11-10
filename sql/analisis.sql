-- 1. Total vendido por cliente y mes
SELECT cliente, date_trunc('month', fecha)::date AS mes, SUM(total) AS total_mes
FROM pedidos_raw
GROUP BY cliente, mes
ORDER BY mes, total_mes DESC;

-- 2. Top 10 clientes por mes (window function RANK)
WITH ventas AS (
    SELECT cliente, date_trunc('month', fecha)::date AS mes, SUM(total) AS total_mes
    FROM pedidos_raw GROUP BY cliente, mes
), ranking AS (
    SELECT *, RANK() OVER (PARTITION BY mes ORDER BY total_mes DESC) AS puesto
    FROM ventas
)
SELECT * FROM ranking WHERE puesto <= 10 ORDER BY mes, puesto;

-- 3. Retención por cohorte: % de clientes que vuelven 1, 2 y 3 meses después de su primer pedido
WITH primer AS (
    SELECT cliente_id, date_trunc('month', MIN(fecha))::date AS cohorte FROM pedidos_raw GROUP BY cliente_id
), actividad AS (
    SELECT DISTINCT cliente_id, date_trunc('month', fecha)::date AS mes FROM pedidos_raw
), cruce AS (
    SELECT p.cohorte, a.cliente_id,
           (EXTRACT(year FROM a.mes) - EXTRACT(year FROM p.cohorte)) * 12
         + (EXTRACT(month FROM a.mes) - EXTRACT(month FROM p.cohorte)) AS meses_despues
    FROM primer p JOIN actividad a USING (cliente_id)
)
SELECT cohorte,
       COUNT(DISTINCT cliente_id) FILTER (WHERE meses_despues = 0) AS clientes,
       COUNT(DISTINCT cliente_id) FILTER (WHERE meses_despues = 1) AS mes_1,
       COUNT(DISTINCT cliente_id) FILTER (WHERE meses_despues = 2) AS mes_2,
       COUNT(DISTINCT cliente_id) FILTER (WHERE meses_despues = 3) AS mes_3
FROM cruce GROUP BY cohorte ORDER BY cohorte;

-- 4. Posibles duplicados: mismo cliente y producto con menos de 10 minutos de diferencia (LAG)
WITH ordenado AS (
    SELECT id, cliente_id, producto_id, creado_en,
           LAG(creado_en) OVER (PARTITION BY cliente_id, producto_id ORDER BY creado_en) AS anterior
    FROM pedidos_raw
)
SELECT * FROM ordenado WHERE creado_en - anterior < interval '10 minutes';

-- 5. Promedio móvil de ventas diarias de 7 días
WITH diario AS (
    SELECT fecha, SUM(total) AS ventas FROM pedidos_raw GROUP BY fecha
)
SELECT fecha, ventas,
       AVG(ventas) OVER (ORDER BY fecha ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS promedio_7d
FROM diario ORDER BY fecha;

-- 6. Producto favorito de cada cliente (ROW_NUMBER)
WITH conteo AS (
    SELECT cliente, producto, SUM(cantidad) AS unidades,
           ROW_NUMBER() OVER (PARTITION BY cliente ORDER BY SUM(cantidad) DESC) AS rn
    FROM pedidos_raw GROUP BY cliente, producto
)
SELECT cliente, producto, unidades FROM conteo WHERE rn = 1 ORDER BY cliente;