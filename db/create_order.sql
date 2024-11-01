-- db/create_order.sql
INSERT INTO orders (id, user_id, product_id, order_no, status, address, billing_address, source, commission_fee)
VALUES (:id, :user_id, :product_id, :order_no, :status, :address, :billing_address, :source, :commission_fee);
