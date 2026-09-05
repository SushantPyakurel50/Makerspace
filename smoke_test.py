import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "makerspace_project.settings")
os.environ.setdefault("DB_ENGINE", "sqlite")

import django

django.setup()

from django.test import Client
from inventory.models import Booking, Equipment

client = Client()
checks = []

def check(label, response, expected):
    ok = response.status_code == expected
    checks.append((label, response.status_code, expected, ok, response.content[:300].decode("utf-8", "replace")))

check("web dashboard", client.get("/"), 200)
check("categories list", client.get("/api/categories/"), 200)
check("members list", client.get("/api/members/"), 200)
check("equipment list", client.get("/api/equipment/"), 200)
check("bookings list", client.get("/api/bookings/"), 200)
check("maintenance list", client.get("/api/maintenance/"), 200)
check("member bookings query", client.get("/api/queries/members/1/bookings/"), 200)
check("category equipment query", client.get("/api/queries/categories/1/equipment/"), 200)
check("maintenance history query", client.get("/api/queries/equipment/2/maintenance/"), 200)
check("overdue report", client.get("/api/queries/overdue-bookings/"), 200)
check("utilization report", client.get("/api/queries/equipment-utilization/"), 200)

# Invalid booking payload should be a client error, not a server error.
check("invalid booking payload", client.post("/api/bookings/", data={}, content_type="application/json"), 400)

# Create, cancel, and return a booking through the public API.
create = client.post(
    "/api/bookings/",
    data={"member": 1, "equipment": 4, "due_date": "2099-01-01T12:00:00Z"},
    content_type="application/json",
)
check("create booking", create, 201)
if create.status_code == 201:
    booking_id = create.json()["booking_id"]
    cancel = client.post(f"/api/bookings/{booking_id}/cancel/")
    check("cancel booking", cancel, 200)

# Return the seeded active booking and allow the background worker to finish.
returned = client.post("/api/bookings/2/return/")
check("return booking", returned, 200)
time.sleep(2.5)
booking = Booking.objects.get(pk=2)
checks.append(("background return status", booking.status, "RETURNED", booking.status == "RETURNED", ""))
checks.append(("background equipment status", Equipment.objects.get(pk=3).status, "AVAILABLE", Equipment.objects.get(pk=3).status == "AVAILABLE", ""))

failed = [item for item in checks if not item[3]]
for label, actual, expected, ok, body in checks:
    print(f"{'PASS' if ok else 'FAIL'} | {label} | actual={actual} expected={expected}")
    if not ok:
        print(body)

if failed:
    raise SystemExit(f"{len(failed)} smoke test(s) failed")
print(f"All {len(checks)} smoke tests passed.")
