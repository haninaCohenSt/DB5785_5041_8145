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
