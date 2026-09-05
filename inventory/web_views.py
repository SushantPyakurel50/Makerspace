"""
Web GUI presentation layer.

Thin, server-rendered views that call the same business service layer
(services.py) and query layer (queries.py) used by the REST API - so the
GUI and the JSON API never drift out of sync with each other.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from . import queries
from .models import Category, Member, Equipment, Booking, MaintenanceRecord
from .forms import CategoryForm, MemberForm, EquipmentForm, BookingForm, MaintenanceRecordForm
from .services import (
    CategoryService, MemberService, EquipmentService,
    MaintenanceService, BookingService, BookingError,
)


def dashboard(request):
    context = {
        "member_count": Member.objects.count(),
        "equipment_count": Equipment.objects.count(),
        "active_bookings": Booking.objects.filter(status=Booking.Status.ACTIVE).count(),
        "overdue_count": len(queries.query_overdue_bookings_report()),
    }
    return render(request, "inventory/dashboard.html", context)


# ------------------------------ Category ---------------------------------

def category_list(request):
    return render(request, "inventory/category_list.html", {
        "categories": CategoryService.list_categories(),
    })


def category_form(request, category_id=None):
    instance = get_object_or_404(Category, pk=category_id) if category_id else None
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Category saved.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=instance)
    return render(request, "inventory/generic_form.html", {
        "form": form, "title": "Category", "back_url": "category_list",
    })


@require_POST
def category_delete(request, category_id):
    CategoryService.delete_category(category_id)
    messages.success(request, "Category deleted.")
    return redirect("category_list")


# ------------------------------- Member -----------------------------------

def member_list(request):
    return render(request, "inventory/member_list.html", {
        "members": MemberService.list_members(),
    })


def member_form(request, member_id=None):
    instance = get_object_or_404(Member, pk=member_id) if member_id else None
    if request.method == "POST":
        form = MemberForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Member saved.")
            return redirect("member_list")
    else:
        form = MemberForm(instance=instance)
    return render(request, "inventory/generic_form.html", {
        "form": form, "title": "Member", "back_url": "member_list",
    })


@require_POST
def member_delete(request, member_id):
    MemberService.delete_member(member_id)
    messages.success(request, "Member deleted.")
    return redirect("member_list")


def member_bookings(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    rows = queries.query_member_bookings(member_id)
    return render(request, "inventory/member_bookings.html", {
        "member": member, "rows": rows,
    })


# ------------------------------ Equipment ----------------------------------

def equipment_list(request):
    return render(request, "inventory/equipment_list.html", {
        "equipment_items": EquipmentService.list_equipment(),
    })


def equipment_form(request, equipment_id=None):
    instance = get_object_or_404(Equipment, pk=equipment_id) if equipment_id else None
    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment saved.")
            return redirect("equipment_list")
    else:
        form = EquipmentForm(instance=instance)
    return render(request, "inventory/generic_form.html", {
        "form": form, "title": "Equipment", "back_url": "equipment_list",
    })


@require_POST
def equipment_delete(request, equipment_id):
    EquipmentService.delete_equipment(equipment_id)
    messages.success(request, "Equipment deleted.")
    return redirect("equipment_list")


def equipment_maintenance(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    records = queries.query_maintenance_history(equipment_id)
    return render(request, "inventory/equipment_maintenance.html", {
        "equipment": equipment, "records": records,
    })


# ------------------------------- Booking -----------------------------------

def booking_list(request):
    return render(request, "inventory/booking_list.html", {
        "bookings": BookingService.list_bookings(),
    })


def booking_form(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                BookingService.create_booking(
                    member_id=form.cleaned_data["member"].member_id,
                    equipment_id=form.cleaned_data["equipment"].equipment_id,
                    due_date=form.cleaned_data["due_date"],
                )
                messages.success(request, "Booking created.")
                return redirect("booking_list")
            except BookingError as exc:
                messages.error(request, str(exc))
    else:
        form = BookingForm()
    return render(request, "inventory/generic_form.html", {
        "form": form, "title": "Booking", "back_url": "booking_list",
    })


@require_POST
def booking_return(request, booking_id):
    try:
        BookingService.return_equipment(booking_id)
        messages.success(
            request,
            "Return recorded. Late fee & equipment status are finalizing in the background.",
        )
    except BookingError as exc:
        messages.error(request, str(exc))
    return redirect("booking_list")


@require_POST
def booking_cancel(request, booking_id):
    try:
        BookingService.cancel_booking(booking_id)
        messages.success(request, "Booking cancelled.")
    except BookingError as exc:
        messages.error(request, str(exc))
    return redirect("booking_list")


@require_POST
def booking_delete(request, booking_id):
    BookingService.delete_booking(booking_id)
    messages.success(request, "Booking deleted.")
    return redirect("booking_list")


# --------------------------- Maintenance Record -------------------------------

def maintenance_list(request):
    return render(request, "inventory/maintenance_list.html", {
        "records": MaintenanceService.list_records(),
    })


def maintenance_form(request):
    if request.method == "POST":
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            MaintenanceService.create_record(**form.cleaned_data)
            messages.success(request, "Maintenance record logged; equipment marked under maintenance.")
            return redirect("maintenance_list")
    else:
        form = MaintenanceRecordForm()
    return render(request, "inventory/generic_form.html", {
        "form": form, "title": "Maintenance Record", "back_url": "maintenance_list",
    })


@require_POST
def maintenance_resolve(request, record_id):
    MaintenanceService.resolve_record(record_id)
    messages.success(request, "Marked resolved; equipment is available again.")
    return redirect("maintenance_list")


# --------------------------------- Reports -----------------------------------

def report_overdue(request):
    return render(request, "inventory/report_overdue.html", {
        "rows": queries.query_overdue_bookings_report(),
    })


def report_utilization(request):
    return render(request, "inventory/report_utilization.html", {
        "rows": queries.query_equipment_utilization_report(),
    })
