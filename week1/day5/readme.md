# PostgreSQL: Tables, Queries, and Aggregate Functions

This guide introduces basic PostgreSQL table creation, sample data, filtering, sorting, and aggregate queries. The examples use a small college database with five related tables.

## 1. Create tables and insert sample data

`CREATE TABLE` defines a table's columns and their data types. A primary key uniquely identifies each row. A foreign key connects a row to a row in another table.

Run the following statements in order. The foreign-key relationships require the referenced tables to exist first.

```sql
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE instructors (
    instructor_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(department_id)
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(department_id),
    instructor_id INT NOT NULL REFERENCES instructors(instructor_id),
    fee NUMERIC(8, 2) NOT NULL CHECK (fee >= 0)
);

CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(student_id),
    course_id INT NOT NULL REFERENCES courses(course_id),
    enrolled_on DATE NOT NULL,
    score NUMERIC(5, 2) CHECK (score >= 0 AND score <= 100)
);
```

`INSERT INTO` adds rows. List the columns explicitly to make it clear which value goes into each column.

```sql
INSERT INTO departments (department_id, department_name) VALUES
    (1, 'Computer Science'),
    (2, 'Mathematics'),
    (3, 'Business');

INSERT INTO instructors (instructor_id, full_name, department_id) VALUES
    (1, 'Asha Rao', 1),
    (2, 'Daniel Kim', 2),
    (3, 'Maya Patel', 3);

INSERT INTO students (student_id, full_name, city) VALUES
    (1, 'Aarav Shah', 'Mumbai'),
    (2, 'Meera Joshi', 'Pune'),
    (3, 'Kabir Singh', 'Mumbai'),
    (4, 'Nina Das', 'Delhi'),
    (5, 'Rohan Verma', 'Pune');

INSERT INTO courses (course_id, course_name, department_id, instructor_id, fee) VALUES
    (1, 'SQL Fundamentals', 1, 1, 120.00),
    (2, 'Python Programming', 1, 1, 150.00),
    (3, 'Calculus I', 2, 2, 100.00),
    (4, 'Business Analytics', 3, 3, 180.00),
    (5, 'Data Structures', 1, 1, 160.00);

INSERT INTO enrollments (enrollment_id, student_id, course_id, enrolled_on, score) VALUES
    (1, 1, 1, '2026-01-10', 88.00),
    (2, 1, 2, '2026-01-12', 92.00),
    (3, 2, 1, '2026-01-11', 76.00),
    (4, 2, 3, '2026-01-15', 84.00),
    (5, 3, 2, '2026-01-14', 81.00),
    (6, 3, 5, '2026-01-18', 95.00),
    (7, 4, 4, '2026-01-20', 89.00),
    (8, 5, 1, '2026-01-21', 91.00),
    (9, 5, 4, '2026-01-22', 73.00);
```

The five tables are `departments`, `instructors`, `students`, `courses`, and `enrollments`. For example, each enrollment points to a student and a course through its foreign keys.

## 2. `SELECT`, `WHERE`, `ORDER BY`, and `LIMIT`

`SELECT` chooses the columns to display. `WHERE` filters rows, `ORDER BY` sorts the results, and `LIMIT` restricts how many rows are returned.

```sql
SELECT full_name, city
FROM students
WHERE city = 'Pune'
ORDER BY full_name ASC
LIMIT 5;
```

This query finds students from Pune, sorts their names alphabetically, and returns at most five rows. Use `DESC` instead of `ASC` to sort in descending order.

You can filter using comparisons and combine conditions:

```sql
SELECT course_name, fee
FROM courses
WHERE fee >= 120 AND fee < 170
ORDER BY fee DESC;
```

## 3. `DISTINCT`

`DISTINCT` removes duplicate values from the query result.

```sql
SELECT DISTINCT city
FROM students
ORDER BY city;
```

Although multiple students may live in the same city, each city appears only once in this result.

## 4. Aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`

Aggregate functions calculate a value from a set of rows:

- `COUNT` counts rows or non-`NULL` values.
- `SUM` adds numeric values.
- `AVG` calculates the average of numeric values.
- `MIN` returns the smallest value.
- `MAX` returns the largest value.

```sql
SELECT
    COUNT(*) AS enrollment_count,
    SUM(score) AS total_score,
    AVG(score) AS average_score,
    MIN(score) AS lowest_score,
    MAX(score) AS highest_score
FROM enrollments;
```

`COUNT(*)` counts every row. By contrast, `COUNT(score)` counts only rows where `score` is not `NULL`.

## 5. `GROUP BY`

`GROUP BY` divides rows into groups that share the same value. Aggregate functions can then calculate a result for each group.

```sql
SELECT course_id, COUNT(*) AS number_of_students
FROM enrollments
GROUP BY course_id
ORDER BY course_id;
```

This returns one row per course with its number of enrollments. To display course names instead of IDs, join the course table:

```sql
SELECT c.course_name, COUNT(*) AS number_of_students
FROM enrollments AS e
JOIN courses AS c ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name
ORDER BY number_of_students DESC;
```

## 6. `HAVING` vs. `WHERE`

`WHERE` filters individual rows **before** grouping. `HAVING` filters the groups **after** `GROUP BY` and is commonly used with aggregate results.

This query first keeps enrollments with a score of at least 80, then returns courses with at least two such enrollments:

```sql
SELECT course_id, COUNT(*) AS high_score_enrollments
FROM enrollments
WHERE score >= 80
GROUP BY course_id
HAVING COUNT(*) >= 2
ORDER BY course_id;
```

In short, use `WHERE` to filter source rows and `HAVING` to filter aggregated groups.

## Practice

**Write 10 queries on the 5-table schema.**

Write a query for each task:

1. List all students who live in Mumbai.
2. List courses with a fee greater than 120, from the highest fee to the lowest.
3. Show the three least expensive courses.
4. List each distinct student city.
5. Count the students in the `students` table.
6. Show the average course fee.
7. For each course, show its name and number of enrollments.
8. For each student, show their name and number of enrolled courses.
9. Show courses with an average enrollment score of at least 85.
10. Show each department name and the total fees of its courses, but include only departments whose total is greater than 200.
