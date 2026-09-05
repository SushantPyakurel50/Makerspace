from django.contrib import admin
from .models import Category, Member, Equipment, Booking, MaintenanceRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "category_name")
    search_fields = ("category_name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("member_id", "first_name", "last_name", "email", "membership_type", "join_date")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("membership_type",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("equipment_id", "name", "category", "serial_number", "status")
    list_filter = ("category", "status")
    search_fields = ("name", "serial_number")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_id", "member", "equipment", "due_date", "return_date", "status", "late_fee")
    list_filter = ("status",)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("record_id", "equipment", "reported_date", "resolved_date", "cost")
