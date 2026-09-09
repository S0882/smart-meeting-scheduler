from typing import List
from models.week_schedule import WeekSchedule


class MonthSchedule:
    """Represents a collection of WeekSchedules for a full month."""

    def __init__(self, year: int, month: int, weeks: List[WeekSchedule] = None):
        self.year = year
        self.month = month
        self.weeks = weeks or []

    def add_week(self, week_schedule: WeekSchedule):
        """Adds a WeekSchedule instance to the month."""
        self.weeks.append(week_schedule)

    def __repr__(self):
        return f"<MonthSchedule {self.year}-{self.month:02d}: {len(self.weeks)} weeks included>"
