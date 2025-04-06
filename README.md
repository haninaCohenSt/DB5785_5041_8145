<a name="workshop-id"></a>

📝 Workshop Files & Scripts (Hanina Cohen & Oded Ofek) 🧑‍🎓
This workshop introduces key database concepts and provides hands-on practice in a controlled, containerized environment using PostgreSQL within Docker. Our project focuses on the financial part of a hotel management system, where we designed and implemented a database to track expenses, transactions, invoices, taxes, and payment methods. Below are the details of our implementation.

Team Members:

Hanina Cohen (ID: 337615041)
Oded Ofek (ID: 215348145)
Key Concepts Covered:
Entity-Relationship Diagram (ERD):

Designed an ERD to model relationships and entities for the financial part of a hotel management system.
Focused on normalizing the database and ensuring scalability for tracking expenses, transactions, invoices, taxes, and payment methods.
ERD Snapshot:

![ERD Diagram](images/erd/ERD.png)

Data Structure Diagram (DSD) Snapshot:

![DSD Diagram](images/erd/DSD.png)

ERD Explanation (Data Dictionary):

Expense Tracking Database: Data Dictionary
Entities and Attributes
Supplier

A vendor or service provider from whom goods or services are purchased.

Attribute	Description	Data Type	Constraints
SupplierID	Unique identifier for each supplier	Integer	Primary Key
SupplierName	Legal name of the supplier	Text	Not Null
ContactDetails	Phone number, email, or other contact info	Text	
Address	Physical or mailing address of the supplier	Text	
Expense

A record of money spent related to business operations.

Attribute	Description	Data Type	Constraints
ExpenseID	Unique identifier for each expense	Integer	Primary Key
Description	Details about what the expense was for	Text	
Category	Classification of expense (e.g., Utilities)	Text	
TransactionID	Reference to the associated transaction	Integer	Foreign Key
SupplierID	Reference to the supplier for this expense	Integer	Foreign Key (Optional)
Transaction

A financial event representing the transfer of money.

Attribute	Description	Data Type	Constraints
TransactionID	Unique identifier for each transaction	Integer	Primary Key
Date	When the transaction occurred	Date	Not Null
Amount	Monetary value of the transaction	Decimal	Not Null
Status	Current state (e.g., Pending, Completed)	Text	
PaymentMethodID	Reference to how payment was made	Integer	Foreign Key
InvoiceID	Reference to associated invoice	Integer	Foreign Key (Optional)
Invoice

A formal document issued by a supplier requesting payment.

Attribute	Description	Data Type	Constraints
InvoiceID	Unique identifier for each invoice	Integer	Primary Key
Discount	Reduction in price offered by supplier	Decimal	Optional
TypeA/D	Classification of invoice type	Text	
PaymentMethod

The means by which a transaction is settled.

Attribute	Description	Data Type	Constraints
PaymentMethodID	Unique identifier for payment method	Integer	Primary Key
MethodName	Name of payment method (e.g., Credit Card)	Text	Not Null
MethodDetails	Detail of method if needed	Text	
Tax

Information about taxation applied to a transaction.

Attribute	Description	Data Type	Constraints
TaxID	Unique identifier for tax record	Integer	Primary Key
TransactionID	Reference to associated transaction	Integer	Foreign Key, Composite Key
Percentage	Tax rate applied (e.g., 7%, 10%)	Decimal	
TaxAmount	Calculated tax value	Decimal	
DoToDate	Due date for tax payment or filing	Date	
Relationships
GetPaidBy: Connects Supplier and Expense (One-to-Many). One supplier can be associated with many expenses. Both sides are optional since some suppliers may not have business with the hotel, and some expenses aren’t for suppliers.
Involves: Connects Expense and Transaction (One-to-Many). Each expense is associated with one or more transactions. Not every transaction has an expense (e.g., it could be income), but every expense must have a transaction.
Used: Connects PaymentMethod and Transaction (Many-to-Many). Many payment methods can be used for many transactions. Not every method has a transaction, but every transaction uses one or more payment methods.
GeneratedBy: Connects Transaction and Invoice (One-to-One). Each transaction is associated with one invoice. Every invoice has a transaction, but not every transaction has an invoice (e.g., some are expenses).
Has: Connects Transaction and Tax (One-to-Many). Each transaction can have one or multiple taxes. Not every tax has a transaction.
Creating Tables:

Translated the ERD into actual tables, defining columns, data types, primary keys, and foreign keys for the financial part of the hotel management system.
Utilized SQL commands to create the tables.
Table Creation Code:

sql

Collapse

Wrap

Copy
-- Supplier Table
CREATE TABLE Supplier (
    SupplierID SERIAL PRIMARY KEY,
    SupplierName TEXT NOT NULL,
    ContactDetails TEXT,
    Address TEXT
);

-- Expense Table
CREATE TABLE Expense (
    ExpenseID SERIAL PRIMARY KEY,
    Description TEXT,
    Category TEXT,
    TransactionID INTEGER NOT NULL,
    SupplierID INTEGER,
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
);

-- Transaction Table
CREATE TABLE Transaction (
    TransactionID SERIAL PRIMARY KEY,
    Date DATE NOT NULL,
    Amount DECIMAL NOT NULL,
    Status TEXT,
    PaymentMethodID INTEGER NOT NULL,
    InvoiceID INTEGER,
    FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID),
    FOREIGN KEY (InvoiceID) REFERENCES Invoice(InvoiceID)
);

-- Invoice Table
CREATE TABLE Invoice (
    InvoiceID SERIAL PRIMARY KEY,
    Discount DECIMAL,
    TypeAD TEXT
);

-- PaymentMethod Table
CREATE TABLE PaymentMethod (
    PaymentMethodID SERIAL PRIMARY KEY,
    MethodName TEXT NOT NULL,
    MethodDetails TEXT
);

-- Tax Table
CREATE TABLE Tax (
    TaxID SERIAL PRIMARY KEY,
    TransactionID INTEGER NOT NULL,
    Percentage DECIMAL,
    TaxAmount DECIMAL,
    DoToDate DATE,
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID)
);
SQL Table Creation Snapshot:

![SQL Table Creation](images/erd/sql.png)

Generating Sample Data:

Generated sample data to simulate real-world financial scenarios for a hotel using SQL Insert Statements.
Inserted data for suppliers, expenses, transactions, invoices, payment methods, and taxes.
Excel Snapshot of Sample Data:

![Excel Sample Data](images/erd/exel.png)

CSV Snapshot of Sample Data:

![CSV Sample Data](images/erd/csv.png)

Writing SQL Queries:

Practiced writing SELECT, JOIN, GROUP BY, and ORDER BY queries to analyze financial data.
Focused on efficient querying for expense tracking and tax calculations.
Example SQL Query:

sql

Collapse

Wrap

Copy
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
Stored Procedures and Functions:

Created a stored procedure to calculate the total tax amount for a given transaction.
Stored Procedure Code:

sql

Collapse

Wrap

Copy
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

-- Call the stored procedure
CALL CalculateTotalTaxForTransaction(1);
Views:

Created a view to simplify querying expenses with supplier and tax details.
View Code:

sql

Collapse

Wrap

Copy
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
PostgreSQL with Docker:

Set up a Docker container to run PostgreSQL for the hotel management system.
Configured database connections and ensured data persistence.
Docker Configuration Code:

bash

Collapse

Wrap

Copy
# Create a Docker volume for persistence
docker volume create hotel_db_data

# Run PostgreSQL container
docker run --name hotel_postgres -e POSTGRES_PASSWORD=securepassword -d -p 5432:5432 -v hotel_db_data:/var/lib/postgresql/data postgres:latest

# Run pgAdmin container
docker run --name hotel_pgadmin -d -p 5050:80 -e PGADMIN_DEFAULT_EMAIL=admin@hotel.com -e PGADMIN_DEFAULT_PASSWORD=adminpass dpage/pgadmin4:latest
