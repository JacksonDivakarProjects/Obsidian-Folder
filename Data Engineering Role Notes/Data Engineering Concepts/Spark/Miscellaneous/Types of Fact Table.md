# Comprehensive Guide to Types of Fact Tables in Data Warehousing

## Introduction to Fact Tables

Fact tables are the central tables in a data warehouse schema. They hold the quantitative measurements, metrics, and facts of a business process, and are typically surrounded by dimension tables that provide descriptive context.

## 1. Fundamental Concepts

### What is a Fact Table?
- Stores quantitative business measurements
- Contains foreign keys to dimension tables
- Includes numerical facts/measures
- Represents a specific business process or event

### Basic Structure
```sql
-- Example fact table structure
CREATE TABLE sales_fact (
    date_key INT,           -- Foreign key to date dimension
    product_key INT,        -- Foreign key to product dimension
    customer_key INT,       -- Foreign key to customer dimension
    store_key INT,          -- Foreign key to store dimension
    sales_amount DECIMAL(10,2),  -- Fact/measure
    quantity_sold INT,           -- Fact/measure
    profit_amount DECIMAL(10,2)  -- Fact/measure
);
```

## 2. Classification of Fact Tables

### Based on Granularity
```
Fact Tables
├── Transaction Fact Tables
├── Periodic Snapshot Fact Tables
├── Accumulating Snapshot Fact Tables
└── Factless Fact Tables
```

## 3. Transaction Fact Tables

### Characteristics
- **One row per business transaction/event**
- Most detailed level of facts
- Captures individual business events as they occur
- Typically very large in size
- Time-stamped at the moment of transaction

### Example: Retail Sales Transaction
```sql
CREATE TABLE sales_transaction_fact (
    transaction_id BIGINT,      -- Unique transaction identifier
    transaction_date_key INT,   -- Date dimension key
    transaction_time TIME,      -- Exact time of transaction
    product_key INT,
    customer_key INT,
    store_key INT,
    sales_amount DECIMAL(10,2),
    quantity INT,
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2)
);

-- Example query: Daily sales summary
SELECT 
    d.full_date,
    SUM(stf.sales_amount) as daily_sales,
    COUNT(*) as transaction_count
FROM sales_transaction_fact stf
JOIN date_dimension d ON stf.transaction_date_key = d.date_key
GROUP BY d.full_date;
```

### Use Cases
- Point-of-sale systems
- Banking transactions
- E-commerce purchases
- Insurance claims processing
- Website clickstream events

## 4. Periodic Snapshot Fact Tables

### Characteristics
- **Captures state at regular intervals** (daily, weekly, monthly)
- One row per entity per time period
- Shows cumulative performance over time
- Less granular than transaction facts

### Example: Bank Account Balance Snapshot
```sql
CREATE TABLE account_balance_snapshot_fact (
    snapshot_date_key INT,      -- End of period date
    account_key INT,
    customer_key INT,
    branch_key INT,
    opening_balance DECIMAL(15,2),
    closing_balance DECIMAL(15,2),
    total_deposits DECIMAL(15,2),
    total_withdrawals DECIMAL(15,2),
    interest_earned DECIMAL(15,2)
);

-- Example query: Monthly balance trend
SELECT 
    d.year_month,
    absf.account_key,
    absf.closing_balance
FROM account_balance_snapshot_fact absf
JOIN date_dimension d ON absf.snapshot_date_key = d.date_key
WHERE d.year_month BETWEEN '2024-01' AND '2024-12'
ORDER BY d.year_month, absf.account_key;
```

### Use Cases
- Monthly bank account balances
- Inventory levels at month-end
- Monthly sales targets vs actuals
- Quarterly financial statements

## 5. Accumulating Snapshot Fact Tables

### Characteristics
- **Tracks process workflow with multiple milestones**
- Single row per process instance
- Dates for key milestones in the process
- Facts updated as process progresses

### Example: Order Fulfillment Process
```sql
CREATE TABLE order_fulfillment_fact (
    order_key INT,
    customer_key INT,
    product_key INT,
    order_date_key INT,          -- Order placed date
    ship_date_key INT,           -- Date shipped (updated when occurs)
    delivery_date_key INT,       -- Date delivered (updated when occurs)
    return_date_key INT,         -- Date returned (if applicable)
    order_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    quantity_ordered INT,
    quantity_shipped INT,
    quantity_delivered INT,
    quantity_returned INT,
    process_status VARCHAR(20)   -- In Progress, Completed, Returned
);

-- Example query: Average fulfillment time
SELECT 
    AVG(DATEDIFF(
        DATE(delivery.full_date), 
        DATE(order.full_date)
    )) as avg_fulfillment_days
FROM order_fulfillment_fact off
JOIN date_dimension order ON off.order_date_key = order.date_key
JOIN date_dimension delivery ON off.delivery_date_key = delivery.date_key
WHERE off.delivery_date_key IS NOT NULL;
```

### Use Cases
- Order processing pipelines
- Insurance claim processing
- Loan application workflows
- Manufacturing assembly lines
- Patient treatment journeys

## 6. Factless Fact Tables

### Characteristics
- **Contains no measurable facts/numbers**
- Records events or relationships only
- Used to track occurrences or coverage
- Contains only foreign keys to dimensions

### Example: Student Attendance Tracking
```sql
CREATE TABLE student_attendance_fact (
    date_key INT,
    student_key INT,
    class_key INT,
    instructor_key INT,
    attendance_status VARCHAR(10) -- Present, Absent, Late
);

-- Example: Event tracking (no measures)
CREATE TABLE event_registration_fact (
    event_key INT,
    customer_key INT,
    registration_date_key INT
);

-- Example query: Attendance rate calculation
SELECT 
    d.month_name,
    COUNT(*) as total_classes,
    SUM(CASE WHEN saf.attendance_status = 'Present' THEN 1 ELSE 0 END) as present_count,
    (SUM(CASE WHEN saf.attendance_status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as attendance_rate
FROM student_attendance_fact saf
JOIN date_dimension d ON saf.date_key = d.date_key
GROUP BY d.month_name;
```

### Use Cases
- Attendance tracking
- Event participation
- Product promotions coverage
- Student-course enrollment
- Insurance policy coverage periods

## 7. Comparative Analysis

### Comparison Table

| Feature | Transaction Fact | Periodic Snapshot | Accumulating Snapshot | Factless Fact |
|---------|------------------|-------------------|----------------------|---------------|
| **Granularity** | Individual events | Regular intervals | Process instances | Events/relationships |
| **Row Count** | Very high | Moderate | Low to moderate | Varies |
| **Update Frequency** | Insert-only | Periodic loads | Updates as process progresses | Insert-only |
| **Time Dimension** | Transaction timestamp | Period end date | Multiple milestone dates | Event date |
| **Typical Use** | Detailed analysis | Trend analysis | Process monitoring | Coverage analysis |

## 8. Advanced Fact Table Types

### Consolidated Fact Tables
- Combine facts from multiple business processes
- Reduce joins in queries
- Pre-aggregated for specific analytical needs

```sql
-- Example: Consolidated customer view
CREATE TABLE customer_360_fact (
    customer_key INT,
    date_key INT,
    total_purchases DECIMAL(15,2),
    purchase_count INT,
    support_tickets INT,
    website_visits INT,
    average_order_value DECIMAL(10,2)
);
```

### Degenerate Dimension Facts
- Include transaction identifiers as dimensions
- Useful for drill-through to source systems

```sql
-- Example: Including transaction ID
CREATE TABLE sales_transaction_detail (
    transaction_number VARCHAR(20),  -- Degenerate dimension
    date_key INT,
    product_key INT,
    sales_amount DECIMAL(10,2)
);
```

## 9. Design Considerations and Best Practices

### Grain Determination
```sql
-- Always define grain explicitly
-- Good: One row per sales transaction line item
-- Bad: Mixed levels of detail

-- Correct grain specification
COMMENT ON TABLE sales_fact IS 'Grain: One row per product per sales transaction';
```

### Fact Table Sizing Considerations
```sql
-- Estimate storage requirements
-- Transaction facts: Millions to billions of rows
-- Snapshot facts: Thousands to millions of rows
-- Consider partitioning strategies for large tables

-- Example partitioning
CREATE TABLE large_transaction_fact (
    -- columns
)
PARTITION BY RANGE (date_key);
```

### Handling NULL Values
```sql
-- Use surrogate keys for unknown dimensions
-- Avoid NULL foreign keys
-- Consider creating "Unknown" records in dimension tables

-- Example: Handling unknown customers
INSERT INTO customer_dim (customer_key, customer_id, customer_name)
VALUES (-1, 'UNKNOWN', 'Unknown Customer');
```

## 10. Implementation Examples

### Complete Retail Example
```sql
-- Transaction fact for point-of-sale
CREATE TABLE pos_transaction_fact (
    transaction_id BIGINT,
    transaction_date_key INT,
    transaction_time TIME,
    store_key INT,
    cashier_key INT,
    customer_key INT,
    product_key INT,
    sales_amount DECIMAL(10,2),
    cost_amount DECIMAL(10,2),
    quantity INT,
    promotion_key INT
);

-- Periodic snapshot for inventory
CREATE TABLE inventory_snapshot_fact (
    snapshot_date_key INT,  -- End of day
    product_key INT,
    store_key INT,
    opening_stock INT,
    closing_stock INT,
    stock_received INT,
    stock_sold INT,
    stock_adjustment INT
);

-- Accumulating snapshot for online orders
CREATE TABLE online_order_fact (
    order_id BIGINT,
    customer_key INT,
    order_date_key INT,
    payment_date_key INT,
    shipping_date_key INT,
    delivery_date_key INT,
    order_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    discount_amount DECIMAL(10,2)
);
```

### Healthcare Example
```sql
-- Transaction fact for patient visits
CREATE TABLE patient_visit_fact (
    visit_id BIGINT,
    patient_key INT,
    provider_key INT,
    facility_key INT,
    visit_date_key INT,
    diagnosis_key INT,
    procedure_key INT,
    charge_amount DECIMAL(10,2),
    payment_amount DECIMAL(10,2),
    visit_duration_minutes INT
);

-- Accumulating snapshot for treatment plans
CREATE TABLE treatment_plan_fact (
    plan_id BIGINT,
    patient_key INT,
    diagnosis_key INT,
    plan_start_date_key INT,
    first_treatment_date_key INT,
    last_treatment_date_key INT,
    plan_end_date_key INT,
    scheduled_sessions INT,
    completed_sessions INT
);
```

## 11. Query Patterns and Examples

### Transaction Fact Queries
```sql
-- Detailed transaction analysis
SELECT 
    p.product_name,
    d.full_date,
    SUM(f.sales_amount) as daily_sales,
    COUNT(*) as transaction_count
FROM sales_transaction_fact f
JOIN product_dim p ON f.product_key = p.product_key
JOIN date_dim d ON f.transaction_date_key = d.date_key
WHERE d.year = 2024
GROUP BY p.product_name, d.full_date;
```

### Snapshot Fact Queries
```sql
-- Monthly trend analysis
SELECT 
    d.year_month,
    AVG(f.closing_balance) as avg_balance,
    MAX(f.closing_balance) as max_balance
FROM account_balance_snapshot_fact f
JOIN date_dim d ON f.snapshot_date_key = d.date_key
GROUP BY d.year_month
ORDER BY d.year_month;
```

### Accumulating Snapshot Queries
```sql
-- Process duration analysis
SELECT 
    AVG(DATEDIFF(delivery_date, order_date)) as avg_process_days
FROM order_fulfillment_fact
WHERE delivery_date_key IS NOT NULL;
```

## 12. Best Practices Summary

1. **Choose the right fact table type** based on business requirements\n2. **Maintain consistent grain** throughout the fact table\n3. **Use surrogate keys** for dimension relationships\n4. **Implement proper indexing** for query performance\n5. **Consider partitioning** for large fact tables\n6. **Document the fact table grain** and refresh frequency\n7. **Handle slowly changing dimensions** appropriately\n8. **Validate data quality** at the ETL stage

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Methodologies/Kimball Methodology|Kimball Methodology]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Links For Types Of Fact Table|Links For Types Of Fact Table]]
