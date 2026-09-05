"""
Data Transfer Objects (DTOs).

These DRF serializers are the boundary objects that move data between the
server (ORM model instances) and clients (JSON over HTTP). They are kept
separate from the ORM models so that the shape of the wire format can
evolve independently of the database schema, and so that read-only /
"nested" query results (see queries.py) have a clean DTO to render into.
"""

from rest_framework import serializers
from .models import Category, Member, Equipment, Booking, MaintenanceRecord


class CategoryDTO(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "description"]


class MemberDTO(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Member
        fields = [
            "member_id", "first_name", "last_name", "full_name",
            "email", "phone", "membership_type", "join_date",
        ]


class EquipmentDTO(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = Equipment
        fields = [
            "equipment_id", "name", "category", "category_name",
            "serial_number", "status", "purchase_date", "replacement_cost",
        ]


class BookingDTO(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "booking_id", "member", "member_name", "equipment", "equipment_name",
            "booking_date", "due_date", "return_date", "status", "late_fee",
        ]
        read_only_fields = ["booking_date", "status", "late_fee"]


class MaintenanceRecordDTO(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            "record_id", "equipment", "equipment_name", "reported_date",
            "description", "resolved_date", "cost",
        ]
        read_only_fields = ["reported_date"]


# ---------------------------------------------------------------------
# DTOs for the "navigation" and "complex" query results (queries.py).
# These don't map 1:1 onto a single model, so they are plain serializers.
# ---------------------------------------------------------------------

class MemberBookingsDTO(serializers.Serializer):
    booking_id = serializers.IntegerField()
    equipment_name = serializers.CharField()
    category_name = serializers.CharField()
    booking_date = serializers.DateTimeField()
    due_date = serializers.DateTimeField()
    status = serializers.CharField()


class OverdueBookingDTO(serializers.Serializer):
    booking_id = serializers.IntegerField()
    member_name = serializers.CharField()
    member_email = serializers.EmailField()
    equipment_name = serializers.CharField()
    category_name = serializers.CharField()
    due_date = serializers.DateTimeField()
    days_overdue = serializers.IntegerField()


class EquipmentUtilizationDTO(serializers.Serializer):
    equipment_id = serializers.IntegerField()
    equipment_name = serializers.CharField()
    category_name = serializers.CharField()
    total_bookings = serializers.IntegerField()
    late_returns = serializers.IntegerField()
    total_late_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
