import logging
from datetime import timedelta, date
from typing import List
from models.event import Event
from models.week_schedule import WeekSchedule
from models.day_schedule import DaySchedule
from services.availability_finder import AvailabilityFinder

# Initialize module-specific logger
logger = logging.getLogger(__name__)


class WeekFinder:
    """Service to calculate availability across a full work week (5 days)."""

    def __init__(self, base_finder: AvailabilityFinder):
        self.base_finder = base_finder

    def find_for_week(
        self,
        events: List[Event],
        target_people: List[str],
        duration_minutes: int,
        start_of_week: date
    ) -> WeekSchedule:
        week_number = start_of_week.isocalendar()[1]
        logger.debug(
            f"Starting weekly availability search for week {week_number} starting on {start_of_week} "
            f"for participants: {target_people}"
        )

        week_schedule = WeekSchedule(week_number=week_number)

        for day_offset in range(5):
            current_date = start_of_week + timedelta(days=day_offset)
            logger.debug(f"Processing date {current_date} for weekly search.")

            # Calculate available slots specifically for current_date using base_finder
            free_slots = self.base_finder.find_available_slots(
                target_people=target_people,
                duration_minutes=duration_minutes,
                target_date=current_date
            )

            day_schedule = DaySchedule(day_date=current_date, available_slots=free_slots)
            week_schedule.add_day(day_schedule)

        logger.info(f"Weekly search completed for week {week_number}. Processed 5 work days.")
        return week_schedule