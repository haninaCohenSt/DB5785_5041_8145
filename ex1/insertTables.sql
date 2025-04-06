-- Insert into Supplier
INSERT INTO Supplier (SupplierName, ContactDetails, Address) VALUES
('Acme Corp', 'email@acme.com', '123 Main St'),
('Beta Supplies', 'phone: 555-1234', '456 Oak Ave');

-- Insert into PaymentMethod
INSERT INTO PaymentMethod (MethodName, MethodDetails) VALUES
('Credit Card', 'Visa ending in 1234'),
('Bank Transfer', 'Account #7890');

-- Insert into Expense
INSERT INTO Expense (Description, Category, SupplierID) VALUES
('Office Supplies', 'Operational', 1),
('Software License', 'IT', 2);

-- Insert into Transaction
INSERT INTO Transaction (Date, Amount, Status, ExpenseID, PaymentMethodID) VALUES
('2025-01-15', 500.00, 'Completed', 1, 1),
('2025-02-20', 1200.00, 'Pending', 2, 2);

-- Insert into Invoice
INSERT INTO Invoice (Discount, TypeAD, TransactionID) VALUES
(10.00, 'TypeA', 1),
(0.00, 'TypeD', 2);

-- Insert into Tax
INSERT INTO Tax (Percentage, TaxAmount, DoToDate, TransactionID) VALUES
(5.00, 25.00, '2025-12-31', 1),
(8.00, 96.00, '2025-12-31', 2);