# SQL Profile Queries Guide

This README explains the SQL concepts covered in `profile.sql` using simple, practical examples. The file focuses on:

- CASE expressions
- Subqueries
- CTEs (Common Table Expressions)
- Window functions
- Query writing patterns used in analytics and reporting

---

## 1. Source table: profiles

The file starts with this table:

```sql
CREATE TABLE profiles (
    profile_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    age INT NOT NULL CHECK (age > 0),
    account_status VARCHAR(20) NOT NULL,
    score INT NOT NULL CHECK (score BETWEEN 0 AND 100)
);
```

Sample records:

```sql
INSERT INTO profiles (
    full_name,
    city,
    age,
    account_status,
    score
)
VALUES
    ('Anuj Biswas', 'Delhi', 22, 'active', 92),
    ('Akash Yas', 'Mumbai', 34, 'inactive', 68),
    ('Rohan Gupta', 'Bangalore', 17, 'active', 81),
    ('Simran Kaur', 'Pune', 45, 'pending', 55),
    ('Meera Shah', 'Kolkata', 29, 'active', 39);
```

This dataset is used for many examples below.

---

## 2. CASE expressions

CASE is used to create custom labels or logic inside a query. It is very useful for reporting.

### 2.1 Simple CASE

This compares one expression to a fixed set of values.

```sql
SELECT
    profile_id,
    full_name,
    account_status,
    CASE account_status
        WHEN 'active' THEN 'Account is active'
        WHEN 'inactive' THEN 'Account is inactive'
        WHEN 'pending' THEN 'Account is waiting for review'
        ELSE 'Unknown account status'
    END AS status_message
FROM profiles;
```

### Example output

| full_name | account_status | status_message |
| --- | --- | --- |
| Anuj Biswas | active | Account is active |
| Akash Yas | inactive | Account is inactive |
| Simran Kaur | pending | Account is waiting for review |

### When to use it

- Convert raw values into readable labels.
- Show user states in dashboards.
- Build business logic directly in SQL.

---

### 2.2 Searched CASE

This checks conditions instead of comparing one value.

```sql
SELECT
    profile_id,
    full_name,
    age,
    CASE
        WHEN age < 18 THEN 'Minor'
        WHEN age BETWEEN 18 AND 30 THEN 'Young adult'
        WHEN age BETWEEN 31 AND 60 THEN 'Adult'
        ELSE 'Senior'
    END AS age_group
FROM profiles;
```

### Example

- age 17 -> Minor
- age 22 -> Young adult
- age 34 -> Adult

This is useful when categories depend on ranges rather than exact matches.

---

### 2.3 Using CASE with score ranges

```sql
SELECT
    profile_id,
    full_name,
    score,
    CASE
        WHEN score >= 80 THEN 'Excellent'
        WHEN score >= 60 THEN 'Good'
        WHEN score >= 40 THEN 'Needs improvement'
        ELSE 'Poor'
    END AS performance
FROM profiles;
```

### Example

- score 92 -> Excellent
- score 68 -> Good
- score 39 -> Poor

This is a standard way to create grade bands in SQL.

---

### 2.4 CASE in ORDER BY

```sql
SELECT
    full_name,
    account_status,
    score
FROM profiles
ORDER BY
    CASE
        WHEN account_status = 'active' THEN 1
        WHEN account_status = 'pending' THEN 2
        ELSE 3
    END,
    full_name;
```

This orders active profiles first, then pending, and then everything else.

---

## 3. Subqueries

A subquery is a query inside another query. It is used when you need a value, row set, or condition based on another query.

### 3.1 Scalar subquery

A scalar subquery returns one single value.

```sql
SELECT
    full_name,
    score
FROM profiles
WHERE score > (
    SELECT AVG(score)
    FROM profiles
)
ORDER BY score DESC;
```

### What it does

- Inner query: `SELECT AVG(score) FROM profiles`
- Finds the overall average score.
- Outer query selects profiles above that average.

This is a common pattern in dashboards and reports.

---

### 3.2 Subquery in SELECT list

```sql
SELECT
    full_name,
    score,
    (SELECT ROUND(AVG(score), 2) FROM profiles) AS overall_average,
    ROUND(score - (SELECT AVG(score) FROM profiles), 2) AS difference_from_average
FROM profiles;
```

This adds the overall average as a column in each row.

Example:

```text
full_name = Anuj Biswas
score = 92
overall_average = 67.00
difference_from_average = 25.00
```

---

### 3.3 Subquery with IN

```sql
SELECT
    full_name,
    account_status,
    score
FROM profiles
WHERE account_status IN (
    SELECT account_status
    FROM profiles
    WHERE score >= 80
);
```

This selects profiles whose status appears in the list of statuses from high-score users.

---

### 3.4 Subquery with ANY

```sql
SELECT
    full_name,
    score
FROM profiles
WHERE score > ANY (
    SELECT score
    FROM profiles
    WHERE age >= 18
)
ORDER BY score DESC;
```

`ANY` means: compare with at least one value returned by the subquery.

Example logic:

- If any adult has a score of 60 or less, then a profile with score 65 qualifies.

---

### 3.5 Subquery with ALL

```sql
SELECT
    full_name,
    score
FROM profiles
WHERE score > ALL (
    SELECT score
    FROM profiles
    WHERE age < 18
)
ORDER BY score DESC;
```

`ALL` means the comparison must be true for every value in the subquery result.

This is useful when you want values greater than the maximum of a group.

---

### 3.6 Correlated subquery

A correlated subquery uses values from the outer query inside the inner query.

```sql
SELECT
    p.full_name,
    p.account_status,
    p.score
FROM profiles AS p
WHERE p.score > (
    SELECT AVG(p2.score)
    FROM profiles AS p2
    WHERE p2.account_status = p.account_status
)
ORDER BY p.score DESC;
```

### Explanation

For each profile row, the query compares the profile's score with the average score of people in the same account status group.

This is helpful for status-wise performance comparisons.

---

### 3.7 EXISTS and NOT EXISTS

#### EXISTS

```sql
SELECT
    p.full_name,
    p.account_status,
    p.score
FROM profiles AS p
WHERE EXISTS (
    SELECT 1
    FROM profiles AS other
    WHERE other.account_status = p.account_status
      AND other.score > p.score
)
ORDER BY p.score DESC;
```

This returns profiles that have someone else in the same status group with a higher score.

#### NOT EXISTS

```sql
SELECT
    p.full_name,
    p.account_status,
    p.score
FROM profiles AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM profiles AS other
    WHERE other.account_status = p.account_status
      AND other.score > p.score
)
ORDER BY p.account_status, p.score DESC;
```

This returns the highest-scoring profile in each status group.

`EXISTS` is very useful for checking whether related data exists before acting on it.

---

### 3.8 Subquery in FROM (derived table)

```sql
SELECT
    status_summary.account_status,
    status_summary.average_score
FROM (
    SELECT
        account_status,
        ROUND(AVG(score), 2) AS average_score
    FROM profiles
    GROUP BY account_status
) AS status_summary
WHERE status_summary.average_score >= 60
ORDER BY status_summary.average_score DESC;
```

This creates a temporary result set called `status_summary`, then filters it in the outer query.

This pattern is helpful when you want to calculate first, then apply filters to the summary.

---

## 4. CTEs (Common Table Expressions)

A CTE is a named temporary result set that exists only for one SQL statement. It makes SQL easier to read and maintain.

### 4.1 Basic CTE

```sql
WITH high_score_profiles AS (
    SELECT
        profile_id,
        full_name,
        score
    FROM profiles
    WHERE score >= 80
)
SELECT *
FROM high_score_profiles
ORDER BY score DESC;
```

This creates a temporary dataset called `high_score_profiles`, then reads from it.

---

### 4.2 CTE with aggregation

```sql
WITH status_summary AS (
    SELECT
        account_status,
        COUNT(*) AS profile_count,
        ROUND(AVG(score), 2) AS average_score
    FROM profiles
    GROUP BY account_status
)
SELECT
    account_status,
    profile_count,
    average_score
FROM status_summary
WHERE average_score >= 60
ORDER BY average_score DESC;
```

This is useful when you want:

- group data first,
- calculate summary metrics,
- then filter the summarized result.

---

### 4.3 Multiple CTEs

```sql
WITH scored_profiles AS (
    SELECT
        profile_id,
        full_name,
        account_status,
        score,
        CASE
            WHEN score >= 80 THEN 'Excellent'
            WHEN score >= 60 THEN 'Good'
            WHEN score >= 40 THEN 'Needs improvement'
            ELSE 'Poor'
        END AS performance
    FROM profiles
),
excellent_profiles AS (
    SELECT *
    FROM scored_profiles
    WHERE performance = 'Excellent'
)
SELECT
    full_name,
    score,
    performance
FROM excellent_profiles
ORDER BY score DESC;
```

This breaks the problem into smaller steps:

1. classify performance,
2. keep only excellent ones,
3. show final results.

This is easier to reason about than one big query.

---

### 4.4 Recursive CTE

A recursive CTE keeps referring to itself until a stop condition is reached.

```sql
WITH RECURSIVE numbers AS (
    SELECT 1 AS number
    UNION ALL
    SELECT number + 1
    FROM numbers
    WHERE number < 5
)
SELECT number
FROM numbers
ORDER BY number;
```

### Output

```text
1
2
3
4
5
```

This is a common technique for generating date ranges, sequence numbers, or hierarchical data.

---

## 5. Window functions

A window function calculates values across a set of related rows while keeping each original row in the output.

Unlike `GROUP BY`, it does not collapse rows together.

### 5.1 ROW_NUMBER

```sql
SELECT
    full_name,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS score_position
FROM profiles
ORDER BY score_position;
```

This gives each row a unique position based on score ranking.

---

### 5.2 RANK and DENSE_RANK

```sql
SELECT
    full_name,
    score,
    RANK() OVER (ORDER BY score DESC) AS score_rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_score_rank
FROM profiles
ORDER BY score DESC;
```

### Difference

- `RANK()` leaves gaps after ties.
- `DENSE_RANK()` keeps rankings compact without gaps.

This matters when multiple rows share the same value.

---

### 5.3 NTILE

```sql
SELECT
    full_name,
    score,
    NTILE(4) OVER (ORDER BY score DESC) AS score_quartile
FROM profiles
ORDER BY score DESC;
```

This divides the rows into 4 equal-ish buckets.

This is useful for segmentation, such as:

- top 25%
- next 25%
- middle 25%
- last 25%

---

### 5.4 PARTITION BY

```sql
SELECT
    full_name,
    account_status,
    score,
    ROW_NUMBER() OVER (
        PARTITION BY account_status
        ORDER BY score DESC
    ) AS status_position
FROM profiles
ORDER BY account_status, status_position;
```

This restarts numbering inside each account status group.

Example:

- active profiles have their own ranking
- pending profiles have their own ranking
- inactive profiles have their own ranking

---

### 5.5 Windowed aggregate

```sql
SELECT
    full_name,
    account_status,
    score,
    ROUND(
        AVG(score) OVER (PARTITION BY account_status),
        2
    ) AS status_average
FROM profiles
ORDER BY account_status, score DESC;
```

This shows each row together with the average score of its status group.

---

### 5.6 Difference from status average

```sql
SELECT
    full_name,
    account_status,
    score,
    ROUND(
        score - AVG(score) OVER (PARTITION BY account_status),
        2
    ) AS difference_from_status_average
FROM profiles
ORDER BY account_status, score DESC;
```

This tells you whether a profile is above or below the average within their status group.

---

### 5.7 Running total and running average

```sql
SELECT
    full_name,
    score,
    SUM(score) OVER (
        ORDER BY score DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    ROUND(
        AVG(score) OVER (
            ORDER BY score DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS running_average
FROM profiles
ORDER BY score DESC;
```

This calculates cumulative totals and cumulative averages as you go through the table in score order.

---

### 5.8 LAG and LEAD

```sql
SELECT
    full_name,
    score,
    LAG(score) OVER (ORDER BY score DESC) AS previous_score,
    LEAD(score) OVER (ORDER BY score DESC) AS next_score
FROM profiles
ORDER BY score DESC;
```

### Meaning

- `LAG(score)` = previous row value
- `LEAD(score)` = next row value

This helps compare a row with the values before and after it.

Example:

- If current score is 92, previous score may be 81
- next score may be 68

---

### 5.9 Highest score in each status group

```sql
WITH ranked_profiles AS (
    SELECT
        full_name,
        account_status,
        score,
        ROW_NUMBER() OVER (
            PARTITION BY account_status
            ORDER BY score DESC
        ) AS status_position
    FROM profiles
)
SELECT
    full_name,
    account_status,
    score
FROM ranked_profiles
WHERE status_position = 1
ORDER BY account_status;
```

This returns the top profile in each status category.

---

## 6. Common patterns in the file

### Pattern 1: Convert raw values into readable categories

```sql
CASE
    WHEN score >= 80 THEN 'Excellent'
    WHEN score >= 60 THEN 'Good'
    WHEN score >= 40 THEN 'Needs improvement'
    ELSE 'Poor'
END
```

### Pattern 2: Compare against a summary value

```sql
WHERE score > (SELECT AVG(score) FROM profiles)
```

### Pattern 3: Build a temporary result first

```sql
WITH status_summary AS (
    SELECT account_status, AVG(score) AS avg_score
    FROM profiles
    GROUP BY account_status
)
SELECT *
FROM status_summary;
```

### Pattern 4: Rank rows inside groups

```sql
ROW_NUMBER() OVER (PARTITION BY account_status ORDER BY score DESC)
```

---

## 7. Why these concepts matter

These SQL patterns are used in real dashboards and applications for:

- classifying records
- comparing a row to averages or groups
- finding top performers
- showing trends across ordered data
- creating reusable summary logic
- generating clean reporting outputs

---

## 8. Example business use cases

### Example 1: employee performance report

```sql
SELECT
    full_name,
    CASE
        WHEN score >= 80 THEN 'Excellent'
        WHEN score >= 60 THEN 'Good'
        ELSE 'Needs attention'
    END AS performance_label
FROM profiles;
```

### Example 2: find users above their group average

```sql
SELECT
    p.full_name,
    p.account_status,
    p.score
FROM profiles p
WHERE p.score > (
    SELECT AVG(p2.score)
    FROM profiles p2
    WHERE p2.account_status = p.account_status
);
```

### Example 3: show latest/top profile in each category

```sql
WITH ranked AS (
    SELECT
        full_name,
        account_status,
        score,
        ROW_NUMBER() OVER (
            PARTITION BY account_status
            ORDER BY score DESC
        ) AS rn
    FROM profiles
)
SELECT *
FROM ranked
WHERE rn = 1;
```

---

## 9. Final summary

The `profile.sql` file teaches a set of advanced but important SQL techniques:

- `CASE` helps create report-friendly categories.
- Subqueries help compare with averages and group values.
- CTEs make complex SQL easier to read.
- Window functions are used for ranking, running totals, and comparisons across rows.

These are not just academic concepts—they are used heavily in real analytics, reporting, and business intelligence work.

---

## 10. Quick revision cheat sheet

```text
CASE               => create custom logic
WHEN / THEN        => branch conditions
SELECT AVG(...)    => scalar subquery
IN / ANY / ALL     => compare with a set of values
EXISTS             => check whether related data exists
CTE                => temporary named result set
WITH RECURSIVE     => generate sequences or hierarchy
ROW_NUMBER()       => unique ranking
RANK()             => ranking with gaps
DENSE_RANK()       => ranking without gaps
NTILE()            => bucket rows into groups
LAG() / LEAD()     => previous and next row values
OVER (PARTITION BY ...) => group calculations per category
```

This file is a strong beginner-to-intermediate SQL practice set for analytics and reporting queries.
