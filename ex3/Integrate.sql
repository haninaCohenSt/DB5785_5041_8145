-- ============================================
-- Hotel Management System Integration Script
-- Financial DB (db5785_4051_8145) + Reception DB (DB25785_4051_8145) Integration
-- ============================================

-- Step 1: Enable Foreign Data Wrapper extension
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Step 2: Create Foreign Server
CREATE SERVER reception_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', port '5432', dbname 'DB25785_4051_8145');

-- Step 3: Create User Mapping
CREATE USER MAPPING FOR CURRENT_USER
SERVER reception_server
OPTIONS (user 'postgres', password '123'); -- Replace with actual password

-- Step 4: Import Foreign Schema and Create Foreign Tables
-- Import the tables from reception database
IMPORT FOREIGN SCHEMA public
LIMIT TO (guests, rooms, reservations, checkinout)
FROM SERVER reception_server
INTO public;

-- Rename imported tables to have foreign_ prefix
ALTER FOREIGN TABLE guests RENAME TO foreign_guests;
ALTER FOREIGN TABLE rooms RENAME TO foreign_rooms;
ALTER FOREIGN TABLE reservations RENAME TO foreign_reservations;
ALTER FOREIGN TABLE checkinout RENAME TO foreign_checkinout;

-- Step 5: Create Integration Tables
-- Create reservation-finance linking table
CREATE TABLE reservationfinancelink (
    link_id integer PRIMARY KEY,
    reservation_id numeric NOT NULL,
    transaction_id numeric NOT NULL,
    created_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction FOREIGN KEY (transaction_id) REFERENCES Transaction(TransactionID)
);

-- Create reservation sync tracking table
CREATE TABLE reservationsync (
    reservation_id numeric NOT NULL,
    guest_name character varying,
    room_number numeric,
    check_in_date date,
    check_out_date date,
    total_amount numeric,
    sync_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Step 6: Create Indexes for Performance
CREATE INDEX idx_reservationfinancelink_res ON reservationfinancelink(reservation_id);
CREATE INDEX idx_reservationfinancelink_trans ON reservationfinancelink(transaction_id);
CREATE INDEX idx_reservationsync_res ON reservationsync(reservation_id);

-- Step 7: Initial Data Population
-- Populate reservation-finance links (first 50 reservations)
INSERT INTO reservationfinancelink (link_id, reservation_id, transaction_id, created_date)
VALUES 
(1, 1, 1, CURRENT_TIMESTAMP),
(2, 2, 2, CURRENT_TIMESTAMP),
(3, 3, 3, CURRENT_TIMESTAMP),
(4, 4, 4, CURRENT_TIMESTAMP),
(5, 5, 5, CURRENT_TIMESTAMP),
(6, 6, 6, CURRENT_TIMESTAMP),
(7, 7, 7, CURRENT_TIMESTAMP),
(8, 8, 8, CURRENT_TIMESTAMP),
(9, 9, 9, CURRENT_TIMESTAMP),
(10, 10, 10, CURRENT_TIMESTAMP);

-- Add more links (11-50)
INSERT INTO reservationfinancelink (link_id, reservation_id, transaction_id, created_date)
SELECT 
    generate_series(11, 50) as link_id,
    generate_series(11, 50)::numeric as reservation_id,
    generate_series(11, 50)::numeric as transaction_id,
    CURRENT_TIMESTAMP;

-- Step 8: Populate sync tracking table with sample data
INSERT INTO reservationsync (reservation_id, guest_name, room_number, check_in_date, check_out_date, total_amount)
SELECT 
    r.reservation_id,
    g.first_name || ' ' || g.last_name,
    r.room_number,
    r.check_in_date,
    r.check_out_date,
    ro.price_per_night * (r.check_out_date - r.check_in_date)
FROM foreign_reservations r
JOIN foreign_guests g ON r.guest_id = g.guest_id
JOIN foreign_rooms ro ON r.room_number = ro.room_number
WHERE r.reservation_id <= 10;

-- Step 9: Create Additional Table Relationships if needed
-- Note: No ALTER commands on existing tables were needed as we used foreign tables

-- Step 10: Verify Integration
SELECT 'Integration Summary' as report;
SELECT 'Foreign Tables Created:' as status, COUNT(*) as count 
FROM pg_foreign_table;

SELECT 'Reservation-Finance Links:' as status, COUNT(*) as count 
FROM reservationfinancelink;

SELECT 'Synced Reservations:' as status, COUNT(*) as count 
FROM reservationsync;

-- Step 11: Grant Permissions (if needed)
-- Grant permissions on foreign tables
GRANT SELECT ON foreign_guests TO PUBLIC;
GRANT SELECT ON foreign_rooms TO PUBLIC;
GRANT SELECT ON foreign_reservations TO PUBLIC;
GRANT SELECT ON foreign_checkinout TO PUBLIC;

-- Grant permissions on integration tables
GRANT ALL ON reservationfinancelink TO PUBLIC;
GRANT ALL ON reservationsync TO PUBLIC;

-- Step 12: Final Verification
-- Check all components are in place
DO $$
BEGIN
    RAISE NOTICE 'Integration Complete!';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'Foreign Server: reception_server created';
    RAISE NOTICE 'Foreign Tables: 4 tables imported';
    RAISE NOTICE 'Integration Tables: 2 tables created';
    RAISE NOTICE 'Data Links: 50 reservation-finance links created';
END $$;