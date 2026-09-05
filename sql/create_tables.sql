--------------------------------------------------------------------------
-- Makerspace Equipment Booking System
-- Oracle Database DDL
--
-- Run this as the application schema user (e.g. makerspace_app) inside
-- Oracle SQL Developer, or via SQL*Plus / sqlcl:
--     sqlplus makerspace_app/password@localhost:1521/XEPDB1 @create_tables.sql
--
-- Note: if you let Django create the schema instead via
--     python manage.py migrate
-- you do NOT need to run this script too - it is provided as a
-- required, explicit submission artifact and as documentation of the
-- exact schema the ORM models map onto.
--------------------------------------------------------------------------

-- Clean slate (ignore errors if objects do not exist yet)
BEGIN EXECUTE IMMEDIATE 'DROP TABLE maintenance_record CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE booking CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE equipment CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE member CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE category CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE category_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE member_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE equipment_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE booking_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE maintenance_record_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

--------------------------------------------------------------------------
-- CATEGORY
--------------------------------------------------------------------------
CREATE TABLE category (
    category_id     NUMBER(10)      NOT NULL,
    category_name   VARCHAR2(100)   NOT NULL,
    description     VARCHAR2(500)   DEFAULT '' ,
    CONSTRAINT pk_category PRIMARY KEY (category_id),
    CONSTRAINT uq_category_name UNIQUE (category_name)
);

CREATE SEQUENCE category_seq START WITH 1 INCREMENT BY 1;

--------------------------------------------------------------------------
-- MEMBER
--------------------------------------------------------------------------
CREATE TABLE member (
    member_id           NUMBER(10)      NOT NULL,
    first_name          VARCHAR2(100)   NOT NULL,
    last_name           VARCHAR2(100)   NOT NULL,
    email                VARCHAR2(254)   NOT NULL,
    phone                VARCHAR2(20)    DEFAULT '',
    membership_type      VARCHAR2(20)    DEFAULT 'STUDENT' NOT NULL,
    join_date            DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_member PRIMARY KEY (member_id),
    CONSTRAINT uq_member_email UNIQUE (email),
    CONSTRAINT ck_member_type CHECK (membership_type IN ('STUDENT','STAFF','COMMUNITY'))
);

CREATE SEQUENCE member_seq START WITH 1 INCREMENT BY 1;

--------------------------------------------------------------------------
-- EQUIPMENT
--------------------------------------------------------------------------
CREATE TABLE equipment (
    equipment_id        NUMBER(10)      NOT NULL,
    name                 VARCHAR2(150)   NOT NULL,
    category_id          NUMBER(10)      NOT NULL,
    serial_number         VARCHAR2(100)   NOT NULL,
    status                VARCHAR2(20)    DEFAULT 'AVAILABLE' NOT NULL,
    purchase_date         DATE            NOT NULL,
    replacement_cost      NUMBER(10,2)    NOT NULL,
    CONSTRAINT pk_equipment PRIMARY KEY (equipment_id),
    CONSTRAINT uq_equipment_serial UNIQUE (serial_number),
    CONSTRAINT fk_equipment_category FOREIGN KEY (category_id)
        REFERENCES category (category_id),
    CONSTRAINT ck_equipment_status CHECK (status IN ('AVAILABLE','BOOKED','MAINTENANCE','RETIRED'))
);

CREATE SEQUENCE equipment_seq START WITH 1 INCREMENT BY 1;
CREATE INDEX idx_equipment_category ON equipment (category_id);

--------------------------------------------------------------------------
-- BOOKING
--------------------------------------------------------------------------
CREATE TABLE booking (
    booking_id       NUMBER(10)      NOT NULL,
    member_id         NUMBER(10)      NOT NULL,
    equipment_id      NUMBER(10)      NOT NULL,
    booking_date      TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    due_date          TIMESTAMP       NOT NULL,
    return_date       TIMESTAMP,
    status             VARCHAR2(20)    DEFAULT 'ACTIVE' NOT NULL,
    late_fee           NUMBER(8,2)     DEFAULT 0 NOT NULL,
    CONSTRAINT pk_booking PRIMARY KEY (booking_id),
    CONSTRAINT fk_booking_member FOREIGN KEY (member_id)
        REFERENCES member (member_id) ON DELETE CASCADE,
    CONSTRAINT fk_booking_equipment FOREIGN KEY (equipment_id)
        REFERENCES equipment (equipment_id) ON DELETE CASCADE,
    CONSTRAINT ck_booking_status CHECK (status IN ('ACTIVE','RETURNED','OVERDUE','CANCELLED'))
);

CREATE SEQUENCE booking_seq START WITH 1 INCREMENT BY 1;
CREATE INDEX idx_booking_member ON booking (member_id);
CREATE INDEX idx_booking_equipment ON booking (equipment_id);
CREATE INDEX idx_booking_status ON booking (status);

--------------------------------------------------------------------------
-- MAINTENANCE_RECORD
--------------------------------------------------------------------------
CREATE TABLE maintenance_record (
    record_id         NUMBER(10)      NOT NULL,
    equipment_id       NUMBER(10)      NOT NULL,
    reported_date       TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    description          VARCHAR2(1000)  NOT NULL,
    resolved_date        TIMESTAMP,
    cost                  NUMBER(8,2),
    CONSTRAINT pk_maintenance_record PRIMARY KEY (record_id),
    CONSTRAINT fk_maintenance_equipment FOREIGN KEY (equipment_id)
        REFERENCES equipment (equipment_id) ON DELETE CASCADE
);

CREATE SEQUENCE maintenance_record_seq START WITH 1 INCREMENT BY 1;
CREATE INDEX idx_maintenance_equipment ON maintenance_record (equipment_id);

--------------------------------------------------------------------------
-- Auto-increment triggers (Oracle < 12c style, portable across versions)
--------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_category_pk
BEFORE INSERT ON category
FOR EACH ROW
WHEN (NEW.category_id IS NULL)
BEGIN
    :NEW.category_id := category_seq.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_member_pk
BEFORE INSERT ON member
FOR EACH ROW
WHEN (NEW.member_id IS NULL)
BEGIN
    :NEW.member_id := member_seq.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_equipment_pk
BEFORE INSERT ON equipment
FOR EACH ROW
WHEN (NEW.equipment_id IS NULL)
BEGIN
    :NEW.equipment_id := equipment_seq.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_booking_pk
BEFORE INSERT ON booking
FOR EACH ROW
WHEN (NEW.booking_id IS NULL)
BEGIN
    :NEW.booking_id := booking_seq.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_maintenance_pk
BEFORE INSERT ON maintenance_record
FOR EACH ROW
WHEN (NEW.record_id IS NULL)
BEGIN
    :NEW.record_id := maintenance_record_seq.NEXTVAL;
END;
/

COMMIT;
