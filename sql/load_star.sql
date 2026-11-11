-- dim_fecha: un día por fila, desde 2024 hasta fin de 2027
INSERT INTO dim_fecha
SELECT to_char(d, 'YYYYMMDD')::int, d::date,
       EXTRACT(day FROM d), EXTRACT(isodow FROM d), EXTRACT(week FROM d),
       EXTRACT(month FROM d), EXTRACT(quarter FROM d), EXTRACT(year FROM d),
       EXTRACT(isodow FROM d) IN (6, 7)
FROM generate_series('2024-01-01'::date, '2027-12-31'::date, '1 day') AS d;

-- dim_producto: una fila por producto, con una categoría simple
INSERT INTO dim_producto (producto_id, nombre, categoria)
SELECT DISTINCT producto_id, producto,
       CASE WHEN producto IN ('jabon', 'detergente', 'papel', 'shampoo') THEN 'aseo'
            WHEN producto IN ('gaseosa', 'agua', 'cerveza') THEN 'bebidas'
            ELSE 'alimentos' END
FROM pedidos_raw;

-- dim_cliente: versión inicial de cada cliente (SCD2: vigente desde su primer pedido)
INSERT INTO dim_cliente (cliente_id, nombre, ciudad, valido_desde)
SELECT cliente_id, MIN(cliente), MIN(ciudad), MIN(fecha)
FROM pedidos_raw GROUP BY cliente_id;

-- fact_pedido_item: cada fila cruda se une con la versión de cliente vigente en su fecha
INSERT INTO fact_pedido_item (pedido_id, cliente_sk, producto_sk, fecha_sk, cantidad, precio_unitario, total)
SELECT r.id, c.cliente_sk, p.producto_sk, to_char(r.fecha, 'YYYYMMDD')::int,
       r.cantidad, r.precio_unitario, r.total
FROM pedidos_raw r
JOIN dim_cliente c ON c.cliente_id = r.cliente_id
                  AND r.fecha >= c.valido_desde AND r.fecha < c.valido_hasta
JOIN dim_producto p ON p.producto_id = r.producto_id;