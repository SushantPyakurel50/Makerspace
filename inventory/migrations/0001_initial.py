from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("category_id", models.AutoField(primary_key=True, serialize=False)),
                ("category_name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, default="", max_length=500)),
            ],
            options={"db_table": "category", "ordering": ["category_name"]},
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("member_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(blank=True, default="", max_length=20)),
                (
                    "membership_type",
                    models.CharField(
                        choices=[
                            ("STUDENT", "Student"),
                            ("STAFF", "Staff"),
                            ("COMMUNITY", "Community"),
                        ],
                        default="STUDENT",
                        max_length=20,
                    ),
                ),
                ("join_date", models.DateField(auto_now_add=True)),
            ],
            options={"db_table": "member", "ordering": ["last_name", "first_name"]},
        ),
        migrations.CreateModel(
            name="Equipment",
            fields=[
                ("equipment_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=150)),
                ("serial_number", models.CharField(max_length=100, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AVAILABLE", "Available"),
                            ("BOOKED", "Booked"),
                            ("MAINTENANCE", "Under Maintenance"),
                            ("RETIRED", "Retired"),
                        ],
                        default="AVAILABLE",
                        max_length=20,
                    ),
                ),
                ("purchase_date", models.DateField()),
                ("replacement_cost", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="equipment_items",
                        to="inventory.category",
                    ),
                ),
            ],
            options={"db_table": "equipment", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("booking_id", models.AutoField(primary_key=True, serialize=False)),
                ("booking_date", models.DateTimeField(auto_now_add=True)),
                ("due_date", models.DateTimeField()),
                ("return_date", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("RETURNED", "Returned"),
                            ("OVERDUE", "Overdue"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="ACTIVE",
                        max_length=20,
                    ),
                ),
                ("late_fee", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="inventory.equipment",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="inventory.member",
                    ),
                ),
            ],
            options={"db_table": "booking", "ordering": ["-booking_date"]},
        ),
        migrations.CreateModel(
            name="MaintenanceRecord",
            fields=[
                ("record_id", models.AutoField(primary_key=True, serialize=False)),
                ("reported_date", models.DateTimeField(auto_now_add=True)),
                ("description", models.CharField(max_length=1000)),
                ("resolved_date", models.DateTimeField(blank=True, null=True)),
                ("cost", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_records",
                        to="inventory.equipment",
                    ),
                ),
            ],
            options={"db_table": "maintenance_record", "ordering": ["-reported_date"]},
        ),
    ]
