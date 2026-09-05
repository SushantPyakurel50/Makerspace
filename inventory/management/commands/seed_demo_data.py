"""
Seeds the database with sample data for demoing the application and
taking screenshots for the report.

Usage:
    python manage.py seed_demo_data
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import Category, Member, Equipment, Booking, MaintenanceRecord


class Command(BaseCommand):
    help = "Populate the database with sample makerspace data for demos/screenshots."

    def handle(self, *args, **options):
        now = timezone.now()

        printing, _ = Category.objects.get_or_create(
            category_name="3D Printing",
            defaults={"description": "FDM and resin printers, filament tools"},
        )
        woodworking, _ = Category.objects.get_or_create(
            category_name="Woodworking",
            defaults={"description": "Saws, sanders, and hand tools"},
        )
        electronics, _ = Category.objects.get_or_create(
            category_name="Electronics",
            defaults={"description": "Soldering stations, oscilloscopes, multimeters"},
        )

        asha, _ = Member.objects.get_or_create(
            email="asha.rai@example.com",
            defaults={"first_name": "Asha", "last_name": "Rai",
                      "phone": "9800000001", "membership_type": Member.MembershipType.STUDENT},
        )
        bikash, _ = Member.objects.get_or_create(
            email="bikash.thapa@example.com",
            defaults={"first_name": "Bikash", "last_name": "Thapa",
                      "phone": "9800000002", "membership_type": Member.MembershipType.STAFF},
        )
        sunita, _ = Member.objects.get_or_create(
            email="sunita.gurung@example.com",
            defaults={"first_name": "Sunita", "last_name": "Gurung",
                      "phone": "9800000003", "membership_type": Member.MembershipType.COMMUNITY},
        )

        printer, _ = Equipment.objects.get_or_create(
            serial_number="SN-3DP-001",
            defaults={"name": "Prusa MK4 3D Printer", "category": printing,
                      "purchase_date": "2024-02-10", "replacement_cost": 899.00},
        )
        resin_printer, _ = Equipment.objects.get_or_create(
            serial_number="SN-3DP-002",
            defaults={"name": "Resin Printer Elegoo", "category": printing,
                      "purchase_date": "2024-05-01", "replacement_cost": 320.00},
        )
        table_saw, _ = Equipment.objects.get_or_create(
            serial_number="SN-WW-001",
            defaults={"name": "Table Saw DeWalt", "category": woodworking,
                      "purchase_date": "2023-08-15", "replacement_cost": 650.00},
        )
        solder_station, _ = Equipment.objects.get_or_create(
            serial_number="SN-EL-001",
            defaults={"name": "Soldering Station Hakko", "category": electronics,
                      "purchase_date": "2024-01-20", "replacement_cost": 150.00},
        )

        # An overdue booking so the overdue report has something to show.
        overdue, created = Booking.objects.get_or_create(
            member=asha, equipment=printer,
            defaults={"due_date": now - timedelta(days=2), "status": Booking.Status.OVERDUE},
        )
        if created:
            printer.status = Equipment.Status.BOOKED
            printer.save(update_fields=["status"])

        # An active, on-time booking.
        active, created = Booking.objects.get_or_create(
            member=bikash, equipment=table_saw,
            defaults={"due_date": now + timedelta(days=2), "status": Booking.Status.ACTIVE},
        )
        if created:
            table_saw.status = Equipment.Status.BOOKED
            table_saw.save(update_fields=["status"])

        MaintenanceRecord.objects.get_or_create(
            equipment=resin_printer,
            description="Resin vat needs replacement, cracked on one edge",
        )

        self.stdout.write(self.style.SUCCESS("Sample data loaded."))
