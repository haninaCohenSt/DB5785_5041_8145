# 📝 Workshop Files & Scripts (Hanina Cohen & Oded Ofek) 🧓‍🎓

This workshop introduces key database concepts and provides hands-on practice in a controlled, containerized environment using PostgreSQL within Docker. Our project focuses on the financial part of a hotel management system, where we designed and implemented a database to track expenses, transactions, invoices, taxes, and payment methods. Below are the details of our implementation.

---

## 🎓 Team Members

* **Hanina Cohen** (ID: 337615041)
* **Oded Ofek** (ID: 215348145)

---

## 🔎 Key Concepts Covered

### Entity-Relationship Diagram (ERD)

* Designed an ERD to model relationships and entities for the financial part of a hotel management system.
* Focused on normalizing the database and ensuring scalability for tracking expenses, transactions, invoices, taxes, and payment methods.

**ERD Snapshot:**
![ERD Diagram](images/erd/ERD.png)

### Data Structure Diagram (DSD) Snapshot

![DSD Diagram](images/erd/DSD.png)

---

## 📊 ERD Explanation (Data Dictionary)

### Supplier

Represents a vendor or service provider from whom goods or services are purchased.

| Attribute      | Description                         | Data Type | Constraints |
| -------------- | ----------------------------------- | --------- | ----------- |
| SupplierID     | Unique identifier for each supplier | Integer   | Primary Key |
| SupplierName   | Legal name of the supplier          | Text      | Not Null    |
| ContactDetails | Phone, email, or other contact      | Text      |             |
| Address        | Physical or mailing address         | Text      |             |

### Expense

Represents a record of money spent related to business operations.

| Attribute     | Description                         | Data Type | Constraints            |
| ------------- | ----------------------------------- | --------- | ---------------------- |
| ExpenseID     | Unique identifier for each expense  | Integer   | Primary Key            |
| Description   | Details about the expense           | Text      |                        |
| Category      | Classification of expense           | Text      |                        |
| TransactionID | Reference to associated transaction | Integer   | Foreign Key (Not Null) |
| SupplierID    | Reference to the supplier           | Integer   | Foreign Key (Optional) |

### Transaction

Represents a financial event involving transfer of money.

| Attribute       | Description                       | Data Type | Constraints            |
| --------------- | --------------------------------- | --------- | ---------------------- |
| TransactionID   | Unique identifier for transaction | Integer   | Primary Key            |
| Date            | When the transaction occurred     | Date      | Not Null               |
| Amount          | Monetary value of transaction     | Decimal   | Not Null               |
| Status          | Current state of transaction      | Text      |                        |
| PaymentMethodID | Payment method used               | Integer   | Foreign Key (Not Null) |
| InvoiceID       | Reference to associated invoice   | Integer   | Foreign Key (Optional) |

### Invoice

Represents a formal document requesting payment.

| Attribute | Description                    | Data Type | Constraints |
| --------- | ------------------------------ | --------- | ----------- |
| InvoiceID | Unique identifier for invoice  | Integer   | Primary Key |
| Discount  | Discount offered by supplier   | Decimal   | Optional    |
| TypeAD    | Classification of invoice type | Text      |             |

### PaymentMethod

Represents the method by which a transaction was settled.

| Attribute       | Description                          | Data Type | Constraints |
| --------------- | ------------------------------------ | --------- | ----------- |
| PaymentMethodID | Unique identifier for payment method | Integer   | Primary Key |
| MethodName      | Name (e.g., Credit Card)             | Text      | Not Null    |
| MethodDetails   | Additional info if needed            | Text      |             |

### Tax

Information about taxation applied to a transaction.

| Attribute     | Description                      | Data Type | Constraints            |
| ------------- | -------------------------------- | --------- | ---------------------- |
| TaxID         | Unique identifier for tax record | Integer   | Primary Key            |
| TransactionID | Related transaction              | Integer   | Foreign Key (Not Null) |
| Percentage    | Tax rate applied                 | Decimal   |                        |
| TaxAmount     | Calculated tax amount            | Decimal   |                        |
| DoToDate      | Due date for payment/filing      | Date      |                        |

---

## 🛠️ Table Relationships with Notation

| Relationship Name | From (Entity) | To (Entity)     | Cardinality     | Description                                                                               |
| ----------------- | ------------- | --------------- | --------------- | ----------------------------------------------------------------------------------------- |
| `GetPaidBy`       | `Expense`     | `Supplier`      | `0..N` → `0..1` | A supplier may be linked to many expenses, and an expense may optionally have a supplier. |
| `Involves`        | `Expense`     | `Transaction`   | `1` → `1`       | Every expense must be linked to exactly one transaction.                                  |
| `GeneratedBy`     | `Transaction` | `Invoice`       | `0..1` ↔ `0..1` | A transaction may optionally generate one invoice and vice versa.                         |
| `Used`            | `Transaction` | `PaymentMethod` | `0..N` → `1`    | Each transaction uses exactly one payment method, which may be used by many transactions. |
| `Has`             | `Transaction` | `Tax`           | `0..1` ← `0..N` | A transaction can have many taxes; each tax belongs to exactly one transaction.           |

**Legend:**

* `1`: Exactly one (mandatory)
* `0..1`: Zero or one (optional)
* `0..N`: Zero or many (optional)
* `1..N`: One or many (at least one, mandatory)
* `↔`: Bidirectional

---

## 📁 Creating Tables

Translated the ERD into actual tables, defining columns, data types, primary keys, and foreign keys.
```sql
CREATE TABLE Supplier (
    SupplierID NUMERIC(5) NOT NULL,
    SupplierName VARCHAR(15) NOT NULL,
    ContactDetails VARCHAR(50) NOT NULL,
    Address VARCHAR(50) NOT NULL,
    PRIMARY KEY (SupplierID)
);

CREATE TABLE PaymentMethod (
    PaymentMethodID NUMERIC(5) NOT NULL,
    MethodName VARCHAR(15) NOT NULL,
    MethodDetails VARCHAR(50) NOT NULL,  -- Fixed typo from MehtodDetails
    PRIMARY KEY (PaymentMethodID)
);

CREATE TABLE Expense (
    ExpenseID NUMERIC(5) NOT NULL,
    Description VARCHAR(100) NOT NULL,
    Category VARCHAR(15) NOT NULL,
    SupplierID NUMERIC(5),  -- Can be NULL if expense doesn't have a supplier
    PRIMARY KEY (ExpenseID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
);

CREATE TABLE Tax (
    TaxID NUMERIC(5) NOT NULL,
    Percentage NUMERIC(5,2) NOT NULL,  -- Changed to support decimals like 10.25%
    TaxAmount NUMERIC(10,2) NOT NULL,  -- Changed to NUMERIC for money values
    DueDate DATE NOT NULL,  -- Fixed typo from DoToDate
    PRIMARY KEY (TaxID)
);

CREATE TABLE Transaction (
    TransactionID NUMERIC(5) NOT NULL,
    Date DATE NOT NULL DEFAULT CURRENT_DATE,  -- Added DEFAULT for convenience
    Amount NUMERIC(10,2) NOT NULL CHECK (Amount > 0),  -- Added CHECK and changed to NUMERIC
    Status VARCHAR(15) NOT NULL DEFAULT 'Pending',  -- Added DEFAULT with common status
    ExpenseID NUMERIC(5),  -- Can be NULL if transaction isn't tied to a specific expense
    PRIMARY KEY (TransactionID),
    FOREIGN KEY (ExpenseID) REFERENCES Expense(ExpenseID)
);

CREATE TABLE Invoice (
    InvoiceID NUMERIC(5) NOT NULL,
    Discount NUMERIC(5,2),  -- Can be NULL if no discount
    Type CHAR(1) NOT NULL CHECK (Type IN ('A', 'D')),  -- Fixed column name from TypeA/D
    TransactionID NUMERIC(5) NOT NULL,
    PRIMARY KEY (InvoiceID),
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID)
);

CREATE TABLE Used (
    TransactionID NUMERIC(5) NOT NULL,
    PaymentMethodID NUMERIC(5) NOT NULL,
    PRIMARY KEY (TransactionID, PaymentMethodID),
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID),
    FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID)
);

CREATE TABLE Has (
    TaxID NUMERIC(5) NOT NULL,
    TransactionID NUMERIC(5) NOT NULL,
    PRIMARY KEY (TaxID, TransactionID),
    FOREIGN KEY (TaxID) REFERENCES Tax(TaxID),
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID)
);
```

**Table Creation Snapshot:**
![SQL Table Creation](images/erd/sql.png)

---

## 📝 Sample Data

Generated realistic sample data using SQL `INSERT` statements.

**Excel Snapshot:**
![Excel Sample Data](images/erd/exel.png)

**CSV Snapshot:**
![CSV Sample Data](images/erd/csv.png)

---

## 🔢 SQL Queries

Practiced writing queries to analyze financial data.

```sql
-- Query to get total expenses per supplier with tax details
SELECT
    s.SupplierName,
    SUM(e.Amount) AS TotalExpense,
    SUM(t.TaxAmount) AS TotalTax,
    t.Percentage
FROM Supplier s
JOIN Expense e ON s.SupplierID = e.SupplierID
JOIN Transaction tr ON e.TransactionID = tr.TransactionID
JOIN Tax t ON tr.TransactionID = t.TransactionID
GROUP BY s.SupplierName, t.Percentage
ORDER BY TotalExpense DESC;
```

---

## 📊 Stored Procedures and Functions

Created a stored procedure to calculate total tax for a given transaction.

```sql
CREATE OR REPLACE PROCEDURE CalculateTotalTaxForTransaction(p_TransactionID INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_TotalTax DECIMAL;
BEGIN
    SELECT SUM(TaxAmount) INTO v_TotalTax
    FROM Tax
    WHERE TransactionID = p_TransactionID;

    RAISE NOTICE 'Total Tax for Transaction %: %', p_TransactionID, v_TotalTax;
END;
$$;

-- Call it:
CALL CalculateTotalTaxForTransaction(1);
```

---

## 🔍 Views

Created a view to simplify querying expense, supplier, and tax details.

```sql
CREATE VIEW ExpenseSummary AS
SELECT
    e.ExpenseID,
    e.Description,
    e.Category,
    s.SupplierName,
    tr.Amount,
    t.TaxAmount,
    t.Percentage
FROM Expense e
JOIN Supplier s ON e.SupplierID = s.SupplierID
JOIN Transaction tr ON e.TransactionID = tr.TransactionID
JOIN Tax t ON tr.TransactionID = t.TransactionID;

-- Query the view
SELECT * FROM ExpenseSummary;
```
## 📘 Stage B – Queries, Constraints, and Transactions

This stage focuses on querying the database, enforcing integrity constraints, and demonstrating transactional control. The work in this stage reflects the business logic needed for interacting with the financial subsystem of our hotel management system.

---

### 🔍 SQL Queries

We wrote complex SELECT, DELETE, and UPDATE queries that span multiple tables, utilize aggregate functions, joins, date logic, and grouping mechanisms.

All queries are numbered sequentially for clarity.

#### 🟢 Query 1 – Expenses with Suppliers and Transactions

```sql
SELECT 
  E.ExpenseID,
  E.Description,
  E.Category,
  S.SupplierName,
  T.Amount
FROM Expense E
JOIN Supplier S ON E.SupplierID = S.SupplierID
LEFT JOIN Transaction T ON E.ExpenseID = T.ExpenseID;
```

📸 Screenshot A – Result with columns from multiple tables
![Query 1](images/erd/q1.png)

#### 🟢 Query 2 – Payment Methods Used in Transactions

```sql
SELECT 
  T.transactionid,
  T.date,
  PM.methodname,
  PM.methoddetails
FROM transaction T
JOIN "paymentMethodUsedInTransaction" U ON T.transactionid = U.transactionid
JOIN paymentmethod PM ON U.paymentmethodid = PM.paymentmethodid;
```

📸 Screenshot B – Results with detailed method names
![Query 2](images/erd/q2.png)

#### 🟢 Query 3 – Total Spending per Supplier

```sql
SELECT 
  S.SupplierName,
  SUM(T.Amount) AS TotalSpent
FROM Supplier S
JOIN Expense E ON S.SupplierID = E.SupplierID
JOIN Transaction T ON E.ExpenseID = T.ExpenseID
GROUP BY S.SupplierName;
```

📸 Screenshot C – Aggregate spending by supplier
![Query 3](images/erd/q3.png)

#### 🟢 Query 4 – Supplier Expense Counts

```sql
SELECT 
  Supplier.SupplierName,
  COUNT(Expense.ExpenseID) AS TotalExpenses
FROM Supplier
LEFT JOIN Expense ON Supplier.SupplierID = Expense.SupplierID
GROUP BY Supplier.SupplierName;
```

📸 Screenshot D – Number of expenses per supplier
![Query 4](images/erd/q4.png)

#### 🟢 Query 5 – Transactions Without Taxes

```sql
SELECT T.transactionid
FROM transaction T
LEFT JOIN "transactionHasTax" H ON T.transactionid = H.transactionid
WHERE H.taxid IS NULL;
```

📸 Screenshot E – Transactions missing tax relationships
![Query 5](images/erd/q5.png)

#### 🟢 Query 6 – Transaction Summary by Supplier, Category, and Payment Method

```sql
SELECT 
    T.TransactionID,
    T.Date,
    T.Amount,
    E.Category,
    S.SupplierName,
    PM.MethodName
FROM Transaction T
LEFT JOIN Expense E ON T.ExpenseID = E.ExpenseID
LEFT JOIN Supplier S ON E.SupplierID = S.SupplierID
LEFT JOIN "paymentMethodUsedInTransaction" U ON T.TransactionID = U.TransactionID
LEFT JOIN PaymentMethod PM ON U.PaymentMethodID = PM.PaymentMethodID;
```

📸 Screenshot F – Full context of each transaction
![Query 6](images/erd/q6.png)

#### 🟢 Query 7 – Supplier with Highest Total Transaction Amount

```sql
SELECT SupplierName
FROM (
  SELECT 
    S.SupplierName,
    SUM(T.Amount) AS Total
  FROM Supplier S
  JOIN Expense E ON S.SupplierID = E.SupplierID
  JOIN Transaction T ON T.ExpenseID = E.ExpenseID
  GROUP BY S.SupplierName
  ORDER BY Total DESC
  LIMIT 1
) AS TopSupplier;
```

📸 Screenshot G – Top supplier only
![Query 7](images/erd/q7.png)

#### 🟢 Query 8 – Invoices from the Last 30 Days

```sql
SELECT *
FROM Transaction
WHERE Date >= CURRENT_DATE - INTERVAL '30 days';
```

📸 Screenshot H – Recent transactions
![Query 8](images/erd/q8.png)

#### 🟢 Query 9 – Final Invoice Amounts (after Discount)

```sql
SELECT 
  Invoice.InvoiceID,
  Transaction.Amount,
  Invoice.Discount,
  (Transaction.Amount - COALESCE(Invoice.Discount, 0)) AS FinalAmount
FROM Invoice
JOIN Transaction ON Invoice.TransactionID = Transaction.TransactionID;
```

📸 Screenshot I – Invoice totals with discount
![Query 9](images/erd/q9.png)

#### 🟢 Query 10 – Transactions Above a Threshold

```sql
SELECT * 
FROM Transaction
WHERE Amount > 10000;
```

📸 Screenshot J – High value transactions
![Query 10](images/erd/q10.png)

#### 🟢 Query 11 – Average Tax Rate

```sql
SELECT AVG(Percentage) AS AvgTaxRate
FROM Tax;
```

📸 Screenshot K – Mean percentage
![query 11](images/erd/q11.png)

#### 🟢 Query 12 – Tax Details Per Transaction

```sql
SELECT 
  T.transactionid,
  Tax.taxamount,
  Tax.percentage,
  Tax.duedate
FROM transaction T
JOIN "transactionHasTax" H ON T.transactionid = H.transactionid
JOIN tax ON H.taxid = Tax.taxid;
```

📸 Screenshot L – Taxes with amounts and deadlines
![query 12](images/erd/q12.png)

#### 🟢 Query 13 – Top 5 Suppliers by Transaction Count

```sql
SELECT 
  S.SupplierName,
  COUNT(T.TransactionID) AS TransactionCount
FROM Supplier S
JOIN Expense E ON S.SupplierID = E.SupplierID
JOIN Transaction T ON E.ExpenseID = T.ExpenseID
GROUP BY S.SupplierName
ORDER BY TransactionCount DESC
LIMIT 5;
```

📸 Screenshot M – Supplier rankings
![query 13](images/erd/q13.png)


---

### 🧹 DELETE Operations

#### Delete Rejected Invoices 

```sql
DELETE FROM invoice
WHERE transactionid IN (
    SELECT transactionid
    FROM transaction
    WHERE status = 'Rejected'
);
```

📸 Screenshot O – Invoice table before and after

![Before – Delete rejected invoices](images/erd/Bd1.png)

![After – Delete rejected invoices](images/erd/Ad1.png)

#### Delete Old Tax Links 

```sql
DELETE FROM "transactionHasTax"
WHERE transactionid IN (
    SELECT transactionid 
    FROM transaction 
    WHERE status = 'Completed' AND date < '2025-05-06'
);
```

📸 Screenshot P – Relationship cleanup

![Before – Delete old tax relationships](images/erd/Bd2.png)

![After – Delete old tax relationships](images/erd/Ad2.png)

#### Delete Old Payment Links 

```sql
DELETE FROM "paymentMethodUsedInTransaction"
WHERE transactionid IN (
    SELECT transactionid 
    FROM transaction 
    WHERE status = 'Completed' AND date < '2025-05-06'
);
```

📸 Screenshot Q – Payment linkage cleaned

![Before – Delete old payment method links](images/erd/Bd3.png)

![After – Delete old payment method links](images/erd/Ad3.png)

---

### ✏️ UPDATE Operations

#### Update Invoice Discounts 

```sql
UPDATE invoice
SET discount = 0.10
WHERE type = 'D';
```

![Before – Update discount](images/erd/Bu1.png)

![After – Update discount](images/erd/Au1.png)

#### Standardize Supplier Contact 
```sql
UPDATE supplier
SET contactdetails = CONCAT(suppliername, '@business.com')
WHERE contactdetails IS NULL 
OR contactdetails = '' 
OR contactdetails NOT LIKE '%@%'
OR contactdetails = 'supplier1@domain.com, 050-1234501';
```

![Before – Update supplier contact](images/erd/Bu3.png)

![After – Update supplier contact](images/erd/Au3.png)

#### Apply Late Fees 

```sql
UPDATE transaction
SET amount = amount * 1.05
WHERE date < CURRENT_DATE - INTERVAL '30 days'
AND status = 'Pending';
```

![Before – Apply late fee](images/erd/Bu2.png)

![After – Apply late fee](images/erd/Au2.png)


---

### ✅ Transaction Control

#### COMMIT Example 

```sql
BEGIN;
UPDATE transaction
SET status = 'Completed'
WHERE status = 'Pending';
COMMIT;
```

📸 Screenshot S – Final committed state

![COMMIT](images/erd/commit.png)

#### ROLLBACK Example (Query 22)

```sql
BEGIN;
UPDATE supplier 
SET contactdetails = 'updated@example.com, 050-1234501' 
WHERE contactdetails IS NULL OR contactdetails = 'supplier1@domain.com, 050-1234501';
-- Check state
SELECT * FROM supplier
WHERE contactdetails = 'updated@example.com, 050-1234501';
ROLLBACK;
```

📸 Screenshot T – Reverted update
![Before&After – Rollback test](images/erd/rollback.png)

---

### 📏 Constraints

#### Constraint 1 – NOT NULL on Transaction Amount

```sql
ALTER TABLE transaction
ALTER COLUMN amount SET NOT NULL;
```
![](images/erd/A1.png)
#### Constraint 2 – DEFAULT on Payment Method Details

```sql
ALTER TABLE paymentmethod
ALTER COLUMN methoddetails SET DEFAULT 'USD';
```
![](images/erd/A3.png)
#### Constraint 3 – DEFAULT on Transaction Status

```sql
ALTER TABLE transaction
ALTER COLUMN status SET DEFAULT 'Approved';
```
![](images/erd/A2.png)


## 🧹 Stage C – Integration & Views

This stage focuses on integrating two separate database systems: the **Financial System** and the **Reception System**, into a unified database model. The integration was achieved using PostgreSQL’s `postgres_fdw` extension. Additionally, two views were created — one for each subsystem — along with meaningful queries to demonstrate data accessibility and insight generation.

---

### 🦇 Integration Strategy

#### 🚪 Databases Involved:

* **db5785\_4051\_8145** – Financial Database (our original project)
* **DB25785\_4051\_8145** – Reception Database (received from another team)

#### 🛠️ Tools Used:

* PostgreSQL
* ERDPlus (for ERD & DSD modeling)
* `postgres_fdw` (Foreign Data Wrapper)
* Git for version control (`stage-c` tag)

---

### 🗱 Step-by-Step Integration Workflow

1. **DSD Creation from Reception DB**
   We received a backup of the Reception system and reverse-engineered the table structures to build its **DSD**.

2. **ERD Reverse Engineering**
   From the DSD, we created a logical **ERD** for the reception system, identifying key entities like `reservations`, `guests`, `rooms`, and `checkinout`.

3. **Designing the Unified ERD**
   We merged our **Financial ERD** with the **Reception ERD**, making key design decisions to:

   * Avoid data duplication
   * Use *foreign tables* instead of direct duplication
   * Introduce **linking tables** (e.g., `reservationfinancelink`)
   * Add **sync-tracking** functionality (`reservationsync`)

   📸 See:

   * `/images/integration/reception_erd.png`
   * `/images/integration/combined_erd.png`

4. **Implementing Integration**
   Using the `Integrate.sql` script:

   * Enabled `postgres_fdw`
   * Created a `FOREIGN SERVER` to the reception database
   * Imported foreign tables: `guests`, `rooms`, `reservations`, `checkinout`
   * Renamed them with a `foreign_` prefix
   * Created `reservationfinancelink` and `reservationsync` tables
   * Populated the linking tables with test data
   * Indexed fields for performance
   * Verified the integration with `SELECT` diagnostics

---

### 📂 Key Integration Tables

#### `reservationfinancelink`

Links a reservation (reception) to a financial transaction (finance).

```sql
CREATE TABLE reservationfinancelink (
    link_id INTEGER PRIMARY KEY,
    reservation_id NUMERIC NOT NULL,
    transaction_id NUMERIC NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transaction(TransactionID)
);
```

#### `reservationsync`

Captures a snapshot of reservation and payment summary for syncing and reporting.

---

### 👁️ Views & Analytical Queries

We created two views — each from the perspective of a different department.

#### 📘 View 1: `financial_reservation_view`

Shows detailed reservation and payment status — for use by the finance team. Combines room pricing, invoice discounts, and payment status.

##### 🔍 Queries on Financial View:

* **Query 1.1 – Outstanding Payments**
  Shows guests with unpaid or pending reservations.
* **Query 1.2 – Revenue by Room Type**
  Aggregates expected vs actual revenue, with discount analysis.

📸 Screenshot: `/images/views/financial_view_sample.png`

---

#### 📗 View 2: `reception_occupancy_financial_view`

Aggregates room utilization and revenue status. Helps reception manage occupancy and payment collection status.

##### 🔍 Queries on Reception View:

* **Query 2.1 – Room Performance Summary**
  Combines total bookings, current occupancy, and revenue.
* **Query 2.2 – Payment Status Alerts**
  Identifies rooms with payment issues (e.g., pending payments).

📸 Screenshot: `/images/views/reception_view_sample.png`

---

### 📌 Design Decisions

* **Foreign Tables vs Physical Merge**: We opted to *import foreign tables* instead of duplicating the structure. This maintains source-of-truth separation.
* **Naming Conventions**: Added `foreign_` prefix to imported tables for clarity.
* **Linking Tables**: Used minimal tables (`reservationfinancelink`) to connect subsystems.
* **Sync Snapshots**: `reservationsync` stores calculated results for fast reporting.

---

### 📋 Files Added in This Stage

| File Name             | Description                                         |
| --------------------- | --------------------------------------------------- |
| `Integrate.sql`       | Script to create foreign tables and perform linking |
| `Views.sql`           | View creation and related queries                   |
| `images/...`          | Visuals for DSD, ERD, and result screenshots        |
| `backup3`             | Updated backup after integration                    |
| `project-report-c.md` | Detailed PDF/Markdown report for Stage C            |

---

### 🧪 Sample Output

**Output from financial reservation view:**

```sql
SELECT * FROM financial_reservation_view LIMIT 10;
```

| guest\_name | room\_number | expected\_amount | paid\_amount | payment\_summary |
| ----------- | ------------ | ---------------- | ------------ | ---------------- |
| Alice Smith | 203          | 1200             | 1200         | Paid             |
| Bob Johnson | 105          | 1500             | 0            | Not Paid         |

---

## ✅ Summary

This stage demonstrated how to:

* Perform schema-level reverse engineering
* Use PostgreSQL’s `FDW` to connect systems
* Design smart linking tables
* Build complex views that reflect meaningful departmental needs
* Document and version control all changes with GIT

> 📁 All new files are under the `stage-c` folder and submitted with `stage-c` git tag.
