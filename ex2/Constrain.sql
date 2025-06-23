ALTER TABLE payment
ALTER COLUMN amount SET NOT NULL;

ALTER TABLE tax
ADD CONSTRAINT chk_percentage CHECK (percentage >= 0 AND percentage <= 100);

ALTER TABLE supplier
ALTER COLUMN country SET DEFAULT 'Israel';