A hash join in SQL is a physical join operation used by database engines to efficiently combine rows from two tables based on a join condition, especially when dealing with large datasets.[learn.microsoft+1](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)​

## How Hash Join Works

- The hash join algorithm works in two main phases: the **build phase** and the **probe phase**.[sisense+1](https://www.sisense.com/blog/how-joins-work/)​
    
- In the **build phase**, the database engine scans the smaller of the two tables (called the build input) and creates an in-memory hash table using the join key (the column used for joining).[learn.microsoft+1](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)​
    
- In the **probe phase**, the engine scans the larger table (called the probe input) and for each row, it computes the hash value of the join key and looks up matching rows in the hash table. If a match is found, the rows are combined and returned as part of the result set.[sisense+1](https://www.sisense.com/blog/how-joins-work/)​
    

## When Hash Join Is Used

- Hash joins are typically chosen by the query optimizer when one or both tables are large and there is no useful index on the join columns.[learn.microsoft+1](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)​
    
- They are especially efficient for equijoins (joins using equality conditions, like `=`) and when the tables are not already sorted.[sisense](https://www.sisense.com/blog/how-joins-work/)​
    
- If the build input is too large to fit in memory, the database may use a "grace hash join," which partitions both tables and performs hash joins on each partition.[learn.microsoft](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)​
    

## Example

Suppose you have two tables, `Orders` and `Customers`, and you want to join them on `CustomerID`:

sql

`SELECT * FROM Orders JOIN Customers ON Orders.CustomerID = Customers.CustomerID;`

If the optimizer decides to use a hash join, it will:

- Build a hash table from the smaller table (say, `Customers`) using `CustomerID`.
    
- Probe the `Orders` table, compute the hash for each `CustomerID`, and find matches in the hash table.
    

## Advantages and Disadvantages

- **Advantages:** Hash joins are fast for large tables and do not require sorting or indexing on the join columns.[sisense+1](https://www.sisense.com/blog/how-joins-work/)​
    
- **Disadvantages:** They require significant memory for the hash table, and performance can degrade if the hash table does not fit in memory.[learn.microsoft](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)​
    

In summary, hash joins are a powerful and efficient way for databases to combine large tables, especially when indexes or sorting are not available.[sisense+1](https://www.sisense.com/blog/how-joins-work/)​

1. [https://www.w3schools.com/sql/sql_join.asp](https://www.w3schools.com/sql/sql_join.asp)
2. [https://www.geeksforgeeks.org/sql/sql-join-set-1-inner-left-right-and-full-joins/](https://www.geeksforgeeks.org/sql/sql-join-set-1-inner-left-right-and-full-joins/)
3. [https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17)
4. [https://www.coursera.org/in/articles/sql-join-types](https://www.coursera.org/in/articles/sql-join-types)
5. [https://www.sisense.com/blog/how-joins-work/](https://www.sisense.com/blog/how-joins-work/)
6. [https://hightouch.com/sql-dictionary/sql-join-where](https://hightouch.com/sql-dictionary/sql-join-where)
7. [https://www.atlassian.com/data/sql/sql-join-types-explained-visually](https://www.atlassian.com/data/sql/sql-join-types-explained-visually)
8. [https://www.w3schools.com/sql/sql_join_full.asp](https://www.w3schools.com/sql/sql_join_full.asp)
9. [https://mode.com/sql-tutorial/sql-joins-where-vs-on/](https://mode.com/sql-tutorial/sql-joins-where-vs-on/)
10. [https://www.datacamp.com/tutorial/sql-update-with-join](https://www.datacamp.com/tutorial/sql-update-with-join)