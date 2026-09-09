from datetime import date
from typing import List
from models.time_slot import TimeSlot

class DaySchedule:
    """Represents schedule and available slots for a single specific day."""
    def __init__(self, day_date: date, available_slots: List[TimeSlot] = None):
        self.day_date = day_date
        self.available_slots = available_slots or []

    def __repr__(self):
        return f"<DaySchedule {self.day_date}: {len(self.available_slots)} slots available>"