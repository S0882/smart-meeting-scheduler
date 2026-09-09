import calendar
import logging
from datetime import date
from typing import List
from models.event import Event
from models.month_schedule import MonthSchedule
from services.week_finder import WeekFinder

# Initialize module-specific logger
logger = logging.getLogger(__name__)


class MonthFinder:
    """Service responsible for finding availability across a full month."""

    def __init__(self, week_finder: WeekFinder):
        self.week_finder = week_finder

    def find_for_month(
        self,
        events: List[Event],
        target_people: List[str],
        duration_minutes: int,
        year: int,
        month: int
    ) -> MonthSchedule:
        """Iterates through each week of the specified month."""
        logger.debug(
            f"Starting monthly availability search for {year}-{month:02d} "
            f"for participants: {target_people}"
        )

        month_schedule = MonthSchedule(year=year, month=month)

        # Initialize calendar with Monday as first day of the week
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.itermonthdates(year, month)

        # Get all Mondays that belong to the target month
        mondays = [d for d in month_days if d.weekday() == 0 and d.month == month]
        logger.debug(f"Found {len(mondays)} weeks starting in month {year}-{month:02d}.")

        for monday_date in mondays:
            # Delegate weekly search to WeekFinder
            week_sched = self.week_finder.find_for_week(
                events=events,
                target_people=target_people,
                duration_minutes=duration_minutes,
                start_of_week=monday_date
            )
            month_schedule.add_week(week_sched)

        logger.info(
            f"Completed monthly availability search for {year}-{month:02d}. "
            f"Processed {len(mondays)} weeks."
        )
        return month_schedule