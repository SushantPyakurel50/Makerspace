"""
REST API layer (presentation layer for JSON clients).

These views are intentionally thin: they parse the request, call into the
business service layer (services.py) or the query layer (queries.py), and
serialize the result through the DTOs (serializers.py). No business logic
or ORM queries live here directly.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from . import queries
from .services import (
    MemberService, CategoryService, EquipmentService,
    MaintenanceService, BookingService, BookingError,
)
from .serializers import (
    MemberDTO, CategoryDTO, EquipmentDTO, BookingDTO, MaintenanceRecordDTO,
    MemberBookingsDTO, OverdueBookingDTO, EquipmentUtilizationDTO,
)


# Explicit views are written per-entity below (rather than a generic CRUD
# factory) so each one stays easy to read/grade and can customize error
# handling where needed (e.g. Booking's business-rule errors).

# ----------------------------- Category -------------------------------

@api_view(["GET", "POST"])
def category_list(request):
    if request.method == "GET":
        dto = CategoryDTO(CategoryService.list_categories(), many=True)
        return Response(dto.data)

    dto = CategoryDTO(data=request.data)
    dto.is_valid(raise_exception=True)
    category = CategoryService.create_category(**dto.validated_data)
    return Response(CategoryDTO(category).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def category_detail(request, category_id):
    if request.method == "GET":
        category = CategoryService.get_category(category_id)
        return Response(CategoryDTO(category).data)

    if request.method == "PUT":
        dto = CategoryDTO(data=request.data, partial=True)
        dto.is_valid(raise_exception=True)
        category = CategoryService.update_category(category_id, **dto.validated_data)
        return Response(CategoryDTO(category).data)

    CategoryService.delete_category(category_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------------------ Member ---------------------------------

@api_view(["GET", "POST"])
def member_list(request):
    if request.method == "GET":
        dto = MemberDTO(MemberService.list_members(), many=True)
        return Response(dto.data)

    dto = MemberDTO(data=request.data)
    dto.is_valid(raise_exception=True)
    member = MemberService.create_member(**dto.validated_data)
    return Response(MemberDTO(member).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def member_detail(request, member_id):
    if request.method == "GET":
        member = MemberService.get_member(member_id)
        return Response(MemberDTO(member).data)

    if request.method == "PUT":
        dto = MemberDTO(data=request.data, partial=True)
        dto.is_valid(raise_exception=True)
        member = MemberService.update_member(member_id, **dto.validated_data)
        return Response(MemberDTO(member).data)

    MemberService.delete_member(member_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------- Equipment --------------------------------

@api_view(["GET", "POST"])
def equipment_list(request):
    if request.method == "GET":
        dto = EquipmentDTO(EquipmentService.list_equipment(), many=True)
        return Response(dto.data)

    dto = EquipmentDTO(data=request.data)
    dto.is_valid(raise_exception=True)
    equipment = EquipmentService.create_equipment(**dto.validated_data)
    return Response(EquipmentDTO(equipment).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def equipment_detail(request, equipment_id):
    if request.method == "GET":
        equipment = EquipmentService.get_equipment(equipment_id)
        return Response(EquipmentDTO(equipment).data)

    if request.method == "PUT":
        dto = EquipmentDTO(data=request.data, partial=True)
        dto.is_valid(raise_exception=True)
        equipment = EquipmentService.update_equipment(equipment_id, **dto.validated_data)
        return Response(EquipmentDTO(equipment).data)

    EquipmentService.delete_equipment(equipment_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------------------ Booking ----------------------------------

@api_view(["GET", "POST"])
def booking_list(request):
    if request.method == "GET":
        dto = BookingDTO(BookingService.list_bookings(), many=True)
        return Response(dto.data)

    dto = BookingDTO(data=request.data)
    dto.is_valid(raise_exception=True)
    try:
        booking = BookingService.create_booking(
            member_id=dto.validated_data["member"].pk,
            equipment_id=dto.validated_data["equipment"].pk,
            due_date=dto.validated_data["due_date"],
        )
    except BookingError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    except ObjectDoesNotExist as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    return Response(BookingDTO(booking).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
def booking_detail(request, booking_id):
    if request.method == "GET":
        booking = BookingService.get_booking(booking_id)
        return Response(BookingDTO(booking).data)

    BookingService.delete_booking(booking_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def booking_return(request, booking_id):
    """
    Client-triggered action that hands off work to the background task
    (see tasks.py). Responds immediately with the booking marked RETURNED;
    late-fee calculation and equipment status update happen asynchronously.
    """
    try:
        booking = BookingService.return_equipment(booking_id)
    except BookingError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    except ObjectDoesNotExist:
        return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            **BookingDTO(booking).data,
            "message": "Return recorded. Late fee and equipment status are "
                       "being finalized in the background.",
        }
    )


@api_view(["POST"])
def booking_cancel(request, booking_id):
    try:
        booking = BookingService.cancel_booking(booking_id)
    except BookingError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    except ObjectDoesNotExist:
        return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(BookingDTO(booking).data)


# -------------------------- Maintenance Record ----------------------------

@api_view(["GET", "POST"])
def maintenance_list(request):
    if request.method == "GET":
        dto = MaintenanceRecordDTO(MaintenanceService.list_records(), many=True)
        return Response(dto.data)

    dto = MaintenanceRecordDTO(data=request.data)
    dto.is_valid(raise_exception=True)
    record = MaintenanceService.create_record(**dto.validated_data)
    return Response(MaintenanceRecordDTO(record).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def maintenance_detail(request, record_id):
    if request.method == "GET":
        record = MaintenanceService.get_record(record_id)
        return Response(MaintenanceRecordDTO(record).data)

    if request.method == "PUT":
        dto = MaintenanceRecordDTO(data=request.data, partial=True)
        dto.is_valid(raise_exception=True)
        record = MaintenanceService.resolve_record(
            record_id, cost=dto.validated_data.get("cost")
        )
        return Response(MaintenanceRecordDTO(record).data)

    MaintenanceService.delete_record(record_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
# Query endpoints (3 navigation queries + 2 complex multi-entity queries)
# ---------------------------------------------------------------------

@api_view(["GET"])
def query_member_bookings_view(request, member_id):
    data = queries.query_member_bookings(member_id)
    return Response(MemberBookingsDTO(data, many=True).data)


@api_view(["GET"])
def query_equipment_by_category_view(request, category_id):
    items = queries.query_equipment_by_category(category_id)
    return Response(EquipmentDTO(items, many=True).data)


@api_view(["GET"])
def query_maintenance_history_view(request, equipment_id):
    items = queries.query_maintenance_history(equipment_id)
    return Response(MaintenanceRecordDTO(items, many=True).data)


@api_view(["GET"])
def query_overdue_bookings_view(request):
    data = queries.query_overdue_bookings_report()
    return Response(OverdueBookingDTO(data, many=True).data)


@api_view(["GET"])
def query_equipment_utilization_view(request):
    data = queries.query_equipment_utilization_report()
    return Response(EquipmentUtilizationDTO(data, many=True).data)
