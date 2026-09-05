"""
Background / asynchronous processing component.

Assignment requirement: "A background task or asynchronous processing
component that updates a database table based on a client request."

Trigger: when a member returns a piece of equipment (BookingService
.return_equipment), the HTTP response is sent back immediately, and this
module's worker thread runs the slower follow-up work in the background:

    1. Recompute whether the return was late, and if so, calculate and
       store a late fee on the Booking row.
    2. Flip the Equipment row's status back to AVAILABLE (unless it was
       simultaneously flagged for maintenance).

A plain Python `threading.Thread` is used so the task genuinely runs
off the request/response cycle without requiring an external broker
(Celery + Redis/RabbitMQ) to be installed for the assignment demo. In a
larger production deployment this function body could be swapped for a
Celery task with no change to the calling code in services.py.

Each worker opens its own database connection (Django connections are not
thread-safe to share) and closes it when done.
"""

import threading
import time
from decimal import Decimal

from django.db import connections
from django.utils import timezone

LATE_FEE_PER_DAY = Decimal("2.50")


def _process_return(booking_id):
    """The actual background unit of work. Runs on a worker thread."""
    # Import here to avoid a circular import between services.py and tasks.py.
    from .models import Booking, Equipment

    # Simulate a slower operation (e.g. calling an external billing system)
    # so the asynchronous behaviour is visible during a demo.
    time.sleep(2)

    try:
        booking = Booking.objects.select_related("equipment").get(pk=booking_id)

        if booking.return_date and booking.due_date and booking.return_date > booking.due_date:
            days_late = (booking.return_date - booking.due_date).days
            days_late = max(days_late, 1)
            booking.late_fee = LATE_FEE_PER_DAY * days_late
            booking.status = Booking.Status.RETURNED
            booking.save(update_fields=["late_fee", "status"])

        equipment = booking.equipment
        if equipment.status != Equipment.Status.MAINTENANCE:
            equipment.status = Equipment.Status.AVAILABLE
            equipment.save(update_fields=["status"])
    finally:
        # Each new thread gets its own DB connection; close it explicitly
        # when the background unit of work is done.
        connections.close_all()


def process_equipment_return_async(booking_id):
    """Kick off background processing for a just-returned booking."""
    worker = threading.Thread(
        target=_process_return, args=(booking_id,), daemon=True
    )
    worker.start()
    return worker
