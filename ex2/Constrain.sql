ALTER TABLE transaction
ALTER COLUMN amount SET NOT NULL;

ALTER TABLE paymentmethod
ALTER COLUMN methoddetails SET DEFAULT 'USD';

ALTER TABLE transaction
ALTER COLUMN status SET DEFAULT 'Approved';
