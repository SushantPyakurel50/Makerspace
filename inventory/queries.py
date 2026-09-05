"""
Query layer.

Assignment requirements met here:
  * Three queries that navigate related database entities
    (query_member_bookings, query_equipment_by_category,
     query_maintenance_history)
  * Two more complex queries involving at least three related entities
    (query_overdue_bookings_report, query_equipment_utilization_report)

All queries use the Django ORM (which compiles to SQL executed against
Oracle) rather than raw SQL, so they stay portable and injection-safe.
"""

from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import Booking, Equipment, MaintenanceRecord


# ---------------------------------------------------------------------
# 1-3: Queries that navigate related entities
# ---------------------------------------------------------------------

def query_member_bookings(member_id):
    """All bookings made by a given member, with equipment + category info.

    Navigates: Member -> Booking -> Equipment -> Category
    """
    bookings = (
        Booking.objects.filter(member_id=member_id)
        .select_related("equipment", "equipment__category")
        .order_by("-booking_date")
    )
    return [
        {
            "booking_id": b.booking_id,
            "equipment_name": b.equipment.name,
            "category_name": b.equipment.category.category_name,
            "booking_date": b.booking_date,
            "due_date": b.due_date,
            "status": b.status,
        }
        for b in bookings
    ]


def query_equipment_by_category(category_id):
    """All equipment items belonging to a given category.

    Navigates: Category -> Equipment
    """
    return Equipment.objects.filter(category_id=category_id).select_related("category")


def query_maintenance_history(equipment_id):
    """Full maintenance history for a given piece of equipment.

    Navigates: Equipment -> MaintenanceRecord
    """
    return (
        MaintenanceRecord.objects.filter(equipment_id=equipment_id)
        .select_related("equipment")
        .order_by("-reported_date")
    )


# ---------------------------------------------------------------------
# 4-5: Complex queries spanning 3+ related entities
# ---------------------------------------------------------------------

def query_overdue_bookings_report():
    """
    All currently overdue bookings, with member contact details and
    equipment/category information, and how many days overdue each is.

    Spans: Booking + Member + Equipment + Category (4 entities)
    """
    now = timezone.now()
    overdue = (
        Booking.objects.filter(
            status__in=[Booking.Status.ACTIVE, Booking.Status.OVERDUE],
            due_date__lt=now,
            return_date__isnull=True,
        )
        .select_related("member", "equipment", "equipment__category")
        .order_by("due_date")
    )

    return [
        {
            "booking_id": b.booking_id,
            "member_name": b.member.full_name,
            "member_email": b.member.email,
            "equipment_name": b.equipment.name,
            "category_name": b.equipment.category.category_name,
            "due_date": b.due_date,
            "days_overdue": (now - b.due_date).days,
        }
        for b in overdue
    ]


def query_equipment_utilization_report():
    """
    For every piece of equipment: total number of bookings, how many of
    those were returned late, and the total late fees it has generated -
    grouped alongside its category. Useful for deciding which equipment
    to retire, duplicate, or move to a stricter booking policy.

    Spans: Equipment + Category + Booking (3 entities), aggregated.
    """
    rows = (
        Equipment.objects.select_related("category")
        .annotate(
            total_bookings=Count("bookings", distinct=True),
            late_returns=Count(
                "bookings",
                filter=Q(bookings__late_fee__gt=0),
                distinct=True,
            ),
            total_late_fees=Sum("bookings__late_fee"),
        )
        .order_by("-total_bookings")
    )

    return [
        {
            "equipment_id": e.equipment_id,
            "equipment_name": e.name,
            "category_name": e.category.category_name,
            "total_bookings": e.total_bookings,
            "late_returns": e.late_returns,
            "total_late_fees": e.total_late_fees or 0,
        }
        for e in rows
    ]
