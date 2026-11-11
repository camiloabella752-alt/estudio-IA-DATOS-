DROP TABLE IF EXISTS fact_pedido_item, dim_cliente, dim_producto, dim_fecha;

CREATE TABLE dim_cliente (
    cliente_sk   serial PRIMARY KEY,
    cliente_id   int NOT NULL,
    nombre       text NOT NULL,
    ciudad       text NOT NULL,
    valido_desde date NOT NULL,
    valido_hasta date NOT NULL DEFAULT '9999-12-31',
    es_actual    boolean NOT NULL DEFAULT true
);

CREATE TABLE dim_producto (
    producto_sk serial PRIMARY KEY,
    producto_id int NOT NULL UNIQUE,
    nombre      text NOT NULL,
    categoria   text NOT NULL
);

CREATE TABLE dim_fecha (
    fecha_sk         int PRIMARY KEY,   -- formato AAAAMMDD, p. ej. 20261106
    fecha            date NOT NULL UNIQUE,
    dia              int, dia_semana int, semana int, mes int, trimestre int, anio int,
    es_fin_de_semana boolean
);

CREATE TABLE fact_pedido_item (
    item_sk         bigserial PRIMARY KEY,
    pedido_id       int NOT NULL,
    cliente_sk      int NOT NULL REFERENCES dim_cliente,
    producto_sk     int NOT NULL REFERENCES dim_producto,
    fecha_sk        int NOT NULL REFERENCES dim_fecha,
    cantidad        int NOT NULL,
    precio_unitario numeric NOT NULL,
    total           numeric NOT NULL
);