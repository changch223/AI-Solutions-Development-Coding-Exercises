DROP TABLE IF EXISTS order_returns;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS subcategories;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS states;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS ship_modes;
DROP TABLE IF EXISTS customer_segments;


CREATE TABLE categories (
    category_code CHAR(3) NOT NULL,
	category_name VARCHAR(64) NOT NULL,
	PRIMARY KEY (category_code)
);

CREATE TABLE subcategories (
	category_code CHAR(3) NOT NULL,
	subcategory_code CHAR(2) NOT NULL,
	subcategory_name VARCHAR(64) NOT NULL,
	PRIMARY KEY (category_code, subcategory_code),
	FOREIGN KEY (category_code) REFERENCES categories(category_code)
);

CREATE TABLE employees (
    employee_id CHAR(8),
	employee_name VARCHAR(64),
	PRIMARY KEY (employee_id)
);

CREATE TABLE regions (
    region_code CHAR(1) NOT NULL,
	region_name VARCHAR(16) NOT NULL,
	manager_employee_id CHAR(8) NOT NULL,
	PRIMARY KEY (region_code),
	FOREIGN KEY (manager_employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE states (
    state_code CHAR(2) NOT NULL,
	region_code CHAR(1) NOT NULL,
	state_name VARCHAR(24) NOT NULL,
	PRIMARY KEY (state_code),
	FOREIGN KEY (region_code) REFERENCES regions(region_code)
);

CREATE TABLE cities (
    city_id INT NOT NULL,
	state_code CHAR(2) NOT NULL,
	city_name VARCHAR(64) NOT NULL,
	PRIMARY KEY (city_id),
	FOREIGN KEY (state_code) REFERENCES states(state_code)
);

CREATE TABLE stores (
    postal_code CHAR(5) NOT NULL,
	city_id INT NOT NULL,
	PRIMARY KEY (postal_code),
	FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE ship_modes (
    ship_mode_code CHAR(1) NOT NULL,
	ship_mode_name VARCHAR(32) NOT NULL,
	PRIMARY KEY (ship_mode_code)
);

CREATE TABLE customer_segments (
    segment_code CHAR(1) NOT NULL,
	segment_name VARCHAR(32) NOT NULL,
	PRIMARY KEY (segment_code)
);

CREATE TABLE customers (
    customer_id CHAR(8) NOT NULL,
	segment_code CHAR(1) NOT NULL,
	customer_name VARCHAR(32) NOT NULL,
	PRIMARY KEY (customer_id),
	FOREIGN KEY (segment_code) REFERENCES customer_segments(segment_code)
);

CREATE TABLE products (
    product_id CHAR(14) NOT NULL,
	product_name VARCHAR(256) NOT NULL,
	category_code CHAR(3) NOT NULL,
	subcategory_code CHAR(2) NOT NULL,
	unit_price DECIMAL(7, 2) NOT NULL,
	unit_cost DECIMAL(7, 2) NOT NULL,
	PRIMARY KEY (product_id, product_name),
	FOREIGN KEY (category_code, subcategory_code) REFERENCES subcategories(category_code, subcategory_code)
);

CREATE TABLE orders (
    order_id CHAR(14) NOT NULL,
	customer_id CHAR(8) NOT NULL,
	postal_code CHAR(5) NOT NULL,
	order_date DATE NOT NULL,
	discount_percentage DECIMAL(2, 2) NOT NULL,
	amount_total DECIMAL(8, 2) NOT NULL,
	ship_mode_code CHAR(1) NULL,
	shipping_date DATE NULL,
	PRIMARY KEY (order_id),
	FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
	FOREIGN KEY (postal_code) REFERENCES stores(postal_code),
	FOREIGN KEY (ship_mode_code) REFERENCES ship_modes(ship_mode_code)
);

CREATE TABLE order_items (
    order_item_id INT NOT NULL,
    order_id CHAR(14) NOT NULL,
	product_id CHAR(14) NOT NULL,
	product_name VARCHAR(256) NOT NULL,
	unit_price DECIMAL(7, 2) NOT NULL,
	unit_cost DECIMAL(7, 2) NOT NULL,
	quantity INT NOT NULL,
	PRIMARY KEY (order_item_id),
	FOREIGN KEY (order_id) REFERENCES orders(order_id),
	FOREIGN KEY (product_id, product_name) REFERENCES products(product_id, product_name)
);

CREATE TABLE order_returns (
    order_id CHAR(14) NOT NULL,
	PRIMARY KEY (order_id)
);
