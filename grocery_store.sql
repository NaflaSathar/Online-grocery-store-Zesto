-- Database creation
CREATE DATABASE IF NOT EXISTS grocery_store;
USE grocery_store;

-- Users table
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    address VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_key VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    stock_quantity INT DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Order items table
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Cart table (for persistent carts if needed)
CREATE TABLE carts (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Cart items table
CREATE TABLE cart_items (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Insert sample products
INSERT INTO products (product_key, name, price, category, image_path) VALUES
('oranges', 'Oranges', 80.00, 'Fruits', 'images/oranges.jpg'),
('grapes', 'Grapes', 90.00, 'Fruits', 'images/grapes.jpg'),
('poha', 'Poha', 35.00, 'Grains', 'images/poha.jpg'),
('bread', 'Whole Wheat Bread', 40.00, 'Bakery', 'images/bread.jpg'),
('milk', 'Organic Milk', 60.00, 'Dairy', 'images/milk.jpg'),
('eggs', 'Eggs (12 pcs)', 70.00, 'Dairy', 'images/eggs.jpg'),
('rice', 'Basmati Rice (1kg)', 120.00, 'Grains', 'images/rice.jpg'),
('toor_dal', 'Toor Dal (1kg)', 100.00, 'Grains', 'images/toor_dal.jpg'),
('tomatoes', 'Tomatoes (1kg)', 30.00, 'Vegetables', 'images/tomatoes.jpg'),
('onions', 'Onions (1kg)', 25.00, 'Vegetables', 'images/onions.jpg');

