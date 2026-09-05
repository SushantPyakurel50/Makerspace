from django import forms
from .models import Category, Member, Equipment, Booking, MaintenanceRecord


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "description"]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["first_name", "last_name", "email", "phone", "membership_type"]


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ["name", "category", "serial_number", "status", "purchase_date", "replacement_cost"]
        widgets = {"purchase_date": forms.DateInput(attrs={"type": "date"})}


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["member", "equipment", "due_date"]
        widgets = {"due_date": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ["equipment", "description"]
