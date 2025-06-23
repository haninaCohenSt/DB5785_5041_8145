--COMMIT example
BEGIN;
UPDATE transaction
SET status = 'Completed'
WHERE status = 'Pending';
COMMIT;

--ROLLBACK example
BEGIN;
UPDATE supplier 
SET contactdetails = 'updated@example.com, 050-1234501' 
WHERE contactdetails IS NULL OR contactdetails = 'supplier1@domain.com, 050-1234501';

SELECT COUNT(*) FROM supplier WHERE contactdetails = 'updated@example.com, 050-1234501';
SELECT * FROM supplier WHERE contactdetails = 'updated@example.com, 050-1234501';

SELECT * FROM public.supplier
ORDER BY supplierid ASC 

ROLLBACK;