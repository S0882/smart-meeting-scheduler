from typing import List
from models.day_schedule import DaySchedule


class WeekSchedule:
    """Represents a collection of DaySchedules for a full week."""

    def __init__(self, week_number: int, days: List[DaySchedule] = None):
        self.week_number = week_number
        self.days = days or []

    def add_day(self, day_schedule: DaySchedule):
        """Adds a DaySchedule instance to the week."""
        self.days.append(day_schedule)

    def __repr__(self):
        return f"<WeekSchedule Week {self.week_number}: {len(self.days)} days included>"
