ALTER TABLE transaction
ALTER COLUMN amount SET NOT NULL;

ALTER TABLE tax
ADD CONSTRAINT chk_percentage CHECK (percentage >= 0 AND percentage <= 100);

ALTER TABLE invoice
ALTER COLUMN type SET DEFAULT 'A';
