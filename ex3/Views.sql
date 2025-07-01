-- ============================================
-- Hotel Management System Views and Queries
-- ============================================

-- ====================
-- VIEW 1: Financial Perspective - Reservation Financial View
-- Description: Shows reservation details with financial information
-- Combines data from both databases to track payments for reservations
-- ====================

CREATE OR REPLACE VIEW financial_reservation_view AS
SELECT 
    r.reservation_id,
    (g.first_name || ' ' || g.last_name) AS guest_name,
    r.room_number,
    ro.room_type,
    r.check_in_date,
    r.check_out_date,
    r.reservation_status,
    (ro.price_per_night * ((r.check_out_date - r.check_in_date)::numeric)) AS expected_amount,
    t.transactionid,
    t.amount AS paid_amount,
    t.status AS payment_status,
    t.date AS payment_date,
    i.invoiceid,
    i.discount,
    CASE
        WHEN t.transactionid IS NULL THEN 'Not Paid'
        WHEN t.status = 'Completed' THEN 'Paid'
        WHEN t.status = 'Pending' THEN 'Pending Payment'
        WHEN t.status = 'Approved' THEN 'Approved'
        WHEN t.status = 'Rejected' THEN 'Rejected'
        ELSE t.status
    END AS payment_summary
FROM foreign_reservations r
JOIN foreign_guests g ON r.guest_id = g.guest_id
JOIN foreign_rooms ro ON r.room_number = ro.room_number
LEFT JOIN reservationfinancelink rfl ON r.reservation_id = rfl.reservation_id
LEFT JOIN transaction t ON rfl.transaction_id = t.transactionid
LEFT JOIN invoice i ON t.transactionid = i.transactionid;

-- ====================
-- VIEW 2: Reception Perspective - Room Occupancy Financial View
-- Description: Shows room occupancy with financial summary
-- Helps reception track which rooms generate revenue and payment status
-- ====================

CREATE OR REPLACE VIEW reception_occupancy_financial_view AS
SELECT 
    ro.room_number,
    ro.room_type,
    ro.floor,
    ro.status as room_status,
    ro.price_per_night,
    COUNT(DISTINCT r.reservation_id) as total_reservations,
    COUNT(DISTINCT CASE 
        WHEN r.check_in_date <= CURRENT_DATE AND r.check_out_date >= CURRENT_DATE 
        THEN r.reservation_id 
    END) as current_occupation,
    COALESCE(SUM(t.amount), 0) as total_revenue,
    AVG(i.discount) as avg_discount,
    COUNT(DISTINCT CASE 
        WHEN t.status = 'Completed' THEN rfl.reservation_id 
    END) as paid_reservations,
    COUNT(DISTINCT CASE 
        WHEN t.status = 'Pending' THEN rfl.reservation_id 
    END) as pending_payments
FROM foreign_rooms ro
LEFT JOIN foreign_reservations r ON ro.room_number = r.room_number
LEFT JOIN reservationfinancelink rfl ON r.reservation_id = rfl.reservation_id
LEFT JOIN transaction t ON rfl.transaction_id = t.transactionid
LEFT JOIN invoice i ON t.transactionid = i.transactionid
GROUP BY ro.room_number, ro.room_type, ro.floor, ro.status, ro.price_per_night;

-- ============================================
-- Queries on Views
-- ============================================

-- Query 1.1: Outstanding Payments Report
-- Purpose: Identify reservations with unpaid or pending payments
SELECT 
    guest_name,
    room_number,
    room_type,
    check_in_date,
    check_out_date,
    expected_amount,
    COALESCE(paid_amount, 0) as paid_amount,
    expected_amount - COALESCE(paid_amount, 0) as balance_due,
    payment_summary
FROM financial_reservation_view
WHERE payment_status IS NULL OR payment_status != 'Completed'
ORDER BY balance_due DESC
LIMIT 10;

-- Query 1.2: Revenue Analysis by Room Type
-- Purpose: Analyze revenue performance by room type including discounts
SELECT 
    room_type,
    COUNT(*) as total_reservations,
    COUNT(transactionid) as paid_reservations,
    SUM(expected_amount) as expected_revenue,
    SUM(paid_amount) as actual_revenue,
    AVG(discount) as average_discount,
    SUM(expected_amount) - SUM(paid_amount) as revenue_gap
FROM financial_reservation_view
GROUP BY room_type
ORDER BY actual_revenue DESC;

-- Query 2.1: Room Performance Summary
-- Purpose: Evaluate room utilization and revenue generation
SELECT 
    room_type,
    COUNT(*) as total_rooms,
    SUM(total_reservations) as total_bookings,
    SUM(current_occupation) as currently_occupied,
    SUM(total_revenue) as total_revenue_generated,
    AVG(price_per_night) as avg_room_price,
    ROUND(AVG(avg_discount), 2) as avg_discount_given
FROM reception_occupancy_financial_view
GROUP BY room_type
ORDER BY total_revenue_generated DESC;

-- Query 2.2: Payment Status by Room
-- Purpose: Identify rooms with pending payments for follow-up
SELECT 
    room_number,
    room_type,
    floor,
    price_per_night,
    total_reservations,
    paid_reservations,
    pending_payments,
    total_revenue,
    CASE 
        WHEN pending_payments > 0 THEN 'Action Required'
        WHEN total_reservations > paid_reservations THEN 'Check Required'
        ELSE 'OK'
    END as payment_status_alert
FROM reception_occupancy_financial_view
WHERE pending_payments > 0 OR (total_reservations > paid_reservations)
ORDER BY pending_payments DESC, room_number
LIMIT 15;