"""
Business service layer.

Views (API and web) call into these services rather than talking to the
ORM directly. This keeps business rules (availability checks, fee
calculation, status transitions) in one place, independent of whether the
request came from the REST API or the server-rendered GUI.
"""

from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .models import Member, Category, Equipment, Booking, MaintenanceRecord
from .tasks import process_equipment_return_async

LATE_FEE_PER_DAY = Decimal("2.50")


class BookingError(Exception):
    """Raised when a booking request violates a business rule."""


class MemberService:
    @staticmethod
    def list_members():
        return Member.objects.all()

    @staticmethod
    def get_member(member_id):
        return Member.objects.get(pk=member_id)

    @staticmethod
    def create_member(**kwargs):
        return Member.objects.create(**kwargs)

    @staticmethod
    def update_member(member_id, **kwargs):
        member = Member.objects.get(pk=member_id)
        for field, value in kwargs.items():
            setattr(member, field, value)
        member.save()
        return member

    @staticmethod
    def delete_member(member_id):
        Member.objects.get(pk=member_id).delete()


class CategoryService:
    @staticmethod
    def list_categories():
        return Category.objects.all()

    @staticmethod
    def get_category(category_id):
        return Category.objects.get(pk=category_id)

    @staticmethod
    def create_category(**kwargs):
        return Category.objects.create(**kwargs)

    @staticmethod
    def update_category(category_id, **kwargs):
        category = Category.objects.get(pk=category_id)
        for field, value in kwargs.items():
            setattr(category, field, value)
        category.save()
        return category

    @staticmethod
    def delete_category(category_id):
        Category.objects.get(pk=category_id).delete()


class EquipmentService:
    @staticmethod
    def list_equipment():
        return Equipment.objects.select_related("category").all()

    @staticmethod
    def get_equipment(equipment_id):
        return Equipment.objects.select_related("category").get(pk=equipment_id)

    @staticmethod
    def create_equipment(**kwargs):
        return Equipment.objects.create(**kwargs)

    @staticmethod
    def update_equipment(equipment_id, **kwargs):
        equipment = Equipment.objects.get(pk=equipment_id)
        for field, value in kwargs.items():
            setattr(equipment, field, value)
        equipment.save()
        return equipment

    @staticmethod
    def delete_equipment(equipment_id):
        Equipment.objects.get(pk=equipment_id).delete()


class MaintenanceService:
    @staticmethod
    def list_records():
        return MaintenanceRecord.objects.select_related("equipment").all()

    @staticmethod
    def get_record(record_id):
        return MaintenanceRecord.objects.get(pk=record_id)

    @staticmethod
    @transaction.atomic
    def create_record(**kwargs):
        record = MaintenanceRecord.objects.create(**kwargs)
        # Business rule: logging a maintenance issue takes the equipment offline.
        equipment = record.equipment
        equipment.status = Equipment.Status.MAINTENANCE
        equipment.save(update_fields=["status"])
        return record

    @staticmethod
    @transaction.atomic
    def resolve_record(record_id, cost=None):
        record = MaintenanceRecord.objects.select_for_update().get(pk=record_id)
        record.resolved_date = timezone.now()
        if cost is not None:
            record.cost = cost
        record.save()
        record.equipment.status = Equipment.Status.AVAILABLE
        record.equipment.save(update_fields=["status"])
        return record

    @staticmethod
    def delete_record(record_id):
        MaintenanceRecord.objects.get(pk=record_id).delete()


class BookingService:
    """Encapsulates the booking lifecycle: create, return, cancel."""

    @staticmethod
    def list_bookings():
        return Booking.objects.select_related("member", "equipment").all()

    @staticmethod
    def get_booking(booking_id):
        return Booking.objects.select_related("member", "equipment").get(pk=booking_id)

    @staticmethod
    @transaction.atomic
    def create_booking(member_id, equipment_id, due_date):
        equipment = Equipment.objects.select_for_update().get(pk=equipment_id)

        if equipment.status != Equipment.Status.AVAILABLE:
            raise BookingError(
                f"Equipment '{equipment.name}' is not available "
                f"(current status: {equipment.get_status_display()})."
            )

        member = Member.objects.get(pk=member_id)

        booking = Booking.objects.create(
            member=member,
            equipment=equipment,
            due_date=due_date,
            status=Booking.Status.ACTIVE,
        )

        equipment.status = Equipment.Status.BOOKED
        equipment.save(update_fields=["status"])

        return booking

    @staticmethod
    @transaction.atomic
    def return_equipment(booking_id):
        """
        Client-facing action: a member returns a piece of equipment.

        This immediately marks the booking as RETURNED so the request can
        respond quickly, then hands off the late-fee calculation and the
        equipment-status update to a background task (see tasks.py) so the
        client is not blocked on that processing.
        """
        booking = (
            Booking.objects.select_related("equipment")
            .select_for_update()
            .get(pk=booking_id)
        )

        if booking.status not in (Booking.Status.ACTIVE, Booking.Status.OVERDUE):
            raise BookingError("This booking has already been closed out.")

        booking.return_date = timezone.now()
        booking.status = Booking.Status.RETURNED
        booking.save(update_fields=["return_date", "status"])

        # Fire-and-forget background processing (see inventory/tasks.py).
        process_equipment_return_async(booking_id)

        return booking

    @staticmethod
    @transaction.atomic
    def cancel_booking(booking_id):
        booking = (
            Booking.objects.select_related("equipment")
            .select_for_update()
            .get(pk=booking_id)
        )
        if booking.status != Booking.Status.ACTIVE:
            raise BookingError("Only an active booking can be cancelled.")

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])

        booking.equipment.status = Equipment.Status.AVAILABLE
        booking.equipment.save(update_fields=["status"])

        return booking

    @staticmethod
    def delete_booking(booking_id):
        Booking.objects.get(pk=booking_id).delete()
