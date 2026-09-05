"""
ORM model classes for the Makerspace Equipment Booking System.

Schema (5 linked tables):
    Category            (1) --- (M) Equipment
    Equipment           (1) --- (M) Booking
    Member               (1) --- (M) Booking
    Equipment           (1) --- (M) MaintenanceRecord

These map directly onto the Oracle tables created by sql/create_tables.sql.
Table names are pinned explicitly (db_table) so the ORM lines up with the
hand-written DDL used for the Oracle Database backend.
"""

from django.db import models


class Category(models.Model):
    """A grouping of equipment, e.g. '3D Printing', 'Woodworking', 'Electronics'."""

    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        db_table = "category"
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


class Member(models.Model):
    """A makerspace member who can book equipment."""

    class MembershipType(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        STAFF = "STAFF", "Staff"
        COMMUNITY = "COMMUNITY", "Community"

    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    membership_type = models.CharField(
        max_length=20, choices=MembershipType.choices, default=MembershipType.STUDENT
    )
    join_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "member"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Equipment(models.Model):
    """A physical item that members can book, e.g. a 3D printer or a drill press."""

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BOOKED = "BOOKED", "Booked"
        MAINTENANCE = "MAINTENANCE", "Under Maintenance"
        RETIRED = "RETIRED", "Retired"

    equipment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="equipment_items"
    )
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    purchase_date = models.DateField()
    replacement_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "equipment"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class Booking(models.Model):
    """A member's reservation of a piece of equipment for a time window."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    booking_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="bookings")
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="bookings"
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = "booking"
        ordering = ["-booking_date"]

    def __str__(self):
        return f"Booking #{self.booking_id}: {self.equipment} -> {self.member}"


class MaintenanceRecord(models.Model):
    """A logged maintenance/repair event for a piece of equipment."""

    record_id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="maintenance_records"
    )
    reported_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=1000)
    resolved_date = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "maintenance_record"
        ordering = ["-reported_date"]

    def __str__(self):
        return f"Maintenance #{self.record_id} for {self.equipment}"
