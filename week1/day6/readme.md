# SQL Analytics Queries Guide

This README explains the SQL concepts covered in `analytics_queries.sql` with simple examples and practical use cases. The file demonstrates table creation, joins, aggregate queries, many-to-many relationships, views, and stored procedures.

---

## 1. Creating Tables and Inserting Data

The first part of the file creates tables like `students` and `marks`.

```sql
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INT,
    subject VARCHAR(50),
    marks INT,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);
```

### Why this is useful

- `students` stores student information.
- `marks` stores marks for different subjects for each student.
- `student_id` connects the two tables.

Example insert:

```sql
INSERT INTO students (name)
VALUES ('Anuj Biswas'), ('Akash Yas'), ('Rohan Gupta');

INSERT INTO marks (student_id, subject, marks)
VALUES
    (1, 'English', 85),
    (1, 'Math', 89),
    (1, 'Science', 92),
    (2, 'English', 80),
    (2, 'Math', 89),
    (2, 'Science', 78);
```

This creates a structure where each student can have multiple entries in the `marks` table.

---

## 2. Basic Data Retrieval

To read data from a table:

```sql
SELECT * FROM students;
SELECT * FROM marks;
```

The `SELECT` statement is the most basic SQL operation. It is used to fetch rows and columns from a table.

Example:

```sql
SELECT student_id, name
FROM students;
```

This returns all student IDs and names.

---

## 3. One-to-Many Relationship: Students and Marks

The `students` table and `marks` table have a one-to-many relationship:

- One student can have many marks rows.
- Each marks row belongs to one student.

### Example query

```sql
SELECT s.name, m.subject, m.marks
FROM students s
JOIN marks m ON s.student_id = m.student_id;
```

### What it does

This combines data from both tables using the common column `student_id` and shows each student with his/her subject marks.

Example result:

| name | subject | marks |
| --- | --- | --- |
| Anuj Biswas | English | 85 |
| Anuj Biswas | Math | 89 |
| Akash Yas | English | 80 |

This is a classic example of a join.

---

## 4. Types of Joins

The SQL file explains the main join types.

### 4.1 INNER JOIN

An `INNER JOIN` returns only matching rows from both tables.

```sql
SELECT *
FROM students s
JOIN marks m ON s.student_id = m.student_id;
```

This returns only the students who have marks available.

### 4.2 LEFT JOIN

A `LEFT JOIN` returns all rows from the left table, even if there is no match in the right table.

```sql
SELECT s.name, m.subject, m.marks
FROM students s
LEFT JOIN marks m ON s.student_id = m.student_id;
```

This is useful when you want to see all students, even if some of them have no marks yet.

### 4.3 RIGHT JOIN

A `RIGHT JOIN` returns all rows from the right table, even if there is no match in the left table.

```sql
SELECT s.name, m.subject, m.marks
FROM students s
RIGHT JOIN marks m ON s.student_id = m.student_id;
```

This is helpful when you want to focus on the right-side table entries.

### 4.4 CROSS JOIN

A `CROSS JOIN` returns every possible combination of rows from both tables.

```sql
SELECT s.name, m.subject, m.marks
FROM students s
CROSS JOIN marks m;
```

This is rarely used for business reporting but is useful for generating combinations.

---

## 5. Student and Profile Example

The file also creates a `student_profiles` table.

```sql
CREATE TABLE student_profiles (
    student_id INT PRIMARY KEY,
    address TEXT,
    age INT,
    phone VARCHAR(15)
);
```

Then it inserts profile data:

```sql
INSERT INTO student_profiles (student_id, address, age, phone)
VALUES
    (1, 'Delhi, India', 22, '9757645678'),
    (2, 'Mumbai, India', 34, '738293847'),
    (3, 'Banglaore, India', 23, '819293322');
```

Now we join the students with their profiles:

```sql
SELECT
    s.student_id,
    s.name,
    sp.address,
    sp.age,
    sp.phone
FROM students s
JOIN student_profiles sp
    ON s.student_id = sp.student_id;
```

### Why this matters

This is a one-to-one relationship:

- One student has one profile.
- One profile belongs to one student.

This pattern is common for user profile data, employee details, or customer metadata.

---

## 6. Practice Questions on Students and Marks

The script includes examples like:

```sql
SELECT s.name, m.subject, m.marks
FROM students s
JOIN marks m ON s.student_id = m.student_id
WHERE s.name = 'Akash Yas';
```

This query gives the marks of only one student.

### Example interpretation

If the student is `Akash Yas`, the result will show all subject marks for that student only.

---

## 7. Products and Orders Analytics

The next part of the file creates a product and order system.

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category TEXT,
    price NUMERIC(10,2),
    stock_quantity INT,
    is_available BOOLEAN,
    added_on DATE
);
```

```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    product_id INT,
    order_date DATE,
    customer_name VARCHAR(50),
    payment_method VARCHAR(50),
    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);
```

### Relationship

- One product can appear in many orders.
- One order refers to one product.

This is a one-to-many relationship.

---

## 8. Product and Order Query Examples

### 8.1 Show each order with product name and price

```sql
SELECT o.order_id, o.customer_name, p.product_name, p.price
FROM orders o
INNER JOIN products p
    ON o.product_id = p.product_id;
```

This helps answer: which product was ordered by which customer and at what price?

### 8.2 Show all products even if they were never ordered

```sql
SELECT o.order_id, p.product_name
FROM products p
LEFT JOIN orders o
    ON o.product_id = p.product_id;
```

This keeps all products in the result, even when there are no matching orders.

### 8.3 Show only electronics orders

```sql
SELECT o.order_id, p.product_name, p.category
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE p.category = 'Electronics';
```

This filters only electronics-related records.

### 8.4 Sort orders by product price (highest first)

```sql
SELECT o.order_id, p.product_name, p.price
FROM orders o
JOIN products p ON o.product_id = p.product_id
ORDER BY p.price DESC;
```

This helps ranking products from most expensive to cheapest sold.

### 8.5 Count how many times each product was ordered

```sql
SELECT p.product_name, COUNT(o.order_id) AS total_orders
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_name;
```

### What it does

- `COUNT(o.order_id)` counts the number of orders per product.
- `LEFT JOIN` ensures products with zero orders are still included.
- `GROUP BY p.product_name` groups the result by product.

### 8.6 Calculate total revenue per product

```sql
SELECT p.product_name, SUM(o.quantity * p.price) AS revenue
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_name;
```

This is a common business query. It calculates total revenue by product.

> Note: The SQL script has a small issue here because the `orders` table in the file does not include a `quantity` column. In a real database, you would usually have a `quantity` field in the `orders` table to calculate total revenue properly.

### 8.7 Show products with revenue above a threshold

```sql
SELECT p.product_name, SUM(o.quantity * p.price) AS revenue
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_name
HAVING SUM(o.quantity * p.price) > 2000;
```

`HAVING` is used after `GROUP BY` to filter grouped results.

### 8.8 Find customers who ordered fitness items

```sql
SELECT DISTINCT o.customer_name
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE p.category = 'Fitness';
```

`DISTINCT` removes duplicate customer names.

---

## 9. Many-to-Many Relationship: Students and Courses

This part of the file shows a many-to-many relationship.

### Example setup

```sql
CREATE TABLE student (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);
```

Then the junction table:

```sql
CREATE TABLE student_courses (
    student_id INT,
    course_id INT,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

### Why use a junction table?

Because many students can take many courses. A direct table with only student and course columns is not enough. The junction table stores each pairing.

Example data:

```sql
INSERT INTO student_courses (student_id, course_id)
VALUES
    (1, 102),
    (2, 101),
    (2, 103),
    (3, 102);
```

### Query to see each student with their courses

```sql
SELECT s.student_name, c.course_name
FROM student_courses sc
JOIN student s ON sc.student_id = s.student_id
JOIN courses c ON sc.course_id = c.course_id;
```

This returns a list of students and the courses they are enrolled in.

### Query to find courses for a specific student

```sql
SELECT c.course_name
FROM student_courses sc
JOIN student s ON sc.student_id = s.student_id
JOIN courses c ON sc.course_id = c.course_id
WHERE s.student_name = 'ANUJ';
```

This is useful when you want to fetch all subjects or courses a student is registered in.

---

## 10. Views

A view is a saved SQL query that behaves like a table.

Example from the file:

```sql
CREATE VIEW student_course_view AS
SELECT
    s.student_name,
    c.course_name
FROM student_courses sc
JOIN student s
    ON sc.student_id = s.student_id
JOIN courses c
    ON sc.course_id = c.course_id;
```

Then query it like this:

```sql
SELECT * FROM student_course_view;
```

### Why views are useful

- Save frequently used complex queries.
- Reuse joins without rewriting the SQL each time.
- Simplify reporting and data access.

Example use case:

- A teacher may want to see all student-course mappings without repeatedly writing the same join logic.

---

## 11. Stored Procedures

A stored procedure is a reusable SQL block that can perform one or more database tasks.

Example from the file:

```sql
CREATE PROCEDURE add_student(
    p_id INT,
    p_name VARCHAR(100)
)
LANGUAGE SQL
AS $$
    INSERT INTO students (student_id, student_name)
    VALUES (p_id, p_name);
$$;
```

Then call it like this:

```sql
CALL add_student(10, 'Anuj');
```

### Why stored procedures are useful

- Reuse common database operations.
- Keep business logic close to the database.
- Reduce duplicated SQL code.

Example: adding a new customer, inserting a new order, or updating product stock can all be done through procedures.

---

## 12. Quick Summary

### Main concepts in this file

- `CREATE TABLE` — creates a table
- `INSERT INTO` — adds data
- `SELECT` — reads data
- `JOIN` — combines rows from related tables
- `LEFT JOIN` — includes all left-side rows
- `RIGHT JOIN` — includes all right-side rows
- `CROSS JOIN` — combines every row pair
- `GROUP BY` — groups data for aggregation
- `COUNT()`, `SUM()`, `AVG()` — aggregate functions
- `HAVING` — filters grouped results
- `VIEW` — saves a query as a reusable virtual table
- `PROCEDURE` — saves reusable database logic

---

## 13. Real-World Example

Suppose a store wants to answer:

- Which products are selling most?
- Which customer bought which products?
- Which items have zero orders?
- What is total monthly revenue by category?

These questions are exactly what joins, groupings, and aggregate functions solve in SQL.

---

## 14. Final Tip

If you want to become strong in SQL, practice these patterns repeatedly:

1. Create tables
2. Insert sample data
3. Write a join query
4. Add filters using `WHERE`
5. Group data using `GROUP BY`
6. Calculate totals with aggregate functions
7. Save repeated logic using views and procedures

This file is a solid beginner-to-intermediate SQL practice set.
