select * from tb_account;
select * from tb_product;
select * from tb_store;
 to2 where store_id = '7ff0f966-59bc-43c8-b76e-3b42c63d8e52';
select * from tb_order_items toi;

ALTER TABLE tb_store
ADD COLUMN cep VARCHAR(9) NOT NULL DEFAULT '00000-000';	

ALTER TABLE tb_product
ADD COLUMN store_id uuid;

ALTER TABLE tb_store
ADD COLUMN delivery_fee FLOAT NOT NULL DEFAULT 0.0;

ALTER TABLE tb_order
ADD COLUMN status_history VARCHAR(100);

ALTER TABLE tb_order 
ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

ALTER TYPE "orderstatusenum" RENAME TO "orderstatusenum_old";

CREATE TYPE "orderstatusenum" AS ENUM (
    'RECEBIDO',
    'EM_PREPARO',
    'ENVIADO',
    'ENTREGUE',
    'CANCELADO'
);

ALTER TABLE tb_order 
ALTER COLUMN status TYPE TEXT 
USING (
    CASE status::text
        WHEN 'PENDING' THEN 'RECEBIDO'
        WHEN 'PROCESSING' THEN 'EM_PREPARO'
        WHEN 'SHIPPED' THEN 'ENVIADO'
        WHEN 'DELIVERED' THEN 'ENTREGUE'
        WHEN 'CANCELLED' THEN 'CANCELADO'
        ELSE 'RECEBIDO'
    END
);

ALTER TABLE tb_order 
ALTER COLUMN status TYPE "orderstatusenum" 
USING status::"orderstatusenum";

DROP TYPE "orderstatusenum_old";

ALTER TABLE tb_order 
ALTER COLUMN status_history TYPE JSONB 
USING status_history::jsonb;



