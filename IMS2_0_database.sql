use ims_ai_database;
ALTER TABLE products 
ADD COLUMN description TEXT AFTER name,
ADD COLUMN supplier VARCHAR(100) AFTER brand,
ADD COLUMN sku VARCHAR(50) AFTER status,
ADD COLUMN barcode VARCHAR(50) AFTER sku,
ADD COLUMN tax_vat DECIMAL(5,2) DEFAULT 0 AFTER sale_price,
ADD COLUMN low_stock_alert INT DEFAULT 5 AFTER stock;

select * from products;

ALTER TABLE products 
DROP COLUMN reorder_level, 
DROP COLUMN vat_percentage;


CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

select * from categories;
select * from sales_items;
select * from sales;
select * from users;
select * from login_logs;
select * from brands;

truncate table products;




