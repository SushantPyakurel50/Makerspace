--------------------------------------------------------------------------
-- Sample data for demo / screenshots. Run after create_tables.sql.
--------------------------------------------------------------------------

INSERT INTO category (category_name, description) VALUES ('3D Printing', 'FDM and resin printers, filament tools');
INSERT INTO category (category_name, description) VALUES ('Woodworking', 'Saws, sanders, and hand tools');
INSERT INTO category (category_name, description) VALUES ('Electronics', 'Soldering stations, oscilloscopes, multimeters');

INSERT INTO member (first_name, last_name, email, phone, membership_type) VALUES ('Asha', 'Rai', 'asha.rai@example.com', '9800000001', 'STUDENT');
INSERT INTO member (first_name, last_name, email, phone, membership_type) VALUES ('Bikash', 'Thapa', 'bikash.thapa@example.com', '9800000002', 'STAFF');
INSERT INTO member (first_name, last_name, email, phone, membership_type) VALUES ('Sunita', 'Gurung', 'sunita.gurung@example.com', '9800000003', 'COMMUNITY');

INSERT INTO equipment (name, category_id, serial_number, status, purchase_date, replacement_cost)
    VALUES ('Prusa MK4 3D Printer', 1, 'SN-3DP-001', 'AVAILABLE', DATE '2024-02-10', 899.00);
INSERT INTO equipment (name, category_id, serial_number, status, purchase_date, replacement_cost)
    VALUES ('Resin Printer Elegoo', 1, 'SN-3DP-002', 'AVAILABLE', DATE '2024-05-01', 320.00);
INSERT INTO equipment (name, category_id, serial_number, status, purchase_date, replacement_cost)
    VALUES ('Table Saw DeWalt', 2, 'SN-WW-001', 'AVAILABLE', DATE '2023-08-15', 650.00);
INSERT INTO equipment (name, category_id, serial_number, status, purchase_date, replacement_cost)
    VALUES ('Soldering Station Hakko', 3, 'SN-EL-001', 'AVAILABLE', DATE '2024-01-20', 150.00);

INSERT INTO booking (member_id, equipment_id, booking_date, due_date, status)
    VALUES (1, 1, SYSTIMESTAMP - 5, SYSTIMESTAMP - 2, 'OVERDUE');
INSERT INTO booking (member_id, equipment_id, booking_date, due_date, status)
    VALUES (2, 3, SYSTIMESTAMP - 1, SYSTIMESTAMP + 2, 'ACTIVE');

INSERT INTO maintenance_record (equipment_id, reported_date, description)
    VALUES (2, SYSTIMESTAMP - 10, 'Resin vat needs replacement, cracked on one edge');

COMMIT;
