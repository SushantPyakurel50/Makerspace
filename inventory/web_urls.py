from django.urls import path
from . import web_views

urlpatterns = [
    path("", web_views.dashboard, name="dashboard"),

    # Category
    path("categories/", web_views.category_list, name="category_list"),
    path("categories/new/", web_views.category_form, name="category_new"),
    path("categories/<int:category_id>/edit/", web_views.category_form, name="category_edit"),
    path("categories/<int:category_id>/delete/", web_views.category_delete, name="category_delete"),

    # Member
    path("members/", web_views.member_list, name="member_list"),
    path("members/new/", web_views.member_form, name="member_new"),
    path("members/<int:member_id>/edit/", web_views.member_form, name="member_edit"),
    path("members/<int:member_id>/delete/", web_views.member_delete, name="member_delete"),
    path("members/<int:member_id>/bookings/", web_views.member_bookings, name="member_bookings"),

    # Equipment
    path("equipment/", web_views.equipment_list, name="equipment_list"),
    path("equipment/new/", web_views.equipment_form, name="equipment_new"),
    path("equipment/<int:equipment_id>/edit/", web_views.equipment_form, name="equipment_edit"),
    path("equipment/<int:equipment_id>/delete/", web_views.equipment_delete, name="equipment_delete"),
    path("equipment/<int:equipment_id>/maintenance/", web_views.equipment_maintenance, name="equipment_maintenance"),

    # Booking
    path("bookings/", web_views.booking_list, name="booking_list"),
    path("bookings/new/", web_views.booking_form, name="booking_new"),
    path("bookings/<int:booking_id>/return/", web_views.booking_return, name="booking_return"),
    path("bookings/<int:booking_id>/cancel/", web_views.booking_cancel, name="booking_cancel"),
    path("bookings/<int:booking_id>/delete/", web_views.booking_delete, name="booking_delete"),

    # Maintenance
    path("maintenance/", web_views.maintenance_list, name="maintenance_list"),
    path("maintenance/new/", web_views.maintenance_form, name="maintenance_new"),
    path("maintenance/<int:record_id>/resolve/", web_views.maintenance_resolve, name="maintenance_resolve"),

    # Reports (the 2 complex queries)
    path("reports/overdue/", web_views.report_overdue, name="report_overdue"),
    path("reports/utilization/", web_views.report_utilization, name="report_utilization"),
]
