-- Canteen Token Management System Schema

CREATE DATABASE IF NOT EXISTS canteen_db;
USE canteen_db;

-- 1. User Table
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_no VARCHAR(15),
    gender ENUM('Male', 'Female', 'Other'),
    role ENUM('Admin', 'Customer') DEFAULT 'Customer',
    password VARCHAR(255) NOT NULL,
    address TEXT
);

-- 2. Item Table
CREATE TABLE Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    dietary ENUM('Veg', 'Non-Veg') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status ENUM('Available', 'Out of Stock') DEFAULT 'Available'
);

-- 3. Orders Table
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Completed') DEFAULT 'Pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- 4. Order_Items Table
CREATE TABLE Order_Items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    item_id INT,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Item(item_id) ON DELETE CASCADE
);

-- 5. Payment Table
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE,
    transaction_id VARCHAR(100) UNIQUE,
    method ENUM('UPI', 'Card', 'Cash') NOT NULL,
    status ENUM('Pending', 'Success', 'Failed') DEFAULT 'Pending',
    paid_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE
);

-- 6. Token Table
CREATE TABLE Token (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE,
    token_no INT NOT NULL,
    token_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Preparing', 'Ready', 'Delivered') DEFAULT 'Preparing',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE
);

-- VIEWS for Admin Analytics
CREATE VIEW Revenue_Summary AS
SELECT 
    DATE(order_date) as date,
    SUM(total_amount) as total_revenue,
    COUNT(order_id) as total_orders
FROM Orders
WHERE status = 'Completed'
GROUP BY DATE(order_date);

CREATE VIEW Most_Sold_Items AS
SELECT 
    i.name,
    SUM(oi.quantity) as total_quantity
FROM Item i
JOIN Order_Items oi ON i.item_id = oi.item_id
GROUP BY i.item_id
ORDER BY total_quantity DESC;

-- TRIGGER for Auto Token Generation
DELIMITER //
CREATE TRIGGER After_Payment_Success
AFTER UPDATE ON Payment
FOR EACH ROW
BEGIN
    IF NEW.status = 'Success' THEN
        -- Generate token_no: Fetch last token_no for the current day and increment
        SET @last_token = (SELECT MAX(token_no) FROM Token WHERE DATE(token_time) = CURDATE());
        IF @last_token IS NULL THEN
            SET @last_token = 0;
        END IF;
        
        INSERT INTO Token (order_id, token_no, token_time, status)
        VALUES (NEW.order_id, @last_token + 1, NOW(), 'Preparing');
        
        -- Mark Order as Completed (or keep as Pending until Delivered)
        -- For this system, we'll keep it Pending until Admin marks it Ready/Delivered
    END IF;
END;
//
DELIMITER ;

-- SAMPLE DATA
INSERT INTO User (name, email, phone_no, gender, role, password, address) VALUES 
('Admin User', 'admin@canteen.com', '9876543210', 'Male', 'Admin', '$2b$12$K7O1/gV/rUpf9A0p8F9GReW7yQ7G9u6W6G6G6G6G6G6G6G6G6G6G', 'Main Canteen Office'),
('John Doe', 'john@gmail.com', '1234567890', 'Male', 'Customer', '$2b$12$K7O1/gV/rUpf9A0p8F9GReW7yQ7G9u6W6G6G6G6G6G6G6G6G6G6G', 'Hostel Block A');

INSERT INTO Item (name, category, dietary, price, status) VALUES 
('Classic Burger', 'Fast Food', 'Non-Veg', 120.00, 'Available'),
('Paneer Butter Masala', 'Main Course', 'Veg', 180.00, 'Available'),
('Veg Hakka Noodles', 'Chinese', 'Veg', 150.00, 'Available'),
('Chicken Tikka', 'Starter', 'Non-Veg', 200.00, 'Available'),
('Cold Coffee', 'Beverages', 'Veg', 60.00, 'Available');
