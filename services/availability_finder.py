import logging
from datetime import datetime, timedelta
from typing import List, Optional
from models.event import Event
from models.time_slot import TimeSlot

# Initialize module-specific logger
logger = logging.getLogger(__name__)


class AvailabilityFinder:
    """Service responsible for finding available time slots for a single day."""

    def __init__(self, work_start_hour: int = 9, work_end_hour: int = 17) -> None:
        self.work_start_hour = work_start_hour
        self.work_end_hour = work_end_hour

    def find_available_slots(
        self,
        events: List[Event],
        target_people: List[str],
        duration_minutes: int
    ) -> List[TimeSlot]:
        """
        Finds available meeting slots for the specified participants in O(n) time complexity.
        """
        if not target_people or duration_minutes <= 0:
            logger.warning(
                f"Invalid parameters provided: target_people={target_people}, duration_minutes={duration_minutes}"
            )
            return []

        logger.debug(
            f"Searching daily availability for participants: {target_people} with duration: {duration_minutes} mins"
        )

        # 1. Conversion to set allows O(1) lookup time for each event check
        target_set = set(target_people)

        # 2. Linear scan O(n) to filter events for target participants
        relevant_events = [
            event for event in events
            if event.person_name in target_set
        ]
        logger.debug(f"Filtered {len(relevant_events)} relevant events out of {len(events)} total events.")

        # 3. Define working hours for the current context
        start_of_day = datetime.strptime(f"{self.work_start_hour:02d}:00", "%H:%M")
        end_of_day = datetime.strptime(f"{self.work_end_hour:02d}:00", "%H:%M")

        available_slots: List[TimeSlot] = []
        current_time = start_of_day
        meeting_delta = timedelta(minutes=duration_minutes)

        # 4. Search for valid time slots without sorting overhead
        while current_time + meeting_delta <= end_of_day:
            slot_end = current_time + meeting_delta
            has_conflict = False

            for event in relevant_events:
                # Check for overlap with existing scheduled events
                if not (slot_end <= event.start_time or current_time >= event.end_time):
                    has_conflict = True
                    break

            if not has_conflict:
                available_slots.append(
                    TimeSlot(start_time=current_time, end_time=slot_end)
                )

            # Move forward in 30-minute steps
            current_time += timedelta(minutes=30)

        logger.info(f"Daily search completed. Found {len(available_slots)} available time slot(s).")
        return available_slots