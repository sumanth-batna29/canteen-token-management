# 📘 CanteenQuick — SQL Queries Reference

Database: `canteen_db`  
Tables: `User`, `Item`, `Orders`, `Order_Items`, `Payment`, `Token`

---

## Part 1 — Aggregate Functions, Constraints & Set Operations

### 🔢 Aggregate Functions

**Total number of orders placed:**
```sql
SELECT COUNT(*) AS total_orders FROM Orders;
```

**Total revenue from completed orders:**
```sql
SELECT SUM(total_amount) AS total_revenue
FROM Orders
WHERE status = 'Completed';
```

**Average order value:**
```sql
SELECT ROUND(AVG(total_amount), 2) AS avg_order_value FROM Orders;
```

**Highest and lowest single order amounts:**
```sql
SELECT MAX(total_amount) AS highest_order,
       MIN(total_amount) AS lowest_order
FROM Orders;
```

**Total quantity sold per item:**
```sql
SELECT i.name, SUM(oi.quantity) AS total_sold
FROM Order_Items oi
JOIN Item i ON oi.item_id = i.item_id
GROUP BY i.item_id, i.name
ORDER BY total_sold DESC;
```

**Number of orders per day:**
```sql
SELECT DATE(order_date) AS order_day, COUNT(*) AS orders_count
FROM Orders
GROUP BY DATE(order_date)
ORDER BY order_day DESC;
```

**Only items sold more than 10 times (HAVING):**
```sql
SELECT i.name, SUM(oi.quantity) AS total_sold
FROM Order_Items oi
JOIN Item i ON oi.item_id = i.item_id
GROUP BY i.item_id, i.name
HAVING total_sold > 10;
```

---

### 🔒 Constraints

**Primary Key — each order has a unique ID:**
```sql
CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id  INT NOT NULL,
    status   VARCHAR(20) DEFAULT 'Pending',
    total_amount FLOAT NOT NULL
);
```

**Foreign Key — order must belong to a valid user:**
```sql
ALTER TABLE Orders
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE;
```

**Unique constraint — each user email must be unique:**
```sql
ALTER TABLE User
ADD CONSTRAINT uq_email UNIQUE (email);
```

**NOT NULL constraint — item price cannot be null:**
```sql
ALTER TABLE Item MODIFY COLUMN price FLOAT NOT NULL;
```

**CHECK constraint — quantity must be at least 1:**
```sql
ALTER TABLE Order_Items
ADD CONSTRAINT chk_quantity CHECK (quantity >= 1);
```

---

### ➕ Set Operations

**Items that have been ordered AND are still available (INTERSECT simulation):**
```sql
SELECT item_id FROM Order_Items
WHERE item_id IN (
    SELECT item_id FROM Item WHERE status = 'Available'
);
```

**Users who have placed orders (UNION with those who haven't):**
```sql
SELECT user_id, 'Has Orders' AS order_status FROM Orders
UNION
SELECT user_id, 'No Orders' AS order_status FROM User
WHERE user_id NOT IN (SELECT DISTINCT user_id FROM Orders);
```

**Items ordered today that are also Veg (simulated INTERSECT):**
```sql
SELECT DISTINCT i.name
FROM Item i
WHERE i.item_id IN (
    SELECT oi.item_id FROM Order_Items oi
    JOIN Orders o ON oi.order_id = o.order_id
    WHERE DATE(o.order_date) = CURDATE()
)
AND i.dietary = 'Veg';
```

**All item names from orders or menu (UNION):**
```sql
SELECT name FROM Item WHERE status = 'Available'
UNION
SELECT i.name FROM Item i
JOIN Order_Items oi ON i.item_id = oi.item_id;
```

**Items never ordered (EXCEPT simulation using NOT IN):**
```sql
SELECT name FROM Item
WHERE item_id NOT IN (SELECT DISTINCT item_id FROM Order_Items);
```

---

## Part 2 — Subqueries, Joins & Views

### 🔗 Joins

**All orders with customer name:**
```sql
SELECT o.order_id, u.name AS customer, o.total_amount, o.status
FROM Orders o
INNER JOIN User u ON o.user_id = u.user_id;
```

**Order details with item names and quantities:**
```sql
SELECT o.order_id, i.name AS item, oi.quantity, oi.subtotal
FROM Orders o
JOIN Order_Items oi ON o.order_id = oi.order_id
JOIN Item i ON oi.item_id = i.item_id
ORDER BY o.order_id;
```

**Orders with their token status (LEFT JOIN — shows orders with no token too):**
```sql
SELECT o.order_id, o.status AS order_status,
       t.token_no, t.status AS token_status
FROM Orders o
LEFT JOIN Token t ON o.order_id = t.order_id;
```

**Orders with payment info (RIGHT JOIN):**
```sql
SELECT p.payment_id, o.order_id, o.total_amount, p.status AS payment_status
FROM Orders o
RIGHT JOIN Payment p ON o.order_id = p.order_id;
```

**Full order summary (multi-table join):**
```sql
SELECT u.name, o.order_id, o.total_amount, t.token_no,
       t.status AS token_status, o.order_date
FROM User u
JOIN Orders o ON u.user_id = o.user_id
LEFT JOIN Token t ON o.order_id = t.order_id
ORDER BY o.order_date DESC;
```

---

### 🔍 Subqueries

**Orders placed by the most active customer:**
```sql
SELECT * FROM Orders
WHERE user_id = (
    SELECT user_id FROM Orders
    GROUP BY user_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);
```

**Items that cost more than the average item price:**
```sql
SELECT name, price FROM Item
WHERE price > (SELECT AVG(price) FROM Item);
```

**Users who have spent more than ₹500 total:**
```sql
SELECT u.name, SUM(o.total_amount) AS total_spent
FROM User u
JOIN Orders o ON u.user_id = o.user_id
GROUP BY u.user_id
HAVING total_spent > (SELECT AVG(total_amount) * 2 FROM Orders);
```

**Orders where all items are Veg (correlated subquery):**
```sql
SELECT o.order_id FROM Orders o
WHERE NOT EXISTS (
    SELECT 1 FROM Order_Items oi
    JOIN Item i ON oi.item_id = i.item_id
    WHERE oi.order_id = o.order_id AND i.dietary = 'Non-Veg'
);
```

**Most recently ordered item:**
```sql
SELECT i.name FROM Item i
WHERE i.item_id = (
    SELECT oi.item_id FROM Order_Items oi
    JOIN Orders o ON oi.order_id = o.order_id
    ORDER BY o.order_date DESC
    LIMIT 1
);
```

---

### 👁️ Views

**View: Full order summary visible to admin:**
```sql
CREATE OR REPLACE VIEW admin_order_summary AS
SELECT o.order_id, u.name AS customer_name, u.email,
       o.total_amount, o.status, o.order_date,
       t.token_no, t.status AS token_status
FROM Orders o
JOIN User u ON o.user_id = u.user_id
LEFT JOIN Token t ON o.order_id = t.order_id;
```

*Usage:*
```sql
SELECT * FROM admin_order_summary WHERE status = 'Pending';
```

**View: Daily revenue report:**
```sql
CREATE OR REPLACE VIEW daily_revenue AS
SELECT DATE(order_date) AS day,
       COUNT(*) AS total_orders,
       SUM(total_amount) AS revenue
FROM Orders
WHERE status = 'Completed'
GROUP BY DATE(order_date);
```

*Usage:*
```sql
SELECT * FROM daily_revenue ORDER BY day DESC;
```

**View: Popular items (top items by quantity sold):**
```sql
CREATE OR REPLACE VIEW popular_items AS
SELECT i.name, i.category, i.price,
       SUM(oi.quantity) AS total_ordered
FROM Item i
JOIN Order_Items oi ON i.item_id = oi.item_id
GROUP BY i.item_id
ORDER BY total_ordered DESC;
```

*Usage:*
```sql
SELECT * FROM popular_items LIMIT 5;
```

---

## Part 3 — Functions, Triggers, Cursors & Exception Handling

### ⚙️ Functions

**Function: Calculate estimated wait time for a user's token:**
```sql
DELIMITER //
CREATE FUNCTION get_wait_time(p_order_id INT)
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE v_token_no INT;
    DECLARE v_min_serving INT;
    DECLARE v_wait INT;

    SELECT token_no INTO v_token_no
    FROM Token WHERE order_id = p_order_id;

    SELECT MIN(token_no) INTO v_min_serving
    FROM Token WHERE status = 'Preparing';

    SET v_wait = (v_token_no - v_min_serving) * 3;

    IF v_wait < 0 THEN
        SET v_wait = 0;
    END IF;

    RETURN v_wait;
END //
DELIMITER ;
```

*Usage:*
```sql
SELECT get_wait_time(5) AS estimated_minutes;
```

**Function: Get order total for a given order:**
```sql
DELIMITER //
CREATE FUNCTION get_order_total(p_order_id INT)
RETURNS DECIMAL(10,2) DETERMINISTIC
BEGIN
    DECLARE v_total DECIMAL(10,2);
    SELECT SUM(subtotal) INTO v_total
    FROM Order_Items WHERE order_id = p_order_id;
    RETURN IFNULL(v_total, 0.00);
END //
DELIMITER ;
```

*Usage:*
```sql
SELECT get_order_total(3) AS calculated_total;
```

---

### ⚡ Triggers

**Trigger: Auto-generate token when a new order is inserted:**
```sql
DELIMITER //
CREATE TRIGGER after_order_insert
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    DECLARE v_next_token INT;
    SELECT IFNULL(MAX(token_no), 0) + 1 INTO v_next_token FROM Token;
    INSERT INTO Token (order_id, token_no, status)
    VALUES (NEW.order_id, v_next_token, 'Preparing');
END //
DELIMITER ;
```

**Trigger: Prevent deletion of a Completed order:**
```sql
DELIMITER //
CREATE TRIGGER before_order_delete
BEFORE DELETE ON Orders
FOR EACH ROW
BEGIN
    IF OLD.status = 'Completed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete a Completed order.';
    END IF;
END //
DELIMITER ;
```

**Trigger: Update token status when order is marked Completed:**
```sql
DELIMITER //
CREATE TRIGGER after_order_status_update
AFTER UPDATE ON Orders
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
        UPDATE Token SET status = 'Ready'
        WHERE order_id = NEW.order_id;
    END IF;
END //
DELIMITER ;
```

---

### 🔄 Cursors

**Cursor: Print each pending order's details:**
```sql
DELIMITER //
CREATE PROCEDURE list_pending_orders()
BEGIN
    DECLARE v_done INT DEFAULT 0;
    DECLARE v_order_id INT;
    DECLARE v_amount FLOAT;

    DECLARE cur CURSOR FOR
        SELECT order_id, total_amount FROM Orders WHERE status = 'Pending';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_order_id, v_amount;
        IF v_done THEN LEAVE read_loop; END IF;
        SELECT CONCAT('Order #', v_order_id, ' — ₹', v_amount) AS order_info;
    END LOOP;
    CLOSE cur;
END //
DELIMITER ;
```

*Usage:*
```sql
CALL list_pending_orders();
```

**Cursor: Apply 10% discount to all items above ₹200:**
```sql
DELIMITER //
CREATE PROCEDURE apply_bulk_discount()
BEGIN
    DECLARE v_done INT DEFAULT 0;
    DECLARE v_item_id INT;
    DECLARE v_price FLOAT;

    DECLARE cur CURSOR FOR
        SELECT item_id, price FROM Item WHERE price > 200;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN cur;
    discount_loop: LOOP
        FETCH cur INTO v_item_id, v_price;
        IF v_done THEN LEAVE discount_loop; END IF;
        UPDATE Item SET price = ROUND(v_price * 0.90, 2)
        WHERE item_id = v_item_id;
    END LOOP;
    CLOSE cur;
END //
DELIMITER ;
```

*Usage:*
```sql
CALL apply_bulk_discount();
```

---

### 🚨 Exception Handling

**Procedure with exception handling: Place order safely:**
```sql
DELIMITER //
CREATE PROCEDURE place_order_safe(
    IN p_user_id INT,
    IN p_item_id INT,
    IN p_quantity INT,
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_price FLOAT;
    DECLARE v_order_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'ERROR: Order failed due to a database error.';
    END;

    START TRANSACTION;

    -- Validate item exists
    SELECT price INTO v_price FROM Item WHERE item_id = p_item_id;
    IF v_price IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Item not found.';
    END IF;

    -- Insert Order
    INSERT INTO Orders (user_id, total_amount, status)
    VALUES (p_user_id, v_price * p_quantity, 'Pending');

    SET v_order_id = LAST_INSERT_ID();

    -- Insert Order Item
    INSERT INTO Order_Items (order_id, item_id, quantity, subtotal)
    VALUES (v_order_id, p_item_id, p_quantity, v_price * p_quantity);

    COMMIT;
    SET p_result = CONCAT('SUCCESS: Order #', v_order_id, ' placed.');
END //
DELIMITER ;
```

*Usage:*
```sql
CALL place_order_safe(1, 2, 3, @result);
SELECT @result;
```

**Procedure: Cancel order with rollback on failure:**
```sql
DELIMITER //
CREATE PROCEDURE cancel_order(IN p_order_id INT, OUT p_msg VARCHAR(200))
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_msg = 'ERROR: Could not cancel the order.';
    END;

    START TRANSACTION;

    SELECT status INTO v_status FROM Orders WHERE order_id = p_order_id;

    IF v_status = 'Completed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot cancel a completed order.';
    END IF;

    DELETE FROM Order_Items WHERE order_id = p_order_id;
    DELETE FROM Token WHERE order_id = p_order_id;
    DELETE FROM Orders WHERE order_id = p_order_id;

    COMMIT;
    SET p_msg = CONCAT('Order #', p_order_id, ' cancelled successfully.');
END //
DELIMITER ;
```

*Usage:*
```sql
CALL cancel_order(7, @msg);
SELECT @msg;
```
