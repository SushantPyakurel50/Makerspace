from django.urls import path
from . import api_views

urlpatterns = [
    # Category CRUD
    path("categories/", api_views.category_list),
    path("categories/<int:category_id>/", api_views.category_detail),

    # Member CRUD
    path("members/", api_views.member_list),
    path("members/<int:member_id>/", api_views.member_detail),

    # Equipment CRUD
    path("equipment/", api_views.equipment_list),
    path("equipment/<int:equipment_id>/", api_views.equipment_detail),

    # Booking CRUD + actions
    path("bookings/", api_views.booking_list),
    path("bookings/<int:booking_id>/", api_views.booking_detail),
    path("bookings/<int:booking_id>/return/", api_views.booking_return),
    path("bookings/<int:booking_id>/cancel/", api_views.booking_cancel),

    # Maintenance Record CRUD
    path("maintenance/", api_views.maintenance_list),
    path("maintenance/<int:record_id>/", api_views.maintenance_detail),

    # Queries: navigate related entities
    path("queries/members/<int:member_id>/bookings/", api_views.query_member_bookings_view),
    path("queries/categories/<int:category_id>/equipment/", api_views.query_equipment_by_category_view),
    path("queries/equipment/<int:equipment_id>/maintenance/", api_views.query_maintenance_history_view),

    # Queries: complex, multi-entity
    path("queries/overdue-bookings/", api_views.query_overdue_bookings_view),
    path("queries/equipment-utilization/", api_views.query_equipment_utilization_view),
]
