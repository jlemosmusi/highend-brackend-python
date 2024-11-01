-- db/update_order_status.sql
UPDATE orders SET status = :status WHERE id = :id;
